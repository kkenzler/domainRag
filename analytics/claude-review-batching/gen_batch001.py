"""Generate batch001.json — Claude review decisions for items 1-50."""
import json
from pathlib import Path

INPUT = Path("claude_review_input.json")
OUTPUT = Path("batch001.json")

with open(INPUT, encoding="utf-8") as f:
    items = json.load(f)

# (align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag_ambiguity, notes)
RAW = [
    # 1
    (3,3,4,False,"REVISE","True",True,False,False,True,False,
     "Dual ambiguity: both A (perfect information) and D (stable everyday low pricing) could be argued as not contributing to bullwhip. EDLP is a known bullwhip remedy making D also potentially correct. Rewrite for single unambiguous answer. Chunks do not explicitly confirm A as the sole non-contributor."),
    # 2
    (4,1,5,False,"REJECT","Partial",True,True,False,True,False,
     "CRITICAL: Options B and C (sqrt(2DK/h) vs sqrt(2KD/h)) are mathematically identical since multiplication is commutative. Two correct answers. Complete rewrite required with genuinely distinct options. Reviewer said REVISE; I say REJECT. Easy difficulty also questionable for formula identification."),
    # 3
    (5,4,5,True,"ACCEPT","True",True,True,True,True,False,
     "Clean item. Source directly states both components of s. Distractor A is a good near-miss as it IS the other component of s just not the uncertainty-accounting element."),
    # 4
    (5,4,3,True,"REVISE","Partial",True,True,True,True,False,
     "Citation artifact [1] in question stem is a bibliographic reference leaked from the source document. Must be removed for student-facing use. Reviewer did not flag this. Otherwise strong item with verbatim source support. Artifact suggests ingest/chunking pipeline fix needed to strip inline citations."),
    # 5
    (5,3,4,True,"REVISE","True",True,True,True,True,False,
     "Correct answer well-supported. Distractors are straw-man statements (always equal to forecast / guarantee higher profits / predicted with certainty) that no supply chain student would choose. Needs more plausible alternatives representing common misconceptions."),
    # 6
    (5,2,4,False,"REVISE","True",True,True,True,True,False,
     "Distractors A, B, D describe desirable supply chain attributes (solutions to the integration problem not barriers). Correct answer is obvious by elimination. Replace with plausible barriers such as inadequate IT systems or misaligned incentive structures."),
    # 7
    (4,4,4,True,"REVISE","Partial",True,True,True,True,True,
     "Minor but meaningful wording mismatch: chunk states cumulative CAPACITY as the feasibility condition but option A says cumulative PRODUCTION QUANTITY. Capacity is the maximum possible production (determines existence); production quantity is the actual plan for a specific solution. Correct wording to match source precisely."),
    # 8
    (5,4,5,True,"ACCEPT","True",True,True,True,True,False,
     "Clean item. Chunk directly states the bidirectional relationship. Distractor A (inverse relationship) is an excellent trap."),
    # 9
    (4,2,4,False,"REVISE","Partial",True,True,True,False,False,
     "Reviewer flagged SOURCE_ALIGNMENT_VAGUE (align=3) but chunk 3 (dist=0.582) directly contains the textbook SCM definition matching option C verbatim -- reviewer_source_call_accurate=False. Real issue is distractor quality: options A/B/D are implausibly wrong and instantly eliminable without supply chain knowledge."),
    # 10
    (5,4,3,True,"REVISE","Partial",True,True,True,True,False,
     "correct_key=A|B -- both options are correct ZIO descriptions. Mathematical condition (A) and conceptual interpretation (B) are both in the source chunk. Single-select MCQ cannot accommodate two correct answers. Merge A+B or use select-all-that-apply or specify notation. Compare Item 34 which properly uses all-of-the-above."),
    # 11
    (2,4,4,False,"REVISE","True",False,False,True,True,True,
     "Numerical computation question -- chunks provide EOQ cost structure but not this specific calculation. By calculation: C* = cD + sqrt(2DKh) = 30 + 44.72 = ~$74.72 not $78 (option B). Flag for arithmetic verification; cannot confirm correct answer from source chunks."),
    # 12
    (3,3,4,True,"REVISE","True",False,False,False,True,False,
     "Option B's specific content (production disruptions, supplier failures, transportation delays) is absent from retrieved chunks which focus on optimization complexity. Distractor A confusingly frames sequential optimization (a problem per the text) as if it were a challenge to embrace. Needs disruptions-focused chunk."),
    # 13
    (3,4,4,True,"REVISE","Partial",False,False,False,False,False,
     "Correct answer D (machinery industry remained stable) is not present in retrieved chunks which only show data for computer/telecom, food manufacturing, and telecom. Reviewer gave align=5 despite machinery data absence -- reviewer_source_call_accurate=False. Distractor C is a good trap (uses real numbers but wrong industry pairing). Needs machinery-specific chunk to verify D."),
    # 14
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean item. Distractor A is particularly well-crafted -- it describes the actual behavior of s* as pi approaches 0 (not infinity), creating a sophisticated confusion. Good medium-difficulty question."),
    # 15
    (4,4,4,True,"ACCEPT","True",True,True,True,True,False,
     "Solid item. Distractor analysis requires close reading: D (decreased agricultural demand) is refuted by chunk 1 showing no effect on U.S. maritime agricultural exports. A and B directly supported by chunk 2."),
    # 16
    (5,4,5,True,"ACCEPT","True",True,True,True,True,False,
     "Clean item. Chunk directly provides the SCOR definition verbatim."),
    # 17
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "Distractor B (facilitate cross-functional order fulfillment teams) is partially correct per the source -- the chunk mentions cross-functional teams as part of what COMS enables. While C is the best answer (integrating mechanism), B creates ambiguity. Replace B with a clearly incorrect COMS function."),
    # 18
    (5,4,4,True,"REVISE","Partial",True,True,True,True,True,
     "Near-duplicate of Item 17 -- same question, same source, same answer concept (COMS as integration mechanism). Item 18 has better distractors (independently / exclusively / without integrating are clear negatives). If deduplicating keep Item 18 distractor set. Flag as duplicate."),
    # 19
    (4,5,5,True,"ACCEPT","True",True,True,True,True,False,
     "Well-constructed fact-recall item. Distractors are strong -- each uses plausible-sounding but wrong values for each cost category. Source chunk at dist=0 should contain the specific percentages."),
    # 20
    (5,3,5,False,"REVISE","Partial",True,True,True,True,False,
     "Distractors B (decreased energy prices), C (reduced demand), D (lower fuel costs) describe the opposite of 2021 economic reality and are eliminated by general knowledge not supply chain expertise. Replace with plausible-sounding incorrect explanations. difficulty_match=False: even easier than easy warrants."),
    # 21
    (4,4,4,True,"REVISE","Partial",True,True,True,True,True,
     "Near-duplicate of Item 7. Both ask the same feasibility condition for dynamic lot sizing with capacity constraints. Item 21 has more systematically constructed distractors. The capacity-vs-production-quantity wording issue from Item 7 persists. Consolidate into one definitive version with corrected wording."),
    # 22
    (4,2,3,False,"REVISE","True",True,False,False,False,False,
     "Partially ambiguous stem: reorder point s depends on BOTH components (average demand x lead time AND z x sigma x sqrt(LT)). Distractors A (lead time only) and B (average demand only) each capture one real factor making them partially correct. More specific stem needed e.g. What determines the safety stock component of s? Replace A and B with clearly wrong options."),
    # 23
    (5,3,5,True,"ACCEPT","True",True,True,False,True,False,
     "Solid item. Distractor B (ap^-b, the multiplicative demand model) is an excellent trap for students confusing additive and multiplicative models. C and D are formulas from elsewhere in the material but not plausible as g(p)."),
    # 24
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Well-constructed. Verbatim source match. Distractor B is a good trap -- uses early supplier involvement (a real development SC feature) paired with a wrong fulfillment SC characterization."),
    # 25
    (5,2,4,False,"REVISE","True",True,True,True,True,False,
     "Distractors A (efficient communication), C (transparent cost tracking), D (accurate demand forecasting) are all desirable supply chain practices not causes of sub-optimization. Correct answer obvious by elimination. Same pattern as Items 6 and 9."),
    # 26
    (4,4,5,False,"REVISE","True",True,False,True,True,False,
     "Conceptually correct -- marginal profit vs marginal cost IS the newsboy framework -- but retrieved chunk uses critical ratio terminology not marginal profit/cost phrasing. Students reading the chunk would not find B's exact language. Easy difficulty also wrong for newsboy concepts."),
    # 27
    (2,1,2,False,"REJECT","Partial",False,False,False,True,False,
     "REJECT: correct_key=A|B|C|D with no all-of-the-above option -- all four options are supposedly correct making this an invalid MCQ structure with no distractors. Source chunk is also too vague to support any specific option. Complete rewrite required."),
    # 28
    (3,4,4,False,"REVISE","Partial",False,False,False,False,False,
     "Missing difficulty label (null) -- data quality issue must be corrected. Source alignment is partial: chunks give context about inventory policy and lead times but do not explicitly state the approximates-optimal-policy-with-safety-factor claim. Reviewer gave align=5 which seems high."),
    # 29
    (4,5,5,True,"REVISE","Partial",True,True,True,True,True,
     "Near-duplicate of Item 19 -- same question about annual inventory carrying cost percentages (insurance 2%, maintenance 6%, opportunity cost 7-10%), same answer A, slightly reworded options. Dataset inflation. Deduplicate: both items test identical knowledge."),
    # 30
    (4,4,4,False,"REVISE","Partial",True,True,False,False,False,
     "Reviewer underestimated source alignment (gave 3; should be 4): chunk 2 directly states estimation error and lead time are key factors in bullwhip amplification. Main correction needed: difficulty label should be medium not easy for a question about decentralized variability amplification across stages. Distractor D (cumulative lead times only) is a good near-miss."),
    # 31
    (5,3,1,False,"REJECT","False",True,True,False,False,False,
     "REJECT: Self-referential question. Correct answer D (Understanding inputs and outputs) is literally the phrase used in the question stem. Any test-taker can answer correctly without reading the source material. Reviewer accepted this -- false positive. Rewrite to ask meaningful content about SC strategy inputs/outputs."),
    # 32
    (3,3,3,True,"REVISE","True",False,False,False,False,False,
     "Retrieved chunks feature P&G success story (a distractor) not Dell (the correct answer). Source alignment issue -- Dell chunk was not retrieved. Without explicit according-to-text reference multiple companies could be the answer. Needs Dell-specific chunk or more specific question stem."),
    # 33
    (4,3,3,True,"REJECT","Partial",True,False,False,False,False,
     "REJECT: Fourth near-duplicate COMS question (Items 17, 18, 33, 42). Additionally Item 33 correct key B (facilitate cross-functional order fulfillment teams) conflicts with Items 17 and 18 where integration is the primary role and cross-functional teams is a secondary feature. Correct key may be wrong. Keep Item 18; reject Items 17, 33, 42."),
    # 34
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Well-constructed all-of-the-above question where all three sub-options are genuinely correct per source. Students must verify each option. Compare with Item 10 which has same multi-correct issue but without a proper all-of-the-above option. Item 34 handles it correctly."),
    # 35
    (3,2,3,True,"REVISE","True",False,False,True,False,False,
     "Chunk mentions minimizing total supply chain costs but does not specifically identify freight costs for transportation lanes as THE key driver. Distractors A (customer satisfaction), B (employee turnover), D (sales revenue) are clearly unrelated to strategic sourcing. Replace with supply chain cost alternatives such as inventory carrying costs or tariff structures."),
    # 36
    (4,4,5,True,"ACCEPT","True",True,True,True,True,False,
     "Stronger version of Item 35 topic. Only qualifiers in distractors A, B, D effectively force students to recognize that strategic sourcing involves multiple simultaneous factors. Well-constructed."),
    # 37
    (4,4,3,True,"REVISE","Partial",True,True,False,False,False,
     "Chunk 2 (dist=0.658) directly defines j(l) as the index of the plant with the l-th highest cost multiplier matching C. Reviewer align=3 seems to have relied on the top chunk only -- reviewer_source_call_accurate=False. Main issue is stem vagueness: What does the optimal policy determine is too broad. Rephrase to What does j(l) represent in the optimal plant allocation policy?"),
    # 38
    (4,3,3,True,"REVISE","True",True,False,False,False,True,
     "Third version of (s,S) reorder point question (Items 22, 38, 41). Item 38 correct answer C (std dev, lead time, and safety stock factor) is INCOMPLETE -- it omits average daily demand which is also a component of s. Item 41 has the most complete answer set. Deduplicate: keep Item 41, reject Items 22 and 38."),
    # 39
    (4,3,3,True,"REVISE","True",True,True,False,True,False,
     "Distractor A (reduce the need for communication with partners) directly contradicts the chunk which says systems enable firms to rapidly communicate with partners -- trivially eliminable. Stem should say which of the following IS a key benefit. D (eliminate the bullwhip effect) is an overstatement."),
    # 40
    (5,5,3,True,"REVISE","Partial",True,True,True,True,False,
     "Strong ordering question -- all four steps in all options but in different sequences forces sequencing recall more rigorously than Item 4. However citation artifact [1] persists in stem. Remove artifact. Best version of this question topic among Items 4 and 40."),
    # 41
    (5,4,4,True,"REVISE","Partial",True,True,False,True,True,
     "Best version of the (s,S) reorder point question (Items 22, 38, 41). Progressive distractor structure is pedagogically sound -- each option adds one more factor. D substitution of fixed costs for service level z is an excellent trap. REVISE only for duplicate flagging; keep this version and discard Items 22 and 38."),
    # 42
    (5,3,4,True,"REJECT","Partial",True,True,True,True,True,
     "REJECT: Fourth near-duplicate COMS question (Items 17, 18, 33, 42). Same correct answer as Item 18. Generator repeatedly returned to the same COMS chunk. Keep Item 18; reject Items 17, 33, and 42."),
    # 43
    (5,1,5,False,"REVISE","Partial",True,True,True,True,False,
     "CRITICAL distractor issue: A (color scheme of marketing materials), C (number of employees), D (CEO favorite vacation spot) are joke distractors no adult would choose. These eliminate all educational value. Replace with substantive supply chain-adjacent but wrong considerations. Reviewer noted dist=3; I rate dist=1 as these are not plausible wrong answers."),
    # 44
    (3,3,3,True,"REVISE","True",False,False,False,True,True,
     "Near-duplicate of Item 32. Same question, same retrieved chunks (featuring P&G not Dell). Dell SC story not in retrieved chunks. All four companies have legitimate SC success stories making multiple answers defensible without specific source grounding. Deduplicate and fix source alignment."),
    # 45
    (4,3,4,True,"REJECT","Partial",True,False,True,False,False,
     "REJECT: Marked correct answer A is FACTUALLY INCOMPLETE. A says inventory must be zero OR production must be at full capacity but the chunk explicitly states THREE conditions: (1) inventory=0, OR (2) production=0, OR (3) production at full capacity. Answer A omits the production=0 case. Reviewer missed this error (align=5 despite incomplete key). Compare Item 47 which correctly states all three conditions."),
    # 46
    (5,4,3,True,"REVISE","Partial",True,True,True,True,False,
     "Both A and B are mathematically equivalent representations of the revenue function (A uses expectation notation, B uses CDF integral via integration by parts). Dual correct answers in single-select format. Specify notation: which uses EXPECTATION notation (answer: A) or use select-all-that-apply."),
    # 47
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Correct version of the ZICO question (compare Item 45 which had incomplete answer key). Distractor B (production only when inventory is zero) is an excellent trap -- it describes ZIO not ZICO testing whether students distinguish between the two policies."),
    # 48
    (2,2,3,False,"REVISE","True",False,False,False,True,False,
     "Retrieved chunks cover basic newsboy quantity model not the newsboy-with-pricing extension. Options C (ratio of profit margin to selling price) and D (critical fractile formula F(y*)=(p-c)/p) are semantically equivalent -- both describe the same quantity creating ambiguity about which is more correct. Needs pricing-specific newsboy chunk."),
    # 49
    (2,4,4,False,"REVISE","True",False,False,False,True,False,
     "Chunk explains the BEHAVIOR (companies treat demand as predictable) but not explicitly WHY. Answer A (simplify forecasting) is an inference. Distractor D (avoid acknowledging uncertainty) is arguably more consistent with the chunk which notes companies ARE aware of uncertainty but still plan far ahead. Needs chunk that explicitly states the reason."),
    # 50
    (4,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Case study question with specific numerical outcome (12.3M cases). Distractors A and B use plausible-sounding specific numbers (good traps for students who know the case but misremember details). D (revenue decrease) is clearly wrong as this is a success story. Full chunk presumably contains the 12.3M figure."),
]

decisions = []
for idx, raw in enumerate(RAW):
    item = items[idx]
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

# Summary
from collections import Counter
decisions_count = Counter(d["claude_decision"] for d in decisions)
print(f"Batch 1 written: {len(decisions)} items")
for k, v in sorted(decisions_count.items()):
    print(f"  {k}: {v}")
