"""Generate batch004.json — Claude review decisions for items 151-200."""
import json
from pathlib import Path

INPUT = Path("claude_review_input.json")
OUTPUT = Path("batch004.json")

with open(INPUT, encoding="utf-8") as f:
    items = json.load(f)

# (align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag, notes)
RAW = [
    # 151
    (2,4,4,False,"REVISE","True",False,False,False,True,False,
     "Chunk (dist=0) is about basic EOQ cost (ordering + holding), not the EOQ-with-backorders model. The question requires knowing Q* ≈ EOQ × √((h+π)/π) and s* = Q × h/(h+π). When π >> h: Q* → EOQ from above (slightly larger), s* → 0. D's text is truncated in export -- cannot verify the full option D without reading source. Chunk mismatch: REVISE to match with the backorder-model chunk."),
    # 152
    (3,4,4,False,"REJECT","Partial",True,True,True,True,False,
     "KEY=A|B|C|D means ALL four options are correct, making this a trivially obvious 'all of the above' question. No discrimination is possible -- any student can pick 'all of the above' without knowing any specific option. REJECT: redesign as a question where exactly one combination is correct, or restructure as a 'which of the following is FALSE about SC network design trade-offs?' format."),
    # 153
    (3,4,4,False,"REJECT","Partial",False,False,False,True,False,
     "Near-duplicate of Item 139 with a CONFLICTING key: Item 139 had KEY=D (powerful customers) while this item has KEY=C (e-commerce). Both are legitimate contemporary SC trends. Having two near-identical questions with different keys confirms neither has a defensible single correct answer. REJECT both 153 and 139 pending expert determination of which trend 'best describes impact on coordination.' Reviewer's REVISE is too lenient given the conflicting keys."),
    # 154
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "Well-constructed factual item about 2021 ocean freight rate dynamics. C correctly identifies the combination of demand surge and port congestion as drivers of sharply higher rates. A (decreased demand = lower rates) is directly wrong. B (absorbed by shipping companies = rate stability) is a plausible but incorrect claim. D (unpredictable fluctuations) is contradicted by the clear directional evidence in the chunk."),
    # 155
    (3,4,3,False,"REVISE","True",True,True,False,True,False,
     "C ('increasing SKU proliferation') directly contradicts what reduces inventory investment (SKU reduction is a stated driver of improved turnover). C is not merely wrong -- it describes the opposite of the correct answer. Replace C with a plausible-but-wrong strategy (e.g., 'Increasing safety stock levels and expanding supplier base'). Also: A and D are also plausible strategies that partially overlap with B -- the question should be clearer about what specifically distinguishes B as the BEST combination."),
    # 156
    (3,4,2,False,"REVISE","True",False,True,False,True,False,
     "The chunk (Wagner-Whitin WITHOUT capacity constraints) does not support ZICO (the capacity-constrained extension). More critically: sc=2 because A and D both describe the ZIO property (inventory × production = 0) not ZICO. B ('production always either full capacity or zero') IS the ZICO property: in any optimal ZICO solution, production is either 0 or at the capacity limit. C ('order placed only at zero inventory') is the ZIO property. Clarify the distinction between ZIO (A/C/D) and ZICO (B) in both stem and distractors."),
    # 157
    (3,4,4,False,"REVISE","True",True,False,False,True,False,
     "The correct answer for 'high demand uncertainty, low product variety' is debatable: centralization (A) reduces safety stock via risk pooling when demand is uncertain; dispersal (B) maximizes responsiveness but increases safety stock. The optimal strategy depends on whether responsiveness or cost-efficiency is prioritized -- not specified in the stem. Reviewer's REVISE and sa=3 are appropriate. Add explicit context about service level priority (responsiveness vs. cost) to make B unambiguously correct."),
    # 158
    (3,4,2,False,"REVISE","True",True,True,False,True,False,
     "B ('S is always greater than s') is trivially true by definition of the (s,S) policy -- S > s is inherent in how the policy is named. This makes B a definitionally obvious correct answer rather than a knowledge test. More interesting distractors would test why S > s and by how much. D ('S less than s when high variability') is an obvious definitional violation. Replace B with a specific mechanistic statement (e.g., 'The difference S-s represents the fixed order quantity Q and is determined by the optimal economic order quantity')."),
    # 159
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "B (decomposition at zero-inventory periods) and C (shortest path for constant capacity) may both be true statements about dynamic lot sizing with capacity constraints. The ZICO shortest-path structure applies when capacity is time-dependent; decomposition is also a valid property. Verify C's accuracy per source and if true, revise C to state something false (e.g., 'A shortest path algorithm requires exponential time to solve'). A (always produce at full capacity) is wrong since ZICO allows zero production too."),
    # 160
    (3,2,4,False,"REVISE","True",True,True,False,True,False,
     "dq=2 confirmed: A and C are both true statements about the optimal multi-plant policy -- A (ranks by cost multiplier) and C (uses piecewise-linear modeling) are both accurate. B (always full capacity regardless of cost = obviously wrong) and D (subcontracting, ignoring plant capacity = obviously wrong) are too clearly wrong. Revise C to state something false about the piecewise-linear modeling (e.g., 'uses branch-and-bound integer programming to find the exact optimal number of plants')."),
    # 161
    (3,4,4,False,"REJECT","Partial",True,True,True,True,False,
     "Near-duplicate of Items 148, 164, and 165 (all test strategic output → operational decision alignment). Four versions of the same conceptual question. Eliminate Items 161, 164, and 165 -- keep the single best version (148 has slightly more nuanced distractors). A (strategic outputs irrelevant) and D (alignment problematic) are obviously wrong. C (strategic outputs dictate specific inventory levels) is too rigid and also wrong, leaving B as the clear answer."),
    # 162
    (5,4,3,False,"REVISE","True",True,True,True,True,False,
     "If the formula s = LT×avg_demand + z×σ√LT is provided directly in the stem, then A is trivially deducible by reading -- B, C, D are all directly contradicted by the formula (B says 'only considers fixed costs', C says 'solely based on historical data', D says 'does not account for lead time'). If the formula IS in the stem, this tests formula comprehension not knowledge. Difficulty mismatch: providing the formula makes this easy-level interpretation, not hard. Either remove the formula and test knowledge of what s represents, or reclassify as easy."),
    # 163
    (4,3,5,False,"REVISE","True",True,True,False,True,False,
     "B ('smoothing factor p is too high') has it backwards: in the bullwhip model Var(q)/Var(D) = 1+2L/p, a LARGER p (longer moving average window) means LESS bullwhip, not more. B describes the opposite of the correct relationship. A ('retailers overestimate inventory') is a contributing factor but not the mathematical driver in the model. Replace B with 'the smoothing factor p is too small, giving insufficient averaging' which correctly describes the direction. Difficulty mismatch: straightforward lead time + variance result."),
    # 164
    (3,4,2,False,"REJECT","Partial",True,True,True,True,False,
     "Near-duplicate of Items 148, 161, and 165. Fourth version of the strategic output → operational/tactical decision alignment question. A (strategic outputs irrelevant) and C (tactical = short-term only), D (strategic dictates exact prices) are obviously wrong for any student familiar with SC strategy. Eliminate in favor of Item 148 which has the most nuanced distractor set."),
    # 165
    (3,4,4,False,"REJECT","Partial",True,True,True,True,False,
     "Near-duplicate of Items 148, 161, and 164. Fifth version of strategic-operational alignment. D ('bullwhip effect is leveraged to amplify fluctuations') is an absurd distractor with zero plausibility. A and B are plausible wrong answers but the question is structurally identical to 148. Eliminate -- this duplication inflates the dataset without adding assessment value."),
    # 166
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean easy item about 2021 ocean freight rate drivers. B correctly identifies port congestion and higher fuel costs as the primary cause. A (decreased demand = lower rates) directly contradicts the known demand surge. C (lower vessel capacity due to shipbuilding slowdowns) is factually incorrect -- the issue was demand surge not vessel shortage. D (reduced energy prices) contradicts the rising fuel cost context."),
    # 167
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean bullwhip definition item. B is correct. A (order sizes decrease) is the direct opposite. C (inventory constant) contradicts the bullwhip premise. D (lead times reduced) is unrelated to the bullwhip definition. Note: this is one of at least 6 near-duplicate bullwhip definition questions (167, 174, 175, 183, 187, 195) -- significant duplication that should be addressed in dataset curation."),
    # 168
    (3,2,4,False,"REVISE","True",True,False,False,True,False,
     "KEY=B (inventory management policies) is suspect as the primary alignment factor -- most SC strategy literature frames logistics as aligning with CUSTOMER SERVICE REQUIREMENTS, not inventory policies specifically. A (customer service levels) is actually the more conventional primary alignment point. dq=2: all four options (customer service, inventory policies, supplier relationships, transportation costs) are legitimate logistics considerations -- the question doesn't provide discriminating context to choose B over A. Reviewer's dq=2 is accurate."),
    # 169
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "Dual-correct-answer issue: A (insurance, maintenance, opportunity cost) and B (storage, handling, deterioration) are BOTH legitimate holding cost components. C (production, transportation, purchasing = ordering/procurement costs, not holding) and D (order, shortage = ordering and stockout costs, not holding) are clearly wrong. The question needs to specify which components are mentioned in the source text to make A vs B discriminable. If the source text lists A's components, add a note that B's components are 'separate from' the defined holding cost formula."),
    # 170
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Sophisticated item acknowledging mathematical equivalence: A and B are equivalent expressions for the additive demand revenue function (E[min(y,D)] = ∫₀ʸ(1-F(x))dx by integration by parts). C is from the multiplicative demand model and D is from the pricing first-order condition. The dual-key (A|B) is mathematically correct. Note: in a standard single-answer MCQ format, the dual key is pedagogically unusual -- consider converting to 'which of the following is NOT equivalent to the revenue function?' format."),
    # 171
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "C (balance cost and service) is clearly correct. A (minimize costs without service) is a classic straw man. B (high quality manufacturing) is a manufacturing not SCM objective. D (maximize variety) is a marketing objective. Replace D with a more plausible wrong answer about SCM (e.g., D: 'Maximizing speed of delivery at any cost regardless of financial constraints'). Near-duplicate of Item 199 (same question, same answer). One version should be eliminated."),
    # 172
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean factual item about PepsiCo Bottling Group sourcing optimization results. C correctly describes the outcome: warehouse out-of-stock reduction leading to additional cases available for sale. A (5% transport miles growth -- a cost increase, not a benefit) and D (capital expenditure increase) describe costs not outcomes. B (raw materials inventory INCREASE) contradicts the optimization goal. Note: near-duplicate of Item 189 (same case study, same outcome, 189 adds the '12.3 million cases' quantification)."),
    # 173
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "Near-duplicate of Item 169 (same inventory carrying cost components question, same dual-answer key A|B). A (insurance, maintenance, opportunity cost) and B (storage, handling, deterioration) are both valid holding cost components -- same dual-correct issue as 169. C (quality improvement, setup reduction = lean manufacturing costs) and D (transportation discounts, purchasing discounts = ordering costs) are wrong. Eliminate in favor of Item 169, or distinguish by asking specifically about the source text's terminology."),
    # 174
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "Near-duplicate of Items 167, 175, 183, 187, 195 (all bullwhip definition questions). dq=3: C ('production plans less variable than distributor orders') and D ('retailer orders more consistent than production plans') describe the OPPOSITE of reality -- production plans and manufacturer orders ARE more variable than retailer demand under bullwhip. These distractors describe the correct direction of bullwhip amplification but attribute it to the wrong tiers. Replace with better distractors or eliminate this version."),
    # 175
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean bullwhip definition item. A (order sizes decrease = directly opposite). C (lead times constant = unrelated to bullwhip definition). D (reduces inventory investment = opposite of reality). B is the precise definition. Note: sixth near-duplicate of the bullwhip definition concept -- dataset contains excessive repetition. Flag for dataset curation."),
    # 176
    (5,3,4,False,"REVISE","True",True,True,False,True,False,
     "B is correct (development SC focuses on early supplier involvement during product architecture). A (managing demand uncertainty) and D (scheduling production/procurement) describe FULFILLMENT SC activities, not development SC. C (distributing via e-commerce) is also fulfillment. Replace one fulfillment-focused distractor with something that plausibly sounds like development SC but is wrong (e.g., A: 'managing finished goods inventory to meet retailer replenishment orders')."),
    # 177
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean definition item for l1 in the multi-plant algorithm. B precisely defines l1 (max m such that sum of excess capacity from top m highest-cost plants ≥ 0). A (plants with production cut back = what l1 DETERMINES, not what l1 IS). C (j(l) index = a different variable). D (fractional adjustment = part of the l* calculation, not l1 definition)."),
    # 178
    (5,1,3,False,"REJECT","Partial",True,True,True,True,False,
     "dq=1: A (color of packaging), C (CEO's favorite color), and D (number of employees) are all joke/irrelevant distractors with zero plausibility as SC design factors. Same distractor failure pattern as Items 43, 98, 102, 178. Only B (transportation costs) is a real answer. This is not a test item -- it has no discriminating power. REJECT and replace with three genuinely plausible SC design factors that are wrong or less important (e.g., A: 'the company's advertising budget', C: 'proximity to raw material suppliers', D: 'regional tax incentives for facility location')."),
    # 179
    (5,3,4,True,"REVISE","True",True,True,True,True,False,
     "B is correct per the chunk. Near-duplicate of Item 197 (same COMS question, same key). Also: all wrong answers (A: complaints/returns, C: inventory only, D: production only) are too narrowly scoped -- any student who knows COMS is an integrating mechanism immediately rejects A, C, D as too narrow. Replace one distractor with a plausible wrong integrating mechanism (e.g., C: 'ERP system that manages financial reporting across business units'). Eliminate one of the two COMS items (179 or 197)."),
    # 180
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean factual item from the inventory turnover passage. KEY=C (sophisticated inventory management software) requires knowing the specific contributor cited. A (decrease in SKUs) is a partial contributor but not the primary cited factor. B (improved forecasting) and D (top management focus) are both mentioned as contributing factors in Items 103/112, suggesting they are also contributors -- verify the chunk directly specifies software (C) as a key contributor distinct from B and D."),
    # 181
    (5,3,4,False,"REVISE","True",True,True,False,True,False,
     "B is correct (SCOR focuses on benchmarking logistics operations across industries). A and C describe GSCF characteristics (inter-firm relationships, collaborative capabilities). Using GSCF features as SCOR distractors is educationally appropriate for the hard/medium level, but these items are labeled 'easy.' dm=False confirmed. At easy level, the GSCF distractors require knowing both frameworks -- more appropriate for medium level. Reclassify as medium or replace A/C with simpler wrong answers about SCOR's purpose."),
    # 182
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "The stem asks for 'the deterministic COMPONENT' g(p). A shows D(p,ε) = g(p) + ε which is the FULL demand expression (both deterministic and stochastic components). A student could confuse A with B since both correctly describe the model -- A is the full expression, B is just g(p). Clarify the stem: 'What is the formula for g(p), the deterministic component of demand in the additive model?' to make the A vs B discrimination unambiguous."),
    # 183
    (1,3,4,False,"REJECT","True",False,True,False,True,False,
     "Reviewer REJECT confirmed. The chunk (dist=0) is about the mathematical derivation of q_t formula (q_t = y_t - y_{t-1} + D_{t-1}) -- not the general conceptual definition of bullwhip. Also: sixth+ near-duplicate of bullwhip definition question (Items 167, 174, 175, 187, 195). REJECT on both wrong-chunk and excessive-duplication grounds."),
    # 184
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "D ('decreased administrative costs') is not merely an 'unmentioned' factor in rising logistics costs -- it describes a COST-REDUCING trend, making it obviously the NOT-contributing answer. Same weak NOT-question pattern as Items 103/112 where the answer is the opposite of the theme rather than simply unmentioned. Replace D with something that sounds plausible as a cost driver but was not specifically mentioned (e.g., D: 'Increasing insurance premiums for freight liability coverage')."),
    # 185
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "Near-duplicate of Items 108, 114, and 116 (multi-plant capacity allocation algorithm). C is correct (sum of excess capacities from top plants determines how many operate at reduced capacity). B (highest cost multiplier alone) determines which plants are reduced, not how MANY. D (index of plant with l-th highest cost = j(l) definition) is a different variable. Near-duplication of the same algorithm sub-question at easy level -- this version should be consolidated with the hard-level versions."),
    # 186
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean item on logistics scorecard purpose. B is directly stated in the chunk. A (identify dept. inefficiencies = internal focus only), C (solely internal efficiency), D (employee performance) all narrow the scope inappropriately. Good discrimination between the integrative external benchmarking purpose (B) and the internal-focus wrong answers."),
    # 187
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean bullwhip definition item. C is correct. A (demand stable), B (orders decrease upstream = opposite of bullwhip), D (lead times no impact = wrong). Note: seventh near-duplicate of bullwhip definition question across the dataset. Flag for dataset curation to eliminate redundancy."),
    # 188
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Specific factual item about U.S. agricultural sector equity performance post-2020. B correctly identifies that strong commodity demand compensated for supply chain cost pressures. A (equity dropped), C (fell then recovered), D (unaffected) all contradict the passage which states equities 'have risen substantially.' Good discrimination between the compensating mechanism (B) and simpler wrong claims."),
    # 189
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean factual item about PepsiCo sourcing optimization. D (12.3 million additional cases) is a specific quantified outcome. A (50% reduction -- wrong percentage), B (transport miles UP -- a cost increase not a benefit), C (decrease in cases = opposite of the actual outcome) are all wrong. Note: near-duplicate of Item 172 (same case study outcome); 189 adds the specific '12.3 million' quantification which makes it slightly harder (requires recalling the specific number)."),
    # 190
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean item on SC strategy development steps. D is directly stated as the FIRST step in the chunk ('First, develop a clear strategy and identify appropriate means of focus'). A (detailed analysis), B (identify major decisions), C (develop scale curves) are all later steps or parallel activities. Good sequential knowledge test."),
    # 191
    (3,2,4,False,"REVISE","True",True,False,False,True,False,
     "KEY=B is problematic: the 'selling price per unit (p)' is the variable being OPTIMIZED in the newsboy-with-pricing problem -- it cannot be its own determining factor. The question asks for a 'key factor in DETERMINING optimal price' and then lists p itself as the answer. This is circular. The correct answer should reference an exogenous factor that determines p* (e.g., cost c, demand elasticity, or the critical fractile). dq=2: A (cost c), C (critical fractile formula), and D (demand distribution) are all more defensible answers than B (p itself). Rewrite the question to ask about the optimal pricing condition."),
    # 192
    (5,4,5,True,"REVISE","True",True,False,False,True,True,
     "FLAG: Potential wrong key. In EOQ, hQ/2 = h × (Q/2) where Q/2 is AVERAGE INVENTORY and h is HOLDING COST RATE. So hQ/2 is the AVERAGE HOLDING COST per unit time (not the average inventory level). KEY=C says hQ/2 represents 'average inventory level' which is Q/2 without h. KEY=B ('holding cost for positive inventory over a cycle time') is more accurate. Reviewer ACCEPT with sa=5 may be in error. Expert must re-verify: does the source text define hQ/2 as the 'average inventory level' or as the 'holding cost'?"),
    # 193
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean item on logistics scorecard framework components. A is correct as the first/primary component (identify measurable outcomes aligned with customer value). B (mapping enabling processes), C (defining logistics-strategy linkage), D (identifying performance drivers) are all also real scorecard components but secondary. The question implicitly tests which component is primary or listed first in the framework."),
    # 194
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean mechanistic item on why centralization reduces safety stock. B correctly identifies risk pooling (serving same service level with less total stock due to variance reduction from pooling). A ('better monitoring of variability') is a plausible-sounding wrong mechanism -- monitoring ≠ pooling. C ('simplifies management by reducing locations') is a benefit but not the mechanism for stock reduction. D ('easier supplier access reduces lead time') is an unrelated supply side benefit."),
    # 195
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean bullwhip definition item. C is correct. A, B, D are clearly wrong. Note: eighth near-duplicate of bullwhip definition across dataset (167, 174, 175, 183, 187, 195 plus duplicates). The haiku/haiku condition appears to have generated excessive repetition of this concept. Flag for dataset curation: retain at most 2 bullwhip definition items, eliminate the rest."),
    # 196
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean item on SC integration barriers. B correctly identifies rigid functional silos as the primary barrier per the chunk. A (increased pace of change = a business challenge, not itself the barrier), C (lack of cross-functional teams = a SYMPTOM of functional silos, not the primary barrier), D (inconsistent service delivery = an outcome of integration failure, not the barrier itself). Good conceptual discrimination."),
    # 197
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean COMS definition item. B is directly stated in the chunk. A (financial transactions), C (customer inquiries), D (track inventory/shipping) are all too narrow for COMS's integrating role. Near-duplicate of Item 179 -- one version should be eliminated. Prefer 197 which has slightly more precise wrong answers (A, C, D are more specific narrow functions vs 179's A which is 'manage complaints and returns')."),
    # 198
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean 2021 ocean freight rate item. B correct. A (decreased global demand = opposite), C (lower operational costs = contradicts rising fuel), D (reduced commodity demand = incorrect as ag demand surged). Near-duplicate of Item 166 (same question, same distractors, same key). One version should be eliminated."),
    # 199
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean SCM focus definition item. D correct (balance cost + service). A, B, C are all one-dimensional extremes that ignore the cost-service trade-off. Near-duplicate of Item 171 (same question, D vs C as key). Both should be reviewed for consolidation -- 199 uses D while 171 uses C. The two items have different keys for essentially the same question, suggesting a key conflict: verify that the source supports one specific answer."),
    # 200
    (3,2,4,False,"REJECT","Partial",True,False,False,False,True,
     "CRITICAL: Wrong correct key. D states 'ZICO policy applies to problems WITHOUT capacity constraints' -- this is definitively incorrect. ZICO (Zero Inventory CAPACITY Ordering) was specifically developed for CAPACITY-CONSTRAINED problems as an extension of ZIO. The true statement is C: 'ZIO policy states that inventory at end of [period] × production = 0' (the zero-inventory ordering condition). KEY=C is correct, not KEY=D. REJECT -- wrong key. Same wrong-key pattern as Items 119/123. dq=2 confirmed: A (Wagner-Whitin minimizes only holding costs = wrong) and B (orders without ordering cost = wrong) are wrong, D is wrong, leaving C as the only true statement, making D's selection as key an error."),
]

COLS = [
    "claude_source_alignment", "claude_distractor_quality", "claude_stem_clarity",
    "claude_difficulty_match", "claude_decision", "agrees_with_reviewer",
    "chunks_support_question", "correct_answer_verifiable", "distractors_clearly_wrong",
    "reviewer_source_call_accurate", "flag_ambiguity", "claude_notes",
]

decisions = []
for offset, row in enumerate(RAW):
    item = items[150 + offset]
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
print(f"Batch 4 written: {len(decisions)} items")
for k, v in sorted(decisions_count.items()):
    print(f"  {k}: {v}")
