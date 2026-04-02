from __future__ import annotations

import os
from pathlib import Path


def review_dir() -> Path:
    override = (os.environ.get("DOMAINRAG_REVIEW_DIR") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (Path.home() / "secrets" / "domainRag" / "claude-review" / "claude-review-batching").resolve()


def input_json_path() -> Path:
    filename = (os.environ.get("DOMAINRAG_REVIEW_INPUT_JSON") or "").strip()
    if filename:
        return review_dir() / filename
    return (Path(__file__).resolve().parent.parent / "review_input.json").resolve()


def decisions_json_path() -> Path:
    filename = (os.environ.get("DOMAINRAG_REVIEW_DECISIONS_JSON") or "").strip()
    return review_dir() / (filename or "claude_review_decisions.json")


def review_output_root() -> Path:
    return review_dir().parent
