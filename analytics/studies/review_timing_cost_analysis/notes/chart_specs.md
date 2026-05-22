# Chart Specs

## Purpose

These are the presentation-facing chart concepts for the `review_timing_cost_analysis` study.

Each chart should answer one clear question and use wording that matches the evidence quality.

## Chart 1

### Name

`Review Lane Observed Elapsed Window`

### Question answered

How long did the Claude and Codex review lanes remain open from shared review export to final decisions-file completion?

### Likely source

- `analytics\merged\review_analysis\review_summary_time_cost.csv`

### Value type

- measured from file mtimes
- coarse

### Required wording

- title or subtitle should include `observed elapsed window`
- caption should explicitly note that decision-level timestamps are not currently logged

### Why it belongs

This is the clearest timing view for the manual/agent review phase, as long as it is not oversold.

## Chart 2

### Name

`Review Lane Throughput`

### Question answered

How many reviewed items per hour were completed by each lane when using the observed elapsed window as the denominator?

### Likely source

- `analytics\merged\review_analysis\review_summary_time_cost.csv`

### Value type

- derived from coarse elapsed window

### Required wording

- use `observed items/hour`
- avoid implying active labor throughput

### Why it belongs

Useful as a secondary comparison if paired directly with Chart 1 and its caveat.

## Chart 3

### Name

`Batch Duration by Condition and Difficulty`

### Question answered

Which generation/review condition combinations took longer at the run level?

### Likely source

- `analytics\_custom_batch_studies\...\batch_*_results.json`

### Value type

- strong recorded runtime evidence

### Required wording

- use `batch duration`
- if normalized, label as `average duration per item`

### Why it belongs

This is probably the strongest timing figure in the whole study because it comes from recorded run results rather than mtime proxies.

## Chart 4

### Name

`Estimated Cost Comparison: Local vs Frontier`

### Question answered

How does the cost surface change when the pipeline uses local models versus frontier API-priced models?

### Likely source

- `analytics\viz_costs.py`
- study-local assumption table built in `exports\`

### Value type

- modeled

### Required wording

- use `estimated`
- separate:
  - `frontier API-equivalent cost`
  - `local compute estimate`
  - `local API spend`

### Why it belongs

This is likely one of the missing figures the write-up actually needs.

## Chart 5

### Name

`Estimated Human Review Cost Context`

### Question answered

How large is the estimated human review burden relative to machine/API cost?

### Likely source

- `analytics\merged\review_analysis\review_summary_time_cost.csv`

### Value type

- modeled estimate based on minutes-per-item and hourly rate assumptions

### Required wording

- use `estimated human review hours`
- use `estimated human review cost`
- preserve the assumption labels

### Why it belongs

It helps frame whether machine cost differences are practically meaningful relative to review labor.

## Chart 6

### Name

`Timing and Cost Summary Dashboard`

### Question answered

What are the main takeaways across review time, batch runtime, and cost in one presentation-ready figure?

### Likely source

- study-local derived exports assembled from the upstream timing/cost surfaces

### Value type

- mixed measured/derived/modeled

### Required wording

- panel labels must separate:
  - measured runtime
  - observed elapsed review window
  - estimated cost

### Why it belongs

This is the synthesis figure for the final report or slide deck.

## Charts to avoid unless new logging is added

- per-question review duration
- true active review time
- exact local operating cost

These would currently overclaim the evidence.

## Promotion rule

A chart should only move into:
- `C:\Users\kadek\source\repos\domainRag\analytics\merged\review_analysis\charts`

if:
- it answers a concrete presentation question
- its wording matches the evidence quality
- its assumptions are documented in this study root first
