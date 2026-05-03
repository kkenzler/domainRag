domainRag small-study roots
===========================

Purpose
- `analytics/studies/` is the canonical home for lighter-weight or confidential study runs.
- Each subfolder should represent one study root with isolated inputs, run outputs, review workdirs, and notes.
- This keeps the tracked `example1_*` large-study archives separate from new smaller runs.

How to scaffold a study
-----------------------

Create a normal small-study root:

  python analytics\create_study.py my-study

Create a strict local-only study root:

  python analytics\create_study.py my-confidential-study --local-only

Expected shape
--------------
- `inputs/`
- `runs/`
- `review/`
- `exports/`
- `notes/`

Safety rule
-----------
- Do not commit corpus-bearing files or machine-local `.env` files into these study roots.
- The scaffold writes a per-study `.gitignore` for that on creation.
