"""Thin compatibility shim -- delegates to the single review-path authority at
analytics/review_paths.py (consolidated 2026-08-06, G010/D011).

This shim IS load-bearing: `codex_aigenticHumanReview/aigenticHumanReview.py` puts this folder
on sys.path ahead of the analytics root, so `from review_paths import ...` resolves here, not to
the authority module directly. Preserves the exact call signature that caller already uses
(`review_dir()`, `input_json_path()`, `decisions_json_path()`, no `lane` argument).

Uses `importlib.util.spec_from_file_location` under an internal name, not a plain
`import review_paths`, because this file and the authority module share the same filename --
a bare import would resolve to whichever `review_paths.py` sys.path finds first, which could be
this very file re-importing itself.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_AUTHORITY_PATH = Path(__file__).resolve().parent.parent / "review_paths.py"
_SPEC = importlib.util.spec_from_file_location("domainrag_review_paths_authority", _AUTHORITY_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load the review-path authority module from {_AUTHORITY_PATH}")
_AUTHORITY = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_AUTHORITY)


def review_dir() -> Path:
    return _AUTHORITY.review_dir("codex")


def input_json_path() -> Path:
    return _AUTHORITY.input_json_path("codex")


def decisions_json_path() -> Path:
    return _AUTHORITY.decisions_json_path("codex")


def review_output_root() -> Path:
    return _AUTHORITY.review_output_root("codex")


__all__ = ["review_dir", "input_json_path", "decisions_json_path", "review_output_root"]
