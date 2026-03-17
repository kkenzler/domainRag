"""Generate batch010.json — Claude review decisions for items 451-500."""
import json
from pathlib import Path

INPUT = Path("claude_review_input.json")
OUTPUT = Path("batch010.json")
BASE_OFFSET = 450

with open(INPUT, encoding="utf-8") as f:
    items = json.load(f)

# (align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag, notes)
RAW = [
    # 451 rev=REVISE sa=5 KEY=A - strategic sourcing cost factors; options A and B both chunk-sourced
    (4, 3, 3, True, "REVISE", "True", True, True, False, True, False,
     "Options A and B both enumerate cost drivers from same chunk; stem needs discriminating language"),
    # 452 rev=REVISE sa=4 KEY=D - four steps; stem says 'combination' but options are singular steps
    (4, 4, 3, True, "REVISE", "True", True, True, True, True, False,
     "Stem asks for combination but options list individual steps; D correctly identifies first step"),
    # 453 rev=REVISE sa=3 KEY=C - EOQ backorder extreme pi>>h; chunk covers basic EOQ not extremes
    (3, 3, 4, True, "REVISE", "True", True, True, True, False, False,
     "Theoretically correct (Q*=s*=sqrt(2DK/h) when pi>>h) but chunk covers basic EOQ, not backorder extremes"),
    # 454 rev=REVISE sa=3 KEY=B - dispersed for high uncertainty; possibly contradicts risk-pooling logic
    (3, 3, 3, True, "REVISE", "True", True, False, False, True, True,
     "KEY=B (dispersed) for high demand uncertainty may contradict risk-pooling principle (centralized typically preferred); flag for expert review"),
    # 455 rev=REVISE sa=4 KEY=B - agricultural exporters; increased demand offset shipping costs
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "Well-constructed; REVISE for minor stem clarity"),
    # 456 rev=REVISE sa=4 KEY=A - strategic sourcing; near-duplicate of item 451
    (4, 3, 3, True, "REVISE", "True", True, True, True, True, False,
     "Near-duplicate of item 451; stem wording nearly identical"),
    # 457 rev=ACCEPT sa=5 KEY=B - s* approaches Q* as pi increases; technically sound
    (5, 4, 5, True, "ACCEPT", "True", True, True, True, True, False,
     "Technically sound; correctly describes backorder limit behavior as pi increases"),
    # 458 rev=REVISE sa=4 KEY=B - Xerox benchmarking; competitive vs internal metrics
    (4, 4, 4, True, "REVISE", "True", True, True, True, True, False,
     "Correct distinction; minor stem clarity issue noted by reviewer"),
    # 459 rev=REVISE sa=3 KEY=B - bullwhip with decentralized info; information distortion is correct cause
    (3, 3, 4, True, "REVISE", "True", True, True, True, False, False,
     "B correctly identifies information distortion; sa=3 reflects partial chunk mismatch"),
    # 460 rev=REVISE sa=3 KEY=D - capacity-constrained Wagner-Whitin; D describes correct production rule
    (3, 3, 3, True, "REVISE", "True", True, True, True, False, False,
     "Capacity-constrained WW; D plausible but chunk only partially covers this extension"),
    # 461 rev=ACCEPT sa=5 KEY=C - SC strategy alignment; balances service, product, transport, customization
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Good integration of SC strategy factors; C correctly balances all dimensions"),
    # 462 rev=REVISE sa=3 KEY=B - (s,S) formula; options B and D appear identical in truncated view
    (3, 2, 2, True, "REVISE", "True", True, True, False, False, True,
     "Options B and D appear to share identical formula text - likely double-correct; distractors need differentiation"),
    # 463 rev=ACCEPT sa=5 KEY=D - rising logistics costs; D correctly captures systemic impact
    (5, 4, 4, True, "ACCEPT", "True", True, True, True, True, False,
     "Well-constructed survey question; D comprehensively covers systemic logistics cost impact"),
    # 464 rev=REVISE sa=3 KEY=B - WRONG KEY: s* should INCREASE as pi increases (confirmed by item 457)
    (2, 2, 4, True, "REJECT", "False", True, False, True, False, True,
     "WRONG KEY: B states s* decreases as pi increases; item 457 (accepted) confirms s* increases toward Q* as pi rises; s*=h*Q*/(h+pi) formula confirms s* increases with pi"),
    # 465 rev=ACCEPT sa=5 KEY=C - push vs pull; C is textbook definition
    (5, 4, 5, True, "ACCEPT", "True", True, True, True, True, False,
     "Textbook definition of push vs pull; C correctly contrasts forecast-driven vs demand-driven"),
    # 466 rev=ACCEPT sa=5 KEY=A - additive demand g(p)=a-bp; easy formula recall
    (5, 4, 5, False, "ACCEPT", "True", True, True, True, True, False,
     "Direct formula recall with clean distractors"),
    # 467 rev=REVISE sa=5 KEY=A - j(l) context-dependent notation; stem needs definition
    (5, 3, 2, False, "REVISE", "True", True, True, True, True, False,
     "Too context-dependent without j(l) defined in stem; requires knowledge of specific optimization notation"),
    # 468 rev=ACCEPT sa=5 KEY=B - step 1 of SC strategy development; correct
    (5, 4, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Solid recall question; B correctly identifies first step of SC strategy development"),
    # 469 rev=ACCEPT sa=5 KEY=C - deterministic price lower than stochastic; mathematically correct
    (5, 4, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Correct: p*_det=(a+bc)/(2b) < p*_stoch=(a+bc+E[min(z*,eps)])/(2b) since E[min(z*,eps)]>0"),
    # 470 rev=ACCEPT sa=5 KEY=B - stochastic optimal price formula; correct (matches item 445 correct answer)
    (5, 4, 5, False, "ACCEPT", "True", True, True, True, True, False,
     "Correct formula p*=(a+bc+E[min(z*,eps)])/(2b); consistent with additive demand model derivation"),
    # 471 rev=ACCEPT sa=5 KEY=A - inventory = cumulative supply-demand difference
    (5, 4, 5, False, "ACCEPT", "True", True, True, True, True, False,
     "Classic definitional question; A is the standard definition"),
    # 472 rev=ACCEPT sa=5 KEY=B - small demand changes amplify upstream (bullwhip)
    (5, 4, 5, False, "ACCEPT", "True", True, True, True, True, False,
     "Standard bullwhip description; B correctly describes amplification phenomenon"),
    # 473 rev=ACCEPT sa=5 KEY=B - 2021 shipping rates from port congestion + reduced capacity
    (5, 4, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Well-grounded in real-world context from source material"),
    # 474 rev=REVISE sa=5 KEY=B - bullwhip; D also correct (both describe same phenomenon)
    (5, 3, 4, False, "REVISE", "True", True, True, False, True, False,
     "Near-duplicate of items 472/478; option D also correctly describes bullwhip phenomenon"),
    # 475 rev=ACCEPT sa=5 KEY=A - Wagner-Whitin minimizes total cost balancing ordering and holding
    (5, 4, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Accurate characterization; B/C/D are clearly wrong"),
    # 476 rev=ACCEPT sa=5 KEY=B - strategic motive for inventory = market presence
    (5, 3, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Correctly identifies strategic (not operational) motive; distractors are operational reasons"),
    # 477 rev=REVISE sa=3 KEY=A - WRONG KEY: A describes C2 (export cost), not C1 (local distribution)
    (2, 2, 3, False, "REJECT", "False", True, False, True, False, True,
     "WRONG KEY: A says C1=cost to markets OTHER than where produced, but items 481/487 confirm C1=local distribution within same market; A describes C2 (export cost)"),
    # 478 rev=ACCEPT sa=5 KEY=B - bullwhip = order sizes increase upstream; D also correct
    (5, 3, 4, False, "REVISE", "True", True, True, False, True, False,
     "B correct; option D also correctly describes bullwhip (both depict same phenomenon from different angles)"),
    # 479 rev=REVISE sa=3 KEY=A - NOT reason for dispersed: scale economies favor centralized
    (3, 3, 3, False, "REVISE", "True", True, True, True, False, False,
     "Negative stem (NOT); A correctly excluded since scale economies favor centralized; weak chunk alignment"),
    # 480 rev=REVISE sa=3 KEY=C - functional silos barrier to SC integration; correct but weak chunk
    (3, 3, 4, False, "REVISE", "True", True, True, True, False, False,
     "C correctly identifies barrier; sa=3 reflects weak chunk support"),
    # 481 rev=ACCEPT sa=5 KEY=B - C1 = within same market distribution cost; correct
    (5, 4, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Correct C1 definition (local distribution within same market)"),
    # 482 rev=ACCEPT sa=5 KEY=C - inventory carrying costs: insurance, maintenance, opportunity cost
    (5, 4, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Standard carrying cost components; C correct"),
    # 483 rev=REVISE sa=2 KEY=D - NOT carrying cost: transportation; correct exclusion, weak chunk
    (2, 3, 4, False, "REVISE", "True", True, True, True, False, False,
     "D correctly excluded (transportation is ordering cost not carrying); sa=2 reflects weak chunk"),
    # 484 rev=REVISE sa=5 KEY=B - SCM aims to maximize value through integrated processes
    (5, 3, 3, False, "REVISE", "True", True, True, True, True, False,
     "Correct; A is partially valid (cost minimization is also a SCM goal); distractors not clearly wrong"),
    # 485 rev=REVISE sa=5 KEY=C - bullwhip; near-duplicate; D partially correct
    (5, 3, 3, False, "REVISE", "True", True, True, False, True, False,
     "Near-duplicate bullwhip item; D partially correct (longer lead times do amplify bullwhip)"),
    # 486 rev=REVISE sa=3 KEY=B - shortage costs = lost demand when stockout; correct but weak chunk
    (3, 3, 4, False, "REVISE", "True", True, True, True, False, False,
     "Correct definition; weak chunk alignment (sa=3)"),
    # 487 rev=ACCEPT sa=5 KEY=B - C1 = within same market; duplicate of 481
    (5, 4, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Correct C1 definition; duplicate of item 481"),
    # 488 rev=ACCEPT sa=5 KEY=A - development vs fulfillment SC distinction; A is correct
    (5, 4, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Correct strategic distinction between development and fulfillment supply chains"),
    # 489 rev=REVISE sa=3 KEY=C - bullwhip primary contributor; B and C both valid causes
    (3, 3, 3, False, "REVISE", "True", True, True, False, False, False,
     "Options B (moving average amplification) and C (safety stock adjustments) are both valid bullwhip causes; ambiguity about which is primary"),
    # 490 rev=ACCEPT sa=5 KEY=A - l1 determination in multi-period production
    (5, 3, 3, False, "ACCEPT", "True", True, True, True, True, False,
     "Technically correct algorithm description; difficult stem but chunk-supported"),
    # 491 rev=REVISE sa=5 KEY=B - raw material costs as sourcing driver; correct but distractors weak
    (5, 4, 3, False, "REVISE", "True", True, True, True, True, False,
     "Correct; distractors A/C/D clearly irrelevant but could be strengthened"),
    # 492 rev=REVISE sa=2 KEY=B - functional org relay-race handoffs; correct but weak chunk
    (2, 3, 4, False, "REVISE", "True", True, True, True, False, False,
     "B correctly describes sequential handoff; sa=2 reflects weak chunk match"),
    # 493 rev=ACCEPT sa=5 KEY=B - physical and information flow as SC links
    (5, 4, 5, False, "ACCEPT", "True", True, True, True, True, False,
     "Classic SCM definition; well-constructed"),
    # 494 rev=ACCEPT sa=5 KEY=B - pull more responsive than push
    (5, 4, 5, False, "ACCEPT", "True", True, True, True, True, False,
     "Straightforward correct; B clearly distinguishes pull responsiveness"),
    # 495 rev=REVISE sa=3 KEY=B - push = forecast-based; C also true (push is less responsive)
    (3, 3, 3, False, "REVISE", "True", True, True, False, False, False,
     "B correct definition; C ('less responsive') is also true of push - ambiguous distractor"),
    # 496 rev=ACCEPT sa=5 KEY=B - SCM focus: minimize total system cost while achieving service
    (5, 4, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Textbook SCM definition; B correctly balances cost and service"),
    # 497 rev=REVISE sa=3 KEY=D - WW solvable as O(T²) shortest path; correct but chunk is capacity WW
    (3, 3, 4, False, "REVISE", "True", True, True, True, False, False,
     "D technically correct (WW=shortest path O(T²)); chunk covers capacity-constrained version, not unconstrained WW"),
    # 498 rev=ACCEPT sa=5 KEY=C - functional silos barrier; duplicate of 480 with better chunk
    (5, 4, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Correct; better chunk alignment than item 480"),
    # 499 rev=ACCEPT sa=5 KEY=C - global SC: balance scale economies vs transport/duties
    (5, 4, 4, False, "ACCEPT", "True", True, True, True, True, False,
     "Well-constructed global strategy question; C correctly balances tradeoffs"),
    # 500 rev=REVISE sa=3 KEY=A - deterministic newsboy p*=(a+bc)/(2b); correct formula, weak chunk
    (3, 3, 4, False, "REVISE", "True", True, True, True, False, False,
     "Correct formula; weak chunk support (sa=3)"),
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
print(f"Batch 10 written: {len(decisions)} items")
print(f"  ACCEPT: {accept}")
print(f"  REJECT: {reject}")
print(f"  REVISE: {revise}")
