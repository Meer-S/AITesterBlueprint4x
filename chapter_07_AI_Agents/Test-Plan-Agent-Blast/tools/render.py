"""SOP 06 - plan.json + frozen template -> the deliverable. PURE.

Section order and headings come from the template, never from the model (BR-10).
The renderer decides how an assumption LOOKS; the model only decided whether
something IS one.
"""
import re
from datetime import datetime
from pathlib import Path

from tools.errors import RenderError

ASSETS = Path(__file__).resolve().parent.parent / "assets"

REQUIRED_HEADINGS = [
    "Objective", "Scope", "Inclusions", "Test Environments",
    "Defect Reporting Procedure", "Test Strategy", "Test Schedule",
    "Test Deliverables", "Entry and Exit Criteria", "Test Execution",
    "Test Closure", "Tools", "Risks and Mitigations", "Approvals",
]

ASSUMED = " _(assumed - confirm)_"


def _table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join([" --- "] * len(headers)) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows]
    return "\n".join(out)


def render(plan: dict, ticket: dict, model: str = "") -> str:
    head = (ASSETS / "test-plan-template.md").read_text()
    head = (head.replace("{{FEATURE}}", ticket.get("summary", "Untitled"))
                .replace("{{KEY}}", ticket.get("key", ""))
                .replace("{{URL}}", ticket.get("url", ""))
                .replace("{{TITLE}}", ticket.get("summary", ""))
                .replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d %H:%M"))
                .replace("{{MODEL}}", model or "unspecified"))

    p = [head, ""]

    p.append("## Objective\n")
    p.append(plan["objective"])
    if plan.get("target_url"):
        p.append(f"\n**System under test:** {plan['target_url']}")
    p.append("")

    p.append("## Scope\n")
    for i, s in enumerate(plan["scope"], 1):
        p.append(f"{i}. **{s['type']} Testing** - {s['rationale']}")
        p.append(f"   - *Justified by:* {s['justified_by']}")
    p.append("\n> Scope may evolve during testing based on feedback, changing "
             "requirements, or discoveries.\n")

    p.append("## Inclusions\n")
    for group in plan["inclusions"]:
        p.append(f"**{group['group']}**\n")
        p.extend(f"- {item}" for item in group["items"])
        p.append("")

    p.append("## Test Environments\n")
    envs = plan.get("environments") or []
    if envs:
        p.append(_table(["Name", "Env URL"],
                        [[e["name"], e["url"] + (ASSUMED if e.get("assumed") else "")]
                         for e in envs]))
    else:
        p.append("_No environments named on the ticket._")
    p.append("")

    p.append("## Defect Reporting Procedure\n")
    dp = plan.get("defect_process") or {}
    p.append(f"- **Tooling:** {dp.get('tool', 'JIRA')}")
    if dp.get("severity_model"):
        p.append(f"- **Triage:** {dp['severity_model']}")
    p.append("- **Reporting:** detailed reproduction steps, screenshots and logs attached.")
    if dp.get("pocs"):
        p.append("\n**Roles / POCs**\n")
        p.append(_table(["Area", "POC"],
                        [[x["area"], x["poc"] + (ASSUMED if x.get("assumed") else "")]
                         for x in dp["pocs"]]))
    p.append("")

    p.append("## Test Strategy\n")
    st = plan["strategy"]
    p.append("**Test design techniques**\n")
    p.extend(f"- {t}" for t in st["techniques"])
    p.append(f"\n**Execution flow.** {st['execution_flow']}")
    if st.get("best_practices"):
        p.append("\n**Best practices**\n")
        p.extend(f"- {b}" for b in st["best_practices"])
    p.append("")

    p.append("## Test Schedule\n")
    sched = plan.get("schedule") or []
    if sched:
        p.append(_table(["Task", "Dates"],
                        [[s["task"], s["dates"] + (ASSUMED if s.get("assumed") else "")]
                         for s in sched]))
    else:
        p.append("_No schedule anchor on the ticket (no sprint or fix version)._")
    p.append("")

    p.append("## Test Deliverables\n")
    p.extend(f"- {d}" for d in plan["deliverables"])
    p.append("")

    p.append("## Entry and Exit Criteria\n")
    for ee in plan.get("entry_exit") or []:
        p.append(f"### {ee['phase']}")
        p.append(f"- **Entry:** {ee['entry']}")
        p.append(f"- **Exit:** {ee['exit']}\n")

    p.append("## Test Execution\n")
    p.append(st["execution_flow"])
    p.append("")

    p.append("## Test Closure\n")
    p.append("Closure is reached when the exit criteria above are met and the Test "
             "Summary Report is delivered and accepted.\n")

    p.append("## Tools\n")
    p.extend(f"- {t}" for t in plan["tools"])
    p.append("")

    p.append("## Risks and Mitigations\n")
    p.append(_table(["Risk", "Mitigation"],
                    [[r["risk"], r["mitigation"]] for r in plan["risks"]]))
    p.append("")

    p.append("## Approvals\n")
    p.append("Sent for review before proceeding to the next step: Test Plan, Test "
             "Scenarios, Test Cases, Reports.\n")

    # BR-14: these are part of the deliverable, not debug output.
    p.append("---\n")
    p.append("## Assumptions (confirm before sign-off)\n")
    assumptions = plan.get("assumptions") or []
    if assumptions:
        p.append(_table(["Field", "Assumed value", "Why"],
                        [[a["field"], a["assumed_value"], a["why"]] for a in assumptions]))
    else:
        p.append("_The model recorded no assumptions._")
    p.append("")

    if plan.get("dropped_scope"):
        p.append("## Scope Deliberately Excluded\n")
        p.append(_table(["Test type", "Reason"],
                        [[d["type"], d["reason"]] for d in plan["dropped_scope"]]))
        p.append("")

    gaps = ticket.get("gaps") or []
    if gaps:
        p.append("## Gaps Found on the Source Ticket\n")
        p.extend(f"- {g}" for g in gaps)
        p.append("")

    ac = ticket.get("acceptance_criteria") or []
    p.append("## Traceability\n")
    if ac:
        p.append(_table(["#", "Acceptance criterion", "Source"],
                        [[i, a["text"].replace("\n", " ")[:160], a["origin"]]
                         for i, a in enumerate(ac, 1)]))
    else:
        p.append("_No acceptance criteria on the ticket, so no traceability matrix "
                 "could be built. This is a gap in the ticket, not in the plan._")
    p.append("")

    text = "\n".join(p)
    _gate(text)
    return text


def _gate(text: str):
    """Output gates. A tripped gate means no file is written (BR-17)."""
    problems = []
    if "{{" in text:
        problems.append(f"unfilled placeholders: {set(re.findall(r'{{[A-Z_]+}}', text))}")
    if "<!--" in text:
        problems.append("authoring comments survived into the output")
    missing = [h for h in REQUIRED_HEADINGS if f"## {h}" not in text]
    if missing:
        problems.append(f"missing sections: {missing}")
    if "—" in text:
        problems.append("em dash found (BR-12)")
    for block in re.findall(r"(?:^\|.*\|$\n?)+", text, re.M):
        rows = [r for r in block.strip().split("\n") if r.strip()]
        if len(rows) < 2:
            continue
        width = rows[0].count("|")
        bad = [r for r in rows if r.count("|") != width]
        if bad:
            problems.append(f"table column mismatch near: {bad[0][:60]}")
            break
    if problems:
        raise RenderError("Output gates failed: " + "; ".join(problems),
                          "The plan was not written. This is a renderer bug, not a "
                          "model problem. Check tools/render.py.")
