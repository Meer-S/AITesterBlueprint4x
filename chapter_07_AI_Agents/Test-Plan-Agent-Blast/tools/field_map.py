"""SOP 02 - resolve the Acceptance Criteria custom field id per site. PURE.

Never hardcode customfield_10034. The id differs per Jira site (risk R2).
"""
import re

AC_PATTERNS = [
    (re.compile(r"^acceptance\s*criteria$", re.I), 100),
    (re.compile(r"acceptance\s*criteria", re.I), 90),
    (re.compile(r"^ac$", re.I), 70),
    (re.compile(r"definition\s*of\s*done", re.I), 60),
    (re.compile(r"criteria", re.I), 40),
]


def resolve(names: dict) -> dict:
    """`names` is the field-id -> display-name map from expand=names."""
    if not names:
        return {"acceptance_criteria": None, "matched_name": None, "candidates": []}

    scored = []
    for field_id, display in names.items():
        if not isinstance(display, str):
            continue
        for pattern, score in AC_PATTERNS:
            if pattern.search(display.strip()):
                scored.append((score, field_id, display))
                break

    scored.sort(key=lambda x: (-x[0], x[1]))
    if not scored:
        return {"acceptance_criteria": None, "matched_name": None, "candidates": []}

    _, best_id, best_name = scored[0]
    return {
        "acceptance_criteria": best_id,
        "matched_name": best_name,
        "candidates": [{"id": i, "name": n, "score": s} for s, i, n in scored],
    }
