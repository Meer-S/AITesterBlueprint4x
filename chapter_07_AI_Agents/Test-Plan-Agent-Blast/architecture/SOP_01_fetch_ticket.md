# SOP 01 - Fetch Ticket

**Tool:** `tools/jira_fetch.py` · **Layer:** 3 · **Purity:** I/O only, no interpretation

## Goal
Turn a Jira issue key into the raw JSON Jira returns. Nothing more. No parsing, no field mapping, no opinions.

## Inputs
- `key: str` matching `^[A-Z][A-Z0-9]+-[0-9]+$`
- credentials from `tools/config_store.py` (`jira_url`, `jira_email`, `jira_api_token`)

## Logic
1. Validate the key against the pattern. Invalid -> `InvalidKeyError` before any network call.
2. `GET {jira_url}/rest/api/3/issue/{key}` with:
   - `fields=` explicit list (never `*all`, it burns LLM context with noise)
   - `expand=renderedFields,names` (HTML cross-check + the field-name map for SOP 02)
   - Basic auth, `Accept: application/json`, timeout 20s
3. Fetch comments separately: `GET /rest/api/3/issue/{key}/comment?maxResults=50&orderBy=-created`
4. Fetch remote links: `GET /rest/api/3/issue/{key}/remotelink`
5. Comments and remote links are **best-effort**. A failure there degrades the result, it does not fail the run. The core issue call is the only one that can fail hard.
6. Write the raw response to `.tmp/{key}_raw.json`. It is both the fixture and the audit trail.

## Edge cases
| Case | Behavior |
|---|---|
| 200 with an HTML body | `JiraError`: "JIRA_URL points at the web app, not the API" |
| 400 | `JiraError` echoing Jira's `errorMessages` verbatim |
| 401 | `AuthenticationError`: "regenerate the API token" |
| 403 | `PermissionError`: account cannot read this project |
| 404 | `NotFoundError`: **"not found OR no browse permission"**, always both (BR-16) |
| 429 | retry honouring `Retry-After`, max 3 attempts, then `RateLimitError` |
| 5xx | retry with backoff 1s/2s/4s, then `JiraError` |
| timeout / DNS | `ConnectionError` naming the URL it tried |

## Output
`dict` with keys `issue`, `comments`, `remote_links`, `_meta` (status, ms, retries).

## Rules cited
BR-15 (errors name the fix), BR-16 (404 conflation), BR-9 (never log the token), AI-4 (explicit paths, no cwd dependence).
