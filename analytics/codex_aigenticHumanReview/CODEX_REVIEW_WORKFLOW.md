## Purpose

Use this workflow when Codex is doing true manual review over the exported
`domainRag` item set and should not keep stopping on Windows permission prompts.

---

## Why This Exists

The canonical review export and decision files normally live under:

- `C:\Users\kadek\source\repos\domainRag\analytics\claude_aigenticHumanReview\claude_review_workdir\`

That is outside the normal workspace write root, which causes repeated
permission prompts during long manual review passes.

The fix is:

1. mirror the export into a repo-local workdir
2. review against the local mirror only
3. sync the finished decisions back to `secrets` once at the end

An additional control-plane issue showed up during this review:

- `codex exec`-driven auto-resume is not reliable on this machine because the
  local Codex CLI hit websocket/socket permission failures during non-interactive
  reconnect attempts

Because of that, the durable restart path is queue-driven through the existing
`agent_sync` Codex listener, not direct `codex exec` looping.

---

## Local Mirror Pattern

Recommended local workdir:

- `C:\Users\kadek\source\repos\domainRag\analytics\codex_aigenticHumanReview\codex_review_workdir\`

Expected files inside the local mirror:

- `codex_review_decisions.json`
- `README.txt`

Shared exported review input now lives at:

- `C:\Users\kadek\source\repos\domainRag\analytics\review_input.json`

The manual decision file remains Codex-owned inside the local workdir.

Preferred bootstrap command:

```powershell
python .\codex_aigenticHumanReview\aigenticHumanReview.py --bootstrap
```

This creates the local mirror if missing and exports fresh review input from
`analytics\merged_master.xlsx` directly into the Codex workdir. Codex no longer
needs to wait for a prior Claude export just to begin manual review.

---

## Environment Overrides

`review_paths.py` supports optional environment overrides so the same helper
code can point at the local mirror without renaming the canonical secret-path
files:

- `DOMAINRAG_REVIEW_DIR`
- `DOMAINRAG_REVIEW_INPUT_JSON`
- `DOMAINRAG_REVIEW_DECISIONS_JSON`

For Codex manual review, use:

```powershell
$env:DOMAINRAG_REVIEW_DIR='C:\Users\kadek\source\repos\domainRag\analytics\codex_aigenticHumanReview\codex_review_workdir'
$env:DOMAINRAG_REVIEW_INPUT_JSON='claude_review_input.json'
$env:DOMAINRAG_REVIEW_DECISIONS_JSON='codex_review_decisions.json'
```

---

## Working Rules

1. Never write batch-by-batch decisions directly into `C:\Users\kadek\secrets`.
2. Read source items from the local mirror.
3. Append decisions locally in bounded batches.
4. Use the local Codex review schema already present in `codex_review_decisions.json`.
5. Only after the manual pass is complete, copy the finished local decision file
   back to the canonical secrets review directory if needed.

---

## Resume Procedure

When resuming a manual review lane:

1. Count local decisions in `codex_review_decisions.json`.
2. Identify the last reviewed `(run_id, item_id)`.
3. Resume from the next item in `analytics\review_input.json`.
4. Keep all incremental writes inside the repo-local mirror.

---

## Queue-Driven Resume

Preferred restart surfaces:

- `C:\Users\kadek\source\repos\domainRag\analytics\codex_aigenticHumanReview\codex_review_resume_prompt.md`
- `C:\Users\kadek\source\repos\domainRag\analytics\codex_aigenticHumanReview\queue_codex_review_resume.ps1`
- `C:\Users\kadek\source\repos\domainRag\analytics\codex_aigenticHumanReview\supervise_codex_review_queue.ps1`

How it works:

1. `queue_codex_review_resume.ps1` writes one prompt payload into the Codex
   `agent_sync` inbox.
2. `supervise_codex_review_queue.ps1` watches
   `codex_review_decisions.json`.
3. After a quiet period, if the inbox is empty and the decision count has not
   yet reached the target, it re-enqueues the same resume prompt.
4. If the count advances, the supervisor resets its quiet timer and waits for
   the next lull before enqueuing again.
5. If the count does not advance, the supervisor can retry re-queueing after a
   longer no-progress interval and records that state to a local status file.
6. The supervisor now reads the real JSON array length from
   `codex_review_decisions.json`; earlier `count = 1` behavior was a fixed
   PowerShell counting bug and should no longer be treated as expected.

This is state-based, not phrase-based:

- re-enqueue because decision count advanced and then stalled
- not because the terminal output matched a magic completion phrase

Active queue-resume files:

- `C:\Users\kadek\source\repos\domainRag\analytics\codex_aigenticHumanReview\codex_review_resume_prompt.md`
- `C:\Users\kadek\source\repos\domainRag\analytics\codex_aigenticHumanReview\queue_codex_review_resume.ps1`
- `C:\Users\kadek\source\repos\domainRag\analytics\codex_aigenticHumanReview\supervise_codex_review_queue.ps1`
- `C:\Users\kadek\source\repos\domainRag\analytics\codex_aigenticHumanReview\codex_review_supervisor_state.json`

Queue-run prerequisites:

- the Codex terminal window must actually exist
- launch it via `C:\Users\kadek\source\.cogark\control_plane\ai_terminals\launchers\launch_codex.ps1`
- its window title must be `codex`
- the Codex `agent_sync` listener should be in `listening` state
- the local workdir JSON files must remain at their current names

---

## Stale Attempt Cleanup

`run_codex_review_loop.ps1` was an earlier attempt to auto-resume via direct
`codex exec` looping. It should not be used on this machine because the CLI
failed with websocket/socket permission errors and made no review progress.

That failed wrapper and its dead-end attempt logs should stay deleted. Do not
recreate them unless the CLI transport problem is resolved first.

---

## Final Sync

At the end of the review:

1. verify local review count is complete
2. optionally write the review sheet/workbook using the local override env vars
3. copy `codex_review_decisions.json` back to the secrets location if the
   downstream tooling still expects the canonical external review directory

The unattended queue loop should stop on its own when the supervisor sees the
target count, which defaults to `1200`.

---

## Notes

- This workflow is for true manual Codex review, not LM Studio or API scoring.
- Local Codex review entries use neutral `review_*` fields rather than the
  Claude-prefixed canonical scoring fields.
- If downstream tooling needs a different review sheet title or a different
  canonical filename, change that deliberately rather than pretending Codex work
  is "Claude review."

