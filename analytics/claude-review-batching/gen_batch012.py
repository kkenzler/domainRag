"""Generate batch012.json — Claude review decisions for items 551-615 (65 items, final batch)."""
import json
from pathlib import Path

INPUT = Path("claude_review_input.json")
OUTPUT = Path("batch012.json")
BASE_OFFSET = 550

with open(INPUT, encoding="utf-8") as f:
    items = json.load(f)

# (align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag, notes)
RAW = [
    # 551 rev=REVISE sa=5 KEY=B - F(X) reflects diminishing returns; stem ambiguous
    (5, 3, 3, True, "REVISE", "True", True, True, True, True, False,
     "B plausible (F(X)=total production cost with concavity); 'diminishing returns' framing ambiguous"),
    # 552 rev=REVISE sa=3 KEY=B - aggregate forecasts reduce uncertainty; correct but weak chunk
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B correct (aggregation reduces uncertainty per law of large numbers); weak chunk support"),
    # 553 rev=REVISE sa=2 KEY=B - decentralized variability larger; duplicate of 517
    (2, 3, 4, True, "REVISE", "True", True, True, True, False, False,
     "Duplicate of item 517; very weak chunk alignment (sa=2)"),
    # 554 rev=ACCEPT sa=5 KEY=B - centralize: high variability + short lead times
    (5, 3, 3, True, "ACCEPT", "True", True, True, True, True, False,
     "B correct per chunk; note: short lead times reduce pooling benefit in theory, but accepted per reviewer and source"),
    # 555 rev=REVISE sa=4 KEY=D - NOT contributor to freight rate rise: decreased ag demand
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "D correctly excluded (agricultural demand remained strong, did not decrease); reviewer flagged for revision"),
    # 556 rev=ACCEPT sa=5 KEY=B - logistics aligns planning with execution
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "B correctly describes logistics as integrative function in transforming organizations"),
    # 557 rev=REVISE sa=3 KEY=D - development SC: product architecture + early supplier involvement
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "D correct fuller description; weak chunk support (sa=3)"),
    # 558 rev=ACCEPT sa=5 KEY=C - global SC: flexible network that shifts production
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "C correctly describes flexible global network strategy balancing scale vs transport"),
    # 559 rev=REVISE sa=3 KEY=D - NOT holding cost: transportation; duplicate of 483/528
    (3, 3, 4, True, "REVISE", "True", True, True, True, False, False,
     "D correctly excluded; duplicate of items 483/528/562"),
    # 560 rev=REVISE sa=5 KEY=A - longer horizon → worse forecast; near-duplicate of 536
    (5, 3, 3, True, "REVISE", "True", True, True, True, True, False,
     "A correct; near-duplicate of item 536"),
    # 561 rev=ACCEPT sa=5 KEY=D - SC strategy step 2: identify decision choices and service requirements
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "D correctly identifies step 2 of SC strategy development framework"),
    # 562 rev=REVISE sa=3 KEY=D - NOT holding cost: transportation; exact duplicate of 559
    (3, 3, 4, True, "REVISE", "True", True, True, True, False, False,
     "Exact duplicate of item 559; D correctly excluded"),
    # 563 rev=ACCEPT sa=5 KEY=B - PepsiCo sourcing: interplant freight and avg run rates
    (5, 5, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "B correct; distractors clearly absurd (logo color, brand reputation, employee count)"),
    # 564 rev=ACCEPT sa=5 KEY=B - bullwhip more severe in decentralized due to compounding
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "B correctly explains decentralized bullwhip amplification vs centralized"),
    # 565 rev=REVISE sa=5 KEY=D - NOT sourcing driver: packaging color; trivially easy for medium
    (5, 4, 5, True, "REVISE", "True", True, True, True, True, False,
     "D trivially correct (packaging color is absurd); distractor quality undermines medium difficulty label"),
    # 566 rev=ACCEPT sa=5 KEY=B - logistics as central driver for SC integration
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "B correctly describes logistics as alignment mechanism between planning and execution"),
    # 567 rev=REVISE sa=4 KEY=B - SCM competitive advantage through integration and optimization
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "B correct; reviewer flagged minor revision needed"),
    # 568 rev=REVISE sa=3 KEY=B - EOQ vs EPQ: independence from product cost claim questionable
    (3, 3, 3, True, "REVISE", "True", False, False, True, False, True,
     "B's claim that EOQ is independent of product cost is questionable if h=ic (holding cost includes cost); EPQ finite production rate portion correct"),
    # 569 rev=REVISE sa=3 KEY=B - globalization complexity; duplicate of 546/598/610
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B correct; near-duplicate of items 546/598/610; weak chunk alignment"),
    # 570 rev=REVISE sa=3 KEY=A - EOQ backorders when pi>>h: both approach unconstrained EOQ
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "A correct (when pi>>h, s* approaches Q* which approaches unconstrained EOQ); weak chunk support"),
    # 571 rev=REVISE sa=3 KEY=D - bullwhip exacerbated by multiplicative variability across stages
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "D correct (variance grows multiplicatively across stages); A/C partially true but wrong direction"),
    # 572 rev=REVISE sa=5 KEY=B - traditional accounting fails due to functional cost centers
    (5, 3, 4, True, "REVISE", "True", True, True, True, True, False,
     "B correct; C also partially true (transport cost visibility is a specific failure)"),
    # 573 rev=ACCEPT sa=5 KEY=D - US ag equities: commodity demand + pricing power offset shipping
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "D correctly explains equity resilience despite logistics headwinds"),
    # 574 rev=REVISE sa=3 KEY=A - stochastic model when: limited storage + unpredictable orders
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "A correct but stem could be clearer; limited storage is a secondary factor vs demand uncertainty"),
    # 575 rev=REVISE sa=3 KEY=B - reduce holding cost by enhancing precautionary motive; contradictory
    (3, 2, 2, True, "REVISE", "True", True, False, False, False, True,
     "Contradictory framing: 'enhancing precautionary motive' means holding MORE stock, contradicting 'reduce holding costs'; options confusingly framed"),
    # 576 rev=REVISE sa=3 KEY=D - facility config: 5 plants with equal cap 133 1/3; missing context
    (3, 3, 2, True, "REVISE", "True", True, False, False, False, True,
     "Numerical facility example requires complete setup not fully present in stem; context-dependent"),
    # 577 rev=REVISE sa=4 KEY=C - centralize: large variety + short lead times + high variability
    (4, 3, 3, True, "REVISE", "True", True, True, True, True, False,
     "C combines valid pooling factors; short lead times reduce pooling benefit creating partial conflict"),
    # 578 rev=ACCEPT sa=5 KEY=A - US ag exports: global demand offset shipping costs
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "A correct; well-constructed explanation of agricultural export resilience"),
    # 579 rev=REVISE sa=4 KEY=A - inventory dimensions: supply, demand, operational constraints, perishability
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "A correct per chunk; reviewer flagged revision needed"),
    # 580 rev=REVISE sa=3 KEY=C - newsboy price-dependent: optimal qty ≤ avg forecast; wrong claim
    (3, 3, 3, True, "REVISE", "True", True, False, False, False, True,
     "C's claim that optimal qty ≤ average demand is incorrect in general (y*=mu+z*sigma where z*>0 is common); ambiguous/potentially wrong"),
    # 581 rev=REVISE sa=3 KEY=B - capacity-constrained: exactly one period with fractional production (ZICO)
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B correct (ZICO property: at most one period has fractional production); weak chunk support"),
    # 582 rev=REVISE sa=3 KEY=D - scale curves help optimize facility sizes; Asian Paradigm integration
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "D correct general principle; Asian Paradigm integration adds specificity beyond chunk"),
    # 583 rev=REVISE sa=3 KEY=D - product variety + scale/flexibility tradeoff
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "D correct general principle about variety-scale tradeoff; weak chunk support"),
    # 584 rev=REVISE sa=3 KEY=B - numerical newsboy; missing key demand parameters in stem
    (3, 3, 2, True, "REVISE", "True", True, False, False, False, True,
     "Numerical question missing demand function parameters (a, b); cannot verify KEY=B=$1.25 without complete setup"),
    # 585 rev=REVISE sa=5 KEY=A - US logistics 1984-2007: A=transportation 52%; contradicts item 532
    (5, 3, 3, True, "REVISE", "True", True, False, False, False, True,
     "Contradicts item 532 (which gives compound factor D as answer); specific 52% transportation figure needs source verification"),
    # 586 rev=REVISE sa=3 KEY=C - bullwhip: lead times amplify by 94%; unverifiable specific statistic
    (3, 2, 3, True, "REVISE", "True", True, False, False, True, True,
     "Specific '94%' amplification claim is not verifiable from chunk; likely hallucinated statistic; distractors also contain suspicious specifics"),
    # 587 rev=REVISE sa=3 KEY=B - 5-plant production cutback: technical piecewise-linear model
    (3, 2, 2, True, "REVISE", "True", True, False, False, False, True,
     "Highly technical; requires full piecewise-linear model context; options not fully distinguishable without complete setup"),
    # 588 rev=ACCEPT sa=5 KEY=B - horizontal org: end-to-end processes, flat hierarchies; near-duplicate
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "B correct; near-duplicate of items 535/591/602"),
    # 589 rev=REVISE sa=5 KEY=B - (s,S) reorder point formula; options A and B mathematically equivalent
    (5, 2, 3, True, "REVISE", "True", True, True, False, True, True,
     "Options A and B are mathematically equivalent representations of same reorder point formula; double-correct issue"),
    # 590 rev=ACCEPT sa=5 KEY=A - as pi increases, s* approaches Q*; correct (consistent with item 457)
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "A correct; consistent with item 457 (accepted); s*=pi*Q/(h+pi) increases with pi"),
    # 591 rev=ACCEPT sa=5 KEY=B - horizontal org: end-to-end, flat hierarchies; near-duplicate
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "B correct; near-duplicate of items 535/588"),
    # 592 rev=REVISE sa=4 KEY=B - ZICO: y_t = remaining capacity or remaining demand
    (4, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B correct (ZICO result); reviewer flagged revision needed"),
    # 593 rev=REVISE sa=4 KEY=B - revenue sharing: decreases risk for both parties
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "B correct; revenue sharing aligns incentives for global optimization"),
    # 594 rev=REVISE sa=3 KEY=? - MALFORMED: empty question stem; options are independent questions
    (1, 1, 1, True, "REJECT", "False", False, False, False, False, True,
     "MALFORMED: empty question stem; four options contain independent unrelated questions (EOQ calculation, EPQ definition, backorder definition, EOQ derivation) - not answer choices for a single stem"),
    # 595 rev=ACCEPT sa=5 KEY=A - US ag exports offset by global demand; near-duplicate of 578
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "A correct; near-duplicate of item 578"),
    # 596 rev=REVISE sa=3 KEY=B - scale analysis: identifies cost-effective production volumes
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B correct; weak chunk alignment (sa=3)"),
    # 597 rev=REVISE sa=3 KEY=B - WW vs ZICO: WW allows fractional, ZICO requires 0 or full
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B technically correct distinction (WW=any level, ZICO=0 or C_t for all but one period); weak chunk"),
    # 598 rev=REVISE sa=3 KEY=B - globalization complexity; near-duplicate of 546/569/610
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B correct; near-duplicate of items 546/569/610; weak chunk alignment (sa=3)"),
    # 599 rev=REVISE sa=4 KEY=B - ABC costing: traces activities to specific costs
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "B correctly describes ABC advantage over functional cost centers in revealing true SC costs"),
    # 600 rev=REVISE sa=3 KEY=C - global SC hybrid model: some plants local, others multi-market
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "C plausible hybrid model; weak chunk support for specific hybrid claim"),
    # 601 rev=REVISE sa=3 KEY=C - bullwhip in lean SC: higher pipeline inventories and variation
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "C correct mechanism (bullwhip → longer lead times → higher pipeline inventory); weak chunk"),
    # 602 rev=REVISE sa=4 KEY=B - horizontal org: cross-functional end-to-end; near-duplicate
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "B correct; near-duplicate of items 535/588/591/603"),
    # 603 rev=REVISE sa=4 KEY=C - horizontal org vs functional silos; near-duplicate
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "C correct; near-duplicate of items 535/588/591/602"),
    # 604 rev=REJECT sa=1 KEY=B - carrying costs with specific percentages; hallucinated numbers
    (1, 1, 1, True, "REJECT", "True", False, False, False, False, True,
     "Reviewer correctly REJECTED (sa=1); specific percentage combinations not from source material; all options present arbitrary plausible-sounding but unverifiable numbers"),
    # 605 rev=REVISE sa=3 KEY=B - high variety → dispersed network; potentially contradicts SC theory
    (3, 3, 3, True, "REVISE", "True", True, False, False, False, True,
     "B's claim (high variety → dispersed) is debatable; postponement theory suggests centralization for high variety to maintain flexibility; flag for expert review"),
    # 606 rev=REVISE sa=3 KEY=B - stochastic price higher than deterministic; correct direction
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B correct direction (p*_stoch > p*_det); explanation 'due to increased variability' is incomplete (should reference E[min(z*,eps)]>0)"),
    # 607 rev=REVISE sa=2 KEY=C - MALFORMED: empty question stem; options are independent claims
    (1, 1, 1, True, "REJECT", "False", False, False, False, False, True,
     "MALFORMED: empty question stem; four options contain independent claims about bullwhip, lead times, Little's Law, and demand variability - not answer choices"),
    # 608 rev=REVISE sa=5 KEY=A - SCOR vs GSCF: A correctly distinguishes internal vs inter-firm
    (5, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "A correctly distinguishes SCOR (internal efficiency) from GSCF (inter-firm relationships); helps contextualize item 501 REVISE"),
    # 609 rev=ACCEPT sa=5 KEY=B - complex inventory model: multiple perishable + stochastic + finite
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "B correctly combines multiple complexity dimensions (perishable, stochastic, finite, imperfect supply)"),
    # 610 rev=REVISE sa=2 KEY=B - globalization; near-duplicate of 546/569/598; very weak chunk
    (2, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "Near-duplicate of items 546/569/598; very weak chunk alignment (sa=2)"),
    # 611 rev=ACCEPT sa=5 KEY=A - US ag exporters: demand + pricing power offset costs; near-duplicate
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "A correct; near-duplicate of items 578/595"),
    # 612 rev=REVISE sa=3 KEY=B - ocean freight post-COVID: energy prices + port congestion
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "B correct; weak chunk alignment (sa=3)"),
    # 613 rev=REVISE sa=3 KEY=B - push vs pull: pull=actual orders, push=forecasts
    (3, 3, 3, True, "REVISE", "True", True, True, True, True, False,
     "B correct push/pull distinction; weak chunk alignment (sa=3)"),
    # 614 rev=REVISE sa=3 KEY=D - ZICO: cumulative capacity ≥ cumulative demand (feasibility constraint)
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "D is a feasibility constraint; C (ZIO property) also plausible; weak chunk support"),
    # 615 rev=REVISE sa=3 KEY=D - reduce holding costs: optimize insurance, maintenance, opportunity cost
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "D correctly targets carrying cost components (insurance, maintenance, opportunity cost) directly"),
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
print(f"Batch 12 written: {len(decisions)} items")
print(f"  ACCEPT: {accept}")
print(f"  REJECT: {reject}")
print(f"  REVISE: {revise}")
