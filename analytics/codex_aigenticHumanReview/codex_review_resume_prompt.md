Continue the true manual `domainRag` review from the next unreviewed item in the local Codex mirror.

Ground rules:
- Work only from `C:\Users\kadek\source\repos\domainRag\analytics\codex_aigenticHumanReview\codex_review_workdir\`
- Read exported items from `C:\Users\kadek\source\repos\domainRag\analytics\review_input.json`
- Write decisions only to `codex_review_decisions.json`
- Do not touch the canonical `secrets` review directory during the incremental pass
- Do not rename files
- Do not change workflow code unless something is actually broken
- Review items manually using your own judgment, not LM Studio or API scoring
- Preserve the existing decision schema already present in `codex_review_decisions.json`
- If an item is malformed, ambiguous, or has a bad key, mark it accordingly and explain briefly in `review_notes`
- Keep working forward from the current last reviewed item
- Use the entire turn for review work and only stop early if a real blocker occurs

Before writing:
1. Count entries in `codex_review_decisions.json`
2. Identify the last reviewed `(run_id, item_id)`
3. Resume from the next item in `review_input.json`

When this run finishes:
- Report only a concise checkpoint:
  - current count
  - last completed `(run_id, item_id)`
  - next item if known
