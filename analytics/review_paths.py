"""analytics/review_paths.py -- single path authority for both review lanes (claude, codex).

WHY THIS EXISTS
    G010/D011 (2026-08-06): domainRag had zero hardcoded absolute paths, but three
    near-duplicate copies of this exact logic existed -- this file (formerly a thin proxy that
    always forwarded to Claude's copy), `claude_aigenticHumanReview/review_paths.py`, and
    `codex_aigenticHumanReview/review_paths.py`. The operator ruled that the triplication itself
    is the drift risk this goal exists to prevent, even with nothing hardcoded today. Consolidated
    to one real module; the two per-lane files are now thin compatibility shims so every existing
    caller's import and call signature keeps working unchanged.

LANES
    "claude" and "codex" have genuinely different behavior, not just different folder names --
    preserved exactly as each lane had it before this consolidation (verified byte-for-byte
    against the original three files before replacing them):
      - claude: `review_output_root()` is a fixed reporting location
        (analytics/merged/review_analysis/charts), and every function is env-overridable
        (DOMAINRAG_REVIEW_DIR / DOMAINRAG_REVIEW_INPUT_JSON / DOMAINRAG_REVIEW_DECISIONS_JSON --
        unprefixed by lane, matching the original claude-only override names exactly, so no
        existing environment/CI config that sets these breaks).
      - codex: `review_output_root()` is relative (`review_dir().parent`), and codex's copy had
        NO env-override support before this consolidation. Added analogous lane-scoped overrides
        (DOMAINRAG_CODEX_REVIEW_DIR / DOMAINRAG_CODEX_REVIEW_INPUT_JSON /
        DOMAINRAG_CODEX_REVIEW_DECISIONS_JSON) as a natural byproduct of sharing one
        implementation -- CODEX_REVIEW_WORKFLOW.md already (incorrectly) documented this lane as
        override-capable, so this closes a real doc-accuracy gap rather than opening a new one.
        With no override set, behavior is byte-identical to the pre-consolidation code.

    The module-level functions below (no `lane` argument, defaulting to "claude") preserve this
    file's prior role as the Claude-lane-facing wrapper named in
    `claude_aigenticHumanReview/DEVOPS.md`, used by `finalize_study.py` and
    `claude_aigenticHumanReview/aigenticHumanReview.py` via `from review_paths import ...`.
    Codex's own lane is reached through `codex_aigenticHumanReview/review_paths.py`'s shim, or
    directly here via `review_dir("codex")` etc.
"""
from __future__ import annotations

import os
from pathlib import Path

_ANALYTICS_ROOT = Path(__file__).resolve().parent

_LANE_CONFIG = {
    "claude": {
        "workdir_parent": _ANALYTICS_ROOT / "claude_aigenticHumanReview",
        "workdir_name": "claude_review_workdir",
        "decisions_filename": "claude_review_decisions.json",
        "env_prefix": "DOMAINRAG",
        # Fixed reporting location, not derived from review_dir() -- matches the original
        # claude_aigenticHumanReview/review_paths.py exactly.
        "output_root": _ANALYTICS_ROOT / "merged" / "review_analysis" / "charts",
    },
    "codex": {
        "workdir_parent": _ANALYTICS_ROOT / "codex_aigenticHumanReview",
        "workdir_name": "codex_review_workdir",
        "decisions_filename": "codex_review_decisions.json",
        "env_prefix": "DOMAINRAG_CODEX",
        # None means "derive from review_dir().parent" -- matches the original
        # codex_aigenticHumanReview/review_paths.py exactly (a different shape than claude's).
        "output_root": None,
    },
}


def _cfg(lane: str) -> dict:
    try:
        return _LANE_CONFIG[lane]
    except KeyError:
        raise ValueError(f"Unknown review lane {lane!r}; expected one of {sorted(_LANE_CONFIG)}") from None


def review_dir(lane: str = "claude") -> Path:
    cfg = _cfg(lane)
    override = (os.environ.get(f"{cfg['env_prefix']}_REVIEW_DIR") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (cfg["workdir_parent"] / cfg["workdir_name"]).resolve()


def input_json_path(lane: str = "claude") -> Path:
    cfg = _cfg(lane)
    filename = (os.environ.get(f"{cfg['env_prefix']}_REVIEW_INPUT_JSON") or "").strip()
    if filename:
        return review_dir(lane) / filename
    # Both lanes share one review_input.json at the analytics root -- matches the original
    # code exactly (each lane's own file computed parent.parent from its own subfolder, which
    # is the same analytics root either way).
    return (_ANALYTICS_ROOT / "review_input.json").resolve()


def decisions_json_path(lane: str = "claude") -> Path:
    cfg = _cfg(lane)
    filename = (os.environ.get(f"{cfg['env_prefix']}_REVIEW_DECISIONS_JSON") or "").strip()
    return review_dir(lane) / (filename or cfg["decisions_filename"])


def review_output_root(lane: str = "claude") -> Path:
    cfg = _cfg(lane)
    if cfg["output_root"] is not None:
        return cfg["output_root"].resolve()
    return review_dir(lane).parent


__all__ = ["review_dir", "input_json_path", "decisions_json_path", "review_output_root"]
