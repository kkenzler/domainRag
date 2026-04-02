from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from review_lanes import REVIEW_LANES, all_lane_progress, all_lanes_complete, shared_input_json


SCRIPT_DIR = Path(__file__).resolve().parent
CLAUDE_REVIEW_PY = SCRIPT_DIR / "claude_aigenticHumanReview" / "aigenticHumanReview.py"
CODEX_REVIEW_PY = SCRIPT_DIR / "codex_aigenticHumanReview" / "aigenticHumanReview.py"
QUEUE_CLAUDE = SCRIPT_DIR / "claude_aigenticHumanReview" / "queue_claude_review_resume.ps1"
QUEUE_CODEX = SCRIPT_DIR / "codex_aigenticHumanReview" / "queue_codex_review_resume.ps1"


def _run(cmd: list[str]) -> int:
    return subprocess.run(cmd, cwd=str(SCRIPT_DIR)).returncode


def bootstrap(refresh_input: bool, reset_codex_decisions: bool) -> int:
    rc = _run([sys.executable, str(CLAUDE_REVIEW_PY), "--export"])
    if rc != 0:
        return rc
    cmd = [sys.executable, str(CODEX_REVIEW_PY), "--bootstrap"]
    if refresh_input:
        cmd.append("--refresh-input")
    if reset_codex_decisions:
        cmd.append("--reset-decisions")
    return _run(cmd)


def queue_both() -> int:
    rc1 = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(QUEUE_CLAUDE)],
        cwd=str(SCRIPT_DIR),
    ).returncode
    rc2 = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(QUEUE_CODEX)],
        cwd=str(SCRIPT_DIR),
    ).returncode
    return 0 if rc1 == 0 and rc2 == 0 else 1


def show_status() -> int:
    print(f"Shared input: {shared_input_json()}")
    for item in all_lane_progress():
        total = int(item["total"])
        decided = int(item["decided"])
        pct = int(100 * decided / total) if total else 0
        print(f"{item['label']}: {decided}/{total} ({pct}%)  decisions={item['decisions_json']}")
    return 0


def require_complete_status() -> int:
    if all_lanes_complete():
        print("Dual human review complete: Claude + Codex")
        return 0
    print("Dual human review incomplete.")
    for item in all_lane_progress():
        if not item["complete"]:
            total = int(item["total"])
            decided = int(item["decided"])
            pct = int(100 * decided / total) if total else 0
            print(f"- {item['label']}: {decided}/{total} ({pct}%)")
            print(f"  {item['status_command']}")
    return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="domainRag dual human-review cycle")
    parser.add_argument("--bootstrap", action="store_true", help="Export shared review input and bootstrap the Codex local lane")
    parser.add_argument("--queue-both", action="store_true", help="Queue one resume prompt to both Claude and Codex listeners")
    parser.add_argument("--status", action="store_true", help="Show Claude + Codex review progress")
    parser.add_argument("--require-complete", action="store_true", help="Exit non-zero unless both human-review lanes are complete")
    parser.add_argument("--refresh-input", action="store_true", help="Force refresh of shared review_input.json during bootstrap")
    parser.add_argument("--reset-codex-decisions", action="store_true", help="Reset the local Codex decisions file during bootstrap")
    args = parser.parse_args()

    rc = 0
    if args.bootstrap:
        rc = bootstrap(refresh_input=args.refresh_input, reset_codex_decisions=args.reset_codex_decisions)
        if rc != 0:
            raise SystemExit(rc)
    if args.queue_both:
        rc = queue_both()
        if rc != 0:
            raise SystemExit(rc)
    if args.status:
        rc = show_status()
    if args.require_complete:
        rc = require_complete_status()
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
