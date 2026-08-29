# Test Plan Agent

Jira ticket in, formal Test Plan out. One prompt box: *"Fetch VWO-49 and create a test plan"*.

Built with the **B.L.A.S.T.** protocol (Blueprint, Link, Architect, Stylize, Trigger) on the
**A.N.T.** 3-layer architecture. See `BLAST.md` for the protocol and `LLM.md` for the
project constitution.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # then fill it in, or use the Settings page
streamlit run app.py
```

Open the **Settings** page first. Add your Jira URL, email and API token
(id.atlassian.com -> Security -> API tokens) and your Groq key
(console.groq.com/keys), then press both **Test connection** buttons.
Do not skip that step: BLAST Phase 2 exists because a broken link fails
in confusing ways much later.

## Use

**UI:** `streamlit run app.py`, type a prompt, press Run.

**CLI:**
```bash
python run.py VWO-49                    # generate a plan
python run.py "make a plan for VWO-49"  # same, natural language
python run.py --health                  # test both connections
python run.py --dry-run VWO-49          # fetch + normalize, no LLM call
python run.py --force VWO-49            # plan even if the ticket is thin
```

Exit codes: `0` ok · `2` bad input · `3` auth · `4` not found · `5` rate limited ·
`6` schema violation · `7` LLM failure.

Output lands in `out/`: the plan markdown plus a `-trace.json` audit record.

## How it works

```
prompt -> parse key -> fetch Jira -> normalize -> readiness -> Groq -> render -> plan.md
         (regex)      (REST v3)     (ADF->md)   (gate)      (1 call) (template)
```

Seven steps. **Six are deterministic Python. Exactly one calls a model.** That is the whole
design: when the output is wrong you can tell which step did it.

| Layer | Where | What |
|---|---|---|
| 1 Architecture | `architecture/` | Six markdown SOPs. If logic changes, the SOP changes first. |
| 2 Navigation | `navigation.py` | Routes data between tools. Decides order and failure branches. |
| 3 Tools | `tools/` | Nine atomic Python tools. Six are pure functions. |

The model returns **JSON, not markdown**. `render.py` owns the format, so the model never
sees the template and cannot drift from it.

## What it will not do

- **Invent anything.** No acceptance criterion, URL, date or tool appears in the plan
  unless it appears on the ticket. Everything else lands in an `Assumptions` table.
- **Pad the scope.** Every scope entry carries a `justified_by` naming the ticket fact
  that put it there. The schema rejects entries that cannot fill it.
- **Plan a thin ticket.** Below 5/11 on readiness the agent refuses and returns a gap
  report naming what to add. Use `--force` to override.

## Tests

```bash
python tests/test_pipeline.py     # 45 checks, no network, no model
```

Fixtures in `fixtures/` cover a rich ADF ticket (tables, code blocks, panels, an unknown
node type) and a deliberately thin one.
