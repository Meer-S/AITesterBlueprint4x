"""SOP 01 - key in, raw Jira JSON out. I/O only, no interpretation."""
import json
import re
import time
from pathlib import Path

import requests

from tools.config_store import load_config
from tools.errors import (InvalidKeyError, JiraAuthError, JiraConnectionError, JiraError,
                          JiraNotFoundError, JiraPermissionError, JiraRateLimitError)
from tools.jira_auth import get_auth

KEY_RE = re.compile(r"^[A-Z][A-Z0-9]+-[0-9]+$")
TMP = Path(__file__).resolve().parent.parent / ".tmp"
TIMEOUT = 25

FIELDS = ("summary,description,issuetype,status,priority,labels,components,"
          "fixVersions,versions,parent,subtasks,issuelinks,attachment,assignee,"
          "reporter,creator,duedate,created,updated,environment")


def extract_key(text: str) -> str:
    """Pull an issue key out of a URL or a sentence. Deterministic, no LLM (AI-2)."""
    if not text:
        raise InvalidKeyError("No Jira key given.", "Include a key such as SCRUM-42.")
    text = text.strip()
    m = re.search(r"/browse/([A-Z][A-Z0-9]+-\d+)", text, re.I)
    if m:
        return m.group(1).upper()
    # Tolerate stray whitespace around the hyphen: real users type "VWO- 49"
    # and "VWO 49" as often as "VWO-49".
    m = re.search(r"\b([A-Z][A-Z0-9]{1,9})\s*-\s*(\d+)\b", text.upper())
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m = re.search(r"\b([A-Z][A-Z0-9]{1,9})\s+(\d{1,6})\b", text.upper())
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    raise InvalidKeyError(
        f"No Jira issue key found in: {text[:80]!r}",
        "Include a key like PROJ-123, or paste the browse URL.",
    )


def _request(url, auth, params=None, attempt=1):
    try:
        resp = requests.get(url, auth=auth, params=params,
                            headers={"Accept": "application/json"}, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        raise JiraConnectionError(f"Cannot reach Jira at {url.split('/rest')[0]}.",
                                  "Check the Jira URL in Settings and your network.")
    except requests.exceptions.Timeout:
        raise JiraConnectionError(f"Jira timed out after {TIMEOUT}s.", "Retry.")

    if resp.status_code == 429 and attempt <= 3:
        time.sleep(float(resp.headers.get("Retry-After", 2 ** attempt)))
        return _request(url, auth, params, attempt + 1)
    if resp.status_code >= 500 and attempt <= 3:
        time.sleep(2 ** (attempt - 1))
        return _request(url, auth, params, attempt + 1)
    return resp, attempt - 1


def _raise_for(resp, key):
    if "application/json" not in resp.headers.get("Content-Type", ""):
        raise JiraError("Jira returned HTML instead of JSON.",
                        "The Jira URL points at the web app, not the API.")
    if resp.status_code == 400:
        try:
            msgs = "; ".join(resp.json().get("errorMessages", [])) or resp.text[:200]
        except Exception:
            msgs = resp.text[:200]
        raise JiraError(f"Jira rejected the request (400): {msgs}",
                        "Usually a bad field name in the request.")
    if resp.status_code == 401:
        raise JiraAuthError("Jira authentication failed (401).",
                            "Regenerate the API token and update Settings.")
    if resp.status_code == 403:
        raise JiraPermissionError("Jira refused the request (403).",
                                  "Your account cannot read this project.")
    if resp.status_code == 404:
        # Jira returns 404 (not 401) from the issue endpoint when auth is bad,
        # because it hides issue existence from unauthenticated callers. Left
        # alone, an expired token reports as "ticket not found" and sends the
        # user to debug the key instead of their credentials. So disambiguate
        # by asking /myself, which DOES answer 401 honestly.
        from tools.jira_auth import verify as verify_auth
        try:
            verify_auth()
        except JiraAuthError:
            raise JiraAuthError(
                "Jira authentication failed, so the ticket lookup returned 404.",
                "Your API token is invalid or expired. Regenerate it at "
                "id.atlassian.com -> Security -> API tokens and update Settings. "
                "(Jira answers 404 rather than 401 on the issue endpoint, which is "
                "why this can look like a missing ticket.)")
        except JiraError:
            pass  # auth is fine, or unverifiable. Fall through to the real 404.
        # BR-16: with auth confirmed good, Jira still conflates these two.
        raise JiraNotFoundError(
            f"{key} was not found, OR your account lacks browse permission for it.",
            "Check the key spelling, then check project access. "
            "Jira returns the same 404 for both cases.")
    if resp.status_code == 429:
        raise JiraRateLimitError("Jira rate limit hit (429), retries exhausted.",
                                 "Wait a minute and retry.")
    if not resp.ok:
        raise JiraError(f"Jira error {resp.status_code}: {resp.text[:200]}", "Retry.")


def fetch(key_or_text: str) -> dict:
    key = extract_key(key_or_text)
    if not KEY_RE.match(key):
        raise InvalidKeyError(f"{key!r} is not a valid Jira key.", "Use the form PROJ-123.")

    base, auth = get_auth()
    cfg = load_config()
    ac_field = (cfg.get("field_map_cache") or {}).get("acceptance_criteria")
    fields = FIELDS + (f",{ac_field}" if ac_field else "")

    t0 = time.time()
    resp, retries = _request(f"{base}/rest/api/3/issue/{key}", auth,
                             {"fields": fields, "expand": "renderedFields,names"})
    _raise_for(resp, key)
    issue = resp.json()
    meta = [{"path": f"/rest/api/3/issue/{key}", "status": resp.status_code,
             "ms": int((time.time() - t0) * 1000), "retries": retries}]

    # Best-effort. A failure here degrades the result, it does not fail the run.
    comments, remote_links = [], []
    try:
        r, _ = _request(f"{base}/rest/api/3/issue/{key}/comment", auth,
                        {"maxResults": 50, "orderBy": "-created"})
        if r.ok:
            comments = r.json().get("comments", [])
        meta.append({"path": f"/issue/{key}/comment", "status": r.status_code})
    except JiraError:
        meta.append({"path": f"/issue/{key}/comment", "status": "failed (non-fatal)"})
    try:
        r, _ = _request(f"{base}/rest/api/3/issue/{key}/remotelink", auth)
        if r.ok:
            remote_links = r.json()
        meta.append({"path": f"/issue/{key}/remotelink", "status": r.status_code})
    except JiraError:
        meta.append({"path": f"/issue/{key}/remotelink", "status": "failed (non-fatal)"})

    raw = {"issue": issue, "comments": comments, "remote_links": remote_links,
           "_meta": {"requests": meta, "site": base}}

    TMP.mkdir(exist_ok=True)
    (TMP / f"{key}_raw.json").write_text(json.dumps(raw, indent=2))
    return raw
