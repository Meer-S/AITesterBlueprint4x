"""Offline verification. No network, no model (invariant AI-8).

Run: python tests/test_pipeline.py
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from tools import adf_flatten, field_map, normalize, readiness, render
from tools.errors import RenderError, SchemaError

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


def load(key):
    return json.loads((BASE / "fixtures" / f"{key}_raw.json").read_text())


def main():
    print("\n=== ADF flattener (SOP 03 Part A) ===")
    raw = load("BOOK-214")
    md, unknown = adf_flatten.flatten_with_report(raw["issue"]["fields"]["description"])
    check("heading rendered", "## Background" in md)
    check("bullets rendered", md.count("\n- ") >= 4, f"{md.count(chr(10)+'- ')} bullets")
    check("table rendered with header separator", "| Case | Status | Code |" in md and "| --- " in md)
    check("table body rows kept", "DATE_RANGE_INVALID" in md and "DATE_RANGE_ZERO" in md)
    check("code block fenced with language", "```json" in md)
    check("panel became a blockquote", "> **WARNING:**" in md)
    check("rule rendered", "\n---\n" in md)
    check("bold mark applied", "**14 tickets**" in md)
    check("link mark applied", "[design doc](https://confluence.example.com/booking-dates)" in md)
    check("unknown node recorded, not silently dropped", unknown == ["expand"], str(unknown))
    check("unknown node CONTENT preserved", "epoch millis" in md)

    print("\n=== Field map (SOP 02) ===")
    fm = field_map.resolve(raw["issue"]["names"])
    check("AC custom field resolved at runtime", fm["acceptance_criteria"] == "customfield_10034",
          str(fm["acceptance_criteria"]))
    other_site = field_map.resolve({"customfield_19999": "Acceptance Criteria"})
    check("resolves a DIFFERENT site's id, so nothing is hardcoded (R2)",
          other_site["acceptance_criteria"] == "customfield_19999",
          str(other_site["acceptance_criteria"]))
    ranked = field_map.resolve({"customfield_1": "Definition of Done",
                                "customfield_2": "Acceptance Criteria"})
    check("exact 'Acceptance Criteria' outranks 'Definition of Done'",
          ranked["acceptance_criteria"] == "customfield_2")
    check("empty names map returns None, does not crash",
          field_map.resolve({})["acceptance_criteria"] is None)

    print("\n=== Normalize (SOP 03 Part C) ===")
    ticket = normalize.normalize(raw, "https://example.atlassian.net")
    check("schema validation passed", ticket["key"] == "BOOK-214")
    check("4 acceptance criteria split from Given/When/Then",
          len(ticket["acceptance_criteria"]) == 4, str(len(ticket["acceptance_criteria"])))
    check("AC origin recorded as custom_field",
          all(a["origin"] == "custom_field" for a in ticket["acceptance_criteria"]))
    check("Given/When/Then kept as one criterion, not split into 3",
          all("Given" in a["text"] and "then" in a["text"].lower()
              for a in ticket["acceptance_criteria"]))
    check("components extracted", ticket["components"] == ["Booking API"])
    check("issue links extracted", ticket["relations"]["links"][0]["key"] == "BOOK-230")
    check("remote links extracted", len(ticket["relations"]["remote_links"]) == 1)
    check("attachments extracted", ticket["attachments"][0]["filename"] == "date-validation-spec.pdf")
    check("unknown ADF node surfaced as a gap",
          any("expand" in g for g in ticket["gaps"]))
    delta = adf_flatten.loss_delta_pct(ticket["description_md"], ticket["description_html"])
    check("HTML cross-check shows no major loss (R3)", delta < 25, f"delta {delta}%")

    print("\n=== AC fallback strategies ===")
    no_cf = json.loads(json.dumps(raw))
    del no_cf["issue"]["fields"]["customfield_10034"]
    no_cf["issue"]["names"].pop("customfield_10034")
    no_cf["issue"]["fields"]["description"]["content"].append(
        {"type": "heading", "attrs": {"level": 2},
         "content": [{"type": "text", "text": "Acceptance Criteria"}]})
    no_cf["issue"]["fields"]["description"]["content"].append(
        {"type": "bulletList", "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [
                {"type": "text", "text": "Invalid ranges are rejected with 400."}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [
                {"type": "text", "text": "Valid ranges still return 201."}]}]}]})
    t2 = normalize.normalize(no_cf, "https://example.atlassian.net")
    check("falls back to description heading when no custom field",
          len(t2["acceptance_criteria"]) == 2 and
          t2["acceptance_criteria"][0]["origin"] == "description_heading",
          f"{len(t2['acceptance_criteria'])} found")

    thin_raw = load("BOOK-999")
    t3 = normalize.normalize(thin_raw, "https://example.atlassian.net")
    check("absent AC yields empty list plus a gap, never an invented list (BR-1)",
          t3["acceptance_criteria"] == [] and
          any("No acceptance criteria" in g for g in t3["gaps"]))

    print("\n=== Readiness (SOP 04) ===")
    rd = readiness.check(ticket)
    check("rich ticket is plannable", rd["plannable"], f"{rd['score']}/{rd['max']}")
    rd_thin = readiness.check(t3)
    check("thin ticket is refused (BR-4)", not rd_thin["plannable"],
          f"{rd_thin['score']}/{rd_thin['max']}")
    check("refusal names actionable blockers", len(rd_thin["blockers"]) >= 2,
          str(rd_thin["blockers"][:1]))

    print("\n=== Render + output gates (SOP 06) ===")
    plan = json.loads((BASE / "fixtures" / "sample_plan.json").read_text())
    md_out = render.render(plan, ticket, model="openai/gpt-oss-120b")
    check("no unfilled placeholders", "{{" not in md_out)
    check("no authoring comments", "<!--" not in md_out)
    check("all 14 sections present, in template order",
          all(f"## {h}" in md_out for h in render.REQUIRED_HEADINGS))
    check("no em dashes (BR-12)", "—" not in md_out)
    check("assumptions rendered into the deliverable (BR-14)",
          "## Assumptions" in md_out and "_(assumed - confirm)_" in md_out)
    check("dropped scope rendered", "## Scope Deliberately Excluded" in md_out)
    check("traceability matrix built from AC", "## Traceability" in md_out and
          "custom_field" in md_out)
    check("justified_by rendered for every scope entry",
          md_out.count("*Justified by:*") == len(plan["scope"]))
    check("ticket gaps surfaced in the deliverable", "## Gaps Found on the Source Ticket" in md_out)

    print("\n=== Gate enforcement (negative tests) ===")
    try:
        bad = dict(plan); bad["objective"] = plan["objective"] + " — with an em dash"
        render.render(bad, ticket)
        check("em dash trips the output gate", False, "no error raised")
    except RenderError:
        check("em dash trips the output gate", True)

    try:
        normalize.validate({"key": "nope"})
        check("bad ticket trips schema validation", False, "no error raised")
    except SchemaError:
        check("bad ticket trips schema validation", True)

    print("\n=== Plan schema gate (SOP 05) ===")
    from tools import plan_build
    check("valid plan passes plan.schema.json", plan_build._errors(plan) == [])
    unjustified = json.loads(json.dumps(plan))
    unjustified["scope"][0]["justified_by"] = ""
    check("scope entry without justified_by is REJECTED (BR-3)",
          plan_build._errors(unjustified) != [])
    fenced = plan_build._extract_json("```json\n{\"a\": 1}\n```")
    check("code-fenced model output is recovered", fenced == {"a": 1})
    prosey = plan_build._extract_json('Sure! Here is the plan:\n{"a": 2}\nHope that helps.')
    check("prose-wrapped model output is recovered", prosey == {"a": 2})

    print(f"\n{'='*56}\n  {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("  FAILED: " + ", ".join(FAIL))
    print("=" * 56)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
