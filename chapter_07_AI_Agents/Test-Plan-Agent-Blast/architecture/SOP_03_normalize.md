# SOP 03 - Normalize

**Tools:** `tools/adf_flatten.py`, `tools/normalize.py` · **Layer:** 3 · **Purity:** both pure

## Goal
Raw Jira JSON -> one `ticket.json` that validates against `schemas/ticket.schema.json`. This is the only interface into the rest of the system (AI-1).

## Part A: ADF flattening (`adf_flatten.py`)

Jira Cloud v3 returns `fields.description` as an Atlassian Document Format tree. A naive extractor that concatenates `text` nodes loses **all structure**: headings, bullet boundaries, table cells, code blocks. For test planning that structure *is* the requirement.

Node handling, ADF type -> markdown:

| ADF node | Markdown |
|---|---|
| `doc` | walk children |
| `heading` (attrs.level) | `#` * level |
| `paragraph` | text + blank line |
| `bulletList` / `listItem` | `- ` with 2-space nesting |
| `orderedList` | `1. ` with nesting |
| `table` / `tableRow` / `tableHeader` / `tableCell` | pipe table, header separator after row 1 |
| `codeBlock` (attrs.language) | fenced block |
| `blockquote` | `> ` prefix |
| `rule` | `---` |
| `panel` (attrs.panelType) | `> **NOTE:**` blockquote |
| `text` with `marks` | `**bold**`, `*em*`, `` `code` ``, `~~strike~~`, `[text](href)` |
| `hardBreak` | newline |
| `mediaSingle` / `media` | `_[attachment: filename]_` |
| `inlineCard` / `blockCard` | `<url>` |
| `emoji` | `attrs.text` |
| `mention` | `@displayName` |
| **unknown** | recurse into `content`, and **record the type in `unknown_nodes`** |

`unknown_nodes` is load-bearing. It is how ADF drift becomes visible instead of becoming silent data loss.

**Self-check:** compare the flattened text length against the text stripped from `renderedFields.description` HTML. A delta over 25% means a node type was dropped. Recorded in the trace as `html_crosscheck_delta_pct` (risk R3).

## Part B: Acceptance criteria extraction (`normalize.py`)

Four strategies, in order, first hit wins. The one that fired is recorded in `origin`:

1. `custom_field` - the id from SOP 02, flattened if ADF
2. `description_heading` - a heading matching `(?i)acceptance criteria|^ac$` in the flattened markdown, take everything until the next heading of the same or higher level
3. `comment` - a comment whose first 200 chars match the AC pattern (only if enabled)
4. none -> `acceptance_criteria: []` **plus** a `gaps[]` entry. Never an invented list (BR-1, BR-2).

Splitting: bullet lines become one AC each; `Given/When/Then` blocks stay together as one AC.

## Part C: Assembly
Build the object exactly as `schemas/ticket.schema.json` requires, then validate. A violation raises `SchemaError` naming the offending path (AI-5, T-2).

`gaps[]` is populated for: no description, no acceptance criteria, no components, no fix version, no sprint dates, no environment.

## Rules cited
BR-1, BR-2, AI-1, AI-4, AI-5, R3.
