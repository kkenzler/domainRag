# Codex aigenticHumanReview

---

## Purpose

This folder is the Codex-side local-control surface for getting
`aigenticHumanReview` running without repeated permission prompts or manual
relaunch friction.

---

## Contents

- `codex_review_workdir\`
- `aigenticHumanReview.py`
- `review_paths.py`
- `codex_review_resume_prompt.md`
- `queue_codex_review_resume.ps1`
- `supervise_codex_review_queue.ps1`
- `codex_review_supervisor_state.json` when the supervisor is running
- `CODEX_REVIEW_WORKFLOW.md`

---

## Operating Notes

- The local workdir keeps incremental Codex decisions inside the repo.
- `aigenticHumanReview.py --bootstrap` creates or refreshes the local Codex
  mirror directly from `analytics\merged_master.xlsx` and refreshes shared
  review input at `analytics\review_input.json`.
- The queue writer pushes one resume prompt into the Codex `agent_sync` inbox.
- The supervisor watches local decision count and listener state, then retries
  after quiet windows, including bounded retries when no progress occurs.
- The supervisor count logic is expected to match the real JSON array length in
  `codex_review_decisions.json`; treat any future `count = 1` result as a
  regression to investigate rather than normal behavior.
- The queue path assumes the live terminal title is exactly `Codex`.
- Codex local decisions use neutral `review_*` fields rather than
  `claude_*`-prefixed fields.

---

## Boundaries

- Shared review/export scripts still live at the analytics root.
- The canonical Claude review lane lives in
  `analytics\claude_aigenticHumanReview\claude_review_workdir\` by default.
  It is not overwritten by this Codex folder.
  Override with `DOMAINRAG_REVIEW_DIR` if needed.
