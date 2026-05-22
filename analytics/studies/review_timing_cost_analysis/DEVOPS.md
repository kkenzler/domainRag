# DEVOPS

## Role

`review_timing_cost_analysis` is a meta-analysis study root under `analytics\studies`.

It exists to analyze timing and cost characteristics of the existing `domainRag` study/archive surfaces without creating a competing canonical merge/output path.

This root is for:
- timing interpretation
- cost modeling assumptions
- chart planning
- derived summary exports

It is not for:
- primary corpus storage
- authoritative merged workbook generation
- replacing `analytics\merged\review_analysis`

## Design intent

This study should bridge three evidence layers that currently live in different places:

1. Review-lane elapsed/cost export
   - `analytics\merged\review_analysis\review_summary_time_cost.csv`
   - useful for lane completion, observed elapsed windows, and estimated human review cost
   - not sufficient for true per-question timing

2. Batch-study run results
   - `analytics\_custom_batch_studies\...\batch_*_results.json`
   - strongest available source for generation/runtime duration comparisons by condition and difficulty

3. Static cost assumptions
   - `analytics\viz_costs.py`
   - current frontier-model API-equivalent cost helper
   - useful as a starting point, but not a full local-compute model

## Folder expectations

- `inputs\`
  - stable copied summaries or hand-selected source manifests used by this study
  - should remain small and explicit
- `exports\`
  - derived timing/cost tables created specifically for this study
  - safe place for intermediate CSV/JSON outputs before anything is promoted into broader chart flows
- `notes\`
  - durable study thinking
  - should carry assumptions, chart semantics, and wording/caveat guidance
- `runs\`
  - optional scratch area if helper scripts are later introduced
  - not a canonical archive destination
- `review\`
  - optional operator signoff or interpretation notes if manual approval becomes part of the flow

## Documentation split for this root

- `README.txt`
  - explains purpose, scope, workflow, and operator intent
- `DEVOPS.md`
  - records evidence sources, assumptions, folder roles, and modification guidance
- `notes\analysis_plan.md`
  - working interpretation of the timing/cost problem
- `notes\chart_specs.md`
  - proposed final figures, source tables, and wording constraints

## Canonical upstream sources

Review-analysis exports:
- `C:\Users\kadek\source\repos\domainRag\analytics\merged\review_analysis\review_summary_time_cost.csv`
- `C:\Users\kadek\source\repos\domainRag\analytics\merged\review_analysis\review_item_lane_long.csv`
- `C:\Users\kadek\source\repos\domainRag\analytics\merged\review_analysis\review_analysis_manifest.json`

Historical batch-control outputs:
- `C:\Users\kadek\source\repos\domainRag\analytics\_custom_batch_studies\`

Current chart/cost code:
- `C:\Users\kadek\source\repos\domainRag\analytics\viz_charts_review_analysis.py`
- `C:\Users\kadek\source\repos\domainRag\analytics\viz_costs.py`

Final destination for presentation-facing charts:
- `C:\Users\kadek\source\repos\domainRag\analytics\merged\review_analysis\charts`

## Current evidence-quality rules

Use these labels consistently in this study:

- `strong`
  - directly recorded batch durations from study results JSON
- `medium`
  - derived review-lane elapsed windows based on file mtimes
- `weak/unavailable`
  - per-question review timing, unless new logging is introduced
- `modeled`
  - local compute cost and frontier-equivalent cost assumptions

## Cost-model guidance

For presentation, separate these components rather than collapsing them into one vague number:

- `frontier_api_cost_estimate`
- `local_api_cost`
  - should remain zero if the lane used local models only
- `local_compute_cost_estimate`
  - electricity-only at minimum
- `human_review_cost_estimate`

Preferred default stance:
- local is `zero API spend`, not `free`
- local compute cost should be presented as a rough estimate
- hardware amortization is optional and should only be added if clearly labeled

## Wording constraints

Do not let charts or captions imply more precision than the evidence supports.

Preferred wording:
- `observed elapsed review window`
- `estimated review hours`
- `estimated API-equivalent cost`
- `rough local compute estimate`

Avoid:
- `time spent reviewing` when the value is derived from file mtimes
- `actual local cost` unless a fuller model exists
- `per-item review time` unless decision-level timestamps are added

## Modification guidance

- Keep this study root separate from the canonical merged outputs until the chart semantics are agreed.
- Put new derived tables here first, not directly into `merged\review_analysis`.
- If later scripts are added, they should read upstream canonical exports and write only into this study root unless promotion is deliberate.
- If a chart concept graduates into the active final chart surface, update the shared analytics docs rather than letting this study remain the only place where the rationale lives.
