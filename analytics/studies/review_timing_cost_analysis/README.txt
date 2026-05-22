domainRag review timing and cost analysis
=========================================

Purpose
- This study root is the working surface for presentation-ready timing and cost analysis of the `domainRag` generation and review pipeline.
- It is not a new generation batch root.
- It exists to turn already-recorded analytics outputs into defensible figures and narrative support for the comparative write-up.

What this study is for
- understand how long the review lanes took
- distinguish coarse elapsed review windows from stronger batch-duration evidence
- compare local-model and frontier-model cost surfaces
- prepare chart concepts before any new chart implementation lands in `analytics\merged\review_analysis\charts`

What this study is not for
- running new corpus ingestion
- storing confidential corpus-bearing files
- replacing the canonical merged outputs under `analytics\merged`

Recommended workflow
1. Read `notes\analysis_plan.md`.
2. Read `notes\chart_specs.md`.
3. Pull source facts from:
   - `analytics\merged\review_analysis\review_summary_time_cost.csv`
   - `analytics\_custom_batch_studies\...\batch_*_results.json`
   - `analytics\viz_costs.py`
4. Build derived summary tables under `exports\`.
5. Only after the assumptions and wording are stable, implement or refine charts for:
   - `analytics\merged\review_analysis\charts`

Current study questions
- What timing claims are actually supported by the current logs?
- Which timing metric should be shown for review lanes?
- How should local compute be framed so the presentation does not overclaim "free"?
- Which final figures belong in the presentation-ready chart surface?

Key stance
- local is not literally free
- local has zero API spend, but still has compute/runtime cost
- review-lane elapsed time is useful, but should be labeled as a coarse observed window rather than active labor time

Expected folders
- `inputs\`
  - copied or referenced source summaries used by this analysis
- `exports\`
  - derived CSV/JSON tables for this study only
- `notes\`
  - planning notes, assumptions, chart specs, and wording guidance
- `runs\`
  - optional scratch artifacts if a helper script is used later
- `review\`
  - optional human signoff notes if needed later

Primary outputs to develop
- timing summary tables
- cost comparison summary tables
- presentation-ready chart specs
- supporting narrative/caption language

Notes
- The canonical final chart destination remains:
  - `C:\Users\kadek\source\repos\domainRag\analytics\merged\review_analysis\charts`
- This study root is the planning and derivation surface that should make those final charts easier to justify.
