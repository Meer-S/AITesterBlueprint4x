"""Test Plan Agent - main UI.

One prompt box: "Fetch SCRUM-42 and create a test plan".
The agent parses the key, fetches the ticket, checks readiness, calls Groq once,
and renders a formal test plan.
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

import navigation
from tools import config_store
from tools.errors import AgentError, NotPlannableError

st.set_page_config(page_title="Test Plan Agent", page_icon="🧭", layout="wide")

from tools import llm_client

try:
    _PROVIDER = llm_client.provider_spec()["label"]
except Exception:
    _PROVIDER = "LLM"

GEN_STEP = f"Generate plan ({_PROVIDER})"
STEPS = ["Parse request", "Fetch from Jira", "Normalize", "Readiness check",
         GEN_STEP, "Render"]

st.title("Test Plan Agent")
st.caption("Jira ticket in, formal test plan out. Built on the B.L.A.S.T. protocol.")

cfg = config_store.load_config()
missing = config_store.missing_credentials()
if missing:
    st.warning(f"Not configured yet: **{', '.join(missing)}**. "
               "Open the **Settings** page in the sidebar to add them.")

with st.sidebar:
    st.subheader("Connection")
    st.write(f"**Jira:** {cfg['jira_url'] or '_not set_'}")
    _mdl = cfg.get(f"{cfg.get('llm_provider','deepseek')}_model") or "?"
    st.write(f"**LLM:** {_PROVIDER} · `{_mdl}`")
    st.caption("Test both connections on the Settings page.")
    st.divider()
    st.subheader("Options")
    force = st.checkbox("Plan anyway if the ticket is thin", value=False,
                        help="By default the agent refuses tickets that score below "
                             "5/11 on readiness and returns a gap report instead.")

default_prompt = (f"Fetch {cfg['default_jira_key']} and create a test plan"
                  if cfg.get("default_jira_key")
                  else "Fetch SCRUM-42 and create a test plan for it")

prompt = st.text_input("What do you want?", value=default_prompt,
                       placeholder="Fetch PROJ-123 and create a test plan")
go = st.button("Run", type="primary", disabled=bool(missing))

if go:
    slots = {name: st.empty() for name in STEPS}
    for name in STEPS:
        slots[name].markdown(f"◻︎ {name}")

    def progress(step, status, detail=""):
        icon = {"running": "⏳", "done": "✅", "fail": "❌"}.get(status, "◻︎")
        extra = f" — {detail}" if detail else ""
        slots[step].markdown(f"{icon} **{step}**{extra}".replace(" — ", " · "))

    try:
        with st.spinner("Working..."):
            result = navigation.run(prompt, progress=progress, force=force)
        st.session_state["result"] = result
        st.success(f"Test plan written to `{result['path'].name}`")
    except NotPlannableError as e:
        st.error(f"**Refused: {e.message}**\n\n{e.remedy}")
        rd = e.report["readiness"]
        st.subheader("What the ticket is missing")
        for b in rd["blockers"]:
            st.markdown(f"- {b}")
        if rd["gaps"]:
            st.subheader("Gaps found")
            for g in rd["gaps"]:
                st.markdown(f"- {g}")
        st.info("This is correct behavior, not a bug. Tick 'Plan anyway' in the "
                "sidebar to override.")
        st.session_state.pop("result", None)
    except AgentError as e:
        st.error(f"**{e.message}**\n\n{e.remedy}")
        st.session_state.pop("result", None)

result = st.session_state.get("result")
if result:
    tabs = st.tabs(["Test Plan", "Ticket", "Trace", "Raw JSON"])

    with tabs[0]:
        c1, c2 = st.columns([1, 1])
        c1.download_button("Download markdown", result["markdown"],
                           file_name=result["path"].name, mime="text/markdown")
        c2.caption(f"Saved to `out/{result['path'].name}`")
        st.markdown(result["markdown"])

    with tabs[1]:
        t = result["ticket"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Acceptance criteria", len(t["acceptance_criteria"]))
        c2.metric("Gaps", len(t["gaps"]))
        c3.metric("Readiness", f"{result['readiness']['score']}/{result['readiness']['max']}")
        c4.metric("Comments", len(t["comments"]))
        st.subheader("Summary")
        st.write(t["summary"])
        st.subheader("Acceptance criteria")
        if t["acceptance_criteria"]:
            st.table([{"criterion": a["text"][:200], "source": a["origin"]}
                      for a in t["acceptance_criteria"]])
        else:
            st.info("None found on the ticket. Recorded as a gap, not invented.")
        st.subheader("Gaps")
        for g in t["gaps"]:
            st.markdown(f"- {g}")
        st.subheader("Description (flattened from ADF)")
        st.markdown(t["description_md"] or "_empty_")

    with tabs[2]:
        u = result["usage"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Schema valid on attempt", u.get("schema_valid_on_attempt", "?"))
        c2.metric("Input tokens", u.get("input_tokens", 0))
        c3.metric("Output tokens", u.get("output_tokens", 0))
        st.json(result["trace"])

    with tabs[3]:
        st.json(result["plan"])
