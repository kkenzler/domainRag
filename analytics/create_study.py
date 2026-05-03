from __future__ import annotations

import argparse
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
STUDIES_DIR = SCRIPT_DIR / "studies"


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "study"


def _write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def _study_readme(study_id: str, local_only: bool) -> str:
    if local_only:
        routing_note = (
            "This study is scaffolded for strict local-only execution.\n"
            "- Keep corpus files in `inputs/corpus_drop/` only as a temporary landing zone.\n"
            "- Move the real corpus to a secrets-backed local path before running.\n"
            "- Keep `INGEST_PROVIDER=local`, `GENERATE_PROVIDER=local`, and `REVIEW_PROVIDER=local`.\n"
            "- Do not use hosted review or generation endpoints for this study.\n"
        )
    else:
        routing_note = (
            "This study root is intended for smaller repeatable runs.\n"
            "- Corpus-bearing files should still be treated as sensitive by default.\n"
            "- If the corpus is confidential, use the local-only profile in `inputs/config/local_only.env.example`.\n"
        )
    return (
        f"domainRag small-study scaffold: `{study_id}`\n"
        f"=========================================\n\n"
        "Purpose\n"
        "- Hold one lighter-weight study in a single predictable root.\n"
        "- Keep corpus inputs, run outputs, review workdirs, and notes separated.\n"
        "- Avoid polluting the large `example1_*` study surfaces.\n\n"
        "Layout\n"
        "- `inputs/corpus_drop/`\n"
        "  - temporary landing zone for corpus files before a run\n"
        "- `inputs/config/`\n"
        "  - per-study config templates and local-only profile examples\n"
        "- `runs/`\n"
        "  - transient run outputs promoted or copied from secrets-backed run folders\n"
        "- `review/`\n"
        "  - review exports and lane workdirs for this study only\n"
        "- `exports/`\n"
        "  - merged or summarized outputs you want to keep for this study\n"
        "- `notes/`\n"
        "  - study-specific operator notes or interpretation writeups\n\n"
        "Routing\n"
        f"{routing_note}\n"
        "Suggested operator flow\n"
        "1. Adjust the template in `inputs/config/` for this study.\n"
        "2. Run generation from `_rag_testGen/interactive_run.py` or the batch path.\n"
        "3. Copy or promote only the run artifacts you want into `runs/`.\n"
        "4. Export review inputs into `review/` and complete both review lanes.\n"
        "5. Save merged summaries or final artifacts into `exports/`.\n"
    )


def _study_gitignore() -> str:
    return (
        "# Corpus-bearing and machine-local study files\n"
        "inputs/corpus_drop/*\n"
        "!inputs/corpus_drop/.gitkeep\n"
        "inputs/config/*.env\n"
        "inputs/config/*.local\n"
        "runs/*\n"
        "!runs/.gitkeep\n"
        "review/input/*\n"
        "!review/input/.gitkeep\n"
        "review/claude_workdir/*\n"
        "!review/claude_workdir/.gitkeep\n"
        "review/codex_workdir/*\n"
        "!review/codex_workdir/.gitkeep\n"
        "exports/generated/*\n"
        "!exports/generated/.gitkeep\n"
    )


def _local_only_template(study_id: str) -> str:
    return (
        "# domainRag local-only profile template\n"
        f"# Study: {study_id}\n"
        "# Copy this to a machine-local .env file outside git or keep it untracked here.\n\n"
        "INGEST_PROVIDER=local\n"
        "GENERATE_PROVIDER=local\n"
        "REVIEW_PROVIDER=local\n"
        "API_PROVIDER=\n"
        "API_MODEL=\n"
        "LLM_API_KEY=\n\n"
        "# Point DOMAIN_DIR at a secrets-backed local corpus path before running.\n"
        "# Example: C:\\Users\\kadek\\secrets\\domainRag\\studies\\<study_id>\\corpus\n"
        "DOMAIN_DIR=\n"
        "DB_DSN=\n"
        "LM_URL=http://localhost:1234\n"
        "EMBED_MODEL=\n"
        "CONTEXT_MODEL=\n"
        "GENERATOR_MODEL=\n"
        "REVIEW_MODEL=\n"
        "CHECKPOINT_CHUNKS=true\n"
        "CHECKPOINT_ITEMS=true\n"
        "CHECKPOINT_REVIEW=true\n"
    )


def create_study(study_label: str, local_only: bool) -> Path:
    study_id = _slugify(study_label)
    study_root = STUDIES_DIR / study_id

    dirs = [
        study_root / "inputs" / "corpus_drop",
        study_root / "inputs" / "config",
        study_root / "runs",
        study_root / "review" / "input",
        study_root / "review" / "claude_workdir",
        study_root / "review" / "codex_workdir",
        study_root / "exports" / "generated",
        study_root / "notes",
    ]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
        gitkeep = directory / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")

    _write_if_missing(study_root / "README.txt", _study_readme(study_id, local_only))
    _write_if_missing(study_root / ".gitignore", _study_gitignore())
    _write_if_missing(study_root / "inputs" / "config" / "local_only.env.example", _local_only_template(study_id))
    _write_if_missing(
        study_root / "notes" / "study_plan.txt",
        (
            f"Study plan: {study_id}\n"
            "====================\n\n"
            "Question\n"
            "- Define the exact comparison this study is intended to answer.\n\n"
            "Run shape\n"
            "- Corpus:\n"
            "- Conditions:\n"
            "- Difficulties:\n"
            "- N items per condition:\n\n"
            "Acceptance rule\n"
            "- Define what result would count as success before running the study.\n"
        ),
    )
    return study_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a small domainRag study root under analytics/studies.")
    parser.add_argument("study_label", help="Study label or ID. It will be slugified for the folder name.")
    parser.add_argument("--local-only", action="store_true", help="Mark the scaffold as a strict no-external-endpoints study.")
    args = parser.parse_args()

    study_root = create_study(args.study_label, args.local_only)
    print(study_root)


if __name__ == "__main__":
    main()
