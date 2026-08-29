"""SOP 05 - ticket.json -> plan.json via Groq. The ONLY probabilistic step (AI-2).

The prompt deliberately does NOT contain the markdown template. The model never
sees the output format, so it cannot drift from it. render.py owns format.
"""
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

from tools import llm_client
from tools.errors import LLMError, SchemaError

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "plan.schema.json"
MAX_ATTEMPTS = 3
CHARS_PER_TOKEN = 4      # rough, and deliberately conservative
SAFETY_MARGIN = 400      # our char/4 estimate runs low on JSON-heavy prompts
MIN_COMPLETION = 1500    # below this a full plan cannot come back
MAX_COMPLETION = 8000


def _est_tokens(*parts) -> int:
    return sum(len(p) for p in parts) // CHARS_PER_TOKEN


def slim(ticket: dict, level: int = 0) -> dict:
    """Progressive slimming, cheapest loss first (SOP 05).

    description_html is dropped at every level: it exists only for the flattener
    loss cross-check in normalize, and the model never needed it.
    """
    t = json.loads(json.dumps(ticket))
    for k in ("description_html", "unknown_adf_nodes", "source", "fetched_at", "url"):
        t.pop(k, None)

    if level >= 1:
        t["attachments"] = [a["filename"] for a in t.get("attachments", [])]
    if level >= 2:
        t["comments"] = [{"author": c["author"], "body_md": c["body_md"][:400]}
                         for c in t.get("comments", [])[:5]]
        t.setdefault("gaps", []).append(
            "Comments were truncated to fit the model token budget.")
    if level >= 3:
        t["comments"] = []
    if level >= 4:
        desc = t.get("description_md", "")
        if len(desc) > 6000:
            t["description_md"] = desc[:6000] + "\n\n[truncated to fit token budget]"
            t.setdefault("gaps", []).append(
                "The description was truncated to fit the model token budget. "
                "Some requirements may not be reflected in this plan.")
    return t

SYSTEM = """You are a senior QA lead writing a formal Test Plan from a Jira ticket.

You return ONE JSON object conforming to the schema below. No markdown, no prose
outside the JSON, no code fences.

STANDING INSTRUCTIONS (violating any of these makes the output unusable):
1. Use ONLY facts present in the supplied ticket object. Do not add knowledge from
   elsewhere about the product, the company, or the technology.
2. Every entry in `scope` MUST have `justified_by` naming the specific ticket fact
   that puts it in scope (quote the acceptance criterion, label, component, or
   description phrase). If you cannot name one, do NOT include the scope entry:
   put it in `dropped_scope` with the reason instead.
3. `scope` is a SUBSET chosen and defended, never a list of every test type. A plan
   listing everything is a failed plan. Typically 4 to 8 entries.
4. Anything you fill without ticket evidence goes in `assumptions[]` with the field
   name, the value you assumed, and why. Environments and schedule rows you invent
   MUST have `assumed: true`.
5. Never invent URLs, dates, version numbers, person names, or tool names. If the
   ticket does not name a test environment URL, use a descriptive placeholder such as
   "QA environment (URL not specified in ticket)" and mark it assumed.
6. Tone: formal QA deliverable. No emoji. No em dashes. Plain professional English.

SCHEMA:
%s
"""


def _validator():
    return Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise LLMError(f"Model did not return JSON. Got: {text[:200]!r}",
                           "Retry. If it persists, the model may not support JSON mode.")
        return json.loads(text[start:end + 1])


def _errors(plan: dict) -> list:
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
            for e in sorted(_validator().iter_errors(plan), key=lambda e: e.path)]


def build(ticket: dict, on_attempt=None) -> tuple[dict, dict]:
    """Returns (plan, meta). Retries on schema violation, max 2 (BR-18)."""
    # Minified, not pretty-printed: same information, far fewer tokens.
    schema_text = json.dumps(json.loads(SCHEMA_PATH.read_text()), separators=(",", ":"))
    system = SYSTEM % schema_text

    # Groq counts max_tokens (the RESERVATION, not the actual completion) against the
    # TPM limit, so prompt + reservation must fit the tier. Budget both together.
    tpm = llm_client.tpm_budget()
    prompt_budget = tpm - MIN_COMPLETION - SAFETY_MARGIN

    level = 0
    while level < 5:
        slimmed = slim(ticket, level)
        user = ("Build the Test Plan JSON for this ticket.\n\n"
                + json.dumps(slimmed, separators=(",", ":")))
        if _est_tokens(system, user) <= prompt_budget:
            break
        level += 1
    est = _est_tokens(system, user)
    max_completion = max(MIN_COMPLETION,
                         min(MAX_COMPLETION, tpm - est - SAFETY_MARGIN))

    last_errors = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        if on_attempt:
            on_attempt(attempt, last_errors)
        prompt = user
        if last_errors:
            prompt = (f"{user}\n\nYour previous response failed schema validation with "
                      f"these errors. Fix them and return the corrected full JSON:\n"
                      + "\n".join(f"- {e}" for e in last_errors[:12]))

        try:
            content, usage = llm_client.chat_json(system, prompt,
                                                  max_tokens=max_completion)
        except LLMError as e:
            # A real 413 means the estimate was optimistic. Slim one level and retry once.
            if "413" in e.message and level < 4:
                level += 1
                user = ("Build the Test Plan JSON for this ticket.\n\n"
                        + json.dumps(slim(ticket, level), separators=(",", ":")))
                est = _est_tokens(system, user)
                max_completion = max(MIN_COMPLETION,
                                     min(MAX_COMPLETION, tpm - est - SAFETY_MARGIN))
                content, usage = llm_client.chat_json(system, user,
                                                      max_tokens=max_completion)
            else:
                raise
        try:
            plan = _extract_json(content)
        except (LLMError, json.JSONDecodeError) as e:
            last_errors = [f"response was not parseable JSON: {e}"]
            continue

        errs = _errors(plan)
        if not errs:
            usage["schema_valid_on_attempt"] = attempt
            usage["temperature"] = 0.2
            usage["slim_level"] = level
            usage["estimated_prompt_tokens"] = est
            usage["max_tokens_reserved"] = max_completion
            usage["tpm_limit"] = tpm
            return plan, usage
        last_errors = errs

    # BR-18: never hand-patch the model's output.
    raise SchemaError(
        "The model could not produce a plan matching the schema after "
        f"{MAX_ATTEMPTS} attempts.",
        "Last errors: " + "; ".join(last_errors[:5]),
    )
