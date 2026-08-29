"""SOP 03 Part B+C - raw Jira JSON -> validated ticket.json. PURE (AI-4).

The schema is the only interface (AI-1): REST, MCP, file and fixture all land here.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

from tools import adf_flatten, field_map
from tools.errors import SchemaError

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "ticket.schema.json"

AC_HEADING = re.compile(r"^#{1,6}\s*(acceptance\s*criteria|ac)\s*:?\s*$", re.I | re.M)
GWT = re.compile(r"^\s*(given|when|then|and)\b", re.I)


def _validator():
    return Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))


def validate(ticket: dict) -> dict:
    errors = sorted(_validator().iter_errors(ticket), key=lambda e: e.path)
    if errors:
        e = errors[0]
        path = "/".join(str(p) for p in e.path) or "<root>"
        raise SchemaError(
            f"ticket.json failed validation at `{path}`: {e.message}",
            "Jira returned a shape this build does not expect. "
            "The raw response is in .tmp/ for inspection.",
        )
    return ticket


def split_criteria(text: str) -> list:
    """Bullets become one AC each. Given/When/Then blocks stay together."""
    if not text:
        return []
    lines = [ln.rstrip() for ln in text.strip().splitlines()]
    out, buf = [], []

    def flush():
        if buf:
            joined = "\n".join(buf).strip()
            if joined:
                out.append(joined)
            buf.clear()

    for ln in lines:
        stripped = ln.strip()
        if not stripped:
            if buf and not GWT.match(buf[-1]):
                flush()
            continue
        if re.match(r"^\s*([-*+]|\d+[.)])\s+", ln) and not GWT.match(stripped):
            flush()
            buf.append(re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", ln))
        elif GWT.match(stripped):
            if buf and re.match(r"^\s*given\b", stripped, re.I):
                flush()
            buf.append(stripped)
        else:
            buf.append(stripped)
    flush()
    return [c for c in out if len(c) > 3]


def extract_ac(fields: dict, description_md: str, comments: list,
               ac_field_id, include_comments: bool) -> tuple[list, list]:
    """Four strategies, first hit wins. Records which one fired (SOP 03 Part B)."""
    gaps = []

    # 1. custom field
    if ac_field_id and fields.get(ac_field_id):
        raw = fields[ac_field_id]
        text = adf_flatten.flatten(raw) if isinstance(raw, dict) else str(raw)
        items = split_criteria(text)
        if items:
            return [{"text": t, "origin": "custom_field", "ref": ac_field_id}
                    for t in items], gaps

    # 2. description heading
    m = AC_HEADING.search(description_md or "")
    if m:
        start = m.end()
        rest = description_md[start:]
        nxt = re.search(r"^#{1,6}\s+\S", rest, re.M)
        block = rest[: nxt.start()] if nxt else rest
        items = split_criteria(block)
        if items:
            return [{"text": t, "origin": "description_heading",
                     "ref": m.group(0).strip()} for t in items], gaps

    # 3. comments
    if include_comments:
        for c in comments:
            body = c.get("body_md", "")
            if re.search(r"acceptance\s*criteria", body[:200], re.I):
                items = split_criteria(re.sub(r"(?i).*acceptance\s*criteria\s*:?", "",
                                              body, count=1))
                if items:
                    gaps.append("Acceptance criteria were found in a comment, "
                                "not in a dedicated field. Confirm they are current.")
                    return [{"text": t, "origin": "comment", "ref": c.get("id")}
                            for t in items], gaps

    # 4. absent. BR-1/BR-2: a gap, never an invented list.
    gaps.append("No acceptance criteria found on the ticket "
                "(checked custom field, description heading, comments).")
    return [], gaps


def normalize(raw: dict, site: str, include_comments: bool = True,
              transport: str = "rest") -> dict:
    issue = raw.get("issue", raw)
    fields = issue.get("fields", {}) or {}
    names = issue.get("names", {}) or {}
    rendered = issue.get("renderedFields", {}) or {}
    key = issue.get("key", "")

    fm = field_map.resolve(names)
    description_md, unknown_nodes = adf_flatten.flatten_with_report(fields.get("description"))
    description_html = rendered.get("description")

    comments = []
    for c in (raw.get("comments") or {}).get("comments", []) if isinstance(
            raw.get("comments"), dict) else (raw.get("comments") or []):
        body = c.get("body")
        comments.append({
            "id": str(c.get("id", "")),
            "author": (c.get("author") or {}).get("displayName", "unknown"),
            "created": c.get("created", ""),
            "body_md": adf_flatten.flatten(body) if isinstance(body, dict) else str(body or ""),
        })

    acceptance_criteria, gaps = extract_ac(fields, description_md, comments,
                                           fm["acceptance_criteria"], include_comments)

    def named(items, attr="name"):
        return [i.get(attr, "") for i in (items or []) if isinstance(i, dict) and i.get(attr)]

    sprint = fields.get("sprint") or {}
    if isinstance(sprint, list):
        sprint = sprint[-1] if sprint else {}
    if not isinstance(sprint, dict):
        sprint = {}

    ticket = {
        "key": key,
        "url": f"{site}/browse/{key}" if site else f"/browse/{key}",
        "summary": fields.get("summary", "") or "",
        "issue_type": (fields.get("issuetype") or {}).get("name", "Unknown"),
        "status": (fields.get("status") or {}).get("name"),
        "priority": (fields.get("priority") or {}).get("name"),
        "labels": fields.get("labels") or [],
        "components": named(fields.get("components")),
        "fix_versions": named(fields.get("fixVersions")),
        "environment": (adf_flatten.flatten(fields["environment"])
                        if isinstance(fields.get("environment"), dict)
                        else fields.get("environment")),
        "description_md": description_md,
        "description_html": description_html,
        "acceptance_criteria": acceptance_criteria,
        "people": {
            "assignee": (fields.get("assignee") or {}).get("displayName"),
            "reporter": (fields.get("reporter") or {}).get("displayName"),
        },
        "schedule": {
            "sprint_name": sprint.get("name"),
            "sprint_start": (sprint.get("startDate") or "")[:10] or None,
            "sprint_end": (sprint.get("endDate") or "")[:10] or None,
            "due_date": fields.get("duedate"),
            "created": fields.get("created"),
            "updated": fields.get("updated"),
        },
        "relations": {
            "parent": (fields.get("parent") or {}).get("key"),
            "subtasks": [s.get("key", "") for s in (fields.get("subtasks") or [])],
            "links": _links(fields.get("issuelinks") or []),
            "remote_links": [
                {"title": (r.get("object") or {}).get("title", ""),
                 "url": (r.get("object") or {}).get("url", "")}
                for r in (raw.get("remote_links") or [])
                if (r.get("object") or {}).get("url")
            ],
        },
        "comments": comments if include_comments else [],
        "attachments": [
            {"id": str(a.get("id", "")), "filename": a.get("filename", ""),
             "mime_type": a.get("mimeType", ""), "size": int(a.get("size", 0) or 0)}
            for a in (fields.get("attachment") or [])
        ],
        "source": {"transport": transport, "api_version": "3", "site": site},
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "gaps": gaps,
        "unknown_adf_nodes": unknown_nodes,
    }

    # BR-2: absence is data.
    if not ticket["description_md"]:
        ticket["gaps"].append("Ticket has no description.")
    elif len(ticket["description_md"]) < 200:
        ticket["gaps"].append("Description is very short (under 200 characters).")
    if not ticket["components"] and not ticket["labels"]:
        ticket["gaps"].append("No components or labels, so the affected area is unstated.")
    if not ticket["fix_versions"] and not ticket["schedule"]["sprint_name"]:
        ticket["gaps"].append("No fix version or sprint, so the schedule has no anchor.")
    if not ticket["environment"]:
        ticket["gaps"].append("No environment named on the ticket.")
    if unknown_nodes:
        ticket["gaps"].append(
            f"Unrecognised ADF node types in the description: {', '.join(unknown_nodes)}.")

    return validate(ticket)


def _links(issuelinks: list) -> list:
    out = []
    for link in issuelinks:
        for direction, label in (("outwardIssue", "outward"), ("inwardIssue", "inward")):
            issue = link.get(direction)
            if issue:
                ltype = (link.get("type") or {}).get(
                    "outward" if direction == "outwardIssue" else "inward", label)
                out.append({"type": ltype, "key": issue.get("key", ""),
                            "summary": (issue.get("fields") or {}).get("summary")})
    return out
