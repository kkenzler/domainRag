"""Generate batch003.json — Claude review decisions for items 101-150."""
import json
from pathlib import Path

INPUT = Path("claude_review_input.json")
OUTPUT = Path("batch003.json")

with open(INPUT, encoding="utf-8") as f:
    items = json.load(f)

# (align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag, notes)
RAW = [
    # 101
    (3,2,4,False,"REVISE","True",True,True,False,True,False,
     "Distractors C (No-shortage EOQ) and D (Infinite planning horizon) are implausible -- no-shortage EOQ by definition precludes shortage scenarios, and infinite planning horizon is unrelated to shortage type. Only A (Lost sale) is a genuine near-miss. Replace C and D with plausible shortage variants (e.g., partial-backorder case or service-level-constrained shortage case)."),
    # 102
    (3,3,4,False,"REJECT","Partial",True,True,False,False,False,
     "REJECT confirmed on distractor quality: D (color preference for packaging) is a joke answer with zero plausibility -- same pattern as Items 43 and 98. A, B, C are all legitimate inventory model dimensions per the chunk. Reviewer's sa=1 is too harsh; chunk (dist=0) directly covers inventory model dimensions (supply characteristics, demand patterns, operational constraints). The REJECT is warranted but the reason is distractor failure, not source misalignment."),
    # 103
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean item, well-supported by chunk. Near-duplicate of Item 112 exists but 103 has better distractor variety (B/C/D are distinct factors vs 112 where D is just the opposite of a listed factor). If one version is eliminated, prefer 103."),
    # 104
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean item. The ZIO/zero-or-full-capacity property is precisely stated in the chunk. Distractor D (can vary as long as it does not exceed cumulative) is a good near-miss representing a plausible but incorrect relaxation of the constraint."),
    # 105
    (3,4,3,False,"REVISE","True",True,True,False,True,False,
     "Potential double-correct-answer: D ('for time-dependent capacity constraints, ZICO can be solved via shortest path') is also a true statement per the ZICO theory. C (final production order = remaining demand) is uniquely correct, but D needs to be revised to something clearly false about the solution method. Also: A applies to ZIO generally, not just the comparison with ZICO. Restructure to test specifically the final-order property that distinguishes ZICO."),
    # 106
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "Clean, well-supported item. Bullwhip amplification in decentralized systems is a core SC result directly supported by the chunk. D ('mitigated by sophisticated demand models') is a good near-miss since it represents a genuine mitigation strategy -- the trap is that it's a fix not an inherent property."),
    # 107
    (1,4,5,False,"REJECT","Partial",False,True,False,True,False,
     "CRITICAL: Chunk mismatch. Dist=0 chunk is about quantity discounts (suppliers offering lower unit prices for larger orders), not the single-period newsboy problem. Question content is academically correct (C is right for newsboy) but the retrieval system pulled the wrong chunk. REJECT due to wrong source material. Reviewer's REVISE is too lenient -- wrong chunk is a reject-level issue requiring re-embedding."),
    # 108
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Technically challenging item testing the l* calculation step. The fractional adjustment (C) uniquely distinguishes l* from l1, requiring genuine understanding of the optimization algorithm. Distractors A (avg cost multiplier -- input not output), B (finding l1 -- the preceding step), D (ranking -- the first step) create a plausible progression through the algorithm that traps students who confuse sequential steps."),
    # 109
    (2,2,4,False,"REVISE","True",False,True,False,True,False,
     "Distractors C and D misuse inventory motive terminology in opposite directions: C says centralization 'increases transaction motive' (wrong -- transaction motive is about purchase economies, not warehouse location) and D says 'precautionary motive strengthened' (wrong -- centralization REDUCES precautionary stock via pooling). Replace C and D with plausible alternatives (e.g., C: 'reduces transportation costs per unit shipped' or D: 'eliminates regional demand variation entirely'). Chunk (dist=0) gives Xerox/Dell examples, not the mathematical rationale for risk pooling."),
    # 110
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean factual item. Dell build-to-order direct model is a well-documented SC case study. All distractors represent plausible alternative business models (indirect retail, hybrid, retail-focus), making this a genuine test of factual knowledge."),
    # 111
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "B is correct (short window = less smoothing = higher order variability). However C says 'longer window causes overestimation of mean demand' which is incorrect -- longer window causes LAG in tracking demand shifts, not overestimation of mean. D ('longer window reduces impact of safety stock adjustments') is vaguely worded. Replace C and D with more precise statements (e.g., C: 'shorter window amplifies seasonal spikes because it overweights recent peaks'; D: 'longer window leads to underreaction to demand trend shifts')."),
    # 112
    (2,2,4,False,"REJECT","Partial",True,True,False,True,False,
     "Near-duplicate of Item 103 (same inventory turnover improvement question, same chunk). Additionally: D (Increased number of SKUs) is not merely an 'unmentioned' factor -- it is the direct OPPOSITE of a mentioned factor (SKU reduction), making this a weak negative-question design. Eliminate in favor of Item 103 which has better distractor variety and cleaner NOT-format structure."),
    # 113
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Well-constructed item on Asian Paradigm dual safety stock thresholds. B correctly identifies that ocean (lower cost, slower) has the lower threshold: when inventory is still ample you order by ocean; when it drops further you switch to air emergency replenishment. Distractor C (air lower threshold) is a plausible reversal trap. D (thresholds determined by SC size) sounds reasonable but conflates SC scope with trigger levels."),
    # 114
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Companion to Item 108, testing a different step of the same multi-plant algorithm. C correctly identifies finding l1 (max m such that sum of excess capacities from top m plants meets demand) as the step that determines how many plants operate at full capacity. This is a distinct sub-question from 108 (which asks about l*), so both items can coexist without being duplicates."),
    # 115
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "Clean risk-pooling item. B correctly captures when centralization provides maximum benefit: high variance AND negative correlation (both effects amplify pooling benefit). A (low variability, positive correlation) is an excellent near-miss trap -- students might think low variability is the condition since you want total variance to decrease."),
    # 116
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "The specific numbers (133 1/3 capacity per plant, 5 plants) are given in the stem but don't affect the answer -- the correct algorithm step is the same regardless of specific values. This makes a hard-labeled question that only tests medium-level algorithm recognition. Either (a) require actual computation using the given numbers (e.g., compute whether l1=2 or 3) to justify hard rating, or (b) relabel as medium and remove the specific capacity values."),
    # 117
    (2,2,4,False,"REVISE","True",False,False,False,True,False,
     "The full question text appears truncated in review (revenue function R(z,p) specification cut off in export). Cannot evaluate correctness of key=C without knowing which specific parameter change is being asked about. Additionally: distractors A, B, D (decrease, unchanged, cannot be determined) are weak for a hard mathematical question -- 'cannot be determined' is a low-quality cop-out distractor. A proper hard newsboy-with-pricing item should show the specific functional forms and require students to derive the directional effect."),
    # 118
    (4,3,5,False,"REVISE","True",True,True,True,True,False,
     "Difficulty mismatch: A (maintain silos), C (add logistics on top of vertical structure), D (increase hierarchy) are all obviously wrong to any student who has read the chapter. The question is fundamentally 'does SC integration require cross-functional teams?' which is medium-level recognition. Reclassify as medium OR redesign with plausible alternatives to B that also involve some form of reorganization (e.g., A: 'matrix organization with dual reporting lines to both function and customer')."),
    # 119
    (2,4,2,False,"REJECT","Partial",True,False,False,False,True,
     "CRITICAL: Wrong correct key. As shortage cost π increases, the optimal shortage level s* should DECREASE (higher shortage cost → less tolerance for backorders → smaller allowable backorder quantity). Option A ('π increases → s* decreases') is economically correct. Key=B ('π increases → s* increases') contradicts inventory management theory. Additionally, B's explanation is truncated/garbled ('higher shortage costs make it less...'). REJECT -- wrong key + sc=2. Expert re-verification required: confirm exact definition of s* in source material (reorder point vs max shortage level would reverse the analysis)."),
    # 120
    (2,3,4,False,"REVISE","True",False,True,True,True,False,
     "Chunk (dist=0) is about the additive demand model with pricing (D(p,ε) = g(p)+ε), not the basic newsboy problem. While B is academically correct for the newsboy, the source is mismatched. Also: C (minimizing expected shortages → implies order infinity) and D (fixed quantity regardless of variability) are too obviously wrong for a hard item. REVISE: match question to appropriate chunk OR rework distractors (e.g., C: 'determined by the critical ratio cu/(cu+co)' as a related but distinct formulation that tests understanding of the formula)."),
    # 121
    (2,4,2,False,"REVISE","True",False,False,False,True,False,
     "Stem contradiction: the scenario says a firm wants to 'minimize holding costs while maintaining operational efficiency' -- this setup most naturally points to transaction or precautionary motive, NOT speculative motive (key=C). Speculative motive (buying in anticipation of future price increases) INCREASES expected holding costs, directly contradicting the stem's objective. Rewrite: if C (speculative motive) is correct, the scenario must describe a firm timing purchases ahead of known price increases, not minimizing holding costs. As written, stem and key are contradictory."),
    # 122
    (3,4,4,False,"REVISE","True",False,True,False,True,False,
     "Two plausibly correct answers: A (buyback agreement) and B (revenue sharing contract) are both valid SC coordination mechanisms that enable near-optimal stocking under uncertain demand. The question provides no discriminating basis for choosing A over B -- both shift risk to achieve channel coordination. Revise to include only one coordination mechanism among options, or add specific context (e.g., 'the supplier has offered to repurchase all unsold units at the wholesale price -- which contract type is this and what is its effect?')."),
    # 123
    (2,4,2,False,"REJECT","Partial",True,False,False,False,True,
     "CRITICAL: Near-duplicate of Item 119 (same EOQ backorder π/s* relationship, just framed with decreasing π). Both items share the same apparent wrong-key problem: if 119 key=B (π↑→s*↑) and 123 key=C (π↓→s*↓), these are consistent but both appear economically incorrect (higher shortage cost should reduce allowable shortage). Multiple items testing the same relationship with a potential systematic wrong key is unacceptable. REJECT both 119 and 123 pending expert re-verification of the s* parameter definition."),
    # 124
    (3,4,2,False,"REVISE","True",True,True,False,True,False,
     "C ('can be either higher or lower') is a hedge answer that sophisticated students will choose to avoid commitment. In the newsboy-with-pricing model the deterministic price is always lower than the stochastic price (uncertainty creates a markup premium), making B correct and C a trap-for-the-cautious rather than a genuine wrong answer. Revise C to state a specific false claim about when deterministic price would be higher, forcing genuine discrimination. Stem clarity (sc=2) must also be improved -- specify what parameter or distributional change is being asked about."),
    # 125
    (5,4,3,True,"ACCEPT","True",True,True,False,True,False,
     "Reviewer ACCEPT is reasonable. However: B uses 'amplifies exponentially' -- the mathematical result (Var(q)/Var(D) ≥ 1+2L/p) is polynomial in lead time and window parameters, not exponential. Verify 'exponentially' is the source text's exact characterization. If not precisely supported, REVISE B to 'amplifies significantly' or the quantitatively accurate descriptor. C ('centralized info sharing eliminates it entirely') is a good trap -- centralization reduces bullwhip but cannot eliminate it if demand is stochastic."),
    # 126
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "Well-constructed item capturing the centralization trade-off. D correctly notes that centralization reduces both safety stock AND average inventory but at the cost of higher transportation/handling costs. This tests whether students know the FULL economic picture. B (reduces both, no caveats) is a strong near-miss trap that rewards students who know the transportation cost trade-off."),
    # 127
    (3,4,2,False,"REVISE","True",True,True,False,True,False,
     "Stem asks how SC management 'integrates' physical and information flows, but options describe what each flow does in isolation. B correctly identifies information flow's coordination role but doesn't address integration directly. D reverses the usual characterization (physical flow is forecast-driven in push, actual-order-driven in pull -- D has it backwards). Rewrite stem to ask specifically about the COORDINATION mechanism between flows rather than their independent characteristics."),
    # 128
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "Clean item on logistics as the transforming agent in SC integration. B is well-supported by the COMS chunk. A (logistics as secondary function supporting each department) is a plausible near-miss representing the traditional pre-integration view of logistics. C and D are obviously wrong but don't harm the item since A provides a genuine distractor."),
    # 129
    (3,3,5,False,"REJECT","Partial",True,True,False,True,False,
     "Duplicate of Item 115: identical concept (which scenario benefits most from centralized inventory), same correct answer (B: high variability + negative correlation), same answer structure. Item 115 has slightly better distractor framing (A uses 'positive correlation' as a clear near-miss trap). Eliminate Item 129 -- retain 115."),
    # 130
    (2,4,5,False,"REJECT","Partial",False,True,False,False,False,
     "CRITICAL: Wrong chunk (dist=0). The chunk is about quantity discounts (suppliers offering lower unit prices for larger orders), not buyback agreements. Question content is academically correct (buyback raises retailer's effective selling price → higher optimal Q) but source material is completely mismatched. REJECT. Same wrong-chunk retrieval pattern as Items 107, 132, 136, and 146. Reviewer's REVISE is too lenient."),
    # 131
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "Both B (multiple products + stochastic demand + setup reduction + space constraints) and C (perishable + endogenous pricing demand) represent highly complex inventory models. The question provides no clear basis for preferring C over B since both involve multiple complexity dimensions. Add an explicit complexity hierarchy or refocus the stem on the unique complexity of ENDOGENOUS pricing (the distinguishing feature of C) vs. the structural complexity of B (multiple products + joint constraints)."),
    # 132
    (1,4,3,False,"REJECT","Partial",False,True,False,False,False,
     "CRITICAL: Chunk mismatch. The dist=0 chunk is about functional silos causing supply chain sub-optimization -- completely unrelated to Activity-Based Costing or Throughput Accounting. The question content is academically defensible (both ABC and Throughput Accounting improve cost transparency over traditional volume-based costing) but the retrieved chunk provides zero support. REJECT due to wrong chunk. Reviewer's REVISE is too lenient."),
    # 133
    (3,4,2,False,"REVISE","True",True,True,False,True,False,
     "C ('at least as large as demand variance') is mathematically precise for the bullwhip result. D ('increases proportionally') is also technically true given the proportional relationship in the Var(q_t)/Var(D_t) formula. This creates a potential double-correct-answer between C and D. Revise D to 'increases by exactly the factor 1+2L/p where L is lead time' (which is a specific claim that either confirms or contradicts the source's formula, not equivalent to C's 'at least' formulation)."),
    # 134
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "Well-constructed strategic sourcing item. A correctly identifies the OPERATIONAL input factors (freight costs, duties, tariffs) that drive sourcing decisions -- distinct from strategic outputs (C) or abstract strategy elements (D). B (technical capability constraints) is a good near-miss. The distinction between operational inputs (A), strategy elements (D), and strategic outputs (C) tests sophisticated understanding of SC decision hierarchy."),
    # 135
    (4,3,5,False,"REVISE","True",True,True,True,True,False,
     "C ('increased internal capacity by 50% across all industries') is an obviously fabricated statistic -- no student familiar with outsourcing trends would choose this. Replace with a plausible alternative (e.g., 'companies outsourced non-core functions primarily to reduce domestic labor costs while keeping production onshore'). Difficulty mismatch: basic outsourcing comprehension labeled hard. Reclassify as medium."),
    # 136
    (1,4,2,False,"REJECT","Partial",False,True,False,False,False,
     "CRITICAL: Chunk mismatch. The dist=0 chunk is about Asian Paradigm dual-mode transportation (ocean vs air replenishment), completely unrelated to production technology scale curves and unit cost economics. The question content is valid (technology unit cost curves vary -- piecewise linear scale economics) but unsupported by the retrieved chunk. REJECT -- wrong source. Same pattern as Items 107, 130, 132, and 146."),
    # 137
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "The stem asks for the 'most effective strategy for a company needing responsiveness.' C (flexible manufacturing + JIT) addresses responsiveness; A (centralize for scale) addresses efficiency but sacrifices responsiveness. The tension is implicit. Revise stem to explicitly state BOTH requirements (responsiveness AND global scale) to force the C vs A discrimination. As written, students who focus only on 'global scale' may be drawn to A."),
    # 138
    (4,3,5,False,"REVISE","True",True,True,True,True,False,
     "C is obviously correct (examine processes + look outside industry = benchmarking definition). A (internal metrics only), B (only direct competitors), and D (avoid non-aligned insights) all obviously contradict benchmarking principles. Difficulty mismatch: this is a recall question about benchmarking definition, not hard level. Either reclassify or replace distractors with nuanced alternatives (e.g., B: 'compare only operations benchmarks from direct competitors using identical KPIs' -- sounds systematic but is too narrow)."),
    # 139
    (3,4,4,False,"REVISE","True",False,False,False,True,False,
     "All four options (cost/service pressure, shorter PLC, e-commerce, powerful customers) are legitimate contemporary SC trends. The question provides no discriminating basis for choosing D over A, B, or C without additional context. Chunk (dist=0) discusses development vs. fulfillment SC dichotomy, not specifically customer power. Either tie to a specific passage result or restructure: 'which trend most directly requires coordination AT THE DEMAND INTERFACE between SC partners?' which more naturally identifies D."),
    # 140
    (3,4,2,False,"REVISE","True",True,True,False,True,False,
     "Options B, C, and D describe pull model characteristics but are presented as wrong answers about push models, creating potential misreading. B ('pull prioritizes long-term planning') is wrong. D ('push emphasizes rapid response to actual customer demand') is incorrect (that's pull -- push responds to forecasts). C appears to describe pull. Rewrite D to unambiguously describe a push model characteristic -- the current 'actual customer demand' phrasing is exactly the language used for pull systems, causing confusion."),
    # 141
    (5,4,3,False,"REVISE","True",True,True,False,True,False,
     "'Market mediation' in the stem is discipline-specific jargon (Fisher 1997) not defined in the question. Students unfamiliar with this term cannot interpret whether B or C better achieves 'market mediation.' Since the core concept (COMS as integrating mechanism) is straightforward, the jargon adds ambiguity without adding discrimination. Either define 'market mediation' parenthetically in the stem or replace with 'cross-functional order fulfillment efficiency' which is directly aligned with COMS's described purpose."),
    # 142
    (5,4,3,False,"REVISE","True",True,True,False,True,False,
     "A (ZICO extends ZIO to capacity-constrained) is directly supported by the chunk. However D ('ZICO can be solved using shortest path algorithms with time-dependent constraints') is also a true statement based on the ZICO theory in earlier items. This creates a double-correct-answer problem between A and D. Revise D to state something false about the ZICO solution method (e.g., D: 'ZICO requires branch-and-bound since the ZIO shortest-path structure breaks down under capacity constraints' -- this is false; ZICO maintains a shortest-path structure)."),
    # 143
    (5,3,4,False,"REVISE","True",True,True,False,True,False,
     "A ('fostering collaboration') is too obviously wrong -- silos by definition reduce collaboration. The question effectively becomes 2-option between B (inventory buildup via independent optimization) and the remaining distractors. C ('ensuring accurate demand signals') is the OPPOSITE of what silos cause. D ('using ABC/Throughput Accounting') describes a solution not a mechanism. Replace A with a plausible-but-wrong sub-optimization mechanism (e.g., A: 'creating clear accountability through specialization, improving local efficiency at the cost of cross-functional visibility')."),
    # 144
    (3,4,4,False,"REVISE","True",True,True,True,True,False,
     "B is correct (retailers estimating variance from limited history). But A (short lead times), C (direct demand data), and D (safety stocks based on actual demand) all describe conditions that HELP REDUCE bullwhip -- they are negative causes rather than neutral wrong answers. A better design would have plausible-but-wrong causes of bullwhip as distractors (e.g., A: 'batch ordering to obtain quantity discounts' -- which IS a real bullwhip cause but not the one tested here)."),
    # 145
    (5,4,3,False,"ACCEPT","True",True,True,False,True,False,
     "Reviewer ACCEPT is appropriate. SCOR/GSCF distinction is well-defined and the item correctly identifies B (SCOR = internal operations, GSCF = inter-firm relationships). sc=3 reflects framework-name familiarity requirement, appropriate for hard level. D ('both equally concerned with relationship management') is a plausible trap for students who associate both frameworks with supply chain coordination broadly."),
    # 146
    (1,3,4,False,"REJECT","Partial",False,True,False,True,False,
     "CRITICAL: Chunk mismatch. The dist=0 chunk is about information systems facilitating SC decisions -- completely unrelated to bullwhip effect tier inventory patterns. B's content (higher inventory at distributors) is directionally correct for bullwhip but is not precisely supported: bullwhip amplification goes upstream, meaning MANUFACTURERS hold more safety stock than distributors who hold more than retailers. Reviewer sa=1 is accurate. REJECT due to wrong chunk -- same wrong-retrieval pattern as Items 107, 130, 132, 136."),
    # 147
    (2,4,2,False,"REJECT","Partial",False,True,False,False,False,
     "CRITICAL: Chunk mismatch. The dist=0 chunk is about production scale analysis (volume vs. unit cost across manufacturing technologies) -- completely unrelated to product variety and SC network configuration decisions. The question content is academically valid (high variety → dispersed network for local responsiveness) but completely unsupported by the retrieved chunk. REJECT -- wrong source. Reviewer's REVISE is too lenient."),
    # 148
    (4,3,5,False,"REVISE","True",True,True,True,True,False,
     "B is clearly correct (strategic outputs like delivery and service level influence operational inventory decisions). A (operational = short-term only), C (alignment impossible), D (operational = cost minimization only) are all obviously wrong to any student familiar with SC strategy. Difficulty mismatch: this is basic SC strategy concept recognition labeled hard. Reclassify as medium or replace distractors with nuanced alternatives (e.g., A: 'operational decisions are upstream inputs that constrain strategic choice, not the reverse')."),
    # 149
    (3,4,2,False,"REVISE","True",False,False,False,True,False,
     "Stem is ambiguous about the decision frame: it says a company is 'considering whether to centralize' then asks which scenario -- but C (high variability across multiple locations) is exactly the condition where centralization HELPS most via risk pooling. This argues FOR centralization, not against it. If the answer is C, the question should explicitly ask 'which scenario most strongly supports the decision to centralize?' As written, students cannot determine if the question asks for pro- or anti-centralization conditions."),
    # 150
    (4,3,5,False,"REVISE","True",False,True,True,True,False,
     "Near-duplicate of Item 120 (same basic newsboy concept: optimal Q balances marginal costs). C ('higher OQ guarantees higher sales') is obviously wrong given uncertain demand. D ('no impact on inventory risk') is trivially wrong. A ('always increases average profit') is a classic error but not highly plausible. This is a medium-level newsboy concept mislabeled as hard. Eliminate in favor of Item 120 OR redesign with more sophisticated distractors (e.g., C: 'optimal Q equals the critical ratio cu/(cu+co)' -- confusing the decision rule with the input parameter)."),
]

COLS = [
    "claude_source_alignment", "claude_distractor_quality", "claude_stem_clarity",
    "claude_difficulty_match", "claude_decision", "agrees_with_reviewer",
    "chunks_support_question", "correct_answer_verifiable", "distractors_clearly_wrong",
    "reviewer_source_call_accurate", "flag_ambiguity", "claude_notes",
]

decisions = []
for offset, row in enumerate(RAW):
    item = items[100 + offset]
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
print(f"Batch 3 written: {len(decisions)} items")
for k, v in sorted(decisions_count.items()):
    print(f"  {k}: {v}")
