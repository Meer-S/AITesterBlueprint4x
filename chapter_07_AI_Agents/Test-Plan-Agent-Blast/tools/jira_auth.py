"""Phase 2 LINK handshake: prove the Jira connection before anything else runs."""
import requests
from requests.auth import HTTPBasicAuth

from tools.config_store import load_config
from tools.errors import ConfigError, JiraAuthError, JiraConnectionError, JiraError

TIMEOUT = 20


def get_auth():
    cfg = load_config()
    for key, label in (("jira_url", "Jira URL"), ("jira_email", "Jira email"),
                       ("jira_api_token", "Jira API token")):
        if not cfg.get(key):
            raise ConfigError(
                f"{label} is not configured.",
                "Open the Settings page and fill in the Jira section.",
            )
    return cfg["jira_url"], HTTPBasicAuth(cfg["jira_email"], cfg["jira_api_token"])


def verify() -> dict:
    """GET /rest/api/3/myself. Returns the account, or raises a typed error."""
    base, auth = get_auth()
    url = f"{base}/rest/api/3/myself"
    try:
        resp = requests.get(url, auth=auth, headers={"Accept": "application/json"},
                            timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        raise JiraConnectionError(
            f"Cannot reach Jira at {base}.",
            "Check the Jira URL in Settings. It must be the bare site URL, "
            "for example https://your-site.atlassian.net",
        )
    except requests.exceptions.Timeout:
        raise JiraConnectionError(f"Jira timed out after {TIMEOUT}s.", "Check your network.")

    ctype = resp.headers.get("Content-Type", "")
    if "application/json" not in ctype:
        raise JiraError(
            "Jira returned HTML instead of JSON.",
            "The Jira URL points at the web app, not the API. Use the bare site URL.",
        )
    if resp.status_code == 401:
        raise JiraAuthError(
            "Jira authentication failed (401).",
            "Regenerate the API token at id.atlassian.com and re-enter it in Settings. "
            "The email must match the account that owns the token.",
        )
    if resp.status_code == 403:
        raise JiraAuthError("Jira refused the request (403).",
                            "The account is authenticated but lacks access.")
    if not resp.ok:
        raise JiraError(f"Jira error {resp.status_code}: {resp.text[:200]}",
                        "Check the Jira URL and credentials in Settings.")

    data = resp.json()
    return {
        "accountId": data.get("accountId", ""),
        "displayName": data.get("displayName", "Connected"),
        "emailAddress": data.get("emailAddress", ""),
        "site": base,
    }
