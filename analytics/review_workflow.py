from __future__ import annotations

import json
from pathlib import Path


def review_progress(input_json: Path, decisions_json: Path) -> dict[str, object]:
    """Return review progress as a dict.

    Keys:
      total    — number of items in the export (0 if not exported or empty)
      decided  — number of decisions made so far
      complete — True only when total > 0 and decided >= total
      state    — one of:
                   "not_exported"  input_json does not exist or could not be read
                   "incomplete"    export exists but decided < total
                   "complete"      decided >= total > 0
    """
    total = 0
    decided = 0
    export_exists = input_json.exists()

    if export_exists:
        try:
            with open(input_json, "r", encoding="utf-8") as f:
                total = len(json.load(f))
        except Exception:
            total = 0

    if decisions_json.exists():
        try:
            with open(decisions_json, "r", encoding="utf-8") as f:
                decided = len(json.load(f))
        except Exception:
            decided = 0

    if not export_exists or total == 0:
        state = "not_exported"
    elif decided >= total:
        state = "complete"
    else:
        state = "incomplete"

    return {
        "total": total,
        "decided": decided,
        "complete": state == "complete",
        "state": state,
    }


def require_complete(input_json: Path, decisions_json: Path) -> dict[str, object]:
    progress = review_progress(input_json, decisions_json)
    state = progress["state"]
    if state == "not_exported":
        raise SystemExit(
            "Claude human review has not been exported yet.\n"
            "Run: python aigenticHumanReview.py --export"
        )
    if state == "incomplete":
        total = progress["total"]
        decided = progress["decided"]
        pct = int(100 * decided / total)
        raise SystemExit(
            f"Claude human review incomplete: {decided}/{total} decisions present ({pct}%).\n"
            "Run: python aigenticHumanReview.py --status  for details."
        )
    return progress
