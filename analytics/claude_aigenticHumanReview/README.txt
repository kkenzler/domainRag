Claude aigenticHumanReview support

This folder documents the Claude-side review lane.

Shared exported review input now lives at:
- `C:\Users\kadek\source\repos\domainRag\analytics\review_input.json`

Claude's canonical review decisions still live at:
- `C:\Users\kadek\secrets\domainRag\claude-review\claude-review-batching\claude_review_decisions.json`

The shared analytics scripts at the repo root still drive export, scoring,
status, append, and workbook write behavior for the Claude lane.

Claude remains the canonical external-review lane.
Codex now has an independent local bootstrap lane under
`analytics\codex_aigenticHumanReview\` and does not require a prior Claude
export to begin manual review.
