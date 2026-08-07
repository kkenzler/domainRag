"""Thin compatibility shim -- delegates to the single review-path authority at
analytics/review_paths.py (consolidated 2026-08-06, G010/D011).

Kept so `from review_paths import ...` continues to work unchanged for any caller that puts
this folder on sys.path directly (today, every actual caller resolves through the analytics-root
authority module instead -- see that file's own docstring -- but this shim exists so a future
caller that imports this folder in isolation still gets correct, non-duplicated behavior rather
than a missing module).

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
    return _AUTHORITY.review_dir("claude")


def input_json_path() -> Path:
    return _AUTHORITY.input_json_path("claude")


def decisions_json_path() -> Path:
    return _AUTHORITY.decisions_json_path("claude")


def review_output_root() -> Path:
    return _AUTHORITY.review_output_root("claude")


__all__ = ["review_dir", "input_json_path", "decisions_json_path", "review_output_root"]
