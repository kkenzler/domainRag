"""Generate batch002.json — Claude review decisions for items 51-100."""
import json
from pathlib import Path

INPUT = Path("claude_review_input.json")
OUTPUT = Path("batch002.json")

with open(INPUT, encoding="utf-8") as f:
    items = json.load(f)

# (align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag, notes)
RAW = [
    # 51
    (3,1,5,False,"REVISE","Partial",True,True,True,False,False,
     "Three of four distractors (A: company logo color, C: CEO vacation spot, D: brand of office computers) are joke answers with zero plausibility. Same distractor quality failure as Items 43 and 98. Replace with substantive wrong supply chain considerations. Reviewer align=1 understates -- chunk 2 (dist=0.54) directly mentions transportation costs as a network design factor."),
    # 52
    (3,4,4,True,"REJECT","False",False,False,False,False,False,
     "CRITICAL: Wrong correct key. The chunk explicitly states development SC focuses on 'product architecture decisions' and fulfillment SC 'manages demand variability' -- which precisely matches option A, not option B. Option B (strategic partnerships during planning / offshoring vs onshoring) does not match the chunk. Reviewer gave align=5 and ACCEPT -- reviewer_source_call_accurate=False. Correct key should be A."),
    # 53
    (5,4,5,True,"ACCEPT","True",True,True,True,True,False,
     "Clean item. Distractors A (butterfly effect), C (ripple effect), D (domino effect) are all real cascade-effect terms making this a genuine test of whether students know the specific supply chain terminology. Well-constructed."),
    # 54
    (4,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Fact-recall with specific numeric answer (19%). Distractors use plausible numbers -- notably 30% is the overall improvement rate making it a good near-miss trap. Full chunk presumably contains the 19% figure for top management emphasis attribution."),
    # 55
    (5,3,5,True,"REVISE","Partial",True,True,True,True,False,
     "Distractors A (solely domestic markets), B (ignoring regional presence), D (avoiding flexibility) all describe obviously bad strategies that any business student would reject. Reviewer ACCEPT noted dist=4 but I rate dist=3 since B and D are too obviously wrong (directly contradicted by the chunk). Replace B and D with plausible but wrong global SC considerations."),
    # 56
    (4,4,4,True,"REVISE","Partial",True,True,True,True,True,
     "Third version of the dynamic lot sizing feasibility condition question (Items 7, 21, 56). This version has the best distractor set -- D (total production capacity over all periods >= total demand) is the best near-miss: necessary but not sufficient since the actual condition requires cumulative capacity at each period i. The capacity-vs-production-quantity wording issue persists in option A. Consider keeping this version over Items 7 and 21."),
    # 57
    (2,4,4,False,"REVISE","True",False,False,False,True,False,
     "Transaction motive for inventory holding is a specific inventory theory term. The chunk discusses inventory as cumulative supply-demand difference but does not define holding motives. The marked correct answer A (maintain market presence through competitive positioning) does not align with standard transaction motive definition (regular order fulfillment to smooth operations between supply and demand). Source alignment is insufficient."),
    # 58
    (2,3,4,False,"REVISE","True",False,False,False,True,True,
     "Near-duplicate of Item 49 (same question about why companies treat demand as predictable). Item 58 has more plausible distractors (perfect forecasting techniques, reduce production costs). The core issue persists: chunk states the BEHAVIOR but not the REASON. Deduplicate; keep Item 58 version for better distractors. Both need a source chunk that explicitly states the reason."),
    # 59
    (3,3,4,False,"REJECT","True",False,True,True,True,False,
     "REJECT: Fifth near-duplicate COMS question (Items 17, 18, 33, 42, 59). Top chunk (dist=0) is a logistics scorecard framework completely unrelated to COMS. COMS chunk at dist=0.668. Generator repeatedly retrieved and generated from the same COMS chunk. Keep Item 18; reject all others."),
    # 60
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "Not a strict duplicate of Item 53 (53 asks for the term name, 60 asks for the definition). Distractor B (customer demand remains stable) is actually the CONTRAST -- customer demand IS relatively stable while upstream orders amplify, making B an interesting educational wrong answer. Distractor D (reduction in inventory costs) is completely unrelated and easily eliminated. Replace D with a more adjacent wrong definition."),
    # 61
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "Source chunk defines s verbatim. Distractor B (minimum inventory level) is the direct opposite of s -- too easily eliminable. Better distractor: 'the order quantity Q minus the maximum backorder quantity' (since Q-s IS the maximum backorder quantity per the chunk). Distractor C (order quantity per cycle) is appropriately adjacent."),
    # 62
    (3,4,5,True,"REVISE","Partial",False,False,False,False,False,
     "Physical flow and information flow as the two linking mechanisms are standard SCM theory, but retrieved chunks discuss decision levels (strategic/tactical/operational) not flow mechanisms. Reviewer align=5 seems too high given the chunk mismatch. Needs a chunk specifically about supply chain flows. Distractor A (financial flow + information) is good -- financial flow is a real but third mechanism."),
    # 63
    (5,3,4,True,"REVISE","True",True,True,True,True,False,
     "Distractors A (minimizing costs only), B (achieving high service levels only), D (solely manufacturing efficiency) all use singular focus qualifiers (only/solely) telegraphing that the correct answer must involve balance. Replace distractors with real but wrong SCM priorities that don't use 'only/solely' qualifiers."),
    # 64
    (4,4,5,True,"ACCEPT","True",True,True,True,True,False,
     "Clean definitional item. The relevant chunk is at dist=0.608 (not the top chunk which discusses company examples). Distractors B and C test whether students confuse inventory with total supply or total demand -- reasonable near-miss traps. Well-constructed."),
    # 65
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Well-constructed. Chunk explicitly confirms variable ordering cost c_t per unit (matching A). Distractor B (objective excludes holding costs) is a good trap requiring knowledge of the full objective function. Distractor D (cannot be solved efficiently) is false -- WW has polynomial-time algorithms. Clean item."),
    # 66
    (4,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "Multi-step optimization algorithm question. All four options describe real algorithmic steps requiring careful reading to identify which step calculates l*. Good medium-difficulty question testing procedural knowledge of the M-plant optimization algorithm."),
    # 67
    (3,2,4,False,"REVISE","True",False,False,False,True,False,
     "NOT question where correct answer D (increased SKUs) would worsen inventory management -- consistent with general knowledge. Distractor C (reduction in SKU proliferation) is an excellent near-miss. However the full list of contributing factors is in the truncated chunk. Reviewer correctly flagged WRONG_DISTRACTORS -- there may be factors in the chunk not represented in the distractors."),
    # 68
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Better version of development vs fulfillment SC question (compare Items 24, 52, 68). Option B correctly identifies product architecture and strategic partnerships for dev SC, and demand variability and lead time management for fulfillment. Distractor D (concepts reversed) is an excellent near-miss trap. Well-constructed."),
    # 69
    (3,4,4,False,"REVISE","True",False,False,False,True,True,
     "Correct answer B (influence of lead times on SC strategy) is questionable -- lead times ARE explicitly incorporated into inventory models as key parameters. The more clearly not-addressed option would be D (globalization trends on demand patterns) which is a strategic/environmental factor outside classical inventory model scope. Possible wrong answer key -- flag for review."),
    # 70
    (3,3,4,False,"REJECT","True",False,True,True,True,False,
     "REJECT: Sixth near-duplicate COMS question (Items 17, 18, 33, 42, 59, 70). Top chunk (dist=0) is logistics scorecard framework unrelated to COMS. This level of duplication (6x) severely inflates the dataset. Generator was stuck in a loop on the COMS chunk. Keep Item 18; reject all others."),
    # 71
    (3,4,4,False,"REVISE","True",False,False,False,True,False,
     "EOQ is in the source chunks but EPQ (Economic Production Quantity) may not be. The EOQ-EPQ distinction (instantaneous vs gradual replenishment with production rate P) is a legitimate medium-difficulty question but needs source chunks covering both models. Distractor A (EOQ production rate exceeds demand) incorrectly implies EOQ has a production rate rather than instantaneous delivery."),
    # 72
    (4,4,3,False,"REVISE","Partial",True,True,False,False,False,
     "Chunk 2 (dist=0.429) directly states the bullwhip variability product formula matching option C. Reviewer align=3 understates alignment -- reviewer_source_call_accurate=False. Main issues: (1) the stem asks for minimum increase matching the lower bound interpretation but this nuance is important, (2) difficulty should be hard not medium for a formula recognition question requiring all three per-stage terms."),
    # 73
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "Good medium-difficulty question. Distractor D (centralized sharing eliminates bullwhip entirely) is a good near-miss -- centralized information significantly reduces but typically cannot eliminate bullwhip. B is well-supported by the compounding formula in chunk 2."),
    # 74
    (3,4,2,False,"REVISE","True",True,False,False,True,False,
     "Confusing stem: how bullwhip manifests specifically with moving average forecasting should target the MA-specific mechanism not the general bullwhip. B describes bullwhip generally. Distractor D has the causal direction completely reversed: increasing L worsens bullwhip; the stem says it is mitigated by increasing L which is wrong. Distractor D should be flagged as containing a factual error that could mislead students."),
    # 75
    (5,2,4,False,"REVISE","True",True,True,True,True,False,
     "Distractors A, B, D directly contradict explicit chunk statements (pace of change INCREASED; customers RAISED expectations; M&A INTENSIFIED competition). These are trivially eliminated by anyone who read the source. Replace with plausible 21st century challenges that are real but not the correct answer."),
    # 76
    (4,4,2,False,"REVISE","True",True,True,False,True,False,
     "Multi-model question asking about both Wagner-Whitin AND its capacity-constrained extension (ZICO). Stem lacks clarity about which feature applies to which model. Correct answer D (production at full capacity or zero) describes the ZICO production property but is incomplete (ZICO also has inventory=0 or production=0 conditions). Distractor B (ZIO: order when inventory=0) is a good trap for students confusing ZIO and ZICO. Simplify to one model per question."),
    # 77
    (5,4,4,False,"REVISE","Partial",True,True,False,False,False,
     "Chunks directly support B. Reviewer align=3 understates -- both chunks provide direct evidence for decentralized vs centralized bullwhip comparison. Distractor A is a good trap: it describes the centralized advantage (each stage has actual demand) but incorrectly attributes it to decentralized. The comparison to centralized is implicit since no centralized system chunk is retrieved. REVISE only for difficulty label -- should be medium not hard."),
    # 78
    (4,4,4,False,"ACCEPT","Partial",True,True,True,False,False,
     "Valid NOT question. Customer satisfaction metrics (A) are performance outcomes not cost parameters that drive sourcing decisions. B, C, D are legitimate strategic sourcing cost drivers per the source. Reviewer underestimated alignment (gave 3; chunk explicitly discusses cost minimization drivers). Distractor D (variable manufacturing costs by process and site) is well-placed as it mirrors specific sourcing cost analysis terminology."),
    # 79
    (4,3,4,True,"REVISE","True",True,True,False,True,False,
     "Option B (shortage cost pi and holding cost h) is correct -- s* = h/(pi+h) × Q* so s* depends on the ratio of h to pi. Distractors A, C, D describe factors that determine Q* not specifically s* -- students who know Q* formula but confuse it with s* would be trapped. Distractor quality is moderate; could add a distractor specifically about s* (e.g., demand rate and lead time)."),
    # 80
    (4,3,5,True,"REVISE","True",True,True,True,True,True,
     "Near-duplicate of Item 15 (easy) and Item 86 (medium) -- same question about ocean freight 2021 NOT contributor, same correct answer D, similar chunks. Medium difficulty label unexplained given identical content. Deduplicate: keep one version."),
    # 81
    (3,4,4,False,"REVISE","True",False,False,True,True,False,
     "Chunk discusses functional silos and sub-optimization but not specifically traditional accounting systems failing to reveal hidden costs. Correct answer B is a valid supply chain insight but isn't directly in the retrieved chunks. Distractors A (accurate tracking -- directly wrong) and D (operational vs strategic) are appropriately wrong but B needs a cost-accounting-specific chunk."),
    # 82
    (3,3,4,False,"REVISE","False",True,False,False,False,False,
     "Reviewer REJECT seems too harsh -- chunk 2 (dist=0.559) covers the base WW model. However correct answer A has imprecise wording: 'balancing production levels with inventory holding costs' should be 'ordering costs and inventory holding costs.' Additionally distractor D (shortest path O(T2)) is actually CORRECT -- WW can be solved in O(T2) -- creating a second potentially correct answer. REVISE rather than REJECT."),
    # 83
    (5,4,2,False,"REVISE","Partial",True,True,False,False,False,
     "Chunk 2 directly states the ZICO condition matching B. Reviewer align=3 understates. Main issues: (1) very long option text makes clarity=2, (2) related to Items 45 and 47 but with better pedagogical distractors (A=ZIO vs B=ZICO is the key distinction, C=WW model, D=(s,S) policy). Consider condensing option text for clarity."),
    # 84
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "Related to Item 14 (same pi-s* relationship, different framing). Item 14 asked about asymptotic behavior; Item 84 asks about directional relationship. Complementary questions. Distractor A (s* decreases as pi increases) is an excellent near-miss. Distractor D (s* approaches Q* as pi DECREASES) has the right asymptote but wrong direction. Well-constructed."),
    # 85
    (3,2,3,True,"REVISE","True",False,False,False,True,False,
     "Reviewer correctly identified that distractors C and D use (b-1) denominator terms characteristic of the multiplicative demand model (power demand) not the additive model. These are implausible alternatives for students familiar with the model structure. Correct answer B may not be directly verifiable from chunk preview. Needs formula derivation in retrieved chunk."),
    # 86
    (3,4,3,False,"REJECT","Partial",True,True,True,True,True,
     "REJECT: Third version of ocean freight NOT contributor question (Items 15, 80, 86). Content is essentially identical across all three. Top chunk for this version (agricultural equity prices) differs from Items 15/80 (agricultural export levels). Deduplicate: keep Item 15 which has the clearest chunk alignment."),
    # 87
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Excellent item. Chunk directly states centralization benefits are maximized with high demand variability and NEGATIVE correlation -- matching B exactly. Distractor A (positive correlation) is a sophisticated trap: high variability sounds sufficient but positive correlation reduces the pooling benefit since demands fluctuate in the same direction. Well-constructed."),
    # 88
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Good question where the correct answer is the nuanced it-depends. Tests metacognitive understanding that supply chain network decisions are context-specific. Distractor C (hybrid network) is a plausible wrong answer for students who want a definitive choice. Chunk directly supports D."),
    # 89
    (4,3,4,True,"REVISE","True",True,False,False,True,False,
     "Core competencies rationale for outsourcing is a valid SCM inference but may not be verbatim in the chunk (which shows outsourcing trend data). Distractor A (expanding internal production) is directly contrary to the outsourcing trend -- trivially eliminable. Better distractors: B (outsourcing marketing/sales) is adjacent but wrong. Needs more nuanced wrong alternatives."),
    # 90
    (3,4,5,True,"REVISE","Partial",False,False,True,True,True,
     "Near-duplicate of Item 81 (same accounting challenge question, better distractors). This version has clearer distractors (A directly contradicts itself). However the source chunks discuss functional silos not accounting practices -- partial alignment for both Items 81 and 90. Deduplicate: keep Item 90 for better distractor quality."),
    # 91
    (4,2,4,False,"REVISE","True",True,False,True,True,False,
     "B (agility and responsiveness) is partially supported by chunk mentioning increased pace of change and volatile markets. Distractors C (focus only on internal processes) and D (maintain traditional structures) are obviously bad practices any student would eliminate. Replace C and D with more plausible wrong challenges. Related to Item 75 but distinct enough to keep if distractors are improved."),
    # 92
    (5,4,5,True,"ACCEPT","True",True,True,True,True,False,
     "Applied scenario question. Chunk directly describes the exact scenario (stable customer demand, amplifying upstream orders). Distractors B, C, D are plausible alternative diagnoses testing whether the student correctly identifies the systemic phenomenon vs blaming individual components. Well-constructed."),
    # 93
    (4,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "Related to Item 66 but asking HOW to determine the cutback count while 66 asked which step calculates l*. Complementary questions from same algorithm. Distractors C and D (lowest capacity cutback, equal cutback above demand) represent naive heuristics a student might attempt without knowing the cost-multiplier ranking approach."),
    # 94
    (5,4,5,True,"ACCEPT","True",True,True,True,True,False,
     "Clean item. Chunk explicitly defines operational decisions as scheduling, monitoring, controlling, and adjusting -- verbatim match. Distractor D (logistics decisions) tests whether students know the three-level SCM framework (strategic/tactical/operational)."),
    # 95
    (2,3,4,False,"REVISE","True",False,False,False,True,False,
     "POSSIBLE WRONG CORRECT KEY: Option B (integrating mechanism for cross-functional teams aligning with order fulfillment) describes COMS (per chunk 2 at dist=0.668) not the Logistics Scorecard Framework. The Scorecard Framework (per top chunk) translates benchmarking insights into actionable KPIs -- that is closer to a performance measurement tool. The question may have confused COMS functionality with Scorecard Framework functionality."),
    # 96
    (4,1,4,True,"REVISE","True",True,True,True,True,False,
     "Distractor quality is the lowest possible: C (color scheme of supply chain diagram) and D (brand of computers) are joke answers. Third instance of joke distractors across this batch (Items 43, 51, 96, 98). Replace C and D with substantive wrong network design considerations (e.g., number of products, warehouse automation level)."),
    # 97
    (3,4,4,False,"REVISE","False",True,False,False,False,False,
     "The backorder EOQ formula (B: sqrt(2DK/h) * sqrt((pi+h)/pi)) is the standard textbook formula. Reviewer REJECT based on context_missing may be too harsh if the formula is derivable from chunk cost structure. Distractors A (basic EOQ), C/D (wrong adjustment operations) are pedagogically sound. REVISE rather than REJECT; verify formula presence in full chunk. Disagree with reviewer's REJECT."),
    # 98
    (5,1,5,True,"REVISE","Partial",True,True,True,False,False,
     "REVISE: Three of four distractors (A: company logo color, B: marketing department employee count, D: CEO favorite vacation spot) are joke answers. Fourth instance of this distractor pattern (Items 43, 51, 96, 98). Reviewer accepted dist=4 as reasonable which is egregiously wrong -- reviewer_source_call_accurate=False for distractor assessment. Replace with substantive wrong considerations."),
    # 99
    (5,3,3,True,"REVISE","True",True,True,True,True,False,
     "Chunk directly supports B. Distractor A (focusing solely on internal metrics) describes what benchmarking SHIFTS AWAY from per the chunk -- an interesting educational near-miss. C (no impact) and D (avoid benchmarking) are too obviously wrong. Stem clarity=3: 'how can benchmarking influence' is vague -- rephrase to 'which best describes the benefit of benchmarking for SCM approach?'"),
    # 100
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Excellent item. The based-on-Little-Law qualifier correctly frames the question. Distractor A (increasing inventory) is a sophisticated trap -- students might think buffer stock helps but it worsens lead times per Little's Law (I = D x L). Verbatim source match for C. Well-constructed."),
]

decisions = []
for idx, raw in enumerate(RAW):
    item_idx = 50 + idx  # items 51-100 are 0-indexed as 50-99
    item = items[item_idx]
    align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag, notes = raw
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

from collections import Counter
decisions_count = Counter(d["claude_decision"] for d in decisions)
print(f"Batch 2 written: {len(decisions)} items")
for k, v in sorted(decisions_count.items()):
    print(f"  {k}: {v}")
