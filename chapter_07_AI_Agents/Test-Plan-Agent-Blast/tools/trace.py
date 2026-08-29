"""Audit record for the human reviewer. Secrets never enter it (BR-9)."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def new(ticket_key: str) -> dict:
    return {
        "run_id": str(uuid.uuid4())[:8],
        "ticket_key": ticket_key,
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "steps": [],
    }


def step(tr: dict, name: str, **detail):
    tr["steps"].append({"step": name,
                        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        **detail})
    return tr


def finish(tr: dict, out_dir: Path, **detail) -> Path:
    tr["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tr.update(detail)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{tr['ticket_key']}-trace.json"
    path.write_text(json.dumps(tr, indent=2))
    return path
