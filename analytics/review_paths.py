from __future__ import annotations

import importlib.util
from pathlib import Path

_CLAUDE_PATH = Path(__file__).resolve().parent / "claude_aigenticHumanReview" / "review_paths.py"
_SPEC = importlib.util.spec_from_file_location("domainrag_claude_review_paths", _CLAUDE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load Claude review_paths from {_CLAUDE_PATH}")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

review_dir = _MODULE.review_dir
input_json_path = _MODULE.input_json_path
decisions_json_path = _MODULE.decisions_json_path
review_output_root = _MODULE.review_output_root

__all__ = [
    "review_dir",
    "input_json_path",
    "decisions_json_path",
    "review_output_root",
]
