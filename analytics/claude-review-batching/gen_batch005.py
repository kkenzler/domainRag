"""Generate batch005.json — Claude review decisions for items 201-250."""
import json
from pathlib import Path

INPUT = Path("claude_review_input.json")
OUTPUT = Path("batch005.json")

with open(INPUT, encoding="utf-8") as f:
    items = json.load(f)

# (align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag, notes)
RAW = [
    # 201
    (3,2,4,False,"REJECT","Partial",True,False,False,True,True,
     "Conflicting key with Item 191 (same question: key factor in newsboy pricing). Item 191 has KEY=B (selling price p), this item has KEY=C (profit margin ratio (p-c)/p). Additionally, C and D are equivalent expressions: C says '(p-c)/p' and D says 'F(y*) = (p-c)/p' -- both represent the critical fractile. REJECT: duplicate-correct-answer (C=D) plus key conflict with 191. The newsboy optimal pricing question needs a single authoritative version."),
    # 202
    (3,4,5,False,"ACCEPT","Partial",True,True,False,True,False,
     "C correctly states that unit cost decrease rate varies by technology. A (costs always increase) and D (subcontracting never economical) are factually wrong. B (at high volumes, one technology always dominates regardless of fixed costs) is too absolute -- the chunk shows technologies cross at different volume thresholds. dm=False is reviewer's assessment but at easy level this is appropriate recall of scale analysis basics. Content is accurate and well-supported."),
    # 203
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean EOQ-backorder definition item. s = maximum inventory level (order-up-to level) is correct. B (order quantity per cycle = Q, not s), C (shortage cost per unit time = π, not s), D (holding cost per unit time = h, not s) are correctly distinguished. The item correctly tests knowledge of variable naming in the backorder model."),
    # 204
    (3,4,3,False,"REVISE","True",True,True,False,True,False,
     "A (p* = (a+bc)/(2b)) is the correct deterministic additive newsboy pricing formula. B (p* = a-bp) is the demand function g(p), not p*. C (contains bc/(b-1) = multiplicative model formula). D (includes E[min(z*,ε)] = stochastic term contradicting 'deterministic'). Content is accurate but difficulty mismatch (requires knowing specific formula derivation result, more than basic recall for an easy item). Reclassify as medium."),
    # 205
    (5,4,5,True,"ACCEPT","True",True,True,True,True,False,
     "Clean SCM characteristic item. B (integration across SC functions) is directly supported by the chunk. A (solely cost), C (disregards service), D (only own operations) are all one-dimensional or too narrow. Well-constructed easy item with appropriate difficulty. C and D are obviously wrong but A is a reasonable near-miss for students who focus only on the cost side of SCM."),
    # 206
    (4,3,5,True,"REJECT","Partial",True,False,False,True,True,
     "CRITICAL: Key conflict with Item 180. Item 180 has KEY=C (sophisticated inventory management software) while this item has KEY=B (top management emphasis) for the same question about the 'most significant factor in the 1995-2000 inventory turnover improvement.' The chunk likely lists multiple factors without clearly ranking one as 'most significant.' REJECT both items with conflicting keys -- the source text either lists multiple factors equally or the ranking is ambiguous. Reviewer's ACCEPT with dq=3 misses this conflict."),
    # 207
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "D correctly states costs decrease as volume increases, but rate varies by technology. A (costs increase), B (costs decrease as volume decreases = backwards), C (costs constant) are all clearly wrong. Near-duplicate of Item 202 but with D phrased more precisely (202's key C and 207's key D both say the same thing). Prefer 207's formulation. Flag 202 for elimination."),
    # 208
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "D (increased demand + reduced effective capacity from congestion + higher fuel costs) correctly captures the full combination of drivers. A (decreased demand = opposite), B (reduced congestion, increased capacity = opposite), C (lower energy costs = opposite). Third near-duplicate of ocean freight 2021 question (166, 198, 208). Flag for dataset curation."),
    # 209
    (4,3,5,True,"REVISE","True",True,True,False,True,False,
     "B (raw material costs including invoice and freight) is a legitimate strategic sourcing driver per the chunk. However dq=3: A (customer satisfaction), C (employee turnover), D (customer wait times) are all indirect business metrics that could be argued to loosely influence sourcing decisions through quality, efficiency, and lead time requirements. Replace C (employee turnover) with a clearly wrong sourcing factor (e.g., 'Office furniture spending per employee') to improve discrimination."),
    # 210
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (vertical org structure with functional silos) is correct per the chunk. A (high customer expectations = a challenge, not the integration barrier itself), C (lack of cross-functional teams = a symptom of functional silos), D (inefficient logistics = an outcome, not the primary barrier). Near-duplicate of Item 196 but with slightly different distractor set. Flag for dataset curation."),
    # 211
    (3,4,5,True,"REVISE","True",False,True,False,False,False,
     "Chunk mismatch: dist=0 chunk is about the LOGISTICS SCORECARD FRAMEWORK ('A logistics scorecard framework translates benchmarking insights...'), not COMS. The question asks about COMS organizational characteristics. Question content is correct (COMS integrates sales, credit, planning, logistics) but the retrieved chunk doesn't support it. Reviewer's ACCEPT with sa=5 appears to be in error -- sa=5 requires the chunk to directly support the item. REVISE: ensure correct chunk is retrieved for COMS items."),
    # 212
    (3,1,2,False,"REJECT","Partial",True,True,True,True,False,
     "dq=1: A (DECREASED pace of change), B (MORE STABLE markets), and D (LOWER customer expectations) are all direct inversions of the actual 21st century business challenges. These are joke/opposite distractors equivalent to the Item 178 pattern. No student who has read the material would choose A, B, or D. REJECT and replace with plausible wrong characterizations of 21st century challenges (e.g., A: 'The primary challenge is increasing automation reducing the need for human coordination across supply chains')."),
    # 213
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (COMS aligns all org activities with market signals, promotions, order fulfillment) is a more complete description than 'facilitating cross-functional teams' (B in Item 214) or 'integrating functions' (other versions). B (inventory and procurement = too narrow for COMS scope), D (central database = a tool, not the role). Near-duplicate of Items 179, 197, 214 -- four COMS definition questions. Flag for dataset curation: retain 2 at most."),
    # 214
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (integrate all order fulfillment functions into unified system) is correct. A (financial transactions), C (customer service inquiries), D (track inventory and prevent stockouts) are all too narrow or mislabeled. Near-duplicate of Items 179, 197, 213. This version has a slightly different emphasis ('unified system' language). Flag for dataset curation."),
    # 215
    (5,3,4,False,"REVISE","True",True,True,False,True,False,
     "B correctly distinguishes incremental from all-units discounts: all-units gives discount on entire order if threshold met; incremental gives discount only on units above the threshold. A reverses the definitions (swapped names) which is a good trap. However D ('all-units reduce risk by allowing repurchase of unsold items') describes a BUYBACK CONTRACT, not quantity discounts at all. Replace D with a plausible wrong description of one of the discount types (e.g., D: 'Incremental discounts provide a steeper reduction than all-units discounts at all quantity levels')."),
    # 216
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean Dell strategy item. A (direct, build-to-order) is correct. B (indirect, mass production = Dell's model inverted), C (centralized SCM = not Dell's distinguishing approach), D (decentralized logistics = not the key differentiator). Near-duplicate of Item 110 but at medium level for haiku/haiku condition. Content is appropriate."),
    # 217
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "B (bullwhip caused by orders based on limited demand info and lead time adjustments) correctly captures the statistical estimation mechanism. A (retailers have perfect info = opposite premise), C (customer demand inherently wildly variable = shifts blame to demand not SC structure), D (production planning more accurate = backwards). Well-constructed bullwhip explanation item -- tests understanding of the CAUSE, not just the definition."),
    # 218
    (1,4,5,True,"REVISE","Partial",False,True,False,False,False,
     "Chunk mismatch: dist=0 chunk is about QUANTITY DISCOUNTS ('suppliers often offer lower unit prices for larger order quantities'), not the single-period newsboy problem. The question content is correct (B: marginal profit vs marginal cost of over/under-stocking is the newsboy optimality condition) but the source chunk is completely mismatched. Reviewer's ACCEPT may be in error given sa=1 is more appropriate. REVISE: needs correct chunk retrieval for the newsboy problem."),
    # 219
    (3,4,3,False,"REVISE","True",True,True,True,True,False,
     "B is correct (short window = less smoothing = larger fluctuations = more variability). A and D claim variability DECREASES with short window (opposite of the moving average bullwhip result). C says variance unchanged (ignores the Var formula showing it increases with L and decreases with p). The distractors are too obviously wrong -- A and D say the same wrong thing (variability decreases) with different justifications. Reclassify as easy or redesign with more nuanced wrong answers about window size effects."),
    # 220
    (5,4,3,False,"REJECT","Partial",True,True,False,True,False,
     "Near-duplicate of Items 225 and 241 (all three PepsiCo NOT-format questions with KEY=D). Three versions of the same question is excessive. REJECT 220 and eliminate in favor of 225 (which has better stem clarity) or 241. The PepsiCo case study has only one version needed in the dataset."),
    # 221
    (3,2,4,False,"REVISE","True",True,True,False,True,False,
     "dq=2: B ('difficulty in maintaining a rigid hierarchical structure') is confusingly worded -- it could mean difficulty in KEEPING the structure (implying companies want to keep it) or difficulty BECAUSE OF the structure. Near-duplicate of Items 226 and 232 (all test 21st century SC integration challenge). Replace B with a clearer wrong answer. Also: A (reduce operational costs) is a perennial business challenge not specific to 21st century SC integration. Eliminate duplicate versions."),
    # 222
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "D (using data, benchmarking, and technology analysis to develop scale curves) correctly identifies the final step of the SC strategy development process. A (clear strategy = step 1), B (identify major decisions = step 2), C (detailed analysis = step 3). Well-constructed item testing sequential process knowledge."),
    # 223
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "Double-correct-answer issue: A (retailers can't accurately predict demand) and C (lead times exacerbate bullwhip) are BOTH true contributing factors to the bullwhip effect. C is confirmed by the Var(q)/Var(D) = 1+2L/p formula where L is lead time. D ('smoothing parameters too HIGH causing overestimation') is backwards -- higher p means MORE smoothing = LESS bullwhip. Revise C to make it clearly wrong OR accept that A is the PRIMARY cause while C is a secondary amplifier. Near-duplicate of Item 217."),
    # 224
    (3,4,3,False,"REVISE","True",False,True,False,True,False,
     "Mixes two different types of EOQ statements: A/B/C discuss π-dependence of Q* and s* while D discusses the EOQ cost sensitivity ratio (γ + 1/γ)/2. The heterogeneous distractor set makes the question feel like a grab-bag. D is the correct EOQ insensitivity result (proven property). A is wrong (Q* and s* DO depend on π). B/C appear wrong based on economics (π↑ should decrease s*). Chunk (basic EOQ) supports D but not the backorder relationships A/B/C. Separate this into two distinct questions: one about π-dependence, one about cost ratio."),
    # 225
    (5,4,3,False,"REJECT","Partial",True,True,False,True,False,
     "Near-duplicate of Items 220 and 241 (same PepsiCo NOT-format question, same KEY=D). Third version of this question. REJECT 225 in favor of keeping one clean version. All three have 'reduction in number of production lines' as the not-mentioned result."),
    # 226
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "Near-duplicate of Items 221 and 232 (21st century SC integration challenge). B is correct. dq=3: A ('need to maintain traditional hierarchical structures despite increasing competition') is a plausible near-miss -- companies might WANT to maintain current structures even though they should change. C ('focus solely on internal efficiency') and D ('reducing number of employees') are poor distractors. Replace C and D with more nuanced wrong characterizations of the 21st century SC challenge."),
    # 227
    (5,4,3,True,"REVISE","True",True,True,False,True,False,
     "C (fractional adjustment based on next plant's excess capacity) is the step computing l* from l1. sc=3 because the stem 'which step involves fractional adjustment' is vague without knowing the algorithm. A (identifying j(l) = step 1 variable definition), B (finding l1 = step 2), D (ranking plants = step 0) form a natural progression. Near-duplicate of Items 108, 114, 185 (all test multi-plant algorithm steps). Add more algorithmic context to the stem or reclassify as hard."),
    # 228
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "A correctly answers the question (longer horizon = worse forecast). B (forecasting always wrong = too absolute, doesn't address time horizon). C (aggregate more accurate than disaggregate = a different forecasting principle unrelated to time horizon). D (inventory definition = completely unrelated to forecasting). Replace D with a relevant forecasting principle that's a plausible wrong answer (e.g., D: 'Short-term tactical forecasts are always less accurate than long-range strategic forecasts' -- the direct opposite of A). Near-duplicate of Item 250."),
    # 229
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "B is correct (variance ratio = 1+2L/p, confirmed by chunk formula). A ('order variability decreases as both L and p increase') is wrong in two ways: L↑ INCREASES bullwhip while p↑ DECREASES it -- they have OPPOSITE effects, not both the same. C (variance ratio constant = directly contradicted by formula). D (safety stock adjustments reduce order variability = only marginally true and not the primary formula result). More than medium-level difficulty: knowing 1+2L/p requires formula recall. Reclassify as hard or provide formula in stem."),
    # 230
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (tactical decisions) correctly identifies the medium-term resource alignment level. A (strategic = long-term structure decisions), C (operational = day-to-day execution), D (physical flow = not a standard decision level term) are all wrong. Clean item testing understanding of SCM decision hierarchy levels."),
    # 231
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Numerical calculation item with embedded explanations in answer options. C (63.4 units with z=1.65) is the stated correct answer. The format (each distractor includes its calculation path) is pedagogically useful for teaching. Cannot independently verify the exact computed value without the full problem parameters in the source, but the approach (s = LT×avg_demand + z×σ×√LT) and z=1.65 for 95% service level are standard. Reviewer ACCEPT with strong ratings is trusted."),
    # 232
    (4,3,5,False,"REVISE","True",True,True,False,True,False,
     "Near-duplicate of Items 196, 210, 221, 226 (barrier to SC integration). B is correct. However: A ('encourage collaboration'), C ('prioritize customer outcomes'), D ('integrate logistics across vertical structures') all describe what traditional structures FAIL to do, phrased as positive capabilities. This creates a confusing all-opposite pattern. Students know all three wrong answers are false, making B trivially obvious. Replace with nuanced wrong explanations of why traditional structures are a barrier (e.g., A: 'because they create too many cross-functional handoffs that slow decision-making')."),
    # 233
    (4,5,5,False,"REVISE","True",True,True,False,True,False,
     "D (decreased global demand for ag commodities) is correctly the NOT-contributing factor -- ag commodity demand actually INCREASED post-pandemic (equity prices rose substantially per the chunk). A, B, C all correctly describe real drivers of 2021 freight rate increases. dq=5 (very good distractors per reviewer). dm=False: labeled medium but is easy-level for anyone who knows ag commodity demand surged post-pandemic. Near-duplicate of Item 242. Replace D with a less obvious NOT-factor (e.g., 'new environmental regulations requiring vessel retrofits' -- plausible but not the cited cause)."),
    # 234
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (bridge between strategic goals and operational performance) is directly supported by the chunk. A (independent assessment tool = contradicts the 'aligned with strategy' purpose), C (solely internal efficiency = too narrow), D (prioritizes market over collaboration = mischaracterizes the balance). Well-constructed logistics scorecard item."),
    # 235
    (3,2,4,False,"REVISE","True",True,True,False,True,False,
     "dq=2: A (exact number of facilities) and D (detailed distribution flow patterns) sound like they could be strategic SC outputs but are actually design decisions/inputs. The distinction between strategic OUTPUTS (delivery time, service level = what logistics achieves) and strategic DECISIONS (number of facilities, flow patterns = how logistics is structured) is subtle and not clearly explained by the stem. Revise stem to clarify: 'Which of the following best represents a strategic OUTCOME that logistics aims to deliver to customers?' to make C unambiguously correct."),
    # 236
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (increase in purchasing efficiency with higher % of sales outsourced from 34% to 54%) is precisely what the chunk describes. A (decrease in outsourcing = opposite), C (shift to localized = contradicts the globalization trend), D (elimination of SC complexity through push-pull = fabricated claim). Clean factual item with specific quantitative support."),
    # 237
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (reorganizes around end-to-end processes with flat hierarchies and cross-functional teams) is directly contrasted with the traditional relay race in the chunk. A (adds logistics on top of vertical structures = hybrid not horizontal), C (maintains rigid hierarchical departments = describes traditional structure, the opposite), D (focuses on departmental inputs = also describes traditional, not horizontal). Well-constructed conceptual comparison item."),
    # 238
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (managing uncertainty including demand and supply-side factors) is correct. A (all suppliers in same country = SC design constraint, not a fundamental challenge), D (deciding logo color = joke distractor). D is a low-quality joke distractor that weakens an otherwise good item. The item is ACCEPT-level but D should be replaced with a plausible wrong answer about SC challenges (e.g., D: 'Ensuring the longest possible lead times to reduce ordering frequency')."),
    # 239
    (3,2,4,False,"REVISE","True",True,True,False,True,False,
     "A (DECREASED global ag demand = directly opposite of what happened) and C/D (ocean shipping cost factors = supply-side factors not commodity demand drivers) are all obviously wrong. Only B (pandemic recovery → higher demand) is correct. dq=2: replace A with a plausible but wrong demand driver (e.g., A: 'Government export restrictions reducing international ag commodity trade') and C/D with more directly related but wrong commodity demand factors."),
    # 240
    (5,4,5,True,"ACCEPT","True",True,True,True,True,False,
     "B (balancing competing objectives across functional areas) is correct. A (same country suppliers = design constraint, not the fundamental challenge), C (minimize production only = too narrow), D (ignore information integration = describes what NOT to do). Near-duplicate of Item 238 (both test 'challenge beyond matching supply and demand') but 240 asks about SC managers specifically. Both are ACCEPT-level, minor thematic overlap."),
    # 241
    (5,4,3,False,"REJECT","Partial",True,True,False,True,False,
     "Near-duplicate of Items 220 and 225 (same PepsiCo NOT-format question, same KEY=D). Three versions of this question in the dataset is excessive. REJECT 241. Keep 225 (medium label is more appropriate for this level of detail recall) and eliminate 220 and 241."),
    # 242
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "Near-duplicate of Item 233 (same 2021 ocean freight NOT/LEAST question). D (decreased ag demand = least likely to contribute to rate increases, since ag demand actually surged) is correct. A, B, C all correctly describe real rate drivers. The near-duplicate with 233 creates redundancy. Eliminate one version. If keeping 242, replace D with a more subtly wrong factor (e.g., D: 'New International Maritime Organization emissions regulations requiring vessel retrofits' -- plausible cost driver but not documented as a 2021 rate driver)."),
    # 243
    (1,3,4,False,"REJECT","True",False,True,False,True,False,
     "Reviewer REJECT confirmed. The chunk (basic EOQ formula) does not provide the backorder EOQ formula √(2DK/h)×√((π+h)/π). The correct formula (B) requires knowing the backorder cost extension of the EOQ model, but the retrieved chunk only covers the standard EOQ. Additionally: B vs C discrimination (√((π+h)/π) vs √(π/(π+h))) requires knowing which factor is in the numerator -- high precision recall. REJECT due to wrong chunk; remap to the appropriate backorder model chunk."),
    # 244
    (3,4,4,False,"REVISE","True",False,True,False,True,False,
     "B (revenue sharing contract) is correct for risk mitigation in uncertain demand context. A (order average forecast = naive newsboy error), C (ignore price elasticity, maximize order = obviously wrong), D (fixed price, no variability = obviously wrong). C and D are too obviously wrong for medium level. Chunk mismatch: the dist=0 chunk is about basic newsboy optimal quantity, not contract mechanisms. Near-duplicate of Item 122. Revise distractors to be more nuanced (e.g., B: revenue sharing vs A: buyback agreement as a true 2-option discrimination)."),
    # 245
    (3,4,4,False,"REVISE","True",False,True,False,True,False,
     "C correctly identifies the limitation: traditional accounting fails to distinguish delivery scenarios, obscuring true costs. A ('accurately track full cost'), B ('provide clear visibility into hidden costs'), D ('effectively manage inventory across locations') all describe capabilities traditional accounting LACKS -- phrased as positive capabilities. This confusing all-opposite format makes the question feel like a trick question. Revise to: 'Which of the following is a known LIMITATION of traditional accounting in SCM?' then phrase all options as limitations, making C the most specific and accurate one."),
    # 246
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "C correctly identifies the challenge: understanding the impact of subcontracting or alternative technologies at various production volumes. A ('calculating exact unit costs is straightforward' = false, but the question asks which is a challenge so A describes a false positive), B ('rate of decrease consistent across all technologies' = directly contradicted by the chunk). D ('fixed costs negligible = scale irrelevant' = obviously wrong). A and D are clearly wrong negative statements, making C somewhat obvious. Better distractor: A: 'Identifying the single technology that minimizes cost across all production volume ranges' (sounds like a reasonable challenge but implies there's always one dominant technology, which is false)."),
    # 247
    (3,4,2,False,"REJECT","Partial",False,True,False,True,False,
     "Near-duplicate of Item 224: both items present the EOQ cost sensitivity formula (γ+1/γ)/2 as correct answer but in different option positions (224 has it as D, 247 has it as C). REJECT as duplicate. Additionally: chunk (basic EOQ) doesn't directly support the backorder-related options A/B. The cost ratio formula (C) is supported by basic EOQ theory but is incorrectly mixed with backorder-specific statements A/B. Eliminate 247 in favor of Item 224."),
    # 248
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "C (larger variations causing excess inventory and stockouts) correctly describes the inventory management impact of bullwhip. A (more stable inventory = opposite), B (smaller fluctuations upstream = opposite of bullwhip), D (decreases need for forecasting = backwards, bullwhip increases forecasting importance). D is a clever near-miss trap for students who know bullwhip is forecasting-related and confuse 'important for' with 'reduces need for.'"),
    # 249
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (freight costs, duties, tariffs) is the correct strategic sourcing driver per the PBG chunk. A (company logo color = joke distractor), B (number of SC employees = HR metric not sourcing driver), D (brand of computers = joke distractor). A and D are low-quality joke distractors that weaken an otherwise good item. Near-duplicate of Item 134 (same concept tested at different difficulty/condition level)."),
    # 250
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "Near-duplicate of Item 228 (same question about forecast accuracy and time horizon, same KEY=A, same distractor D is inventory definition). D (inventory = supply - demand) is completely unrelated to forecasting accuracy -- same weak distractor as in Item 228. Eliminate one of the two versions and replace D in the remaining version with a relevant forecasting principle (e.g., D: 'Short-range operational forecasts have higher error rates than long-range strategic forecasts')."),
]

COLS = [
    "claude_source_alignment", "claude_distractor_quality", "claude_stem_clarity",
    "claude_difficulty_match", "claude_decision", "agrees_with_reviewer",
    "chunks_support_question", "correct_answer_verifiable", "distractors_clearly_wrong",
    "reviewer_source_call_accurate", "flag_ambiguity", "claude_notes",
]

decisions = []
for offset, row in enumerate(RAW):
    item = items[200 + offset]
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

from collections import Counter
decisions_count = Counter(d["claude_decision"] for d in decisions)
print(f"Batch 5 written: {len(decisions)} items")
for k, v in sorted(decisions_count.items()):
    print(f"  {k}: {v}")
