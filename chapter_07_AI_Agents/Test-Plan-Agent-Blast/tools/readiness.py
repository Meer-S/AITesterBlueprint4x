"""SOP 04 - is this ticket plannable at all? PURE.

BR-4: the agent must be willing to return no plan. A confident plan built on an
empty ticket is worse than no plan, because it gets reviewed and approved.
"""
THRESHOLD = 5
MAX_SCORE = 11


def check(ticket: dict) -> dict:
    score = 0
    gaps = list(ticket.get("gaps", []))
    blockers = []

    summary = (ticket.get("summary") or "").strip()
    if len(summary.split()) >= 3:
        score += 2
    else:
        blockers.append("Give the ticket a descriptive summary of at least 3 words.")

    desc = ticket.get("description_md") or ""
    if len(desc) >= 200:
        score += 3
    elif len(desc) >= 40:
        score += 1
        blockers.append("Expand the description. Under 200 characters is not enough "
                        "to derive test scope from.")
    else:
        blockers.append("Add a description. The ticket has effectively no body.")

    ac = ticket.get("acceptance_criteria") or []
    if len(ac) >= 1:
        score += 3
    else:
        blockers.append("Add acceptance criteria. They are the strongest input to a test plan.")
    if len(ac) >= 3:
        score += 1

    if ticket.get("components") or ticket.get("labels"):
        score += 1
    if ticket.get("fix_versions") or (ticket.get("schedule") or {}).get("sprint_name"):
        score += 1

    return {
        "plannable": score >= THRESHOLD,
        "score": score,
        "max": MAX_SCORE,
        "threshold": THRESHOLD,
        "gaps": gaps,
        "blockers": blockers,
    }
