from __future__ import annotations

import os
from pathlib import Path


def review_dir() -> Path:
    override = (os.environ.get("DOMAINRAG_REVIEW_DIR") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (Path(__file__).resolve().parent / "claude_review_workdir").resolve()


def input_json_path() -> Path:
    filename = (os.environ.get("DOMAINRAG_REVIEW_INPUT_JSON") or "").strip()
    if filename:
        return review_dir() / filename
    return (Path(__file__).resolve().parent.parent / "review_input.json").resolve()


def decisions_json_path() -> Path:
    filename = (os.environ.get("DOMAINRAG_REVIEW_DECISIONS_JSON") or "").strip()
    return review_dir() / (filename or "claude_review_decisions.json")


def review_output_root() -> Path:
    return (Path(__file__).resolve().parent.parent / "merged" / "review_analysis" / "charts").resolve()
