# Analysis Plan

## Goal

Develop presentation-ready timing and cost figures for the `domainRag` comparative study without overstating what the logs can prove.

The analysis needs to answer:
- how long the main lanes took
- which timing metrics are defensible
- how local-model cost should be compared with frontier-model cost
- which figures are strong enough to promote into the final chart surface

## Core evidence split

### 1. Review-lane elapsed window

Source:
- `analytics\merged\review_analysis\review_summary_time_cost.csv`

What it gives:
- lane completion counts
- observed elapsed window from shared review export mtime to lane decisions-file mtime
- coarse throughput estimate
- estimated human review hours/cost from assumed minutes-per-item

What it does not give:
- active labor time
- decision-by-decision timestamps
- true per-question review duration

Interpretation rule:
- use this for `calendar elapsed review window`
- do not use this as `actual hands-on review time`

### 2. Batch generation/runtime duration

Source:
- `analytics\_custom_batch_studies\...\batch_*_results.json`

What it gives:
- run-level duration strings by condition and difficulty
- model/provider labels
- condition labels such as `local/local`, `local/haiku`, etc.

Interpretation rule:
- this is the strongest timing evidence currently available for condition-level runtime comparison

### 3. Cost assumptions

Source:
- `analytics\viz_costs.py`

What it gives:
- existing frontier pricing assumptions
- current stage-level token-cost helper

What still needs interpretation:
- whether the token assumptions should be reused directly
- how to express local compute cost
- whether hardware amortization belongs in the presentation

## Cost stance

### Local is not free

Local is only free in the narrow sense of:
- no vendor API bill for local-only runs

Local is not free in the broader sense because it still consumes:
- machine runtime
- electricity
- hardware wear / opportunity cost

### Recommended default framing

Use four distinct cost surfaces:
- frontier API-equivalent cost
- local API cost
- local compute estimate
- human review cost estimate

This gives a cleaner and more defensible presentation than collapsing everything into a single "cost" line.

### Preferred local estimate

Start with:
- electricity-only local compute estimate

Optional second layer:
- electricity plus rough hardware amortization

If hardware amortization is introduced, it must be clearly labeled as an assumption-heavy model rather than a recorded fact.

## Timing stance

### Review lanes

Primary message:
- Codex and Claude lane timing can be shown as coarse observed elapsed windows

Secondary message:
- throughput derived from those windows is useful for broad comparison, but should inherit the same caveat

### Generation conditions

Primary message:
- condition-level batch durations are the stronger timing story

This likely matters more for the final comparative narrative because it reflects actual machine-run performance rather than human/agent review cadence across calendar time.

## Presentation goals

The final figures should be able to survive skeptical reading in a report or deck.

That means:
- honest labels
- explicit caveats
- no hidden assumption jumps
- clean distinction between measured, derived, and modeled values

## Proposed working sequence

1. Inventory the exact timing/cost source fields.
2. Build study-local summary tables under `exports\`.
3. Decide the local compute assumption set.
4. Write chart specs with labels/caveats before implementation.
5. Implement only the charts that answer a real presentation question.

## Immediate deliverables for this study root

- `notes\chart_specs.md`
- study-local timing/cost source inventory
- study-local derived summary tables
- final selection of which charts should be promoted to `merged\review_analysis\charts`
