"""Settings - credentials and connection tests for Jira and Groq."""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import config_store, jira_auth, llm_client
from tools.errors import AgentError

st.set_page_config(page_title="Settings - Test Plan Agent", page_icon="⚙️", layout="centered")
st.title("Settings")
st.caption("Credentials are saved to `config.json`, which is gitignored. "
           "They are never written to a log, a trace, or the generated plan.")

cfg = config_store.load_config()

st.subheader("Jira")
jira_url = st.text_input("Jira URL", value=cfg["jira_url"],
                         placeholder="https://your-site.atlassian.net",
                         help="The bare site URL. Not the /browse/ or /jira/ path.")
jira_email = st.text_input("Jira email", value=cfg["jira_email"],
                           placeholder="you@example.com",
                           help="Must be the account that owns the API token.")
jira_token = st.text_input("Jira API token", value=cfg["jira_api_token"], type="password",
                           help="id.atlassian.com -> Security -> Create and manage API tokens")
default_key = st.text_input("Default Jira key (optional)", value=cfg["default_jira_key"],
                            placeholder="SCRUM-42",
                            help="Pre-fills the prompt box on the main page.")

st.subheader("LLM provider")
providers = list(llm_client.PROVIDERS)
current = (cfg.get("llm_provider") or "deepseek").lower()
provider = st.selectbox(
    "Provider", providers, index=providers.index(current) if current in providers else 0,
    format_func=lambda p: llm_client.PROVIDERS[p]["label"],
    help="Both are OpenAI-compatible. DeepSeek has far more token headroom; "
         "Groq's free tier caps at 8000 tokens per minute, which makes the agent "
         "slim rich tickets before sending them.")

spec = llm_client.PROVIDERS[provider]
st.caption(f"Endpoint: `{spec['base']}` · default TPM budget {spec['tpm']:,}")

llm_key = st.text_input(f"{spec['label']} API key", value=cfg.get(spec["key_setting"], ""),
                        type="password", help=spec["console"])
llm_model = st.text_input(f"{spec['label']} model",
                          value=cfg.get(spec["model_setting"]) or spec["default_model"],
                          help=f"Default: {spec['default_model']}")

st.subheader("Behavior")
include_comments = st.checkbox(
    "Treat ticket comments as a source of acceptance criteria",
    value=cfg.get("include_comments", True),
    help="Teams often bury the real acceptance criteria in a comment. Including "
         "them catches that, but also drags in off-topic discussion. "
         "Comment-sourced criteria are tagged with origin 'comment' either way.")

if st.button("Save settings", type="primary"):
    config_store.save_config({
        "jira_url": jira_url.rstrip("/"),
        "jira_email": jira_email,
        "jira_api_token": jira_token,
        "llm_provider": provider,
        spec["key_setting"]: llm_key,
        spec["model_setting"]: llm_model,
        "default_jira_key": default_key.upper(),
        "include_comments": include_comments,
    })
    st.success("Saved to config.json")
    st.rerun()

st.divider()
st.subheader("Where these values come from")
sources = config_store.value_sources()
shadowed = [k for k, v in sources.items() if "shadowing" in v]
if shadowed:
    st.warning(
        f"**{', '.join(shadowed)}** in `config.json` differ from what is in `.env`. "
        "config.json wins, so edits to .env are being ignored for those keys. "
        "Press **Reload from .env** if you just edited that file.")
st.table([{"setting": k, "source": v} for k, v in sources.items()])
if st.button("Reload from .env"):
    changed = config_store.reload_from_env()
    if changed:
        st.success("Reloaded from .env: " + ", ".join(changed))
    else:
        st.info("config.json already matches .env. Nothing changed.")
    st.rerun()

st.divider()
st.subheader("Test connections")
st.caption("BLAST Phase 2 (Link): prove both connections before running the pipeline.")

c1, c2 = st.columns(2)

with c1:
    if st.button("Test Jira connection"):
        try:
            info = jira_auth.verify()
            st.success(f"Connected as **{info['displayName']}**")
            st.caption(f"{info['emailAddress']} · {info['site']}")
        except AgentError as e:
            st.error(e.message)
            st.info(e.remedy)

with c2:
    if st.button(f"Test {spec['label']} connection"):
        try:
            info = llm_client.verify()
            if info["model_available"]:
                st.success(f"Connected. Model **{info['model']}** is available.")
            else:
                st.warning(f"Connected, but **{info['model']}** was not in the "
                           f"{info['models_visible']} models this key can see.")
                st.caption("Available includes: " + ", ".join(info["sample"]))
        except AgentError as e:
            st.error(e.message)
            st.info(e.remedy)

st.divider()
with st.expander("Current configuration (secrets redacted)"):
    cfg = config_store.load_config()
    st.json({
        "jira_url": cfg["jira_url"] or "<not set>",
        "jira_email": cfg["jira_email"] or "<not set>",
        "jira_api_token": config_store.redact(cfg["jira_api_token"]),
        "llm_provider": cfg.get("llm_provider"),
        "llm_api_key": config_store.redact(cfg.get(spec["key_setting"], "")),
        "llm_model": cfg.get(spec["model_setting"]),
        "default_jira_key": cfg["default_jira_key"] or "<not set>",
        "include_comments": cfg["include_comments"],
        "acceptance_criteria_field_cached":
            (cfg.get("field_map_cache") or {}).get("acceptance_criteria") or "<not resolved yet>",
    })
