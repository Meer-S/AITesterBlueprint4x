"""ADF (Atlassian Document Format) -> markdown. PURE (AI-4).

SOP 03 Part A. A naive extractor that concatenates `text` nodes loses headings,
bullet boundaries, table cells and code blocks. For test planning that structure
IS the requirement, so this emits markdown, not a text blob.
"""
import re

MARK_WRAP = {
    "strong": ("**", "**"),
    "em": ("*", "*"),
    "code": ("`", "`"),
    "strike": ("~~", "~~"),
    "underline": ("", ""),
}

PANEL_LABEL = {
    "info": "NOTE", "note": "NOTE", "warning": "WARNING",
    "error": "ERROR", "success": "SUCCESS",
}


def flatten(doc, unknown=None) -> str:
    """ADF dict (or plain string) -> markdown. `unknown` collects unseen node types."""
    if unknown is None:
        unknown = set()
    if doc is None:
        return ""
    if isinstance(doc, str):
        return doc.strip()
    if not isinstance(doc, dict):
        return ""
    out = _node(doc, unknown, depth=0)
    return re.sub(r"\n{3,}", "\n\n", out).strip()


def flatten_with_report(doc) -> tuple[str, list]:
    unknown = set()
    text = flatten(doc, unknown)
    return text, sorted(unknown)


def _children(node, unknown, depth=0, sep=""):
    return sep.join(_node(c, unknown, depth) for c in node.get("content", []) or [])


def _node(node, unknown, depth=0) -> str:
    if not isinstance(node, dict):
        return ""
    t = node.get("type", "")

    if t == "doc":
        return _children(node, unknown, depth, sep="\n\n")

    if t == "text":
        txt = node.get("text", "")
        for mark in node.get("marks", []) or []:
            mt = mark.get("type")
            if mt == "link":
                href = mark.get("attrs", {}).get("href", "")
                txt = f"[{txt}]({href})"
            elif mt in MARK_WRAP:
                pre, post = MARK_WRAP[mt]
                txt = f"{pre}{txt}{post}"
        return txt

    if t == "paragraph":
        return _children(node, unknown, depth)

    if t == "heading":
        level = int(node.get("attrs", {}).get("level", 1))
        return "#" * max(1, min(6, level)) + " " + _children(node, unknown, depth)

    if t in ("bulletList", "orderedList"):
        ordered = t == "orderedList"
        lines = []
        for i, item in enumerate(node.get("content", []) or [], start=1):
            body = _node(item, unknown, depth + 1).strip()
            if not body:
                continue
            marker = f"{i}. " if ordered else "- "
            pad = "  " * depth
            first, *rest = body.split("\n")
            lines.append(f"{pad}{marker}{first}")
            lines.extend(r if r.startswith(" ") else f"{pad}  {r}" for r in rest if r.strip())
        return "\n".join(lines)

    if t == "listItem":
        return _children(node, unknown, depth, sep="\n")

    if t == "table":
        rows = []
        for row in node.get("content", []) or []:
            cells = [_node(c, unknown, depth).replace("\n", " ").strip()
                     for c in row.get("content", []) or []]
            rows.append(cells)
        if not rows:
            return ""
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        lines = ["| " + " | ".join(rows[0]) + " |",
                 "|" + "|".join([" --- "] * width) + "|"]
        lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
        return "\n".join(lines)

    if t in ("tableRow", "tableHeader", "tableCell"):
        return _children(node, unknown, depth, sep=" ")

    if t == "codeBlock":
        lang = node.get("attrs", {}).get("language", "") or ""
        return f"```{lang}\n{_children(node, unknown, depth)}\n```"

    if t == "blockquote":
        body = _children(node, unknown, depth, sep="\n")
        return "\n".join(f"> {ln}" for ln in body.split("\n"))

    if t == "panel":
        label = PANEL_LABEL.get(node.get("attrs", {}).get("panelType", "info"), "NOTE")
        body = _children(node, unknown, depth, sep="\n")
        return "\n".join(f"> **{label}:** {ln}" if i == 0 else f"> {ln}"
                         for i, ln in enumerate(body.split("\n")))

    if t == "rule":
        return "---"

    if t == "hardBreak":
        return "\n"

    if t in ("mediaSingle", "mediaGroup"):
        return _children(node, unknown, depth, sep="\n")

    if t == "media":
        attrs = node.get("attrs", {})
        return f"_[attachment: {attrs.get('alt') or attrs.get('id', 'file')}]_"

    if t in ("inlineCard", "blockCard", "embedCard"):
        return f"<{node.get('attrs', {}).get('url', '')}>"

    if t == "emoji":
        return node.get("attrs", {}).get("text", "")

    if t == "mention":
        return "@" + node.get("attrs", {}).get("text", "").lstrip("@")

    if t == "date":
        return node.get("attrs", {}).get("timestamp", "")

    if t == "status":
        return f"[{node.get('attrs', {}).get('text', '')}]"

    # Unknown node: recurse so content is not lost, but RECORD it (SOP 03).
    unknown.add(t)
    return _children(node, unknown, depth)


def strip_html(html: str) -> str:
    """Crude text extraction from renderedFields HTML, for the loss cross-check."""
    if not html:
        return ""
    txt = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = (txt.replace("&nbsp;", " ").replace("&amp;", "&")
              .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    return re.sub(r"\s+", " ", txt).strip()


def loss_delta_pct(markdown: str, html: str) -> float:
    """Percent of the rendered text that the flattener did not reproduce (risk R3)."""
    ref = strip_html(html)
    if not ref:
        return 0.0
    got = re.sub(r"\s+", " ", re.sub(r"[#*`>|\-\[\]()_~]", " ", markdown)).strip()
    return round(max(0.0, (len(ref) - len(got)) / len(ref) * 100), 1)
