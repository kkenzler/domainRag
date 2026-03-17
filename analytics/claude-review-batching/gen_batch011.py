"""Generate batch011.json — Claude review decisions for items 501-550."""
import json
from pathlib import Path

INPUT = Path("claude_review_input.json")
OUTPUT = Path("batch011.json")
BASE_OFFSET = 500

with open(INPUT, encoding="utf-8") as f:
    items = json.load(f)

# (align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag, notes)
RAW = [
    # 501 rev=REVISE sa=5 KEY=B - SCOR focus: internal efficiency; stem ambiguous (SCOR is also inter-firm)
    (5, 3, 3, True, "REVISE", "True", True, True, True, True, False,
     "B correct per chunk; stem ambiguous - SCOR also covers inter-firm coordination beyond internal efficiency"),
    # 502 rev=REVISE sa=4 KEY=C - strategic motive for inventory = market presence; duplicate of 476
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "Correct; duplicate of items 476 and 531"),
    # 503 rev=ACCEPT sa=5 KEY=B - shortage costs = losses from not satisfying demand
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Standard shortage cost definition; B correct"),
    # 504 rev=REVISE sa=3 KEY=C - newsboy pricing: key factor = (p-c)/p; conflates price and qty decisions
    (3, 3, 3, True, "REVISE", "True", True, False, False, False, True,
     "Conflates price optimization with quantity critical ratio (p-c)/p; ambiguous framing of 'key factor in determining optimal price'"),
    # 505 rev=ACCEPT sa=5 KEY=B - 19% improvement from top management emphasis on inventory reduction
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Data-specific recall from source; B correct"),
    # 506 rev=ACCEPT sa=5 KEY=B - EOQ: doubling/halving Q increases costs by 25%; C also true (avg inv=Q/2)
    (5, 3, 4, True, "ACCEPT", "True", True, True, False, True, False,
     "B correct (25% rule); option C also true (average inventory during cycle = Q/2) - double-correct issue"),
    # 507 rev=ACCEPT sa=5 KEY=B - two-stage SC order-up-to based on mean+std with lead time
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Correct description of order-up-to policy incorporating demand uncertainty and lead time"),
    # 508 rev=ACCEPT sa=5 KEY=C - strategic sourcing driver: freight costs (distractors clearly absurd)
    (5, 5, 5, True, "ACCEPT", "True", True, True, True, True, False,
     "C correct; clearly absurd distractors (logo color, CEO preferences) make this unambiguous"),
    # 509 rev=ACCEPT sa=5 KEY=A - deterministic newsboy: p*=(a+bc)/(2b)
    (5, 4, 5, True, "ACCEPT", "True", True, True, True, True, False,
     "Correct formula; good distractors including stochastic formula and critical ratio"),
    # 510 rev=ACCEPT sa=5 KEY=C - global SC: balance scale economies with flexibility for high-cost markets
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Well-constructed; C correctly captures global SC tradeoff"),
    # 511 rev=ACCEPT sa=5 KEY=A - C1 lower when distributing within same market
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Correct C1 vs C2 distinction; A=local distribution at lower cost C1"),
    # 512 rev=ACCEPT sa=5 KEY=B - SCM goal: maximize customer value through integration
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Standard SCM goal definition; B correct"),
    # 513 rev=ACCEPT sa=5 KEY=A - additive demand revenue: r(y,p) = -cy + p*E[min(y,D)]
    (5, 4, 5, True, "ACCEPT", "True", True, True, True, True, False,
     "Correct revenue function formulation"),
    # 514 rev=REVISE sa=5 KEY=A - WRONG KEY: D='Planning,Sourcing,Making,Delivering,Returning,Enabling' is SCOR standard
    (2, 2, 4, True, "REJECT", "False", True, False, True, False, True,
     "WRONG KEY: D lists actual SCOR standard processes (Plan/Source/Make/Deliver/Return/Enable); KEY=A lists non-standard terms (forecasting, procurement, manufacturing, order mgmt, reverse logistics, IT)"),
    # 515 rev=ACCEPT sa=5 KEY=B - C1 = within same market distribution cost
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Correct C1 definition; duplicate of items 481/487"),
    # 516 rev=REVISE sa=3 KEY=B - development SC: strategic partnerships during product architecture
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B correct; weak chunk support (sa=3) for development vs fulfillment distinction"),
    # 517 rev=REVISE sa=2 KEY=B - decentralized info has LARGER variability; B correct, very weak chunk
    (2, 3, 4, True, "REVISE", "True", True, True, True, False, False,
     "B correct (decentralized info amplifies bullwhip); very weak chunk alignment (sa=2)"),
    # 518 rev=REVISE sa=3 KEY=C - multi-plant: l* fractional adjustment step; highly technical
    (3, 3, 2, True, "REVISE", "True", True, True, True, False, False,
     "Technically correct; stem requires familiarity with specific piecewise-linear optimization algorithm"),
    # 519 rev=REVISE sa=3 KEY=D - LEAST contributor to freight rate increase: agricultural demand
    (3, 4, 4, True, "REVISE", "True", True, True, True, False, False,
     "D correctly excluded (agricultural demand resisted decline but didn't cause rate increases); weak chunk alignment"),
    # 520 rev=REVISE sa=3 KEY=C - multi-stage bullwhip: upstream estimates from downstream orders
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "C correct; A also partially true (variability IS function of L and p); ambiguity"),
    # 521 rev=ACCEPT sa=5 KEY=A - production >> customer demand = bullwhip effect recognition
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Scenario-based bullwhip recognition; A correct"),
    # 522 rev=ACCEPT sa=5 KEY=B - 2021 freight: port congestion + reduced capacity; near-duplicate
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Correct; near-duplicate of items 473/549"),
    # 523 rev=REVISE sa=3 KEY=C - EOQ backorders higher cost: C=high demand + low Q
    (3, 3, 3, True, "REVISE", "True", True, False, False, False, True,
     "Ambiguous framing - conflates planned backorder model with ad hoc stockouts; C plausible but unclear in planned backorder context"),
    # 524 rev=ACCEPT sa=5 KEY=C - PepsiCo sourcing: freight, duties, raw materials
    (5, 5, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "PepsiCo case-specific; C correct; distractors clearly absurd"),
    # 525 rev=ACCEPT sa=5 KEY=B - centralize when high variability + negatively correlated demand
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Correct risk-pooling logic: negative correlation maximizes pooling benefit"),
    # 526 rev=REVISE sa=3 KEY=C - which step involves calculating l*: fractional adjustment
    (3, 3, 2, True, "REVISE", "True", True, True, True, False, False,
     "Highly technical notation; requires knowledge of specific facility optimization algorithm"),
    # 527 rev=REVISE sa=2 KEY=B - newsboy: optimal Q = marginal cost vs marginal profit; weak chunk
    (2, 3, 4, True, "REVISE", "True", True, True, True, False, False,
     "B correct (critical ratio); chunk is additive demand model not directly newsboy Q decision"),
    # 528 rev=REVISE sa=3 KEY=D - NOT carrying cost: transportation; duplicate of 483
    (3, 3, 4, True, "REVISE", "True", True, True, True, False, False,
     "D correctly excluded (transportation = ordering/acquisition cost); duplicate of item 483"),
    # 529 rev=ACCEPT sa=5 KEY=D - WRONG KEY: D says pi DECREASES → s* approaches Q*; contradicts item 457
    (2, 2, 4, True, "REJECT", "False", True, False, True, False, True,
     "WRONG KEY: D says 'as pi decreases, s* approaches Q*' but s*=pi*Q/(h+pi) INCREASES with pi; item 457 (accepted) confirms s* approaches Q* as pi INCREASES; KEY=B is correct"),
    # 530 rev=ACCEPT sa=5 KEY=B - outsourcing increased 1993-1996; purchasing % sales rising
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Specific data from source; B correct"),
    # 531 rev=REVISE sa=3 KEY=C - strategic motive: market presence through availability; duplicate
    (3, 3, 4, True, "REVISE", "True", True, True, True, False, False,
     "Duplicate of items 476/502; weak chunk alignment (sa=3)"),
    # 532 rev=REVISE sa=5 KEY=D - US logistics costs: energy, rail, truck drivers, security
    (5, 4, 3, True, "REVISE", "True", True, True, True, True, False,
     "D correct compound answer; stem 'contributed most significantly' with compound option is somewhat ambiguous"),
    # 533 rev=REVISE sa=3 KEY=C - functionally organized challenge: rigid hierarchy
    (3, 3, 3, True, "REVISE", "True", True, True, False, False, False,
     "C correct; B (absence of unified systems) also a valid challenge; ambiguity about key challenge"),
    # 534 rev=REVISE sa=3 KEY=B - SCM challenge: conflicting objectives across functional areas
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B correct; weak chunk support (sa=3)"),
    # 535 rev=ACCEPT sa=5 KEY=B - horizontal process-driven orgs: end-to-end with flat hierarchies
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Well-constructed contrast; B correctly describes horizontal organization"),
    # 536 rev=ACCEPT sa=5 KEY=A - longer forecast horizon → worse forecast
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Classic forecasting principle; A correct"),
    # 537 rev=REVISE sa=4 KEY=B - optimal order quantity: balance marginal cost vs profit
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "B correct; reviewer noted revision needed for clarity"),
    # 538 rev=REVISE sa=3 KEY=C - traditional accounting: obscures demand signals, transport cost differences
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "C plausible but overly specific; functional silos primarily distort demand signals upstream"),
    # 539 rev=ACCEPT sa=5 KEY=C - SCM dual focus: cost minimization AND service level
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "C correctly captures dual focus of SCM"),
    # 540 rev=ACCEPT sa=5 KEY=C - operational decisions: scheduling, monitoring, controlling production
    (5, 4, 5, True, "ACCEPT", "True", True, True, True, True, False,
     "Correct classification of operational vs strategic vs tactical decisions"),
    # 541 rev=REVISE sa=4 KEY=B - bullwhip two-stage: variance of orders >> demand variance
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "B correct mathematical description; reviewer flagged for minor revision"),
    # 542 rev=REVISE sa=3 KEY=B - ZICO policy: extends ZIO to capacity-constrained
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B technically correct; A describes ZIO not ZICO; weak chunk support"),
    # 543 rev=REVISE sa=3 KEY=D - NOT in SC network design: product standardization
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "D correctly excluded from SC network design factors; weak chunk alignment"),
    # 544 rev=ACCEPT sa=5 KEY=C - buyback: increases order quantities by reducing retailer risk
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Correct buyback mechanism; C accurately describes incentive effect"),
    # 545 rev=REVISE sa=3 KEY=A - stochastic price > deterministic; A correct direction, weak reasoning
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "A correct (stochastic price higher) but 'allows more flexibility' is weak explanation; correct reason: E[min(z*,eps)]>0"),
    # 546 rev=REVISE sa=3 KEY=B - modern global SCs: lower-scale, higher-skill, JIT, vendor integration
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B plausible from outsourcing context; weak chunk alignment (sa=3)"),
    # 547 rev=REVISE sa=3 KEY=D - NOT contributor to inventory turnover improvement: increased SKUs
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "D correctly excluded (chunk mentions SKU reduction as contributor); weak chunk alignment"),
    # 548 rev=ACCEPT sa=5 KEY=B - tactical decisions most directly influence inventory levels
    (5, 3, 3, True, "ACCEPT", "True", True, True, False, True, False,
     "B most directly tied to inventory (tactical planning sets schedules); D='all of above' also defensible"),
    # 549 rev=ACCEPT sa=5 KEY=B - 2021 freight: port congestion reducing vessel capacity; near-duplicate
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Correct; near-duplicate of items 473/522"),
    # 550 rev=ACCEPT sa=5 KEY=A - production >> demand = bullwhip; near-duplicate of 521
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Correct; near-duplicate of item 521"),
]

decisions = []
for offset, row in enumerate(RAW):
    item = items[BASE_OFFSET + offset]
    (align, dist, clarity, dm, decision, agrees, chunks_ok,
     verifiable, distractors_wrong, rev_acc, flag, notes) = row
    decisions.append({
        "run_id": item["run_id"],
        "item_id": item["item_id"],
        "batch_label": item["batch_label"],
        "condition": item["condition"],
        "difficulty": item["difficulty"],
        "claude_source_alignment": align,
        "claude_distractor_quality": dist,
        "claude_stem_clarity": clarity,
        "claude_difficulty_match": dm,
        "claude_decision": decision,
        "reviewer_decision": item["reviewer_decision"],
        "agrees_with_reviewer": agrees,
        "chunks_support_question": chunks_ok,
        "correct_answer_verifiable": verifiable,
        "distractors_clearly_wrong": distractors_wrong,
        "reviewer_source_call_accurate": rev_acc,
        "flag_ambiguity": flag,
        "claude_notes": notes,
    })

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(decisions, f, indent=2, ensure_ascii=False)

accept = sum(1 for d in decisions if d["claude_decision"] == "ACCEPT")
revise = sum(1 for d in decisions if d["claude_decision"] == "REVISE")
reject = sum(1 for d in decisions if d["claude_decision"] == "REJECT")
print(f"Batch 11 written: {len(decisions)} items")
print(f"  ACCEPT: {accept}")
print(f"  REJECT: {reject}")
print(f"  REVISE: {revise}")
