# Claude aigenticHumanReview

---

## Purpose

This folder is the documentation/control surface for the canonical Claude
review lane.

---

## Canonical Paths

- Review input (shared):
  `analytics\review_input.json`
- Review decisions:
  `analytics\claude_aigenticHumanReview\claude_review_workdir\claude_review_decisions.json`

---

## Shared Script Surfaces

- `C:\Users\kadek\source\repos\domainRag\analytics\claude_aigenticHumanReview\aigenticHumanReview.py`
- `C:\Users\kadek\source\repos\domainRag\analytics\claude_aigenticHumanReview\review_paths.py`
- `C:\Users\kadek\source\repos\domainRag\analytics\review_export.py`
- `C:\Users\kadek\source\repos\domainRag\analytics\review_workflow.py`

Compatibility wrappers also exist at the analytics root:

- `C:\Users\kadek\source\repos\domainRag\analytics\aigenticHumanReview.py`
- `C:\Users\kadek\source\repos\domainRag\analytics\review_paths.py`

---

## Boundary

- Claude now uses the repo-local review workdir under
  `analytics\claude_aigenticHumanReview\claude_review_workdir\`.
- Shared exported review input now lives at
  `C:\Users\kadek\source\repos\domainRag\analytics\review_input.json`.
- Codex local manual review lives under
  `analytics\codex_aigenticHumanReview\` and should not be confused with the
  Claude lane.
- Shared export logic now lives in `review_export.py`, so both lanes can derive
  review input from the same `merged_master.xlsx` source without duplicating
  workbook parsing logic.
