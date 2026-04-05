## Analytics DEVOPS

### Scope

`analytics` is the canonical study workspace for `domainRag`.

It owns:
- generation/archive scripts
- shared review export and lane coordination
- merge/finalization logic
- chart rendering
- archived study sources
- merged study outputs

It should not require `C:\Users\kadek\secrets` for normal large-study analytics operation, except where a future confidential-corpus mode deliberately routes corpus-bearing files there.

### Top-level roles

Tracked source/archive roots:
- `example1_local-local`
  - archived `local/local` source runs
- `example1_haikuPermutations`
  - archived `local/haiku`, `haiku/local`, `haiku/haiku` source runs
- `example1_gptBaseline`
  - GPT baseline source inputs

Lane roots:
- `claude_aigenticHumanReview`
  - Claude review workflow, prompts, supervisor, lane-local charts helper, and repo-local `claude_review_workdir`
- `codex_aigenticHumanReview`
  - Codex review workflow, prompts, supervisor, lane-local charts helper, and repo-local `codex_review_workdir`

Derived outputs:
- `merged`
  - derived merged workbook outputs and review-analysis exports
- `merged\review_analysis`
  - shared review-analysis exports
- `merged\review_analysis\charts`
  - active final chart surface

Transient/staging:
- `runs`
  - transient batch staging during generation
  - should be empty or absent between completed studies
- `.mplconfig`
  - Matplotlib runtime config/cache used to keep chart rendering writable inside the repo-local workspace

Historical/non-canonical:
- `_custom_batch_studies`
  - historical study-control outputs from earlier iterations
  - currently not read by the active merge/finalization path

### Script relationships

Generation/archive:
- `run_batches.py`
  - executes batch generation and archives outputs into the tracked example1 study roots
- `run_full_study.py`
  - higher-level study execution wrapper

Merge/export:
- `merge_runs.py`
  - reads the tracked archived study roots and builds `merged_master.xlsx`
- `review_export.py`
  - exports shared review items into `review_input.json`

Review lane coordination:
- `review_lanes.py`
  - canonical lane registry for Claude and Codex
- `review_paths.py`
  - shared analytics-root path helpers
- `review_workflow.py`
  - progress/count helpers shared by review surfaces
- `human_review_cycle.py`
  - shared support for review sequencing

Lane-local review writing:
- `claude_aigenticHumanReview\aigenticHumanReview.py`
  - Claude status, metadata repair, workbook write-back, and lane operations
- `codex_aigenticHumanReview\...`
  - Codex lane equivalents

Finalization/rendering:
- `build_review_analysis_exports.py`
  - builds lane-agnostic review exports from merged workbook plus review decisions
- `finalize_study.py`
  - orchestrates review sheet write-back, export build, and chart rendering
- `analyticsVizs.py`
  - direct chart rendering entrypoint
- `viz_render.py`
  - chart output routing and render orchestration
- `viz_io.py`
  - normalization layer for merged/review datasets
- `viz_conditions.py`
  - condition ordering/display semantics
- `viz_theme.py`
  - chart theme and Matplotlib workspace config behavior

Chart families:
- `viz_charts_merged.py`
  - merged-generation charts
- `viz_charts_review_analysis.py`
  - shared review-analysis charts
- `claude_aigenticHumanReview\viz_charts_claude_review.py`
  - Claude lane-local charts
- `codex_aigenticHumanReview\viz_charts_codex_review.py`
  - Codex lane-local charts

### Key data surfaces

Canonical shared review input:
- `review_input.json`

Canonical lane decision files:
- `claude_aigenticHumanReview\claude_review_workdir\claude_review_decisions.json`
- `codex_aigenticHumanReview\codex_review_workdir\codex_review_decisions.json`

Canonical merged workbook:
- `merged_master.xlsx`

Canonical review-analysis output root:
- `merged\review_analysis`

Canonical chart output root:
- `merged\review_analysis\charts`
- this folder is now intentionally pruned to a smaller final review surface
- retired diagnostics should not be reintroduced casually; add them back only if they answer a concrete operator question

### Current design constraints

- The archived example1 roots are source-of-truth study archives for the current large run. `merge_runs.py` reads from them directly.
- `runs` is not a durable archive root. Anything needed after a study ends should be archived into the tracked study folders.
- GPT rows are a special review slice:
  - they have Claude and Codex review decisions
  - they do not have an original reviewer baseline
  - reviewer-agreement visuals must exclude GPT rows or label the scope explicitly
- Active review chart semantics should prefer:
  - `gpt/claude`
  - `gpt/codex`
  rather than raw `gpt/baseline` labels when the chart is expressing review behavior

### Modification guidance

- If archive routing changes, update `run_batches.py` and verify `merge_runs.py` still reads the correct tracked study roots.
- If lane workdirs move, update:
  - lane-local `review_paths.py`
  - `review_lanes.py`
  - any queue/supervisor scripts that hardcode the workdir
- If chart output routing changes, update:
  - `analyticsVizs.py`
  - `finalize_study.py`
  - `viz_render.py`
- Keep chart-folder cleanup explicit before rerendering so stale PNGs do not linger.
- Do not reintroduce `secrets` as a default dependency for normal analytics execution.

### Next-phase pressure points

- prune the final chart set
- simplify top-level analytics surfaces
- formalize small-study mode under a cleaner study-root structure
- define a strict no-external-endpoints mode for confidential corpora
