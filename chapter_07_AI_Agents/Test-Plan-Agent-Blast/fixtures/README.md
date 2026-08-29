# Fixtures

Offline test data. No network needed (invariant AI-8).

| File | What it is |
|---|---|
| `BOOK-214_raw.json` | A rich ticket: ADF headings, bullets, a table, a code block, a warning panel, a rule, bold and link marks, an `expand` node the flattener does not know (deliberate, to prove `unknown_adf_nodes` works), plus acceptance criteria in `customfield_10034`, components, fix version, links and an attachment. |
| `BOOK-999_raw.json` | A deliberately thin ticket: two-word summary, four-word description, no acceptance criteria. Proves the readiness refusal path (BR-4). |
| `sample_plan.json` | **A hand-written test fixture, not model output.** It exists so `render.py` and the output gates can be tested without calling Groq. |

These are synthetic tickets, not real Jira data. Replace `BOOK-214` with a
captured real response once live credentials are available (Phase 2 fixture capture).
