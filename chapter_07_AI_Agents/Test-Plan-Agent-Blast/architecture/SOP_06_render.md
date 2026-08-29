# SOP 06 - Render

**Tool:** `tools/render.py` · **Layer:** 3 · **Purity:** pure

## Goal
`plan.json` + the frozen template -> the final markdown deliverable. Deterministic. Same input, same bytes.

## Logic
1. Load `assets/test-plan-template.md`. Section order and headings come from it, never from the model (BR-10).
2. Fill each section from the validated plan object.
3. Assumption rendering: any item with `assumed: true` renders its value followed by `_(assumed - confirm)_`. The renderer decides how an assumption *looks*; the model only decided whether something *is* one.
4. Append the **Assumptions** and **Scope Deliberately Excluded** sections from `assumptions[]` and `dropped_scope[]`. These are part of the deliverable, not debug output (BR-14).
5. Strip every `<!-- guidance -->` comment.
6. Header block: source ticket key, link, generation timestamp, model used, and a "DRAFT - human review required" line (BR-5).

## Output gates (the run fails if any trip)
| Gate | Check |
|---|---|
| Placeholder sweep | zero occurrences of `{{` (BR-11) |
| Comment sweep | zero occurrences of `<!--` (BR-11) |
| Section completeness | all 14 headings present, in template order |
| Table integrity | every pipe-table row has the same column count as its header |
| Tone | zero em dashes, zero emoji (BR-12) |

A tripped gate means no file is written (BR-17).

## Output
`out/{KEY}-test-plan.md` plus `out/{KEY}-trace.json`.
