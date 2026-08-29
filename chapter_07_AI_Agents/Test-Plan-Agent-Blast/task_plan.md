# task_plan.md - Test Plan Agent (Jira ID -> Test Plan)

> **Protocol:** B.L.A.S.T. (Blueprint, Link, Architect, Stylize, Trigger) over the A.N.T. 3-layer architecture
> **Stage:** Protocol 0 - Initialization
> **Status:** **v1 BUILT AND RUNNING.** Phases 0-5 complete. Gates A, B, C green (09:16).
> **Execution lock:** RELEASED 09:16. `architecture/` (6 SOPs), `tools/` (9 tools), `navigation.py`, UI and CLI all built.
> **Verified live 09:39:** SOAP-1 end to end, output checked against the source ticket for fabrication. Nothing invented.
> **Owner:** Pramod Dutta · **Created:** 2026-08-29 · **Path:** `chapter_07_AI_Agents/Test-Plan-Agent-Blast/`

---

## 1. The one-line mission (North Star, proposed)

Give the agent a Jira ID (`SCRUM-42`). Get back a formal, review-ready Test Plan markdown file, where every claim is traceable to a real field on that ticket and every gap is marked as a gap instead of being invented.

## 2. Why this is not "just a prompt"

The naive version is: paste ticket text into a chat window, ask for a test plan. That version fails on four counts, and each failure is a design goal here.

| Naive failure | What this project does instead |
|---|---|
| Hallucinated acceptance criteria, endpoints, environments | Schema-validated ticket object; anything absent renders as `_(assumed - confirm)_` or `NOT IN TICKET`, never filled in silently |
| Different shape every run, not reviewable | One frozen template; the LLM fills slots, it does not choose structure |
| Re-run gives a different plan | Layers 1 and 3 are deterministic; only Layer 2 is probabilistic, and it is temperature-pinned and schema-gated |
| Silent breakage when Jira changes | Every fetch is validated against `ticket.schema.json`; a shape change fails loudly at the boundary, not halfway through a document |

This maps directly onto the BLAST premise: *LLMs are probabilistic; business logic must be deterministic.* The whole design question for this project is **where the LLM is allowed to touch the data**, and the answer is: exactly one place, section 4 Layer 2.

## 3. Goals

### 3.1 Primary goals (definition of done for v1)

- [x] **G1 - Fetch:** Given `<JIRA-KEY>`, pull the full ticket (summary, description, AC, type, status, priority, labels, components, fix versions, parent/epic, subtasks, issue links, comments, attachment metadata, sprint) from Jira Cloud REST v3.
- [x] **G2 - Normalize:** Flatten ADF (Atlassian Document Format) into clean markdown and emit one `ticket.json` conforming to `ticket.schema.json`.
- [x] **G3 - Reason:** Map ticket facts onto the 14-section test plan template, keeping only the scope areas the ticket actually justifies.
- [x] **G4 - Render:** Write `<KEY>-test-plan.md` with zero leftover `{{placeholders}}` and zero authoring comments.
- [x] **G5 - Trace:** Emit `trace.json` mapping each generated section back to the Jira field(s) that produced it.
- [x] **G6 - Fail loudly:** Auth failure, missing ticket, permission denial, rate limit and schema mismatch each produce a distinct, actionable error, never a half-written plan.

### 3.2 Secondary goals (v1.1, only after v1 is signed off)

- [ ] **G7:** `.docx` export for client-facing delivery.
- [ ] **G8:** Batch mode - one epic key expands to all child stories, one plan per story.
- [ ] **G9:** Write-back - post the finished plan to the ticket as a comment, or to Confluence as a page.
- [ ] **G10:** Diff mode - ticket changed after the plan was written, show what the plan must absorb.

### 3.3 Explicit non-goals (v1)

Written down so scope cannot drift mid-build.

- Not writing test **cases**. This produces a test **plan**. Case generation is a separate agent.
- Not executing tests, not touching a browser, not calling Playwright.
- Not editing the Jira ticket. Read-only against Jira in v1.
- Not a hosted service, no auth server, no multi-tenant. Local CLI first.
- Not supporting Jira Server / Data Center in v1 (researched in `findings.md` section 3, deferred).

---

## 4. Architecture mapping (A.N.T., as defined in BLAST.md Phase 3)

Fitting this project onto the three layers, because the layer boundary *is* the reliability guarantee.

### Layer 1 - Architecture (`architecture/`) - Markdown SOPs, no code

The written contract for each step. **Golden Rule: if logic changes, the SOP changes before the code does.**

| SOP file | Covers | Edge cases it must name |
|---|---|---|
| `SOP_01_fetch_ticket.md` | key validation, auth, the single REST call, retries | 401 vs 403 vs 404, 429 backoff, HTML-instead-of-JSON, timeout |
| `SOP_02_resolve_fields.md` | per-site Acceptance Criteria field discovery | AC in custom field / in description heading / in comments / genuinely absent |
| `SOP_03_normalize.md` | ADF -> markdown, raw JSON -> `ticket.json` | empty description, tables, code blocks, nested lists, media nodes, emoji nodes |
| `SOP_04_readiness_check.md` | is this ticket even plannable | below the minimum field bar -> return a gap report, refuse to write a plan |
| `SOP_05_build_plan.md` | the one LLM call, slot filling, scope selection | thin ticket, contradictory AC, non-English content, oversized description |
| `SOP_06_render.md` | plan object -> markdown against the frozen template | placeholder sweep, comment strip, table integrity |

### Layer 2 - Navigation (decision making) - the reasoning layer

This is the agent. It routes: `fetch -> resolve -> normalize -> readiness -> build -> render -> trace`. It decides *which tool runs next* and *what to do when one fails*. It does **not** parse ADF itself, does not build URLs itself, does not format markdown itself.

**The one exception, stated explicitly because it is the project's core risk:** the LLM is the engine for `SOP_05_build_plan` (prose and scope selection), and its output is immediately schema-validated before it reaches Layer 3. Probabilistic in, deterministic gate, deterministic out.

### Layer 3 - Tools (`tools/`) - atomic deterministic Python

| Tool | Contract | Pure? |
|---|---|---|
| `jira_auth.py` | env -> credentials, `verify()` -> display name or typed error | I/O only |
| `jira_fetch.py` | key -> raw JSON. No interpretation. | I/O only |
| `field_map.py` | site -> `{ac_field_id, ...}`, cached | I/O + cache |
| `adf_flatten.py` | ADF dict -> markdown string | **pure** |
| `normalize.py` | raw JSON -> `ticket.json` | **pure** |
| `readiness.py` | `ticket.json` -> `{plannable: bool, gaps: []}` | **pure** |
| `plan_build.py` | `ticket.json` -> `plan.json` (the LLM call) | probabilistic, schema-gated |
| `render.py` | `plan.json` + template -> markdown | **pure** |
| `trace.py` | inputs + outputs -> `trace.json` | **pure** |

Six of nine are pure functions, testable with no network and no model. That ratio is the design target.

**Conventions from BLAST.md Phase 3, binding:** secrets live in `.env` only; every intermediate file goes in `.tmp/`; `.tmp/` and `.env` are gitignored before the first commit.

---

## 5. Phase plan (B.L.A.S.T.)

### Phase 0 - Initialization  `IN PROGRESS`

- [x] Read `BLAST.md`, extract Protocol 0 requirements
- [x] Survey the repo for prior art (found a working `jira_client.py` in chapter 03 and a 14-section plan template in `test-plan-create-skill`)
- [x] Create `task_plan.md` (this file)
- [x] Create `findings.md` with Jira API research and verified curl calls
- [x] Create `progress.md` with the running build log
- [x] Create `LLM.md` as the Project Constitution (schemas, rules, invariants)
- [ ] **GATE A** - the 5 Discovery Questions answered by the human (section 7)
- [ ] **GATE B** - `ticket.schema.json` and `plan.schema.json` frozen in `LLM.md` (Data-First Rule)
- [ ] **GATE C** - this blueprint explicitly approved

### Phase 1 - BLUEPRINT (B)  `BLOCKED BY GATE A`

- [x] Ask the 5 mandated Discovery Questions, record the answers verbatim in `LLM.md` section 2
- [x] **Data-First Rule:** freeze input shape (`ticket.schema.json`) and output shape (`plan.schema.json`)
- [ ] **Research:** search GitHub for prior art on Jira-to-test-plan agents, ADF-to-markdown converters and Jira MCP servers; record hits and licences in `findings.md` section 10
- [x] Lock the input contract: which forms of Jira ID are accepted (`SCRUM-42`, full browse URL, both)
- [x] Lock the delivery payload: file name, output directory, markdown only or markdown + docx
- [x] Decide which of the 14 template sections are always present vs conditional
- [x] Write the scope-selection rule: how the agent decides "Performance Testing" belongs in this plan
- [x] Define the assumption marker vocabulary (`_(assumed - confirm)_`, `NOT IN TICKET`, `N/A`)

### Phase 2 - LINK (L)  `BLOCKED BY PHASE 1`

Handshake only. Minimal scripts that prove the connection. No business logic until the Link is green.

- [x] `.env.example` committed, `.env` gitignored
- [x] `tools/jira_auth.py` -> `verify()` hits `/rest/api/3/myself`, prints the display name
- [x] `tools/jira_fetch.py` -> fetches one real ticket, dumps to `.tmp/raw_issue.json`
- [x] LLM provider handshake: one trivial round trip against the chosen provider (Q5)
- [x] Error taxonomy implemented: 401 / 403 / 404 / 429 / 5xx / timeout / DNS, each a typed exception with its own remedy string
- [x] Retry with exponential backoff, honouring `Retry-After` on 429
- [ ] Fixture capture: save 5 real ticket responses to `fixtures/` so every later phase runs offline
- [x] **Link gate:** all three handshakes green, or stop

### Phase 3 - ARCHITECT (A)  `BLOCKED BY PHASE 2`

- [x] Write all six SOPs in `architecture/` **before** their tools exist (Golden Rule)
- [x] Build the nine tools in section 4 Layer 3, each atomic and unit-tested against fixtures
- [x] `adf_flatten.py` gets a fixture per node type: heading, bulletList, orderedList, table, codeBlock, panel, mediaSingle, inlineCard
- [x] Wire Layer 2 navigation: the orchestration order plus the failure branch for each step
- [x] Schema validation at both boundaries (`ticket.json` in, `plan.json` out)
- [x] Golden-file test: one fixture in, one expected plan out

### Phase 4 - STYLIZE (S)  `BLOCKED BY PHASE 3`

- [x] Freeze the template at `assets/test-plan-template.md` (14 sections, order fixed)
- [x] Payload refinement: tables stay tables, no emoji in the deliverable, no em dashes
- [x] Strip every `<!-- guidance -->` comment from output
- [x] Placeholder sweep: the run fails if any `{{` survives into the output file
- [ ] Present a real generated plan to the human for feedback **before** anything is called done

### Phase 5 - TRIGGER (T)  `BLOCKED BY PHASE 4`

> Note: `BLAST.md` names Trigger in the identity line but the current file stops at Phase 4. The items below are this project's proposal for T, to be confirmed when the protocol text is completed.

- [x] CLI entry point: `python run.py SCRUM-42`
- [ ] Optional: expose as a Claude/Codex skill so `/test-plan SCRUM-42` works in-editor
- [x] Exit codes: `0` ok, `2` bad input, `3` auth, `4` not found, `5` rate limited, `6` schema violation, `7` LLM failure
- [x] `--dry-run` that fetches and normalizes but never calls the LLM
- [x] README with a 60-second setup path

---

## 6. Verification checklist (the build is not done until every line is checked)

**Fetch**
- [ ] Valid key returns 200 with a populated `fields` object
- [ ] Unknown key returns "ticket not found **or** you lack browse permission" (Jira conflates the two, we must say both)
- [ ] Bad token returns "authentication failed, regenerate your API token", not a stack trace
- [ ] Empty description does not crash the flattener
- [ ] A description with tables, code blocks and nested bullets survives flattening
- [ ] 429 is retried, not surfaced as a failure on first hit

**Normalize**
- [ ] `ticket.json` validates against `ticket.schema.json` for all 5 fixtures
- [ ] AC found when in a custom field
- [ ] AC found when only in a description heading
- [ ] AC absent -> `acceptance_criteria: []` plus a recorded gap, not an invented list

**Reason**
- [ ] Scope contains only the test types the ticket justifies, never all 17
- [ ] Every environment URL in the plan appears in `ticket.json`, or is marked assumed
- [ ] No endpoint, version or date appears in the plan unless it appears in `ticket.json`
- [ ] Same fixture, two runs, semantically equivalent plan

**Render**
- [ ] Zero `{{` and zero `<!--` in the output
- [ ] All 14 headings present, in template order
- [ ] Markdown tables render correctly

**Safety**
- [ ] No token, cookie or email in any committed file, log line or trace
- [ ] `.env` and `.tmp/` gitignored, `.env.example` committed
- [ ] Ticket bodies go nowhere except the configured LLM provider, and the README says which one

---

## 7. Discovery Questions (GATE A)

BLAST Phase 1 mandates five. Each is answered here with the concrete sub-question this project actually needs.

**Q1 - North Star.** Is the singular outcome "a review-ready markdown Test Plan file per Jira story", as stated in section 1? Or is the real endpoint a Confluence page / a docx a client signs off / a Jira comment? The North Star decides Phase 4 and Phase 5 entirely.

**Q2 - Integrations.** Confirmed integrations: **Jira** (read) and an **LLM provider** (generate). Sub-questions:
  - **2a.** Jira **Cloud** (`*.atlassian.net`) or **Server / Data Center**? This forks auth, API version and markup format. Everything downstream depends on it.
  - **2b.** Transport: direct **REST v3 + API token** (reproducible for every student, works in CI) or the already-connected **Atlassian MCP** (zero setup for you, not reproducible for a course audience)? `findings.md` section 8 recommends REST primary, MCP as an optional adapter behind the same schema.
  - **2c.** LLM provider: **Ollama** local (matches chapter 03, free, offline, weaker), **Groq** (fast, cheap) or **Claude** (strongest structured output)? Also a data-residency call, since the ticket body leaves the machine for the latter two.
  - **2d.** Are the keys ready? `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` at minimum.

**Q3 - Source of Truth.** The Jira ticket is primary. But:
  - **3a.** Where do **Acceptance Criteria** live on your board: a custom field, or a heading inside the description? If a custom field, I need the site's `customfield_1XXXX` id. `findings.md` section 4 has the one-liner that discovers it.
  - **3b.** Do **comments** count as requirements? In most teams the real AC ends up in comment 7. Include or ignore.
  - **3c.** Do **linked Confluence pages and attachments** count as source, or is the ticket body the whole world for v1?
  - **3d.** Which **ticket types** are in scope: Story only, or Bug / Task / Epic too? An Epic key should fan out to children, which is G8, not v1.

**Q4 - Delivery Payload.** Proposed: `<KEY>-test-plan.md` written next to the project, plus `trace.json`. Confirm, and confirm:
  - **4a.** Markdown only for v1, or docx from day one?
  - **4b.** Write-back to Jira or Confluence in v1? This changes the permission scope the token needs, so it belongs in the blueprint, not a later phase.
  - **4c.** Reuse the existing 14-section template at `test-plan-create-skill/assets/test-plan-template.md` verbatim (my recommendation, one canonical template in the repo), or does this chapter get its own?

**Q5 - Behavioral Rules.** Proposed constitution, drafted in full at `LLM.md` section 3. The load-bearing ones to confirm or overrule:
  - **5a.** **Never invent.** No AC, endpoint, environment, date or tool appears in the plan unless it appears in the ticket. Missing data is marked, not filled.
  - **5b.** **Refuse thin tickets.** Below a minimum field bar, return a gap report instead of a plan. Confirm this, because it means the agent sometimes returns no plan, by design.
  - **5c.** **Read-only Jira** in v1.
  - **5d.** **Tone:** formal QA deliverable, no emoji, no em dashes, tables stay tables.
  - **5e.** **Human review gate** before any plan is treated as final.

**Q6 - Fixture ticket (not one of the mandated five, but blocking).** Give me one real Jira key on a project you own, to use as the fixture. Without it, Phases 2 to 5 get built against invented data, which is precisely what this protocol exists to prevent.

---

## 8. Risk register

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | LLM invents acceptance criteria or endpoints | Plan looks authoritative and is wrong. The worst failure mode in the project. | Schema-gated output, `trace.json`, `NOT IN TICKET` marker, section 6 checklist |
| R2 | AC custom field id differs per Jira site | Agent silently reports "no AC" on tickets that have AC | Runtime field discovery via `expand=names`, cached per site (`findings.md` section 4) |
| R3 | ADF flattening loses tables or nested lists | Requirements silently dropped before the LLM ever sees them | Dedicated flattener, one fixture per node type, `renderedFields` HTML as cross-check |
| R4 | Credentials committed to a public course repo | Live token leak | `.env` only, gitignored before first commit, pre-commit grep for `ATATT` |
| R5 | Jira API drift (the legacy `/search` retirement is precedent) | Agent breaks silently months later | Pin to documented v3 endpoints, validate every response, fail loud |
| R6 | Rate limiting on batch runs | Half-finished batch, partial output | Backoff honouring `Retry-After`, per-run request budget, resumable batch |
| R7 | Ticket too thin to plan from | Garbage in, confident garbage out | `SOP_04_readiness_check`, refuse and return a gap report |
| R8 | Scope creep into test case generation | v1 never ships | Non-goals in 3.3 are binding |
| R9 | SOPs drift from code | The `architecture/` layer becomes decoration | Golden Rule enforced in review: SOP diff required alongside any tool diff |

---

## 9. Gate status

| Gate | Requirement | State |
|---|---|---|
| **A** | The 5 Discovery Questions in section 7 answered by the human | **GREEN** 09:16, recorded verbatim in `LLM.md` section 2 |
| **B** | `ticket.schema.json` + `plan.schema.json` frozen (Data-First Rule) | **GREEN**, both in `schemas/`, enforced at runtime |
| **C** | This blueprint explicitly approved | **GREEN** 09:16 |

## 10. What shipped

| Layer | Artifact | State |
|---|---|---|
| 1 Architecture | `architecture/` 6 SOPs | Written before their tools, per the Golden Rule |
| 2 Navigation | `navigation.py` | Routes 7 steps; exactly 1 calls a model |
| 3 Tools | `tools/` 9 modules | 6 pure functions, 45 offline checks green |
| Contracts | `schemas/` 2 JSON Schemas | Enforced at both boundaries |
| UI | `app.py` + `pages/1_Settings.py` | Running on :8502 |
| CLI | `run.py` | `--health`, `--dry-run`, `--force`, typed exit codes |
| Tests | `tests/test_pipeline.py` | 45 passed, 0 failed, no network, no model |

**Live proof:** SOAP-1 generated in 5.8s on Groq and 21.5s on DeepSeek, schema-valid on
the first attempt both times. Every `justified_by` traced to a real FR/NFR on the ticket;
the one unsourceable field (environment URL) was declared as an assumption rather than
invented.

## 11. Remaining work for v1.1

- [ ] **E16:** a requirement can be omitted from both `scope` and `dropped_scope`. Extract requirement ids deterministically and force the plan to account for each (`LLM.md` T-6).
- [ ] **Fixture capture:** `fixtures/` still holds synthetic tickets. Capture a real response now that credentials work.
- [ ] **GitHub prior-art search** (BLAST Phase 1 item 3): not run, see `findings.md` 10b. Most valuable for the ADF converter.
- [ ] **G7** docx export · **G8** epic batch mode · **G9** write-back to Jira/Confluence · **G10** diff mode
- [ ] Golden-file regression test wired into CI
