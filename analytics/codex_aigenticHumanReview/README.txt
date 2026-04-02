Codex aigenticHumanReview support

This folder contains the local Codex-only manual review workflow:
- prompt requeue helpers
- supervisor state
- Python bootstrap/status helpers
- workflow notes
- the repo-local Codex review workdir

Use this folder when Codex is manually reviewing exported items without writing
incremental state back into the canonical secrets directory.

Shared exported review input is now:
- `C:\Users\kadek\source\repos\domainRag\analytics\review_input.json`

For unattended resume:
- keep the terminal title as `Codex`
- run `supervise_codex_review_queue.ps1`
- watch `codex_review_supervisor_state.json` for real count, listener status,
  inbox count, last queue result, and retry state

Bootstrap the local mirror with:
- `python .\codex_aigenticHumanReview\aigenticHumanReview.py --bootstrap`

Useful follow-up commands:
- `python .\codex_aigenticHumanReview\aigenticHumanReview.py --status`
- `python .\codex_aigenticHumanReview\aigenticHumanReview.py --print-paths`
