"""
finalize_study.py — Finalize a domainRag comparative study.

Orchestrates the end-of-study pipeline in order:

  1. merge_runs.py           consolidate all batch XLSXs → merged_master.xlsx
  2. aigenticHumanReview     export items → review_input.json
  3. dual review gate        hard-stop unless Claude + Codex review are complete
  4. write review sheets     write Claude Review + Codex Review into merged_master.xlsx
  5. analyticsVizs --merged  render cross-condition comparison charts
  6. analyticsVizs --review  render Claude review charts

Usage:
    python analytics/finalize_study.py
    python analytics/finalize_study.py --skip-merge
        Use when merged_master.xlsx is already current and you are re-running
        finalization after completing more review decisions.
        Also suppresses the automatic re-export (export is only skipped when
        merge was skipped AND the export file already exists).
    python analytics/finalize_study.py --force
        Render charts even if review is incomplete.
        For a work-in-progress preview only — do not treat output as final.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "claude_aigenticHumanReview"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from review_paths import decisions_json_path, input_json_path, review_output_root, review_dir
from review_lanes import all_lane_progress, all_lanes_complete

# ---------------------------------------------------------------------------
# Paths — all anchored to this file's directory so cwd is irrelevant
# ---------------------------------------------------------------------------

SCRIPT_DIR     = Path(__file__).resolve().parent
MERGED_XLSX    = SCRIPT_DIR / "merged_master.xlsx"
REVIEW_DIR     = review_dir()
INPUT_JSON     = input_json_path()
DECISIONS_JSON = decisions_json_path()

MERGE_PY  = SCRIPT_DIR / "merge_runs.py"
REVIEW_PY = SCRIPT_DIR / "claude_aigenticHumanReview" / "aigenticHumanReview.py"
CODEX_REVIEW_PY = SCRIPT_DIR / "codex_aigenticHumanReview" / "aigenticHumanReview.py"
VIZ_PY    = SCRIPT_DIR / "analyticsVizs.py"

_W = 56


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hdr(label: str) -> None:
    print(f"\n{'─' * _W}")
    print(f"  {label}")
    print(f"{'─' * _W}")


def _run(cmd: list[str], label: str) -> int:
    _hdr(label)
    result = subprocess.run(cmd, cwd=str(SCRIPT_DIR))
    return result.returncode


def _review_progress() -> dict[str, object]:
    """Import review_workflow at call time so sys.path manipulation is localised."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from review_workflow import review_progress  # noqa: PLC0415
    return review_progress(INPUT_JSON, DECISIONS_JSON)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Finalize a domainRag comparative study — merge, gate, then render final analytics."
    )
    parser.add_argument(
        "--skip-merge",
        action="store_true",
        help=(
            "Skip merge_runs step. Use when merged_master.xlsx is already current. "
            "Also skips re-export if review_input.json already exists."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Render charts even if review is incomplete. "
            "For a progress preview only — output is NOT final."
        ),
    )
    parser.add_argument(
        "--score-opus",
        action="store_true",
        help=(
            "After export, score pending review items with Claude Opus before checking "
            "the completion gate."
        ),
    )
    args = parser.parse_args()

    print("=" * _W)
    print("  domainRag  —  Study Finalization")
    print("=" * _W)

    # ── Step 1: Merge ────────────────────────────────────────────────────────
    if args.skip_merge:
        print("\n[1] Merge: SKIPPED (--skip-merge)")
        if not MERGED_XLSX.exists():
            print(f"  ERROR: {MERGED_XLSX} not found and --skip-merge was set.")
            sys.exit(1)
        print(f"  Using existing: {MERGED_XLSX.name}")
    else:
        rc = _run([sys.executable, str(MERGE_PY)], "Step 1 — merge_runs")
        if rc != 0:
            print(f"\nERROR: merge_runs.py failed (exit {rc}). Resolve merge issues before continuing.")
            sys.exit(rc)
        if not MERGED_XLSX.exists():
            print(f"\nERROR: merge_runs.py exited 0 but {MERGED_XLSX.name} was not produced.")
            sys.exit(1)

    # ── Step 2: Export review input ──────────────────────────────────────────
    # Skip re-export only when merge itself was skipped AND the export already
    # exists.  If merge ran, the merged data may have changed, so always
    # re-export to keep the review input in sync.
    _hdr("Step 2 — export review input")
    skip_export = args.skip_merge and INPUT_JSON.exists()
    if skip_export:
        try:
            with open(INPUT_JSON, encoding="utf-8") as f:
                n = len(json.load(f))
            print(f"  Skipping re-export (--skip-merge): {INPUT_JSON.name} ({n} items already exported).")
        except Exception:
            print(f"  Skipping re-export (--skip-merge): {INPUT_JSON.name} already exists.")
    else:
        REVIEW_DIR.mkdir(parents=True, exist_ok=True)
        rc = _run([sys.executable, str(REVIEW_PY), "--export"], "Step 2 — export review input")
        if rc != 0:
            print(f"\nERROR: review export failed (exit {rc}).")
            sys.exit(rc)

    if args.score_opus:
        rc = _run([sys.executable, str(REVIEW_PY), "--score-opus"], "Step 2b — Claude Opus review scoring")
        if rc != 0:
            print(f"\nERROR: Claude Opus review scoring failed (exit {rc}).")
            sys.exit(rc)

    # ── Step 3: Dual review gate ──────────────────────────────────────────────
    _hdr("Step 3 — dual review gate")
    lane_status = all_lane_progress()
    complete = all_lanes_complete()

    for item in lane_status:
        total = int(item["total"])
        decided = int(item["decided"])
        state = str(item["state"]).upper()
        pct = int(100 * decided / total) if total else 0
        print(f"  {item['label']:6s} : {state:10s} {decided}/{total} ({pct}%)")
        print(f"    Input     : {item['input_json']}")
        print(f"    Decisions : {item['decisions_json']}")

    if not complete:
        print("\n  Required steps before final analytics:")
        print(r"    1. python analytics\human_review_cycle.py --status")
        print(r"    2. Continue both lanes until Claude + Codex are complete")
        print(r"    3. python analytics\human_review_cycle.py --require-complete")
        print(r"    4. python analytics\finalize_study.py --skip-merge")
        if not args.force:
            sys.exit(1)
        print("\n  --force is set. Continuing with incomplete dual review.")
        print("  NOTE: outputs rendered now are NOT final results.")
    else:
        print("  State : COMPLETE — Claude + Codex review complete.")
        print("  Proceeding to final analytics.")

    # ── Step 4: Write review sheets into merged_master.xlsx ───────────────────
    if complete or args.force:
        if DECISIONS_JSON.exists():
            rc = _run([sys.executable, str(REVIEW_PY), "--write"], "Step 4a — write Claude Review sheet")
            if rc != 0:
                print(f"\nWARNING: Claude --write failed (exit {rc}). Claude Review sheet may be stale.")
        else:
            print(f"\n[4a] Write Claude sheet: SKIPPED — {DECISIONS_JSON.name} does not exist.")

        codex_decisions = SCRIPT_DIR / "codex_aigenticHumanReview" / "codex_review_workdir" / "codex_review_decisions.json"
        if codex_decisions.exists():
            rc = _run([sys.executable, str(CODEX_REVIEW_PY), "--write"], "Step 4b — write Codex Review sheet")
            if rc != 0:
                print(f"\nWARNING: Codex --write failed (exit {rc}). Codex Review sheet may be stale.")
        else:
            print(f"\n[4b] Write Codex sheet: SKIPPED — {codex_decisions.name} does not exist.")
    else:
        print(f"\n[4] Write review sheets: SKIPPED — dual review incomplete (use --force for preview).")

    # ── Step 5a: Merged condition comparison charts ───────────────────────────
    rc_merged = _run(
        [sys.executable, str(VIZ_PY), "--merged", str(MERGED_XLSX)],
        "Step 5a — merged condition comparison charts",
    )

    # ── Step 5b: Claude review charts ────────────────────────────────────────
    review_charts_rendered = False
    if DECISIONS_JSON.exists() and (complete or args.force):
        rc_review = _run(
            [sys.executable, str(VIZ_PY), "--claude-review", str(DECISIONS_JSON)],
            "Step 5b — Claude review charts",
        )
        review_charts_rendered = rc_review == 0
    else:
        rc_review = 0
        if not DECISIONS_JSON.exists():
            print(f"\n[5b] Claude review charts: SKIPPED — {DECISIONS_JSON.name} does not exist.")
        else:
            print(f"\n[5b] Claude review charts: SKIPPED — review incomplete (use --force for preview).")

    # ── Summary ───────────────────────────────────────────────────────────────
    merged_out = MERGED_XLSX.parent / "merged"
    review_out = review_output_root()

    print(f"\n{'=' * _W}")
    errors = []
    if rc_merged != 0:
        errors.append(f"merged charts: exit {rc_merged}")
    if rc_review != 0:
        errors.append(f"review charts: exit {rc_review}")

    if errors:
        print(f"  DONE with errors — {', '.join(errors)}")
    elif complete and review_charts_rendered:
        print("  DONE — study finalization complete.")
    elif complete and not review_charts_rendered:
        print("  DONE — merged charts complete. Review charts were not rendered.")
    elif args.force:
        print("  DONE — preview charts rendered (review was incomplete).")
        print("  Re-run without --force once review is complete.")
    else:
        print("  DONE.")

    print(f"  Merged charts : {merged_out}")
    if review_charts_rendered:
        print(f"  Review charts : {review_out}")
    print("=" * _W)


if __name__ == "__main__":
    main()
