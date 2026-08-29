"""Groq client. OpenAI-compatible REST, called with `requests` - no extra SDK.

AI-2: this is the ONLY module in the project permitted to call a model.
"""
import json

import requests

from tools.config_store import load_config
from tools.errors import ConfigError, LLMError

TIMEOUT = 120

PROVIDERS = {
    "deepseek": {
        "label": "DeepSeek",
        "base": "https://api.deepseek.com/v1",
        "key_setting": "deepseek_api_key",
        "model_setting": "deepseek_model",
        "default_model": "deepseek-chat",
        "tpm": 60000,
        "console": "platform.deepseek.com/api_keys",
    },
    "groq": {
        "label": "Groq",
        "base": "https://api.groq.com/openai/v1",
        "key_setting": "groq_api_key",
        "model_setting": "groq_model",
        "default_model": "openai/gpt-oss-120b",
        "tpm": 8000,
        "console": "console.groq.com/keys",
    },
}


def provider_spec(name: str = None) -> dict:
    cfg = load_config()
    name = (name or cfg.get("llm_provider") or "deepseek").lower()
    if name not in PROVIDERS:
        raise ConfigError(f"Unknown LLM provider {name!r}.",
                          f"Pick one of: {', '.join(PROVIDERS)}")
    return {"name": name, **PROVIDERS[name]}


def tpm_budget() -> int:
    cfg = load_config()
    spec = provider_spec()
    override = cfg.get(f"{spec['name']}_tpm_limit") or cfg.get("groq_tpm_limit")
    return int(override) if override and spec["name"] == "groq" else int(
        cfg.get(f"{spec['name']}_tpm_limit") or spec["tpm"])


def _key_and_model():
    cfg = load_config()
    spec = provider_spec()
    key = cfg.get(spec["key_setting"])
    if not key:
        raise ConfigError(
            f"{spec['label']} API key is not configured.",
            f"Open the Settings page and paste your key from {spec['console']}",
        )
    return key, cfg.get(spec["model_setting"]) or spec["default_model"], spec


def verify() -> dict:
    """Phase 2 LINK handshake: prove the provider answers and the model exists."""
    key, model, spec = _key_and_model()
    try:
        resp = requests.get(f"{spec['base']}/models",
                            headers={"Authorization": f"Bearer {key}"}, timeout=30)
    except requests.exceptions.RequestException as e:
        raise LLMError(f"Cannot reach {spec['label']}: {e}",
                       "Check your network connection.")

    if resp.status_code == 401:
        raise LLMError(f"{spec['label']} rejected the API key (401).",
                       f"Generate a new key at {spec['console']} and update Settings.")
    if not resp.ok:
        raise LLMError(f"{spec['label']} error {resp.status_code}: {resp.text[:200]}",
                       "Check Settings.")

    ids = [m["id"] for m in resp.json().get("data", [])]
    return {
        "ok": True,
        "provider": spec["label"],
        "model": model,
        "model_available": model in ids,
        "models_visible": len(ids),
        "sample": sorted(ids)[:8],
    }


def chat_json(system: str, user: str, temperature: float = 0.2,
              max_tokens: int = 8000) -> tuple[str, dict]:
    """One JSON-mode completion. Returns (content, usage_meta)."""
    key, model, spec = _key_and_model()
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    try:
        resp = requests.post(f"{spec['base']}/chat/completions",
                             headers={"Authorization": f"Bearer {key}",
                                      "Content-Type": "application/json"},
                             json=payload, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        raise LLMError(f"{spec['label']} timed out after {TIMEOUT}s.",
                       "Retry, or pick a smaller model in Settings.")
    except requests.exceptions.RequestException as e:
        raise LLMError(f"Cannot reach {spec['label']}: {e}",
                       "Check your network connection.")

    if resp.status_code == 401:
        raise LLMError(f"{spec['label']} rejected the API key (401).",
                       "Update the key in Settings.")
    if resp.status_code == 413:
        raise LLMError(
            f"{spec['label']} error 413: {resp.text[:300]}",
            f"The request exceeds your {spec['label']} tokens-per-minute limit. The agent "
            "slims the payload automatically; if this persists, use a smaller ticket "
            "or upgrade the Groq tier.")
    if resp.status_code == 429:
        raise LLMError(f"{spec['label']} rate limit hit (429).",
                       f"Wait {resp.headers.get('Retry-After', '60')}s and retry.")
    if not resp.ok:
        raise LLMError(f"{spec['label']} error {resp.status_code}: {resp.text[:300]}",
                       "Check the model name in Settings.")

    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise LLMError(f"Unexpected {spec['label']} response shape: {json.dumps(data)[:300]}",
                       "Retry. If it persists, the model may not support JSON mode.")

    usage = data.get("usage", {})
    return content, {
        "model": data.get("model", model),
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
    }
