"""
domainRag Run Quality + Cost Dashboard
======================================
Per-batch mode:
    python analyticsVizs.py <runs_dir>
    python analyticsVizs.py           # default: analytics/runs

Merged mode:
    python analyticsVizs.py --merged <merged_master.xlsx>

Claude review mode:
    python analyticsVizs.py --claude-review <claude_review_decisions.json>

Codex review mode:
    python analyticsVizs.py --codex-review <codex_review_decisions.json>
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_MPLCONFIGDIR = Path(__file__).parent / ".mplconfig"
_MPLCONFIGDIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPLCONFIGDIR))

from viz_render import run_batch_mode, run_claude_review_mode, run_codex_review_mode, run_merged_mode, run_review_analysis_mode


def main():
    parser = argparse.ArgumentParser(description="domainRag quality dashboard")
    parser.add_argument("runs_dir", nargs="?", default=None, help="Path to runs folder (per-batch mode)")
    parser.add_argument("--merged", metavar="MASTER_XLSX", help="Path to merged_master.xlsx (merged mode)")
    parser.add_argument("--claude-review", metavar="DECISIONS_JSON", help="Path to claude_review_decisions.json (Claude Review mode)")
    parser.add_argument("--codex-review", metavar="DECISIONS_JSON", help="Path to codex_review_decisions.json (Codex Review mode)")
    parser.add_argument("--review-analysis", metavar="ANALYSIS_DIR", help="Path to merged review_analysis export directory")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    review_chart_dir = script_dir / "merged" / "review_analysis" / "charts"

    if args.review_analysis:
        analysis_dir = Path(args.review_analysis)
        run_review_analysis_mode(analysis_dir, analysis_dir / "charts")
    elif args.codex_review:
        decisions = Path(args.codex_review)
        override = (os.environ.get("DOMAINRAG_REVIEW_DIR") or "").strip()
        out_dir = Path(override).expanduser().resolve() if override else review_chart_dir
        run_codex_review_mode(decisions, out_dir)
    elif args.claude_review:
        decisions = Path(args.claude_review)
        override = (os.environ.get("DOMAINRAG_REVIEW_DIR") or "").strip()
        out_dir = Path(override).expanduser().resolve() if override else review_chart_dir
        run_claude_review_mode(decisions, out_dir)
    elif args.merged:
        master = Path(args.merged)
        out_dir = master.resolve().parent / "merged"
        out_dir.mkdir(exist_ok=True)
        run_merged_mode(master, out_dir)
    else:
        if args.runs_dir:
            runs_dir = Path(args.runs_dir)
        else:
            runs_dir = script_dir / "runs"
        runs_dir = runs_dir.resolve()
        out_dir = runs_dir
        run_batch_mode(runs_dir, out_dir)


if __name__ == "__main__":
    main()
