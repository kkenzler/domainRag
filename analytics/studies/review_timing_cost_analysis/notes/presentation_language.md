# Presentation Language

## Approved wording

- `Observed elapsed review window`
- `Observed review throughput`
- `Estimated human review hours`
- `Estimated human review cost`
- `Estimated frontier API-equivalent cost`
- `Rough local compute estimate`
- `Zero API spend`

## Wording to avoid

- `Free local cost`
- `Actual review time`
- `Per-question review time`
- `True local operating cost`

## Caption rule

Any chart based on `review_summary_time_cost.csv` should state that the review timing is derived from file-modified timestamps and therefore represents a coarse elapsed window rather than decision-level active work.

## Local-cost rule

For presentation:
- local may be described as avoiding vendor API spend
- local should not be described as costless
- if local compute is estimated from runtime plus electricity assumptions, label it as rough or modeled
