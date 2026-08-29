"""Layer 2 - Navigation. The reasoning and routing layer.

This module decides WHICH tool runs next and WHAT to do when one fails. It does
not parse ADF, does not build URLs, does not format markdown. Those are Layer 3.

AI-2: exactly one step here is probabilistic (build_plan). Everything else is
deterministic Python, including the intent parse.
"""
from pathlib import Path

from tools import (config_store, jira_fetch, llm_client, normalize, plan_build,
                   readiness, render, trace)
from tools.errors import AgentError, NotPlannableError

BASE = Path(__file__).resolve().parent
OUT = BASE / "out"
TMP = BASE / ".tmp"


def parse_intent(prompt: str) -> dict:
    """Natural-language prompt -> a Jira key. Deterministic regex, NOT an LLM call.

    "Fetch SCRUM-42 and create a test plan" -> {"key": "SCRUM-42"}

    An LLM here would add a failure mode and a network round trip to a problem a
    regex solves exactly. Invariant AI-2 says one probabilistic step, and this is
    not the one worth spending it on.
    """
    key = jira_fetch.extract_key(prompt)
    return {"key": key, "raw_prompt": prompt}


def run(prompt: str, progress=None, force: bool = False) -> dict:
    """The full pipeline. `progress(step, status, detail)` is the UI hook."""
    def emit(step, status="running", detail=""):
        if progress:
            progress(step, status, detail)

    emit("Parse request")
    intent = parse_intent(prompt)
    key = intent["key"]
    tr = trace.new(key)
    trace.step(tr, "parse_intent", key=key, method="regex (deterministic)")
    emit("Parse request", "done", f"Jira key: {key}")

    emit("Fetch from Jira")
    raw = jira_fetch.fetch(key)
    site = raw["_meta"]["site"]
    trace.step(tr, "fetch", requests=raw["_meta"]["requests"])
    emit("Fetch from Jira", "done", raw["issue"]["fields"].get("summary", ""))

    emit("Normalize")
    cfg = config_store.load_config()
    ticket = normalize.normalize(raw, site, include_comments=cfg.get("include_comments", True))

    # Cache the resolved AC field id so later runs skip discovery (SOP 02).
    from tools import field_map
    fm = field_map.resolve(raw["issue"].get("names", {}))
    if fm["acceptance_criteria"]:
        config_store.save_config({"field_map_cache": fm})

    from tools import adf_flatten
    delta = adf_flatten.loss_delta_pct(ticket["description_md"],
                                       ticket.get("description_html") or "")
    trace.step(tr, "normalize",
               ac_found=len(ticket["acceptance_criteria"]),
               ac_origin=(ticket["acceptance_criteria"][0]["origin"]
                          if ticket["acceptance_criteria"] else None),
               ac_field_resolved=fm["acceptance_criteria"],
               unknown_adf_nodes=ticket.get("unknown_adf_nodes", []),
               html_crosscheck_delta_pct=delta,
               gaps=ticket["gaps"])
    TMP.mkdir(exist_ok=True)
    import json
    (TMP / f"{key}_ticket.json").write_text(json.dumps(ticket, indent=2))
    emit("Normalize", "done",
         f"{len(ticket['acceptance_criteria'])} acceptance criteria, "
         f"{len(ticket['gaps'])} gaps")

    emit("Readiness check")
    rd = readiness.check(ticket)
    trace.step(tr, "readiness", **rd)
    if not rd["plannable"] and not force:
        trace.finish(tr, OUT, outcome="refused_thin_ticket")
        raise NotPlannableError(
            f"{key} scored {rd['score']}/{rd['max']} on readiness "
            f"(threshold {rd['threshold']}). No plan was written.",
            "A confident plan built on a thin ticket is worse than no plan. "
            "Fix the ticket, or use 'Plan anyway'.",
            report={"ticket": ticket, "readiness": rd},
        )
    emit("Readiness check", "done", f"score {rd['score']}/{rd['max']}")

    try:
        gen_step = f"Generate plan ({llm_client.provider_spec()['label']})"
    except Exception:
        gen_step = "Generate plan (LLM)"
    emit(gen_step)
    plan, usage = build_plan(ticket)
    trace.step(tr, "llm", **usage)
    (TMP / f"{key}_plan.json").write_text(json.dumps(plan, indent=2))
    emit(gen_step, "done",
         f"{len(plan['scope'])} scope areas, {len(plan.get('assumptions', []))} assumptions, "
         f"valid on attempt {usage.get('schema_valid_on_attempt')}")

    emit("Render")
    markdown = render.render(plan, ticket, model=usage.get("model", ""))
    OUT.mkdir(exist_ok=True)
    out_path = OUT / f"{key}-test-plan.md"
    out_path.write_text(markdown)
    trace_path = trace.finish(tr, OUT, outcome="ok",
                              output={"path": str(out_path), "bytes": len(markdown)})
    emit("Render", "done", str(out_path.name))

    return {"key": key, "ticket": ticket, "readiness": rd, "plan": plan,
            "markdown": markdown, "path": out_path, "trace_path": trace_path,
            "trace": tr, "usage": usage}


def build_plan(ticket: dict):
    """The single probabilistic step, isolated behind one function (AI-2)."""
    return plan_build.build(ticket)


def health() -> dict:
    """Phase 2 LINK status, used by the UI and the CLI."""
    from tools import jira_auth
    out = {}
    try:
        out["jira"] = {"ok": True, "detail": jira_auth.verify()}
    except AgentError as e:
        out["jira"] = {"ok": False, "error": e.message, "remedy": e.remedy}
    try:
        spec = llm_client.provider_spec()
        label = spec["label"].lower()
    except AgentError:
        label = "llm"
    try:
        out[label] = {"ok": True, "detail": llm_client.verify()}
    except AgentError as e:
        out[label] = {"ok": False, "error": e.message, "remedy": e.remedy}
    return out
