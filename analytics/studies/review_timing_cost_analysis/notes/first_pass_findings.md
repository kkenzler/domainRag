# First-Pass Findings

## Scope

This is a study-local first pass on machine-cost framing for the archived `example1_50x3` batch study.

It uses:
- recorded batch durations from `batch_*_results.json`
- frontier stage-cost assumptions from `analytics\viz_costs.py`
- a first-pass local electricity model

It does not yet include:
- hardware amortization
- a verified local utility rate
- a measured machine power log

## First-pass assumptions

- electricity rate: `$0.15 / kWh`
- average blended system draw during local compute: `350 W`
- local compute allocation: `local_stages / 3`
  - modeled pipeline stages are `ingest`, `generate`, `review`

## Main pattern

The first-pass machine-cost model says:

- `local/local` is cheapest
- `haiku/haiku` is most expensive
- the hybrid conditions sit between them

That is not surprising, but the important presentation point is this:

- local is not literally free
- local machine cost is still very small in the first-pass model
- frontier API cost dominates machine-cost differences much more than local electricity does

## Condition-level first-pass averages

- `local/local`
  - avg duration: `1.4771 h`
  - avg local compute estimate: `$0.0775`
  - avg API estimate: `$0.0000`
  - avg combined machine estimate: `$0.0775`

- `local/haiku`
  - avg duration: `1.5203 h`
  - avg local compute estimate: `$0.0532`
  - avg API estimate: `$0.0652`
  - avg combined machine estimate: `$0.1184`

- `haiku/local`
  - avg duration: `1.4860 h`
  - avg local compute estimate: `$0.0520`
  - avg API estimate: `$0.0856`
  - avg combined machine estimate: `$0.1376`

- `haiku/haiku`
  - avg duration: `1.7647 h`
  - avg local compute estimate: `$0.0309`
  - avg API estimate: `$0.1508`
  - avg combined machine estimate: `$0.1817`

## Review-lane context

The current shared review export still shows:

- Claude observed elapsed review window: `139.77 h`
- Codex observed elapsed review window: `119.184 h`

These should remain labeled as coarse observed windows, not active review labor time.

## Practical presentation implication

For a presentation-ready cost story, the clean message is:

1. Local removes vendor API spend.
2. Local still has non-zero compute cost.
3. In this first pass, local compute cost is small compared with frontier API-priced stages.
4. Human review cost remains much larger than either of those machine-cost layers.

## Caution

This first-pass model is useful for relative comparison, not for claiming exact real-world operating cost.

The next refinement step, if needed, would be:
- better electricity-rate assumption
- better average-power assumption
- optional second scenario with hardware amortization
