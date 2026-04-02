"""
domainRag Run Quality + Cost Dashboard
======================================
Per-batch mode:
    python analyticsVizs.py <runs_dir>
    python analyticsVizs.py           # default: ~/secrets/domainRag/runs

Merged mode:
    python analyticsVizs.py --merged <merged_master.xlsx>

Claude review mode:
    python analyticsVizs.py --claude-review <claude_review_decisions.json>

Codex review mode:
    python analyticsVizs.py --codex-review <codex_review_decisions.json>
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "claude_aigenticHumanReview"))
sys.path.insert(0, str(Path(__file__).parent / "codex_aigenticHumanReview"))


def _load_review_paths(subdir: str, alias: str):
    spec = importlib.util.spec_from_file_location(
        alias, Path(__file__).parent / subdir / "review_paths.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_claude_rp = _load_review_paths("claude_aigenticHumanReview", "claude_review_paths")
_codex_rp = _load_review_paths("codex_aigenticHumanReview", "codex_review_paths")

from viz_render import run_batch_mode, run_claude_review_mode, run_codex_review_mode, run_merged_mode


def main():
    parser = argparse.ArgumentParser(description="domainRag quality dashboard")
    parser.add_argument("runs_dir", nargs="?", default=None, help="Path to runs folder (per-batch mode)")
    parser.add_argument("--merged", metavar="MASTER_XLSX", help="Path to merged_master.xlsx (merged mode)")
    parser.add_argument("--claude-review", metavar="DECISIONS_JSON", help="Path to claude_review_decisions.json (Claude Review mode)")
    parser.add_argument("--codex-review", metavar="DECISIONS_JSON", help="Path to codex_review_decisions.json (Codex Review mode)")
    args = parser.parse_args()

    script_dir = Path(__file__).parent

    if args.codex_review:
        decisions = Path(args.codex_review)
        out_dir = _codex_rp.review_output_root()
        run_codex_review_mode(decisions, out_dir)
    elif args.claude_review:
        decisions = Path(args.claude_review)
        out_dir = _claude_rp.review_output_root()
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
            runs_dir = Path.home() / "secrets" / "domainRag" / "runs"
        runs_dir = runs_dir.resolve()
        out_dir = runs_dir.parent if runs_dir.parent != script_dir else script_dir
        run_batch_mode(runs_dir, out_dir)


if __name__ == "__main__":
    main()
