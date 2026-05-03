domainRag analytics

Purpose
- This folder is the study and review workspace for domainRag item generation, human-review lanes, merge/finalization, and chart output.

Main entrypoints
- `run_batches.py`
  - runs unattended generation batches and archives them into the tracked study folders
- `create_study.py`
  - scaffolds a clean small-study root under `analytics\studies\`
- `merge_runs.py`
  - merges archived study sources into `merged_master.xlsx`
- `review_export.py`
  - exports shared review items into `review_input.json`
- `finalize_study.py`
  - writes review sheets, builds review-analysis exports, and renders charts
- `analyticsVizs.py`
  - renders chart sets directly when you want visualization without rerunning the full finalization flow

Main folders
- `example1_local-local`
  - archived source runs for the `local/local` study slice
- `example1_haikuPermutations`
  - archived source runs for the `local/haiku`, `haiku/local`, and `haiku/haiku` slices
- `example1_gptBaseline`
  - GPT baseline source inputs
- `claude_aigenticHumanReview`
  - Claude review lane workflow and repo-local review workdir
- `codex_aigenticHumanReview`
  - Codex review lane workflow and repo-local review workdir
- `merged`
  - derived merged outputs and review-analysis exports
- `studies`
  - canonical home for smaller repeatable study roots and confidential local-only study scaffolds
- `_custom_batch_studies`
  - historical batch-control outputs from earlier study iterations
  - not part of the current canonical end-to-end path

Important files
- `merged_master.xlsx`
  - merged workbook and the main operator-facing study artifact
- `review_input.json`
  - shared review export consumed by both review lanes

Current output surface
- active review charts render to:
  - `analytics\merged\review_analysis\charts`
- that chart folder is now intentionally pruned to the smaller final review surface rather than the full diagnostic bundle

Typical operator flow
1. Run generation/archive through `run_batches.py` or the canonical wrapper that calls it.
2. Merge archived runs into `merged_master.xlsx`.
3. Export shared review items to `review_input.json`.
4. Complete both review lanes:
   - Claude
   - Codex
5. Run `finalize_study.py`.
6. Inspect:
   - `merged_master.xlsx`
   - `merged\review_analysis\charts`

Notes
- `analytics\runs` is transient staging only when active. Finished study state should live in the tracked archive folders, not there.
- Small-study and confidential-corpus work should start under `analytics\studies\`.
- Use `python analytics\create_study.py <study-id> --local-only` when corpus material must never leave local endpoints.
