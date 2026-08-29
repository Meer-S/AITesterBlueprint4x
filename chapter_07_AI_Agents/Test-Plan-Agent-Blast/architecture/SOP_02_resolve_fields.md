# SOP 02 - Resolve Fields

**Tool:** `tools/field_map.py` · **Layer:** 3 · **Purity:** pure given the `names` map

## Goal
Find the Acceptance Criteria custom field id **for this Jira site**, at runtime. Never hardcode `customfield_10034`.

## Why this SOP exists
On Jira Cloud there is no standard Acceptance Criteria field. The id differs per site. The prior-art client in `chapter_03` falls back to scanning field *keys* for the substring "acceptance", which can never match on Cloud, where keys are `customfield_10034` and the human name lives in the `names` map. That is risk R2 and it is the single most likely cause of a silently wrong plan.

## Inputs
- `names: dict[str, str]` from `expand=names` on the issue response (field id -> display name)

## Logic
1. Scan `names` for a display name matching `(?i)acceptance|criteria|definition of done`.
2. Rank hits: exact "Acceptance Criteria" beats "AC" beats "Definition of Done".
3. Return `{"acceptance_criteria": "customfield_XXXXX" | None}` plus the human name that matched.
4. Cache per site in `config.json` under `field_map_cache`. The map is stable per site; re-resolving on every run is wasted latency.

## Edge cases
| Case | Behavior |
|---|---|
| No match | Return `None`. Not an error. SOP 03 falls through to description-heading parsing. |
| Multiple matches | Take the highest-ranked, record all candidates in the trace |
| `names` absent (expand dropped) | Return `None` and record a gap, do not crash |

## Output
`{"acceptance_criteria": str|None, "matched_name": str|None, "candidates": list}`

## Rules cited
BR-2 (absence is data), R2.
