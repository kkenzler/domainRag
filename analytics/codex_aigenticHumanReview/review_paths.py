from __future__ import annotations

from pathlib import Path


def review_dir() -> Path:
    return (Path(__file__).resolve().parent / "codex_review_workdir").resolve()


def input_json_path() -> Path:
    return (Path(__file__).resolve().parent.parent / "review_input.json").resolve()


def decisions_json_path() -> Path:
    return review_dir() / "codex_review_decisions.json"


def review_output_root() -> Path:
    return review_dir().parent
