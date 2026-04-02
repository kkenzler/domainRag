from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from review_lanes import all_lane_progress, all_lanes_complete


SCRIPT_DIR = Path(__file__).resolve().parent
RUN_BATCHES_PY = SCRIPT_DIR / "run_batches.py"
HUMAN_REVIEW_PY = SCRIPT_DIR / "human_review_cycle.py"
FINALIZE_PY = SCRIPT_DIR / "finalize_study.py"
CLAUDE_SUPERVISOR = SCRIPT_DIR / "claude_aigenticHumanReview" / "supervise_claude_review_queue.ps1"
CODEX_SUPERVISOR = SCRIPT_DIR / "codex_aigenticHumanReview" / "supervise_codex_review_queue.ps1"


def _run(cmd: list[str]) -> int:
    return subprocess.run(cmd, cwd=str(SCRIPT_DIR.parent)).returncode


def _start_supervisor(script_path: Path) -> subprocess.Popen:
    return subprocess.Popen(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
        cwd=str(SCRIPT_DIR.parent),
    )


def _print_lane_status() -> None:
    for item in all_lane_progress():
        total = int(item["total"])
        decided = int(item["decided"])
        pct = int(100 * decided / total) if total else 0
        print(f"  {item['label']}: {decided}/{total} ({pct}%)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full domainRag study end-to-end, including both human-review lanes.")
    parser.add_argument("--skip-batches", action="store_true", help="Skip the batched generation phase and start from shared human review.")
    parser.add_argument("--skip-finalize", action="store_true", help="Skip the finalization phase after human review completes.")
    parser.add_argument("--review-poll-seconds", type=int, default=15, help="Polling interval while waiting for Claude + Codex review completion.")
    args = parser.parse_args()

    if not args.skip_batches:
        rc = _run([sys.executable, str(RUN_BATCHES_PY)])
        if rc != 0:
            raise SystemExit(rc)

    rc = _run([sys.executable, str(HUMAN_REVIEW_PY), "--bootstrap", "--refresh-input"])
    if rc != 0:
        raise SystemExit(rc)

    rc = _run([sys.executable, str(HUMAN_REVIEW_PY), "--queue-both"])
    if rc != 0:
        raise SystemExit(rc)

    claude_proc = _start_supervisor(CLAUDE_SUPERVISOR)
    codex_proc = _start_supervisor(CODEX_SUPERVISOR)

    try:
        print("\nWaiting for dual human review to complete...")
        _print_lane_status()
        while not all_lanes_complete():
            time.sleep(max(1, int(args.review_poll_seconds)))
            _print_lane_status()
        print("\nDual human review complete.")
    finally:
        for proc in (claude_proc, codex_proc):
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()

    if not args.skip_finalize:
        rc = _run([sys.executable, str(FINALIZE_PY), "--skip-merge"])
        if rc != 0:
            raise SystemExit(rc)


if __name__ == "__main__":
    main()
