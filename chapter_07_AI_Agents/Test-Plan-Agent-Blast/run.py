#!/usr/bin/env python3
"""CLI entry point. `python run.py SCRUM-42` or `python run.py --health`."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import navigation
from tools.errors import (AgentError, InvalidKeyError, JiraAuthError, JiraNotFoundError,
                          JiraRateLimitError, LLMError, NotPlannableError, SchemaError)

EXIT = {InvalidKeyError: 2, JiraAuthError: 3, JiraNotFoundError: 4,
        JiraRateLimitError: 5, SchemaError: 6, LLMError: 7}


def main():
    ap = argparse.ArgumentParser(description="Jira ticket -> formal test plan")
    ap.add_argument("prompt", nargs="*", help='e.g. SCRUM-42, or "make a plan for SCRUM-42"')
    ap.add_argument("--health", action="store_true", help="test both connections and exit")
    ap.add_argument("--dry-run", action="store_true",
                    help="fetch and normalize, but never call the LLM")
    ap.add_argument("--force", action="store_true", help="plan even if the ticket is thin")
    args = ap.parse_args()

    if args.health:
        h = navigation.health()
        for name, r in h.items():
            if r["ok"]:
                d = r["detail"]
                print(f"  {name:6} OK   {d.get('displayName') or d.get('model')}")
            else:
                print(f"  {name:6} FAIL {r['error']}\n         -> {r['remedy']}")
        return 0 if all(r["ok"] for r in h.values()) else 3

    if not args.prompt:
        ap.error("give a Jira key or a prompt")
    prompt = " ".join(args.prompt)

    def progress(step, status, detail=""):
        if status == "done":
            print(f"  [ok] {step}" + (f": {detail}" if detail else ""))

    try:
        if args.dry_run:
            from tools import jira_fetch, normalize, readiness
            key = navigation.parse_intent(prompt)["key"]
            raw = jira_fetch.fetch(key)
            ticket = normalize.normalize(raw, raw["_meta"]["site"])
            rd = readiness.check(ticket)
            print(f"  {key}: {ticket['summary']}")
            print(f"  acceptance criteria: {len(ticket['acceptance_criteria'])}")
            print(f"  gaps: {len(ticket['gaps'])}")
            print(f"  readiness: {rd['score']}/{rd['max']} "
                  f"({'plannable' if rd['plannable'] else 'NOT plannable'})")
            print("  (dry run: no LLM call made)")
            return 0

        result = navigation.run(prompt, progress=progress, force=args.force)
        print(f"\nWritten: {result['path']}")
        print(f"Trace:   {result['trace_path']}")
        return 0

    except NotPlannableError as e:
        print(f"\nREFUSED: {e.message}\n-> {e.remedy}\n")
        print("What the ticket is missing:")
        for b in e.report["readiness"]["blockers"]:
            print(f"  - {b}")
        return 0  # refusing is correct behavior, not a failure (BR-4)
    except AgentError as e:
        print(f"\nERROR: {e.message}\n-> {e.remedy}", file=sys.stderr)
        return EXIT.get(type(e), 1)


if __name__ == "__main__":
    sys.exit(main())
