# SOP 04 - Readiness Check

**Tool:** `tools/readiness.py` · **Layer:** 3 · **Purity:** pure

## Goal
Decide whether this ticket is plannable at all. The agent must be willing to return **no plan** (BR-4).

## Why
A confident test plan built on an empty ticket is worse than no plan, because it gets reviewed and approved. The gap report is the useful output in that case: it names exactly what to add to the ticket.

## Scoring
| Signal | Points | Notes |
|---|---|---|
| Summary present, >= 3 words | 2 | required |
| Description >= 200 chars | 3 | the main substance |
| Description >= 40 chars | 1 | partial credit |
| >= 1 acceptance criterion | 3 | strongest signal |
| >= 3 acceptance criteria | +1 | bonus |
| Components or labels present | 1 | scope hints |
| Fix version or sprint present | 1 | schedule input |

**Threshold: 5 of 11.** Below it -> `plannable: false`.

Chosen so that summary + a real description (5) passes, and summary + one-line description (3) does not. A ticket with acceptance criteria and a summary (5) always passes.

## Output
`{"plannable": bool, "score": int, "max": 11, "gaps": [...], "blockers": [...]}`

`blockers` are the specific things to add to the ticket, phrased as instructions to the author: "Add acceptance criteria", "Expand the description beyond one line".

## Behavior on false
Navigation stops. No LLM call is made, no plan file is written. The UI renders the gap report. Exit code 0, because refusing is correct behavior, not a failure (BR-4, BR-17).

## Override
The UI exposes "plan anyway". If used, every generated section carries an assumption entry and the plan header states the ticket failed readiness. Explicit human choice, recorded.
