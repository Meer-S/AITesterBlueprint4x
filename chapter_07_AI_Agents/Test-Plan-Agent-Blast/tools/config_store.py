"""Config and credential loading.

Invariant AI-10: secrets come from .env or config.json only. Never a literal,
never a default, never committed. Both files are gitignored.
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"
ENV_PATH = BASE_DIR / ".env"

DEFAULTS = {
    "jira_url": "",
    "jira_email": "",
    "jira_api_token": "",
    "llm_provider": "deepseek",
    "groq_api_key": "",
    "groq_model": "openai/gpt-oss-120b",
    "groq_tpm_limit": 8000,
    "deepseek_api_key": "",
    "deepseek_model": "deepseek-chat",
    "deepseek_tpm_limit": 60000,
    "include_comments": True,
    "default_jira_key": "",
    "field_map_cache": {},
}

ENV_MAP = {
    "jira_url": "JIRA_URL",
    "jira_email": "JIRA_EMAIL",
    "jira_api_token": "JIRA_API_TOKEN",
    "groq_api_key": "GROQ_API_KEY",
    "groq_model": "GROQ_MODEL",
    "deepseek_api_key": "DEEPSEEK_API_KEY",
    "deepseek_model": "DEEPSEEK_MODEL",
    "llm_provider": "LLM_PROVIDER",
    "default_jira_key": "DEFAULT_JIRA_KEY",
}


def load_config() -> dict:
    """config.json wins, .env seeds anything missing."""
    load_dotenv(ENV_PATH)

    config = {}
    if CONFIG_PATH.exists():
        try:
            config = json.loads(CONFIG_PATH.read_text())
        except json.JSONDecodeError:
            config = {}

    merged = dict(DEFAULTS)
    merged.update({k: v for k, v in config.items() if v not in ("", None)})

    for key, env_var in ENV_MAP.items():
        if not merged.get(key):
            merged[key] = os.getenv(env_var, DEFAULTS[key])

    merged["jira_url"] = str(merged.get("jira_url", "")).rstrip("/")
    return merged


def save_config(updates: dict) -> None:
    existing = {}
    if CONFIG_PATH.exists():
        try:
            existing = json.loads(CONFIG_PATH.read_text())
        except json.JSONDecodeError:
            pass
    existing.update(updates)
    CONFIG_PATH.write_text(json.dumps(existing, indent=2))


def get_setting(key: str):
    return load_config().get(key, DEFAULTS.get(key))


def set_setting(key: str, value) -> None:
    save_config({key: value})


def redact(value: str) -> str:
    """BR-9: secrets never reach a log, trace or output file."""
    if not value:
        return "<not set>"
    return f"<set, {len(value)} chars, ...{value[-4:]}>"


def value_sources() -> dict:
    """Where each setting actually came from.

    config.json wins over .env. That is right for a UI-driven app, but a stale
    config.json silently shadowing a freshly edited .env is a confusing failure
    (it cost a debugging cycle during the build). The Settings page renders this.
    """
    load_dotenv(ENV_PATH)
    stored = {}
    if CONFIG_PATH.exists():
        try:
            stored = json.loads(CONFIG_PATH.read_text())
        except json.JSONDecodeError:
            pass
    out = {}
    for key, env_var in ENV_MAP.items():
        in_cfg = bool(stored.get(key))
        env_val = os.getenv(env_var, "")
        if in_cfg:
            shadowed = bool(env_val) and str(stored.get(key)) != env_val
            out[key] = "config.json (shadowing a DIFFERENT value in .env)" if shadowed \
                else "config.json"
        elif env_val:
            out[key] = ".env"
        else:
            out[key] = "<not set>"
    return out


def reload_from_env() -> list:
    """Overwrite config.json from .env. Returns the keys that changed."""
    load_dotenv(ENV_PATH, override=True)
    changed = []
    updates = {}
    current = load_config()
    for key, env_var in ENV_MAP.items():
        env_val = os.getenv(env_var, "")
        if env_val and str(current.get(key, "")) != env_val:
            updates[key] = env_val
            changed.append(key)
    if updates:
        save_config(updates)
    return changed


def missing_credentials() -> list:
    cfg = load_config()
    missing = []
    for key in ("jira_url", "jira_email", "jira_api_token"):
        if not cfg.get(key):
            missing.append(key)
    provider = (cfg.get("llm_provider") or "deepseek").lower()
    key_name = f"{provider}_api_key"
    if not cfg.get(key_name):
        missing.append(key_name)
    return missing
