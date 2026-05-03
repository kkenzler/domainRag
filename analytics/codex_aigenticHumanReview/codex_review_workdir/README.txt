Codex manual review workdir

Files:
- codex_review_decisions.json

Shared review input lives at analytics\review_input.json — not in this workdir.

This folder exists to keep long manual review passes inside the repo workspace.
Do not write batch-by-batch decisions directly to the secrets review folder.

The Codex decision file uses neutral review fields:
- review_source_alignment
- review_distractor_quality
- review_stem_clarity
- review_difficulty_match
- review_decision
- review_notes

If tooling must point here, set:
- DOMAINRAG_REVIEW_DIR (to this workdir)
- DOMAINRAG_REVIEW_DECISIONS_JSON=codex_review_decisions.json
(review input defaults to analytics\review_input.json — do not override it)
