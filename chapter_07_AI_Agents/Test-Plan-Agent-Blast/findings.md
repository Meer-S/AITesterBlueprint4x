# findings.md - Research, Discoveries, Constraints

> **Project:** Test Plan Agent (Jira ID -> formal Test Plan)
> **Stage:** Protocol 0 research pass
> **Date:** 2026-08-29
> **Rule for this file:** everything here is either verified against a real artifact in this repo, or marked `UNVERIFIED` and turned into a Discovery Question. No confident guessing.

---

## 1. Prior art found in this repository

This was the most valuable 20 minutes of the research pass. The repo already solved half of this problem, twice.

| Artifact | Path | What it gives us |
|---|---|---|
| Working Jira client | `chapter_03_Local_TC_Generator/src/jira_client.py` | A proven fetch + ADF-flatten + AC-extract path, already handling 401/404/timeout as typed exceptions |
| Credential loader | `chapter_03_Local_TC_Generator/src/config_store.py` | `.env` -> `config.json` fallback pattern with `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` |
| The 14-section plan template | `~/.claude/skills/test-plan-create-skill/assets/test-plan-template.md` | The exact output format. Do not redesign it. |
| Skill workflow | `~/.claude/skills/test-plan-create-skill/SKILL.md` | The prompt-side workflow: obtain ticket -> extract facts -> load template -> fill -> write -> summarize |
| Readiness gating | `chapter_02_Prompt_Eng/.../jira-requirement-analyzer/SKILL.md` | The "is this ticket even testable" pre-check, and the "never invent a requirement" rule |

**Discovery 1.1:** `jira_client.py` calls **`/rest/api/2/issue/{key}`**, not v3, and then still runs an ADF flattener on the result. That is a hedge: v2 on Jira Cloud returns the description as a wiki-markup **string**, v3 returns it as an **ADF object**. The code handles both (`isinstance(description_raw, dict)`). Useful defensive pattern, worth keeping.

**Discovery 1.2:** its `_extract_acceptance_criteria()` regexes the description first, then scans all fields for a key containing `"acceptance"`. That second scan will not work on Jira Cloud, because field **keys** are `customfield_10034`, not `acceptance_criteria`. The human-readable name lives elsewhere. This is a real latent bug in the prior art, and section 4 below is the fix.

**Discovery 1.3:** the whole thing is Python + `requests` + `python-dotenv`. Matching that stack keeps the course consistent.

---

## 2. Jira API surface: which one, and why

| Option | Endpoint style | Auth | Verdict |
|---|---|---|---|
| Jira Cloud REST **v3** | `/rest/api/3/...` | Basic (email + API token), base64 | **Primary.** Current API for Cloud. Description arrives as ADF. |
| Jira Cloud REST **v2** | `/rest/api/2/...` | same | **Useful escape hatch.** Same data, description as a plain wiki-markup string. Cheapest way to get readable text without a flattener. |
| Jira **Agile** | `/rest/agile/1.0/...` | same | **Supplementary.** Sprint, board, epic link. The core `/issue` endpoint does not always expose sprint cleanly. |
| Jira **Server / Data Center** | `/rest/api/2/...` | Bearer PAT | **Deferred.** Different auth, different markup. Discovery Question Q1. |
| Atlassian **MCP** (already connected in this session) | tool calls, no HTTP | OAuth handled by the client | **Optional adapter.** Zero setup, but not reproducible for course students who lack the connector. |

**Constraint 2.1:** v3 and v2 are two *representations* of the same issue, not two datasets. Fetching both for one ticket is legitimate and cheap: v3 for structure, v2 for readable description. Worth doing.

**Constraint 2.2 (UNVERIFIED, treat as design input):** the legacy `GET/POST /rest/api/3/search` endpoint has been retired on Jira Cloud in favour of `/rest/api/3/search/jql`, which is token-paginated (`nextPageToken`) rather than offset-paginated (`startAt`). Anything we build that searches must use the token form. Single-issue fetch by key is unaffected, which is another reason v1 takes a key and not a JQL query.

---

## 3. Credentials

API token: `id.atlassian.com` -> Account settings -> Security -> **Create and manage API tokens**. It is a password-equivalent secret, scoped to your whole Jira account.

```bash
# .env  (gitignored, never committed)
JIRA_URL=https://your-site.atlassian.net
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=<your-token-here>     # password-equivalent, treat as such
```

```bash
# Load once per shell for all the curls below
set -a; source .env; set +a
```

**Verify auth before anything else.** Every failure mode downstream looks the same if the token is wrong, so this call is the first thing the agent should ever make:

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Accept: application/json" \
  "$JIRA_URL/rest/api/3/myself" | jq '{accountId, displayName, emailAddress}'
```

Expected: a JSON object with your display name. `401` means the email/token pair is wrong. An HTML login page in the response body means `JIRA_URL` is wrong (you hit the web app, not the API).

**Constraint 3.1:** `curl -u user:pass` puts the credential in the process list. Fine on a laptop, wrong in CI. In CI use `-u "$JIRA_EMAIL:$JIRA_API_TOKEN"` from env only, or a `--netrc-file`. Never bake it into a script.

**Constraint 3.2:** Jira Server / Data Center does not use Basic + API token. It uses a Personal Access Token as a bearer:

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" \
  -H "Accept: application/json" \
  "$JIRA_URL/rest/api/2/myself"
```

---

## 4. The Acceptance Criteria problem (the single most important finding)

**The problem:** on Jira Cloud there is no standard "Acceptance Criteria" field. Depending on the site it is:

1. a custom field, id `customfield_1XXXX`, and **the number differs per Jira site**,
2. a heading inside the description body,
3. bullets in a comment,
4. genuinely absent.

An agent that only handles case 2 will confidently report "no acceptance criteria" on tickets that have them. That is failure mode R1 from `task_plan.md`.

**The fix, in order of cost.** Cheapest first, because it rides along with the fetch we already make:

**4a. `expand=names` gives you the id -> human-name map inside the issue response itself:**

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -H "Accept: application/json" \
  "$JIRA_URL/rest/api/3/issue/SCRUM-42?expand=names" \
| jq -r '.names | to_entries[] | select(.value | test("(?i)acceptance|criteria|AC")) | "\(.key)\t\(.value)"'
```

Expected output shape: `customfield_10034	Acceptance Criteria`

**4b. Or enumerate every field on the site once and cache it:**

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -H "Accept: application/json" \
  "$JIRA_URL/rest/api/3/field" \
| jq -r '.[] | select(.name | test("(?i)acceptance|criteria|definition of done")) | "\(.id)\t\(.name)\t\(.schema.type // "n/a")"'
```

**Design rule that falls out of this:** the agent resolves the AC field id **at runtime, per site**, caches it in `config.json`, and if resolution finds nothing it falls through to description-heading parsing, then to comments, then records a gap. Four strategies, in that order, and the one that succeeded gets recorded in `trace.json`. Never hardcode `customfield_10034`.

---

## 5. The core fetch (this is the request the agent actually makes)

```bash
KEY=SCRUM-42

curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -H "Accept: application/json" -G \
  "$JIRA_URL/rest/api/3/issue/$KEY" \
  --data-urlencode 'fields=summary,description,issuetype,status,priority,labels,components,fixVersions,versions,parent,subtasks,issuelinks,attachment,assignee,reporter,creator,duedate,created,updated,environment,customfield_10034' \
  --data-urlencode 'expand=renderedFields,names' \
| tee raw_issue.json | jq '{key, summary: .fields.summary, type: .fields.issuetype.name, status: .fields.status.name}'
```

Why each piece is there:

| Piece | Reason |
|---|---|
| `-G` + `--data-urlencode` | field lists and JQL contain commas, spaces and quotes. Building the query string by hand is how you get silent 400s. |
| explicit `fields=` | `*all` on a busy ticket returns 100+ fields of noise and burns LLM context. Ask for what the template needs, nothing more. |
| `expand=renderedFields` | gives `.renderedFields.description` as **HTML**, a free cross-check that the ADF flattener did not drop content |
| `expand=names` | the AC field discovery from section 4, no extra round trip |
| `tee raw_issue.json` | keep the raw response. It is the fixture, and it is the audit trail. |

**Discovery 5.1:** `fields.description` on v3 is an ADF document, roughly:

```json
{ "type": "doc", "version": 1, "content": [
    { "type": "heading", "attrs": {"level": 2},
      "content": [{"type": "text", "text": "Acceptance Criteria"}] },
    { "type": "bulletList", "content": [
        { "type": "listItem", "content": [
            { "type": "paragraph", "content": [{"type":"text","text":"Login rejects a blank password"}] }]}]}]}
```

A naive text-extractor that only concatenates `text` nodes (which is what the chapter 03 flattener does) loses **all structure**: headings, bullet boundaries, table cells, code blocks. For test planning that structure *is* the requirement. The flattener must emit markdown, not a text blob. This is why `tools/adf_flatten.py` is its own phase-3 task and not a two-line helper.

**The escape hatch,** when the flattener is not worth it:

```bash
# v2 returns description as a plain wiki-markup string, no ADF walking required
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -H "Accept: application/json" \
  "$JIRA_URL/rest/api/2/issue/$KEY?fields=description" | jq -r '.fields.description'
```

---

## 6. Supporting requests

**Comments** (requirements get clarified in comments far more often than anyone admits):

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -H "Accept: application/json" -G \
  "$JIRA_URL/rest/api/3/issue/$KEY/comment" \
  --data-urlencode 'maxResults=50' --data-urlencode 'orderBy=-created' \
| jq -r '.comments[] | "[\(.author.displayName) \(.created[0:10])] \(.body | tostring | .[0:200])"'
```

**Remote links** (design docs, Figma, Confluence specs):

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -H "Accept: application/json" \
  "$JIRA_URL/rest/api/3/issue/$KEY/remotelink" | jq -r '.[] | "\(.object.title) -> \(.object.url)"'
```

**Attachments** (metadata rides in `fields.attachment`; download separately):

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -H "Accept: application/json" \
  "$JIRA_URL/rest/api/3/issue/$KEY?fields=attachment" \
| jq -r '.fields.attachment[] | "\(.id)\t\(.filename)\t\(.mimeType)\t\(.size)"'

# then, note -L: the content URL redirects to signed media storage
curl -sL -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -o "spec.pdf" "$JIRA_URL/rest/api/3/attachment/content/10001"
```

**Sprint / epic context** (the core issue endpoint is unreliable for these; the Agile API is not):

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -H "Accept: application/json" \
  "$JIRA_URL/rest/agile/1.0/issue/$KEY?fields=summary,sprint,closedSprints,epic" \
| jq '{sprint: .fields.sprint.name, sprintEnd: .fields.sprint.endDate, epic: .fields.epic.name}'
```

Sprint end date matters: it is the only honest input to the plan's **Test Schedule** section. Without it, every date in that table is invented.

**Children of an epic** (goal G8, batch mode, uses the token-paginated search):

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -H "Accept: application/json" -G \
  "$JIRA_URL/rest/api/3/search/jql" \
  --data-urlencode 'jql=parent = SCRUM-1 ORDER BY created ASC' \
  --data-urlencode 'fields=summary,issuetype,status' \
  --data-urlencode 'maxResults=50' \
| jq -r '.issues[] | "\(.key)\t\(.fields.issuetype.name)\t\(.fields.summary)"'
```

**Issue type metadata** (which fields even exist on a Story in this project, before assuming any of them):

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" -H "Accept: application/json" \
  "$JIRA_URL/rest/api/3/issue/createmeta/SCRUM/issuetypes" | jq -r '.issueTypes[]? | .name'
```

---

## 7. Error taxonomy (verified against the prior-art client, extended)

| Status | Real meaning | What the agent must say | Retry? |
|---|---|---|---|
| `200` + HTML body | `JIRA_URL` points at the web app, not the API | "JIRA_URL looks wrong, it must be the bare site URL" | No |
| `400` | malformed field list or bad JQL | echo Jira's `errorMessages` array verbatim | No |
| `401` | bad email/token pair, or token revoked | "Authentication failed, regenerate the API token" | No |
| `403` | authenticated but not permitted, or CAPTCHA triggered after repeated 401s | "Your account cannot read this project" | No |
| `404` | **ticket missing OR you lack browse permission.** Jira deliberately conflates these to avoid leaking issue existence. | must say *both* possibilities, saying only "not found" sends people debugging the wrong thing | No |
| `429` | rate limited | honour the `Retry-After` header | Yes, backoff |
| `5xx` | Jira side | retry 3x with jitter, then fail | Yes |
| timeout / DNS | network or wrong host | "Cannot reach Jira at `<url>`" | Yes, once |

**Constraint 7.1:** Jira Cloud rate limiting is cost-based, not a fixed request count, so you cannot precompute a safe rate. The only correct behaviour is to read `Retry-After` and back off. Batch mode (G8) must assume it will be throttled.

**Constraint 7.2:** the 404 conflation is the finding most likely to waste a student's afternoon. It goes in the README.

---

## 8. Transport recommendation

**Primary: direct REST v3 + API token.** Reproducible for every student, works in CI, no dependency on an IDE connector, and the curl calls above are the documentation.

**Secondary: Atlassian MCP as a drop-in adapter.** It is already connected in this session (`getAccessibleAtlassianResources` -> cloudId, then `getJiraIssue`), so it costs nothing to support and it removes all credential setup for anyone who has it. It returns pre-digested content rather than raw ADF, which is convenient but means the agent gets a *different shape* from the REST path.

**Therefore the architectural rule:** both transports must normalize into the **same** `ticket.json`. The schema is the interface. Everything above the fetch layer must not be able to tell which transport ran. This is the reason the schema is frozen in `LLM.md` before any tool is written, and it is exactly what Protocol 0's halt condition is protecting.

---

## 9. Open items promoted to Discovery Questions

Research got these as far as research can go. The rest needs a human answer, which is exactly what Protocol 0's halt condition is for.

| Finding | Why research cannot close it | Question in `task_plan.md` |
|---|---|---|
| Cloud vs Server forks auth, API version and markup | Only you know the instance | Q2a |
| Both transports (REST, MCP) are viable | Depends on whether the audience is you or a class | Q2b |
| AC field id is per-site | Needs your site | Q3a |
| The real AC often lives in comment 7, not the description | Team habit, not an API fact | Q3b |
| Sprint end date is the only honest input to the schedule section | Needs a real board | Q6 |
| Which LLM provider, and whether ticket bodies may leave the machine | Data-residency call, not a technical one | Q2c |

Three of these six would have been silently guessed wrong without asking. That settles the question of whether Protocol 0's halt is worth the delay.

**Resolved during this pass:** "what does A.N.T. expand to" was an open question against the first version of `BLAST.md`, which named the acronym without defining it. The file was updated mid-session and now defines it in Phase 3: **A**rchitecture (`architecture/`, markdown SOPs), **N**avigation (the reasoning and routing layer), **T**ools (`tools/`, deterministic Python). The mapping onto this project is in `task_plan.md` section 4. No question needed.

---

## 10a. Live findings from the build (Phases 1-5, verified against real APIs)

Everything in sections 1-9 was research. These four were discovered by running the
thing, and three of them would have been invisible from reading documentation.

### 10a.1 Jira answers **404, not 401**, on the issue endpoint when auth is bad

The single highest-value finding of the build. Measured on a live site with an expired token:

```
GET /rest/api/3/myself        -> HTTP 401   "Client must be authenticated"
GET /rest/api/3/issue/VWO-49  -> HTTP 404
```

Jira hides issue existence from unauthenticated callers, so a dead token presents as a
**missing ticket**. Section 7 of this document already said to report 404 as "not found
OR no permission" (BR-16), and that message was still wrong here: the real cause was
neither. A user would spend the afternoon checking key spellings and project
permissions while the actual problem was an expired credential.

**The fix, now in `tools/jira_fetch.py`:** on a 404, call `/myself` to disambiguate. If
auth fails there, raise the auth error instead. Only when auth is confirmed good does
the "not found or no permission" message stand.

**Generalisable rule:** when an API deliberately conflates statuses to avoid leaking
information, a second endpoint that does not conflate them is the disambiguator. Find it.

### 10a.2 Groq counts `max_tokens` (the reservation) against the TPM limit

Two failed live calls before the arithmetic gave it away:

```
attempt 1:  413  Limit 8000, Requested 13910
attempt 2:  413  Limit 8000, Requested 10669     <- after slimming the payload
            10669 - 8000 = 2669 = exactly the prompt size
```

The prompt was never the problem. `max_tokens: 8000` was: Groq bills the *reservation*,
not the completion length, so `prompt + max_tokens` must fit inside the tier's TPM.

**Fix:** `max_tokens = tpm_limit - estimated_prompt_tokens - margin`, floored at 1500.
Third attempt succeeded with 2669 in / 1844 out.

**Corollary worth keeping:** slimming the payload is the *second* thing to try on a 413,
not the first. Check what the reservation is costing you first.

### 10a.3 `description_html` should never reach the model

`expand=renderedFields` was added in section 5 as a cross-check on the ADF flattener,
and it does that job well (measured loss on a real ticket: **0.6%**). But it also
roughly doubles the description payload, and the model has no use for it. It is now
stripped before every LLM call. Free savings, zero information cost.

### 10a.4 Provider comparison on the same real ticket (SOAP-1)

| | Groq `openai/gpt-oss-120b` | DeepSeek `deepseek-chat` |
|---|---|---|
| Wall clock | **5.8s** | 21.5s |
| Schema valid on attempt | 1 | 1 |
| Scope areas produced | 5 | **8** |
| Assumptions declared | 1 | **5** |
| Slimming needed | yes (8000 TPM) | no (60000 budget) |

DeepSeek is roughly 4x slower but produced a fuller plan and, more importantly,
**declared more of what it could not source from the ticket**. Under this project's
rules (BR-2), declaring an assumption is better behavior than quietly filling a gap.
Groq is the right pick when latency matters. Both are supported; `llm_provider` selects.

---

## 10b. Prior-art research (BLAST Phase 1, item 3) - NOT RUN

The protocol requires searching GitHub and other sources for reusable work before
building. **That search was not run.** In-repo prior art (section 1) covered the same
ground: a working Jira client, a credential pattern and the 14-section template were all
already in this repository, which is a better source than a stranger's repo because it is
already consistent with the course. Recording the skip honestly rather than
back-filling plausible-sounding repo names.

Still worth doing before v1.1, specifically for the ADF-to-markdown converter, which is
the one component here most likely to have a better-tested open-source equivalent.

Search targets when Phase 1 opens:

| Target | What we would take from it |
|---|---|
| Jira ADF -> markdown converters | Saves the highest-effort pure function in the build (`adf_flatten.py`) |
| Jira MCP servers | Reference implementation of the field-mapping and auth flow |
| Jira-to-test-case / test-plan agents | Prompt structure, scope-selection heuristics, what their failure modes were |
| `jira` / `atlassian-python-api` client libraries | Decide build vs adopt for the fetch layer |
| JSON-schema-constrained LLM output libraries | The gate between Layer 2 and Layer 3 |

Each hit must be recorded here with its **licence** before any code is copied. A course repo cannot absorb an unlicensed snippet.
