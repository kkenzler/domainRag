"""
Claude Human Review scoring script for items 0-99.
Writes batch_0000_0099.json to the same directory.
"""
import json
from pathlib import Path

# Manual scoring decisions based on reviewing each item's question, options, correct_key, and chunks.
# Keys: index into the 100-item slice (0–99).
# Each entry: (sa, dq, sc, dm, decision, agrees, ambig, chunks_support, verifiable, dist_wrong, rev_sa_accurate, notes)

scores = [
    # IDX 0 — item_1, easy, REVISE
    # Q: key benefit of risk pooling. Correct=B (reduces safety stock via combined variability).
    # Chunk 0 perfectly supports B. Option C implies no safety stock needed at each warehouse — misleading but not catastrophically wrong.
    # Option D (eliminates bullwhip) is incorrect per chunk (chunk says bullwhip can be reduced not eliminated).
    # SA=5 accurate. DQ: C is somewhat plausible, D is more easily dismissed. DM: easy is fine. SC=4 is fair.
    # Decision: REVISE (D is clearly wrong; C is misleading but option quality is mixed).
    (5, 3, 4, 4, "REVISE", True, False, True, True, False, True,
     "Chunk 0 perfectly grounds the correct answer B. Option D (eliminates bullwhip) is clearly wrong and easily dismissed; option C is partially misleading — risk pooling does reduce safety stock but doesn't eliminate it — making distractor quality uneven and a REVISE appropriate."),

    # IDX 1 — item_2, easy, ACCEPT
    # Q: bullwhip effect and demand variability. Correct=B. Chunks directly support. A is directly contradicted, C is wrong, D is wrong.
    # Perfect item. Agrees with ACCEPT.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunks directly state that small consumer demand changes amplify into large upstream fluctuations, perfectly grounding answer B. All three distractors are clearly contradicted by the chunks."),

    # IDX 2 — item_3, easy, REVISE
    # Q=None; options ARE the questions (multi-stem format). correct_key=C|B|A|D — garbled item.
    # This is a badly structured item: the question stem is None, and options are themselves questions.
    # This is fundamentally a malformed item — should be REJECT not REVISE.
    (2, 2, 1, 2, "REJECT", False, True, True, False, False, False,
     "The question stem is None and the answer options are themselves full questions, indicating a generation failure that produced a multi-stem item rather than a single MCQ. The correct_key C|B|A|D is meaningless, making this item unscoreable and irreparable by revision alone."),

    # IDX 3 — item_4, easy, REVISE
    # Q=None again; options are full statements about EOQ. correct_key=D.
    # Q stem is None — same malformed pattern. Correct answer D (EOQ assumptions) is verifiable from chunks.
    # But with no stem, item is fundamentally broken.
    (3, 3, 1, 3, "REJECT", False, True, True, True, False, False,
     "The question stem is None; options are declarative statements about EOQ without a guiding question. While the correct answer D (EOQ assumptions) is supported by chunk content, the absence of a stem makes this unacceptable as an MCQ item without a complete rewrite."),

    # IDX 4 — item_5, easy, ACCEPT
    # Q: What does the bullwhip effect refer to? Correct=B. Chunk directly defines it. A is opposite. C contradicts. D wrong.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk 1 provides a verbatim definition matching answer B. The distractors are clearly wrong to anyone familiar with the concept, appropriate for an easy item."),

    # IDX 5 — item_6, easy, ACCEPT
    # Q: Little's Law and inventory/lead times. Correct=B. Chunk 0 directly states longer lead times → higher inventory → amplifies variability.
    # C is too absolute ("always"). D is directly contradicted.
    (5, 3, 4, 4, "ACCEPT", True, False, True, True, True, True,
     "Chunk 0 directly states the relationship between lead times and inventory per Little's Law, grounding answer B. Option C's absolute phrasing is easily dismissed; the item is slightly generous on distractor quality for an easy item."),

    # IDX 6 — item_7, easy, REVISE
    # Q=None again; multi-stem. correct_key=B|A|C|D. Same generation failure.
    (2, 2, 1, 2, "REJECT", False, True, True, False, False, False,
     "Same structural failure as item_3: question stem is None and options are themselves separate questions, with correct_key B|A|C|D indicating a garbled multi-question item that cannot be used as a single MCQ."),

    # IDX 7 — item_8, easy, REVISE
    # Q: key strategic concern of dispersed supply chains. Correct=C (scale economies + logistics optimization).
    # Chunk 0 discusses FMS, JIT, global complexity. Chunk 1 mentions global optimization.
    # C is supported — scale economies at facilities. A (reducing suppliers) not grounded. B (minimizing transport) too narrow. D (increasing inventory) contradicted.
    # The reviewer called REVISE; I agree — C is close but the chunk says "exploiting scale economies at individual facilities AND optimizing logistics" which matches C well. Easy tag seems appropriate.
    (4, 3, 4, 4, "REVISE", True, False, True, True, False, True,
     "Chunk 0 references scale economies and logistical optimization relevant to dispersed supply chains, loosely grounding answer C. However, option B (minimizing transportation costs) is a plausible distractor that could mislead test-takers since transportation is prominently discussed, warranting revision."),

    # IDX 8 — item_9, easy, ACCEPT
    # Same as item_6 (Little's Law). Correct=B. Chunk directly supports. Nearly identical to item_6.
    # Near-duplicate of item_6 (item_9 vs item_6 differ only in option C/D wording).
    (5, 3, 4, 4, "ACCEPT", True, False, True, True, True, True,
     "Chunk directly supports the relationship between lead times and inventory amplification per Little's Law, grounding B. This item is nearly identical to item_6; distractor quality is moderate for an easy item but the correct answer is clearly verifiable."),

    # IDX 9 — item_10, easy, REVISE
    # Q=None. Options are statements about ZICO/DELS. correct_key=B.
    # No stem — structurally broken. But B is the correct ZICO theorem statement (verifiable from chunk 0).
    (3, 3, 1, 3, "REJECT", False, True, True, True, False, False,
     "The question stem is None; options are declarative statements about the capacitated DELS model. While answer B correctly states the ZICO theorem as found in chunk 0, the complete absence of a question stem makes this unusable as an MCQ without a full rewrite."),

    # IDX 10 — item_11, easy, REVISE
    # Q: what traditional accounting fails to provide. Correct=B (transparency into true costs by segment/channel).
    # Chunk 0 directly states "making it difficult to see the true cost of serving different customers or channels." B is perfectly grounded.
    # A (financial reports) — accounting does provide those. C (inventory levels) — also tracked. D (production efficiency) — partially tracked.
    # Reviewer called REVISE; I'd consider ACCEPT. The item is clean. Distractors are plausible for easy.
    (5, 3, 4, 4, "ACCEPT", False, False, True, True, True, True,
     "Chunk 0 directly states that traditional accounting fails to reveal true costs across customer segments and channels, perfectly grounding answer B. The distractors are plausible for an easy item and the stem is clear; ACCEPT is warranted despite the reviewer's REVISE."),

    # IDX 11 — item_12, easy, REVISE
    # Q=None. Multi-stem again. correct_key=B|A|C|D. Same failure.
    (2, 2, 1, 2, "REJECT", False, True, True, False, False, False,
     "Question stem is None with options being independent questions and a multi-part correct key — another garbled generation output that is irreparable without a complete rewrite."),

    # IDX 12 — item_13, easy, REVISE
    # Q: which principle does NOT apply. Correct=A ("Forecasts are always perfectly accurate").
    # Chunk says "forecasting is always wrong." So A correctly identifies the false principle.
    # B, C, D are all true per the chunk. This is a "NOT" question — stems are fine but "NOT" framing is slightly tricky.
    # Reviewer said REVISE. I agree — "NOT" phrasing can be tricky; the item is otherwise well-grounded.
    (5, 4, 4, 4, "REVISE", True, False, True, True, True, True,
     "Chunk clearly states the three forecasting principles, making A (the false statement 'forecasts are always accurate') verifiable. The 'does NOT apply' framing adds cognitive complexity beyond easy level and the near-opposite wording of A vs. the chunk may cause confusion."),

    # IDX 13 — item_14, easy, REVISE
    # Q=None. Multi-stem. correct_key=B|C|D|A. Same failure pattern.
    (2, 2, 1, 2, "REJECT", False, True, True, False, False, False,
     "No question stem; options are separate questions with multi-part correct key — a structurally broken generation artifact requiring full rewrite."),

    # IDX 14 — item_15, easy, REVISE
    # Q: What does cumulative production Y_k represent in capacitated shortest path network? Correct=B.
    # Chunk 0: "Y_k = sum of production quantities from period i+1 to k." B says exactly that.
    # A says "total demand for all periods up to k" — wrong. C says "max capacity constraint" — wrong. D says "minimum cost" — wrong.
    # SA is good, stem is clear. Reviewer said REVISE — perhaps because it's technical and the "easy" tag is questionable.
    # The concept is advanced (capacitated DELS shortest path) for an easy tag. Difficulty mismatch.
    (5, 4, 4, 2, "REVISE", True, False, True, True, True, True,
     "Chunk 0 directly defines Y_k as the sum of production quantities from i+1 to k, fully grounding answer B. However, the capacitated shortest-path network concept is distinctly advanced (medium-hard level) making the 'easy' difficulty label a significant mismatch."),

    # IDX 15 — item_16, easy, ACCEPT
    # Q: EOQ true statement. Correct=B (infinite horizon, constant deterministic demand). Chunk directly states these assumptions.
    # A (variable ordering cost per unit) — wrong, EOQ has variable cost c but the formula uses it differently. C wrong. D wrong.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly states EOQ assumptions including infinite planning horizon and constant deterministic demand, perfectly grounding B. Distractors are plausible misconceptions for an easy item."),

    # IDX 16 — item_17, easy, ACCEPT
    # Q: difference between SC planning and execution systems. Correct=A.
    # Chunk says: "planning systems enable firms to model supply chain, generate forecasts, develop sourcing plans" vs "execution systems manage flow of products through distribution centers."
    # A matches exactly. B is wrong (not supplier vs distributor split). C inverts capabilities. D is wrong.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk directly distinguishes planning systems (forecasting/optimization) from execution systems (product flow management), perfectly grounding A. All distractors introduce plausible but incorrect distinctions."),

    # IDX 17 — item_18, easy, REVISE
    # Q: which factor most amplifies bullwhip? Correct=C (many stages in supply chain).
    # Chunk 1 says: "Structure drives behavior, and causes of the bullwhip effect include lack of visibility, long lead times, many supply chain stages, lack of pull signals, order batching, price discounts and promotions, forward buying, and rationing."
    # B (perfect information sharing) reduces bullwhip per chunk. A (short lead times) reduces it. D (low demand variability) reduces it.
    # C is a valid cause but so are long lead times (A=short lead times). The question asks for "most responsible" — the chunk lists many factors equally. Slight ambiguity.
    (4, 3, 4, 4, "REVISE", True, True, True, True, False, True,
     "Chunks list multiple co-equal causes of the bullwhip effect including many stages, long lead times, and lack of visibility; singling out 'many stages' as the amplifier is defensible but potentially ambiguous since long lead times (option A phrased as short lead times) is also prominent in the chunk. Distractor quality suffers because option B (perfect information) is a bullwhip mitigation, not a neutral or irrelevant choice."),

    # IDX 18 — item_19, easy, ACCEPT
    # Q: primary benefit of Union Carbide storefront concept. Correct=A (centralizing inventory/distribution, decentralizing customer-facing).
    # Chunk 0 directly describes storefront concept. B, C, D not grounded.
    (5, 3, 5, 4, "ACCEPT", True, False, True, True, True, True,
     "Chunk 0 explicitly states the storefront concept centralizes inventory/distribution while decentralizing customer-facing functions, directly grounding answer A. The distractors are not supported by the chunks but are plausible enough for an easy item."),

    # IDX 19 — item_20, easy, REVISE
    # Q=None. Options are statements about ZIO/DELS. correct_key=A.
    # A says "ZIO policy states order placed only if inventory at end of previous period is zero." This is the ZIO definition per chunk.
    # But stem is None — broken.
    (3, 3, 1, 3, "REJECT", False, True, True, True, False, False,
     "Question stem is None; declarative option statements about the DELS/ZIO model with no guiding question. Answer A correctly states the ZIO policy per the chunk, but without a stem the item cannot function as an MCQ."),

    # IDX 20 — item_21, easy, REVISE
    # Q: primary reason for inefficiency in conventional org structures. Correct=B.
    # Chunk 0 (21st century challenges) mentions functional silos and departmental focus. B (overemphasis on individual departmental goals) is grounded.
    # A (excessive communication) — not in chunks. C (lack of technology) — not the primary reason stated. D (insufficient management layers) — not grounded.
    # SA is good, but reviewer said REVISE — possibly because the chunk mentions this in broader business context.
    (4, 3, 4, 4, "REVISE", True, False, True, True, True, True,
     "Chunk discusses how conventional hierarchical structures prioritize departmental objectives over overall efficiency, supporting answer B. The stem is clear but options A and C are not easily eliminated by someone with only partial knowledge, and the item is labeled easy despite requiring specific recall of the org-structure critique."),

    # IDX 21 — item_22, easy, REVISE
    # Q=None. Multi-stem. correct_key=B|C|D|B. Same failure.
    (2, 2, 1, 2, "REJECT", False, True, True, False, False, False,
     "Question stem is None with multi-part correct key — a structurally broken generation output that is unrepairable without complete rewrite."),

    # IDX 22 — item_23, easy, REVISE
    # Q: strategic challenge for supply chain firms. Correct=B (balancing global product volumes with regional market presence).
    # Chunk 0 says "lower-scale, higher-skill manufacturing" and global complexity. Chunk 1 mentions global optimization difficulty.
    # B is partially supported (global vs. regional balance). A (perfect synchronization) — too absolute, not grounded. C (employee satisfaction) — irrelevant. D (constant oil prices) — absurd distractor.
    # D is trivially dismissible, reducing DQ. B is the least-bad option but not precisely stated in chunks.
    (3, 2, 4, 4, "REVISE", True, False, True, False, False, True,
     "The chunks discuss global supply chain complexity at a high level but do not explicitly mention 'balancing global product volumes with regional market presence' as a specific challenge. Option D (constant oil prices) is a trivially dismissible distractor, and the correct answer requires inference rather than direct lookup."),

    # IDX 23 — item_24, easy, REVISE
    # Q: EOQ assumes no shortages — how does this impact total cost function? correct_key=A|B (two correct?).
    # A: "total cost is minimized when there are no shortages" — this follows from the no-shortage assumption.
    # The EOQ model with no shortages has a single objective: minimize ordering + holding cost. Shortages are prohibited so we can't compare.
    # Chunk has the EOQ model with planned backorders (separate model). The question is about the base EOQ.
    # Having two correct keys (A|B) indicates a generation error. This is ambiguous/broken.
    (3, 3, 3, 3, "REJECT", False, True, True, False, False, False,
     "The correct_key A|B indicates two correct answers, which is a generation error — a single-answer MCQ cannot have two correct keys. The question also has a subtle logical issue: the 'no shortages' assumption in EOQ means shortages are excluded from the model, so statements about their effect on cost are ambiguous and not directly verifiable from the chunks."),

    # IDX 24 — item_25, easy, REVISE
    # Q: applying focus in SC strategy reduces what. Correct=A (complexity).
    # Chunk says "Focus can be achieved along several dimensions" and the benefit of focus is implied to reduce complexity.
    # Chunk 0 says focus reduces complexity (product/market/process focus). A is grounded. B, C, D not specifically stated.
    (4, 3, 4, 4, "REVISE", True, False, True, True, True, True,
     "Chunk references supply chain focus reducing complexity, grounding answer A. However, the stem is very sparse and the other options (operational tasks, fixed costs, variable costs) could all plausibly be things focus reduces, making the distractors somewhat ambiguous without stronger chunk grounding."),

    # IDX 25 — item_26, easy, ACCEPT
    # Q: EPQ assumes P > D. Correct=B. Chunk on EPQ... Let me check: chunk 0 mentions EOQ with backorders, not EPQ directly.
    # Actually the EPQ chunk isn't in the retrieved chunks shown. Chunk 0 is about EOQ backorders, chunk 1 about EOQ sensitivity.
    # The EPQ assumption (P > D) is a standard fact but not directly in the provided chunks. SA might be lower.
    (3, 3, 4, 4, "REVISE", False, False, False, False, True, False,
     "The retrieved chunks cover EOQ with backorders and EOQ sensitivity but do not explicitly discuss the Economic Production Quantity (EPQ) model's assumption that P > D. The correct answer B is standard knowledge but not directly verifiable from the provided chunk content, reducing source alignment."),

    # IDX 26 — item_27, easy, ACCEPT
    # Q: capacity-constrained production sequence in DELS. Correct=B.
    # Chunk 0 on DELS capacity constraints and chunk 1 on ZICO. The capacity-constrained sequence definition (at most one period has 0 < y_k < C_k) is in the chunk.
    # B is a very precise technical statement matching the chunk. For easy difficulty, this is quite advanced.
    (5, 4, 4, 2, "REVISE", False, False, True, True, True, True,
     "The chunk explicitly defines a capacity-constrained production sequence exactly as stated in answer B. However, this is a highly technical DELS concept that is inappropriate for 'easy' difficulty — it requires understanding of the capacitated production model, making the difficulty label a significant mismatch."),

    # IDX 27 — item_28, easy, REVISE
    # Q: impact of SC disruptions on U.S. agricultural sector financial performance. Correct=B (unaffected despite pressures).
    # Chunk says stock prices rose and no statistically significant negative effects. B is correct.
    # A says "significantly harmed" — wrong. C says only food processing/retail affected — not what chunks say. D says chemicals saw decline — wrong.
    # Well-grounded. Reviewer said REVISE — possibly because B says "unaffected" which is slightly stronger than "no statistically significant negative effects."
    (4, 4, 4, 4, "REVISE", True, True, True, True, True, True,
     "Chunk states 'no statistically significant negative effects' while answer B says 'unaffected' — a slight overstatement that introduces ambiguity for a knowledgeable reader. The agricultural sector chunk supports the general direction of B but the precise wording diverges from the research finding."),

    # IDX 28 — item_29, easy, REVISE
    # Q: inventory management primary aim. Correct=B (balance between minimizing costs and achieving target service levels).
    # Chunk says "minimizing total system cost subject to satisfying service requirements." B captures this exactly.
    # A (minimize production costs exclusively) — too narrow. C (maximize sales revenue) — wrong. D (eliminate customer service) — absurd.
    # Reviewer said REVISE — perhaps because D is trivially dismissible (absurd), reducing DQ.
    (5, 2, 5, 4, "REVISE", True, False, True, True, False, True,
     "Chunk directly states the cost-service balance objective of inventory management, grounding answer B perfectly. However, distractor D (eliminate customer service) is trivially absurd and easily dismissed, substantially reducing distractor quality below acceptable standards."),

    # IDX 29 — item_30, easy, ACCEPT
    # Q: key benefit of benchmarking. Correct=C (standardized common language for comparing logistics operations).
    # Chunk says benchmarking provides a "standardized common language" — exact match to C.
    # A (guarantees sales) — wrong. B (guarantees order fulfillment) — wrong. D (eliminates customer feedback) — wrong.
    (5, 3, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly mentions benchmarking provides a 'standardized common language' for comparing logistics operations, directly verifying answer C. Distractors A, B, D use extreme language ('guarantees', 'eliminates') that makes them dismissible but plausible enough for an easy item."),

    # IDX 30 — item_31, easy, REVISE
    # Q: primary goal of SCM. Correct=B (minimize total system cost subject to satisfying service requirements).
    # Chunk says exactly that. B is perfectly grounded.
    # A (maximize profits by increasing production costs) — contradicts chunk. C (all suppliers in same region) — not grounded. D (solely customer satisfaction) — too narrow.
    # Reviewer said REVISE — perhaps because the item is clean but D could be confused with the SCM definition.
    (5, 3, 5, 5, "ACCEPT", False, False, True, True, True, True,
     "The chunk provides a verbatim match to answer B. The item is well-structured and clean; the reviewer's REVISE appears to be overly conservative for this straightforward and well-grounded item — ACCEPT is warranted."),

    # IDX 31 — item_32, easy, REVISE
    # Q: which principle does NOT apply. Correct=A (forecasts are always accurate). Chunk says always wrong.
    # Near-duplicate of item_13. Same NOT framing issue.
    (5, 4, 4, 4, "REVISE", True, False, True, True, True, True,
     "A near-duplicate of item_13 with the same 'does NOT apply' framing; the chunk clearly supports identifying A as the false statement. The negation phrasing adds complexity above typical easy-level and the item should be re-evaluated for deduplication."),

    # IDX 32 — item_33, easy, ACCEPT
    # Q: ZIO policy true statement. Correct=B (optimal solution: no orders placed when inventory is non-zero).
    # Chunk directly states ZIO: I_{t-1} * y_t = 0 for all t. B captures this.
    # A (order when inventory non-zero) — directly contradicts. C (only for time-independent costs) — wrong. D (order every period) — wrong.
    (5, 4, 5, 4, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly states the ZIO condition I_{t-1}·y_t=0 for all t, directly grounding answer B. The distractors present plausible misconceptions about when ordering occurs, appropriate for a moderately technical easy item."),

    # IDX 33 — item_34, easy, ACCEPT
    # Q: purpose of benchmarking in logistics. Correct=B. Chunk says "comparing logistics operations against industry leaders, competitors, and customer expectations for continuous improvement."
    # B matches exactly. A (solely internal) — wrong. C (without external partners) — wrong. D (unrelated to performance measurement) — wrong.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk directly states the comparative and continuous-improvement purpose of benchmarking, perfectly grounding answer B. All distractors contradict the chunk's explicit description."),

    # IDX 34 — item_35, easy, REVISE
    # Q: ZIO policy description. Correct=B (order only if inventory at end of previous period is zero).
    # Chunk directly supports this. B is correct. A (every period) — wrong. C (never placed) — wrong. D (carry over without ordering) — wrong.
    # Slight duplicate of item_33. DQ is good.
    (5, 4, 4, 4, "ACCEPT", False, False, True, True, True, True,
     "Chunk directly defines the ZIO policy as ordering only when previous-period inventory is zero, grounding B. This is nearly identical to item_33 (ZIO); the reviewer's REVISE may reflect concern about duplication rather than item quality — the item itself is clean and ACCEPT is warranted."),

    # IDX 35 — item_36, easy, ACCEPT
    # Q: physical flow in supply chains. Correct=A.
    # Chunk directly says "Physical flow involves the transformation, movement, and storage of goods." A matches exactly.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk provides a verbatim definition of physical flow matching answer A exactly. Distractors B (information flow), C (financial flow), D (human resource flow) are all plausible supply chain flow types, with C and D requiring knowledge to eliminate."),

    # IDX 36 — item_37, easy, REVISE
    # Q=None. Multi-stem. correct_key=B|C. Same failure.
    (2, 2, 1, 2, "REJECT", False, True, True, False, False, False,
     "Question stem is None with multi-part correct key B|C — a structurally broken multi-question item that cannot function as a single MCQ."),

    # IDX 37 — item_38, easy, REVISE
    # Q: key benefit of risk pooling. Correct=B (reduces need to hold separate safety stocks at each warehouse).
    # Chunk supports B directly. A (increases total safety stock) — wrong. C (higher transaction costs) — contradicts chunk. D (eliminates precautionary motive) — too extreme and not grounded.
    # D is somewhat dismissible (eliminates precautionary motive entirely) — partially plausible if misunderstanding pooling.
    (5, 3, 4, 4, "REVISE", True, False, True, True, False, True,
     "Chunk directly supports answer B. Distractor D claims risk pooling eliminates the precautionary motive entirely, which is too extreme but partially plausible for test-takers who confuse risk reduction with risk elimination; item quality is slightly uneven across distractors."),

    # IDX 38 — item_39, easy, ACCEPT
    # Q=None. Multi-stem. correct_key=A|B|C. Same failure.
    # Wait — reviewer says ACCEPT. But this has Q=None and multi-part key. This should be rejected.
    (2, 2, 1, 2, "REJECT", False, True, True, False, False, False,
     "Question stem is None with a multi-part correct key A|B|C, indicating a garbled multi-question generation. The automated reviewer's ACCEPT decision appears to be erroneous for this structurally invalid item."),

    # IDX 39 — item_40, easy, ACCEPT
    # Q: primary goal of SCM. Correct=B (maximize customer value by delivering products when/where/how customers want at low cost).
    # Chunk says SCM is "active management...to maximize customer value and achieve a sustainable competitive advantage." B matches.
    # A (internal only) — wrong. C (minimize suppliers) — wrong. D (increase production costs) — absurd.
    (5, 3, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk directly states that SCM aims to maximize customer value, grounding B. Option D (increase production costs for quality) is easily dismissed; distractor quality is moderate but acceptable for an easy item."),

    # IDX 40 — item_41, easy, ACCEPT
    # Q: key benefit of risk pooling. Correct=B (reduces safety stock by consolidating inventory). Duplicate of items 1 and 38.
    # Chunk directly supports. C (eliminates safety stock entirely) — too extreme, clearly wrong.
    (5, 3, 4, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk directly defines risk pooling and its safety stock reduction benefit, grounding B. Option C (eliminates all safety stock) is clearly wrong from the chunk, and the item is appropriately easy. Note: this is a near-duplicate of items 1 and 38."),

    # IDX 41 — item_42, easy, REVISE
    # Q: type of ordering cost where lower per-unit price applies to entire order. Correct=D (all-units discounts).
    # Chunk says: "Under all-units discounts, a lower unit price c₂ < c₁ applies to the entire order once quantity exceeds threshold q." D matches exactly.
    # A (linear) — wrong. B (concave) — wrong. C (general ordering costs) — general category, not specific.
    (5, 3, 4, 4, "ACCEPT", False, False, True, True, True, True,
     "Chunk explicitly defines all-units discounts with the threshold mechanism described in the question, directly grounding answer D. The reviewer's REVISE seems overly conservative — this is a clean, well-grounded item. Option C (general ordering costs) is a plausible but clearly distinct category per the chunk."),

    # IDX 42 — item_43, easy, ACCEPT
    # Q: factor causing increase in ocean freight rates. Correct=D (destination port congestion).
    # Chunk says: empirical analysis shows demand for shipping, fuel prices, port congestion affect rates. D is supported.
    # A (decreased demand) — would decrease rates. B (lower fuel) — would decrease rates. C (increased fleet capacity) — would decrease rates.
    (5, 4, 4, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk on ocean freight rate determinants includes port congestion as a demand-side factor driving rates up, grounding D. The other three distractors all represent factors that would decrease rates, making them plausible but clearly wrong for someone who understands supply/demand dynamics."),

    # IDX 43 — item_44, easy, REVISE
    # Q: primary reason Blockbuster market share increased after revenue sharing. Correct=A.
    # Chunk says: "Before 1998, Blockbuster purchased cassette copies for $65 each and rented for $3, requiring at least 22 rentals per copy to earn a profit. This high breakeven point meant retailers could not justify purchasing enough copies to meet peak demand."
    # Answer A says "high breakeven point for cassette copies decreased, allowing more rentals." But the chunk says the high breakeven point PREVENTED enough copies before the revenue sharing. After revenue sharing, the breakeven dropped, allowing more copies and thus better availability.
    # A is somewhat misleadingly worded ("decreased" breakeven is correct) but the causal chain is right.
    # B (could afford more copies) — also true post-revenue sharing. C (customers could rent desired movie) — outcome not cause. D (rental income higher) — not primary reason for market share.
    (4, 3, 4, 4, "REVISE", True, True, True, True, False, True,
     "Chunk supports that the high pre-1998 breakeven prevented sufficient stock; revenue sharing reduced the effective cost per copy (lowering the breakeven), grounding A. However, answer B (Blockbuster could afford more copies) is also directly implied by the same mechanism, creating genuine ambiguity between A and B for knowledgeable test-takers."),

    # IDX 44 — item_45, easy, ACCEPT
    # Q: ZIO policy true statement. Correct=C (it is never optimal to carry inventory into a period when an order is placed).
    # Chunk states ZIO: I_{t-1} * y_t = 0, meaning if inventory > 0, y_t = 0, i.e., no order when inventory is carried. Equivalently, if order is placed, inventory must be zero. C captures this.
    # A (order even with inventory) — wrong. B (only time-independent costs) — wrong. D (each order covers several periods) — this is a TRUE property of ZIO but isn't the "if and only if" statement about carrying inventory.
    (5, 4, 4, 4, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly states the ZIO condition; C correctly rephrases it as 'never optimal to carry inventory into a period when an order is placed.' D is also a true property of ZIO (covered demand for several consecutive periods) but is a different statement, making it a good distractor requiring careful distinction."),

    # IDX 45 — item_46, easy, REVISE
    # Q=None. Declarative statements. correct_key=A.
    # Same pattern as other None-stem items.
    (3, 3, 1, 3, "REJECT", False, True, True, True, False, False,
     "Question stem is None; options are declarative statements about the capacitated DELS model. While answer A correctly states the ZICO condition, the absence of a stem makes this item non-functional as an MCQ."),

    # IDX 46 — item_47, easy, ACCEPT
    # Q: why U.S. agricultural companies' stock prices rose despite SC pressures. Correct=B (infrastructure improvements eased congestion).
    # Chunk says stock prices rose substantially. The chunk mentions no statistically significant negative effects.
    # B (infrastructure improvements) is stated in the chunk as a possible reason.
    (4, 3, 4, 4, "ACCEPT", True, False, True, True, True, True,
     "Chunks support that U.S. agricultural stock prices rose and that infrastructure improvements helped ease congestion pressures, grounding B. The item is clean with plausible distractors, though infrastructure improvements is mentioned briefly in the chunk context."),

    # IDX 47 — item_48, easy, ACCEPT
    # Q: trend in U.S. agricultural stock indices. Correct=B (increase despite high SC pressures).
    # Chunk directly states stock prices rose. B is exact.
    (5, 3, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly states that U.S. agricultural sector stock price indices rose substantially despite supply chain pressures, directly grounding B. Distractors A and C are clearly contradicted by the chunk."),

    # IDX 48 — item_49, easy, REVISE
    # Q=None. Multi-stem. correct_key=B|A|C|D.
    (2, 2, 1, 2, "REJECT", False, True, True, False, False, False,
     "Question stem is None with a garbled multi-part correct key — structurally broken item requiring complete rewrite."),

    # IDX 49 — item_50, easy, ACCEPT
    # Q: key benefit of risk pooling. Correct=B (reduces combined variability of demand across multiple markets).
    # Chunk: "combined demand has a lower coefficient of variation (CV) than either individual market." B is correct.
    # Another near-duplicate of risk pooling items. C (eliminates safety stock) — too extreme. D (guarantees higher margins) — not grounded.
    (5, 3, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk directly states that consolidating inventory reduces combined demand variability (lower CV), grounding B. This is a clean, well-grounded item though it is a near-duplicate of several other risk-pooling questions in this batch."),

    # ============ MEDIUM DIFFICULTY ITEMS ============

    # IDX 50 — medium item_1, ACCEPT
    # Q: volume-process focus "on" focus. Correct=B (separate facilities for specific volume-process combinations).
    # Chunk says when focus is "on": separate facilities dedicated (Detroit for job work, Fremont for batch). B matches.
    # A (single plant serving all) — that's focus "off." C (subcontract) — not described. D (logistics strategic outputs) — irrelevant.
    (5, 4, 4, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly describes 'on' focus as separate facilities dedicated to specific volume-process combinations, using the exact Detroit/Fremont example in option B. Distractor A correctly describes focus 'off,' requiring knowledge to distinguish."),

    # IDX 51 — medium item_2, REVISE
    # Q: bullwhip effect with lead time L. Correct=D (bullwhip increased when lead times longer because leads to higher inventory levels which increases demand forecast variance).
    # Chunk says bullwhip is increasing function of lead time. D's causal chain (longer LT → higher inventory → increased forecast variance) is partially right but the primary mechanism per chunk is that longer LT increases the var(q)/var(D) ratio.
    # D's reasoning (higher inventory → increased demand forecast variance) is imprecise but directionally correct.
    # Options A, B, C have "bullwhipeffect" as one word (typo).
    (4, 3, 3, 5, "REVISE", True, False, True, True, False, True,
     "Chunk confirms bullwhip effect increases with lead time, grounding D directionally. However, options A/B/C contain the typo 'bullwhipeffect' as one word, reducing stem clarity, and D's causal mechanism (longer LT → higher inventory → forecast variance) is an imprecise but plausible chain that could mislead careful readers."),

    # IDX 52 — medium item_3, REVISE
    # Q: SnowTime optimal production quantity if marginal profit = $45. Correct=A (10,000 units).
    # Chunk: SnowTime marginal profit = S - C = 125 - 80 = $45. Marginal cost unsold = C - V = 80 - 20 = $60. Critical ratio = 45/(45+60) = 45/105 = 0.4286. With average demand 13,000, looking at demand distribution, optimal qty at F^{-1}(0.4286).
    # The chunk doesn't provide the demand distribution details needed to confirm 10,000 units specifically. SA is lower.
    (3, 3, 4, 5, "REVISE", True, False, True, False, True, False,
     "The chunk confirms marginal profit = $45 (S-C = 125-80) and marginal cost unsold = $60 (C-V = 80-20), establishing a critical ratio, but the demand distribution required to derive the optimal quantity of 10,000 units is not provided in the retrieved chunks, making the correct answer unverifiable from sources alone."),

    # IDX 53 — medium item_4, ACCEPT
    # Q: role of benchmarking. Correct=B (ongoing comparison with best-in-class for improvement and competitive advantage).
    # Chunk directly supports. A (one-time activity) — wrong. C (only customer satisfaction) — wrong. D (only execution phase) — wrong.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly describes benchmarking as an ongoing process comparing with industry leaders for competitive advantage, perfectly grounding B. Distractor A (one-time activity) is a common misconception, making it a good distractor."),

    # IDX 54 — medium item_5, REVISE
    # Q: which factor reduces safety stock. Correct=A (decrease in customer demand variability).
    # Chunk: safety stock = z * STD * sqrt(LT). Decreased demand variability (STD) → less safety stock. A is correct.
    # B (increase in supplier lead times) → increases safety stock. C (decrease in products carried) — not directly related to safety stock formula. D (increase in production costs) — unrelated.
    # C could confuse test-takers since fewer products could reduce complexity. Reviewer said REVISE.
    (4, 3, 4, 5, "REVISE", True, False, True, True, False, True,
     "The safety stock formula in the chunk (z × STD × √LT) directly supports A since decreased demand variability (STD) reduces safety stock. Option C (fewer products) is a plausible-sounding but ungrounded distractor that may confuse without being clearly wrong from chunk content."),

    # IDX 55 — medium item_6, REVISE
    # Q: most effective strategy for reducing bullwhip. Correct=C (sharing point-of-sale data).
    # Primary chunk retrieved is risk pooling chunk, not the bullwhip mitigation chunk.
    # BUT: the bullwhip mitigation chunk IS in the data (chunk_index 2 in item_1): "Sharing point-of-sale data gives upstream partners visibility into actual consumer demand." C is supported.
    # The retrieved chunks for THIS item are risk pooling + inventory motives, not the direct bullwhip mitigation chunk. This is a retrieval mismatch issue.
    (3, 3, 4, 5, "REVISE", True, False, False, False, True, False,
     "The retrieved chunks for this item are primarily about risk pooling and inventory motives, not about bullwhip effect mitigation strategies. While option C (point-of-sale data sharing) is correct per domain knowledge, the specific bullwhip mitigation chunk is not among the retrieved chunks, making source alignment and verifiability from these chunks limited."),

    # IDX 56 — medium item_7, REVISE
    # Q: most responsible factor for amplifying demand variability. Correct=B (long lead times).
    # Chunk 0 directly says "Lead time plays a central role in amplifying the bullwhip effect."
    # B is strongly supported. A, C, D are also real causes but less central per the chunk.
    # However, the chunk also lists A (lack of visibility), C (order batching), D (price discounts) as causes.
    # Singling out B as "most responsible" is defensible given "Lead time plays a central role."
    (5, 3, 4, 5, "REVISE", True, True, True, True, False, True,
     "Chunk states that lead time 'plays a central role' in amplifying the bullwhip effect, supporting B. However, the chunk also lists lack of visibility, order batching, and price discounts as causes of equal standing; knowledgeable test-takers may flag ambiguity in identifying a single 'most responsible' factor."),

    # IDX 57 — medium item_8, REVISE
    # Q: primary barrier to effective SC integration. Correct=B (functional silos and hierarchical structures).
    # Chunk discusses how conventional structures prioritize departmental goals. B is grounded.
    # A (inadequate communication) — partially related but not the primary barrier stated. C (lack of tech) — not primary per chunk. D (insufficient training) — not in chunks.
    (5, 3, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk directly discusses functional silos and hierarchical structures that prioritize departmental goals as the primary barrier to supply chain integration, grounding B. The reviewer's REVISE appears overly conservative; this is a clean, well-supported item that merits ACCEPT."),

    # IDX 58 — medium item_9, ACCEPT
    # Q: key challenge in SCM. Correct=B (balancing cost minimization with service level satisfaction).
    # Chunk: SCM goal is "minimizing total system cost subject to satisfying service requirements." B captures the tension.
    # A (only internal) — wrong. C (identical objectives) — impossible/wrong. D (only production) — too narrow.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk defines SCM as balancing cost minimization with service requirements, directly grounding B. All three distractors represent common misconceptions about SCM scope, appropriate for medium difficulty."),

    # IDX 59 — medium item_10, ACCEPT
    # Q: factor with significant impact on ocean shipping rates during pandemic. Correct=D (port congestion AND higher fuel prices).
    # Chunk says: "destination port congestion and higher fuel prices" are demand-side factors per empirical analysis. D matches compound cause.
    # A (decreased demand) — wrong direction. B (lower fuel) — wrong direction. C (increased fleet AND port congestion) — C partially right (port congestion) but increased fleet capacity would decrease rates.
    (5, 4, 4, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk from empirical analysis explicitly names destination port congestion and fuel prices as factors driving higher shipping rates, grounding D. Option C is a near-miss (port congestion is correct but increased fleet capacity would decrease rates), making it a strong distractor requiring careful reading."),

    # IDX 60 — medium item_11, ACCEPT
    # Q: transaction motive for holding inventory. Correct=A (exploit economies of scale in production/transportation).
    # Chunk: "transaction motive involves exploiting economies of scale in production, transportation, discounts, and replenishment." A matches.
    # B (maintain competitive position) — also mentioned under transaction motive in chunk, but A is more core. Actually chunk says both are transaction motive.
    # This creates mild ambiguity: B is also listed as part of transaction motive in the chunk. Flag ambiguity.
    (4, 3, 4, 5, "REVISE", False, True, True, True, False, True,
     "The chunk lists both 'exploiting economies of scale' (A) and 'maintaining competitive position' (B) as part of the transaction motive, creating genuine ambiguity between A and B for a knowledgeable test-taker. The item should specify which aspect of the transaction motive is being asked about."),

    # IDX 61 — medium item_12, REVISE
    # Q: which is NOT a strategic concern of dispersed supply chains. Correct=D (reducing product variety).
    # Chunk on dispersed SC mentions scale economies (A), logistics optimization (B), operational focus (C). D (reducing product variety) is not mentioned.
    # A, B, C are legitimate concerns. D is not supported as a concern — so it's the NOT item.
    # The chunk is about globalization complexity, not specifically listing dispersed SC concerns as a list. SA is moderate.
    (3, 3, 4, 5, "REVISE", True, False, True, True, True, False,
     "The retrieved chunks discuss global supply chain challenges broadly but do not explicitly enumerate 'exploiting scale economies, optimizing logistics, achieving operational focus' as a defined list of dispersed supply chain strategic concerns. While D (reducing product variety) is clearly not mentioned, the grounding for A, B, C relies on inference rather than direct chunk support."),

    # IDX 62 — medium item_13, ACCEPT
    # Q: research on ocean shipping rate increases and US maritime agricultural exports. Correct=C (US gained market share in corn/soybeans).
    # Chunk says "no statistically significant negative effects on U.S. maritime agricultural exports" and implies US competitive position was maintained or improved. C is supported.
    # A (significant negative effect) — contradicted. B (lower producer prices) — not stated. D (substantial decrease) — contradicted.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly states no significant negative effects on US agricultural exports and implies market share gains for corn and soybeans, directly grounding C. All three distractors are clearly contradicted by the chunk."),

    # IDX 63 — medium item_14, REVISE
    # Q: Polaroid JoyCams dual safety stock policy addressed which challenge. Correct=B (long lead times, dual transport modes, demand uncertainty, min container size, accelerated requirements).
    # Chunk (Asian Paradigm Model): "characterized by long lead times, dual transportation modes (air and ocean), demand uncertainty, minimum container size constraints, and accelerated requirements schedules with constrained production." B matches exactly.
    # A (high fixed costs) — not specifically mentioned. C (single reorder point) — wrong. D (multi-period normally distributed) — that's the standard safety stock model.
    (5, 4, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk describes the Asian Paradigm Model addressing exactly the challenges listed in B (long lead times, dual transportation modes, demand uncertainty, min container size, accelerated schedules). The reviewer's REVISE appears unwarranted — the item is well-grounded and the correct answer B is precisely verifiable."),

    # IDX 64 — medium item_15, ACCEPT
    # Q: challenge in SCM. Correct=B (coordinating activities across different functional groups).
    # Chunk: SCM involves coordination across suppliers, factories, warehouses, stores. B is grounded.
    # A (identical objectives) — impossible. C (internal only) — wrong. D (ignoring integration) — contradicts SCM definition.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk defines SCM as integrating and coordinating across multiple functional groups, grounding B. All distractors either contradict the definition or describe what SCM explicitly avoids."),

    # IDX 65 — medium item_16, REVISE
    # Q: research findings during pandemic. Correct=C (despite higher ocean shipping costs, US gained market share in corn/soybeans).
    # Chunk directly supports: no significant negative effects and US gains in global market share. C is correct.
    # A (significant negative impact) — wrong. B (lower producer prices) — not stated. D (increased demand not associated with rates) — wrong.
    # Near-duplicate of item_13.
    (5, 4, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk directly states US maritime agricultural exports were unaffected and US gained market share in corn and soybeans, grounding C. This is a near-duplicate of medium item_13; the reviewer's REVISE may reflect concern about duplication. The item itself is clean and well-grounded — ACCEPT."),

    # IDX 66 — medium item_17, REVISE
    # Q=None. Correct=A.
    # Chunk says "each order placed covers exactly the demands of several consecutive periods" — but the options debate whether orders must be in consecutive periods.
    # A says "orders can cover demands for multiple periods but must be placed in consecutive periods." The chunk says EACH ORDER covers demands of SEVERAL CONSECUTIVE PERIODS — not that orders themselves must be placed consecutively.
    # A is actually WRONG: orders don't have to be placed in consecutive periods; rather, each individual order covers consecutive future periods.
    # The correct interpretation: an order placed in period t covers demands for periods t, t+1, ..., t+k (consecutive periods starting from t). Orders don't need to be placed in consecutive periods.
    # So A incorrectly states "must be placed in consecutive periods" — the chunk doesn't say that.
    # No stem means this item is malformed. Plus A may be incorrect.
    (3, 3, 1, 3, "REJECT", False, True, True, False, False, False,
     "Question stem is None, and the correct answer A appears to misstate the ZIO implication: the chunk says each order covers consecutive future demands, not that orders themselves must be placed in consecutive periods. This item has both a structural defect (no stem) and a potentially incorrect answer key."),

    # IDX 67 — medium item_18, ACCEPT
    # Q: decentralized vs centralized information — variability at stage k. Correct=B (larger due to multiplicative amplification factors).
    # Chunk: "In a multi-stage supply chain...Under centralized information...Var(q^i_t)/Var(D_t) = (1 + 2L_i/p)(1 + 2(L_1+...)/p)... under decentralized... multiplicative across stages."
    # B is correct — multiplicative amplification. A (smaller) — wrong. C (unchanged) — wrong. D (unpredictable) — wrong.
    (5, 4, 4, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk describes the multiplicative structure of variability amplification under decentralized information, directly grounding B. The technical nature of the question is appropriate for medium difficulty."),

    # IDX 68 — medium item_19, REVISE
    # Q: optimal price p* for additive demand model. Correct=B ((a + bc + E[min(z*, ε)]) / (2b)).
    # Chunk: "stochastic optimal price p* = (a + bc + E[min(z*, ε)])/(2b)." B matches exactly.
    # A (without E[min...] term) — that's p^0. C (multiplicative formula) — wrong. D (minus term) — wrong.
    # This is highly technical. For medium level, it's appropriate.
    (5, 4, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk provides the exact formula for p* = (a + bc + E[min(z*, ε)])/(2b), matching answer B precisely. The reviewer's REVISE seems unwarranted — the item is technically rigorous, well-grounded, and the correct answer is directly verifiable. ACCEPT is appropriate."),

    # IDX 69 — medium item_20, ACCEPT
    # Q: Dell Computer strategy for shareholder value growth. Correct=A (direct business model and build-to-order).
    # Chunk: "Dell Computer outperformed competitors in shareholder value growth by implementing a direct business model and build-to-order strategy." A matches.
    # B (jointly creating business plans) — that's Procter & Gamble. C (overhauling logistics) — not Dell. D (grocery industry) — not Dell.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly attributes Dell's shareholder value growth to its direct business model and build-to-order strategy, directly grounding A. Distractors B, C, D reference other companies or unrelated strategies from the same chunk, making them plausible but clearly wrong for Dell."),

    # IDX 70 — medium item_21, REVISE
    # Q: capacitated DELS optimal production sequences. Correct=B (at most one period with 0 < y_k < C_k).
    # Chunk: exactly describes capacity-constrained sequences with this property. B is correct.
    # A (always full capacity) — too restrictive. C (solely by period demand) — wrong. D (cumulative <= demand) — wrong (it should be >=).
    (5, 4, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk defines capacity-constrained production sequences as having at most one period with 0 < y_k < C_k, perfectly grounding B. The reviewer's REVISE appears unwarranted for this technically precise, well-grounded item. ACCEPT."),

    # IDX 71 — medium item_22, REVISE
    # Q: (s,S) policy reorder point. Correct=B (formula: LT × AVG + z × STD × √LT).
    # Chunk gives exact formula. B is correct.
    # A (only average demand) — missing safety stock. C (reorder > order-up-to S) — impossible by definition. D (doesn't account for variability) — wrong.
    (5, 4, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk provides the exact reorder point formula matching B. The reviewer's REVISE appears unwarranted — this is a clean, well-grounded item where B is precisely verifiable. Distractor A (ignoring safety stock) is a common misconception, making it a good medium-difficulty distractor. ACCEPT."),

    # IDX 72 — medium item_23, REVISE
    # Q: challenge in achieving effective SCM. Correct=A (inherent conflict between functional groups' objectives).
    # Chunk: "conflicting objectives among supply chain participants." A is grounded.
    # B (integrating legacy hierarchical structures) — partially grounded but not the primary challenge stated. C (only reducing costs) — wrong. D (only integration of suppliers/factories) — too narrow.
    (5, 3, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk explicitly discusses conflicting objectives among supply chain participants as a primary challenge, grounding A. Distractor B (integrating legacy structures) is partially plausible but the chunk specifically names the objectives conflict as the core challenge. ACCEPT over REVISE."),

    # IDX 73 — medium item_24, ACCEPT
    # Q: how benchmarking contributes to competitive advantage. Correct=B (ongoing comparison with industry leaders).
    # Chunk directly supports. Clean item.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly describes benchmarking as ongoing comparison with industry leaders for competitive advantage, directly grounding B. All distractors represent narrow or incorrect descriptions of benchmarking."),

    # IDX 74 — medium item_25, REVISE
    # Q: most effective strategy for reducing bullwhip. Correct=C (sharing point-of-sale data).
    # Same issue as medium item_6 (IDX 55): retrieved chunks are about risk pooling, not bullwhip mitigation.
    (3, 3, 4, 5, "REVISE", True, False, False, False, True, False,
     "Retrieved chunks are primarily about risk pooling and inventory motives rather than bullwhip effect mitigation. While C (POS data sharing) is correct per domain knowledge and supported by other chunks in the dataset, the specific mitigation chunk is not retrieved here, reducing grounding quality for this item."),

    # IDX 75 — medium item_26, ACCEPT
    # Q: why bullwhip effect is significant for businesses. Correct=A (small demand changes → large fluctuations at each stage).
    # Chunk directly says this. A is exactly stated. B, C, D are all consequences but not the primary definitional significance.
    (5, 3, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk directly states that small consumer demand changes translate into large upstream production and procurement swings, grounding A. The other options B, C, D represent real but secondary consequences, making them plausible but clearly less central distractors."),

    # IDX 76 — medium item_27, ACCEPT
    # Q: best description of bullwhip effect. Correct=C.
    # C: "small changes in end-customer demand can translate into large swings in upstream production and procurement due to inaccurate information amplification."
    # Chunk: this is the core definition. A has "accurate information" — wrong (it's inaccurate). B says variability decreases — wrong. D says chains become more efficient — wrong.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk provides a comprehensive definition of the bullwhip effect matching C. Distractors A, B, D each invert or distort a key element of the definition, requiring careful reading to eliminate."),

    # IDX 77 — medium item_28, REVISE
    # Q: role of SC planning systems. Correct=B (model existing SC, generate forecasts, develop sourcing plans).
    # Chunk: "Supply chain planning systems enable firms to model their existing supply chain, generate forecasts, and develop sourcing plans." B matches exactly.
    # A (manage flow) — that's execution. C (building, transporting, tracking) — execution. D (setting inventory targets, scheduling work centers) — more execution.
    # Reviewer said REVISE — perhaps because the stem could be clearer.
    (5, 3, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk provides a verbatim description matching answer B for supply chain planning systems. The reviewer's REVISE appears overly conservative for this well-grounded, clear item. Distractors A, C, D all describe execution system functions, appropriate for medium difficulty. ACCEPT."),

    # IDX 78 — medium item_29, ACCEPT
    # Q: 5-stage SC strategy — which stage evaluates transportation. Correct=D (Stage 4: evaluating location and process options).
    # Chunk: "Stage 4 evaluates location and process options." Transportation choices would fit here.
    # A (Stage 1: business/ops strategy) — too high level. B (Stage 2: technology scale curves) — not transportation. C (Stage 3: network options) — possible but stage 4 is more specific.
    (5, 4, 4, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk describes the five-stage approach with Stage 4 involving location and process evaluation including transportation, directly grounding D. Stage 3 (major network options) could also arguably involve transportation decisions, but D is more directly supported."),

    # IDX 79 — medium item_30, REVISE
    # Q=None. Multi-stem. correct_key=B|A|C|D.
    (2, 2, 1, 2, "REJECT", False, True, True, False, False, False,
     "Question stem is None with multi-part correct key — structurally broken generation output requiring complete rewrite."),

    # IDX 80 — medium item_31, ACCEPT
    # Q: Union Carbide storefront implementation. Correct=B (eliminated two of five distribution steps).
    # Chunk: storefront concept and distribution steps. The chunk mentions the storefront extends the supply chain by separating retail functions.
    # B says eliminated 2 of 5 steps. This specific numeric claim needs to be verified in the chunk.
    # Chunk mentions "five steps" in the storefront context. Let me check: chunk says "eliminating all five steps in their supply chain process" — no, that's option D in item_19. The storefront chunk says it "recognizes that the retailing or dealer end...bundles multiple distinct functions."
    # The specific "eliminated two out of five steps" claim needs chunk verification.
    (4, 3, 4, 4, "REVISE", True, False, True, False, True, True,
     "The storefront chunk discusses separating distribution functions but does not explicitly state that storefronts eliminated exactly two out of five steps. Answer B's specific numeric claim is not directly verifiable from the retrieved chunk text, requiring inference or external knowledge."),

    # IDX 81 — medium item_32, REVISE
    # Q: forecasting accuracy principles — which BEST REFLECTS the context. Correct=D ("Forecasting is always perfectly accurate").
    # Wait — D says "Forecasting is always perfectly accurate" — but this is FALSE. The question asks which "best reflects" the principles. If correct=D, it means D is the answer, but D is a false statement. That's a contradiction.
    # Actually looking at it: the question is "Which of the following statements best reflects the principles discussed regarding forecasting accuracy?" and the correct key is D. But D says "Forecasting is always perfectly accurate" — which is the OPPOSITE of what the chunk says.
    # This appears to be a wrong correct_key. The correct answer should be something like "forecasting is always wrong" (which isn't an option here, but closest to B: "Aggregate forecasts tend to be less accurate" — also wrong per chunk).
    # Actually A says "Long-term forecasts are more accurate than short-term" — wrong (chunk says opposite). B says "Aggregate forecasts LESS accurate than disaggregated" — wrong (chunk says aggregate MORE accurate). C says "longer horizon → better" — wrong. D says "always perfectly accurate" — wrong.
    # ALL options are false statements. The correct answer per chunk should be that D (perfectly accurate) is the most extreme falsehood. But the question asks which BEST REFLECTS — all are bad.
    # This is a fundamentally flawed item — wrong correct key likely. Should be REJECT.
    (2, 2, 3, 3, "REJECT", False, True, True, False, False, False,
     "All four answer options appear to contradict the chunk's forecasting principles: A inverts the horizon-accuracy relationship, B inverts the aggregate-accuracy finding, C inverts the horizon principle, and D claims perfect accuracy which the chunk explicitly refutes. The correct_key D is almost certainly wrong; this item has a fundamentally incorrect answer key and should be rejected."),

    # IDX 82 — medium item_33, REVISE
    # Q: strategy to improve planning accuracy. Correct=C (aggregating demand forecasts).
    # Chunk: "aggregate forecasts are more accurate than disaggregated ones." C is correct.
    # A (extending lead times) — would hurt accuracy. B (increasing forecast horizons) — would hurt accuracy per chunk. D (postponing replenishment) — not directly about forecast accuracy.
    # B is plausible (some might think longer horizon helps). D is a reasonable supply chain practice but not specifically about forecast accuracy.
    (5, 3, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk explicitly states that aggregate forecasts are more accurate, directly grounding C. Options A and B represent actions that would worsen accuracy per the chunk's principles, making them good distractors. ACCEPT over REVISE."),

    # IDX 83 — medium item_34, REVISE
    # Q: most critical strategy for firms facing global optimization challenges. Correct=C (aligning logistics policies to match strategic goals).
    # Chunk: "aligning logistics policies to further specific strategic goals and objectives." C is grounded.
    # A (reducing transportation costs only) — too narrow. B (prioritizing local over global) — opposite of what chunk suggests. D (ignoring non-tariff barriers) — obviously wrong.
    (4, 3, 4, 5, "REVISE", True, False, True, True, False, True,
     "Chunk references aligning logistics to strategic goals, supporting C. However, this is a high-level inference — the chunk doesn't make this as the singular solution to global optimization challenges. Distractor D (ignoring non-tariff barriers) is trivially dismissible, reducing distractor quality."),

    # IDX 84 — medium item_35, REVISE
    # Q: strategy to minimize inventory by receiving goods only when needed. Correct=A (just-in-time).
    # Chunk: "One important strategy for effective supply chain management is the just-in-time approach." A matches.
    # B (bullwhip effect) — a problem, not a strategy. C (information flow management) — too broad. D (physical flow optimization) — too broad.
    # The reviewer called REVISE — perhaps because the item asks about "minimizing inventory" but the chunk only briefly mentions JIT. The definition of JIT as receiving goods only when needed is standard knowledge.
    (4, 3, 4, 4, "REVISE", True, False, True, True, True, True,
     "Chunk briefly mentions JIT as an important strategy without explicitly defining it as minimizing inventory by receiving goods only when needed; the definition relies partly on external knowledge. Distractors B (bullwhip effect) is a problem not a strategy, making it easily dismissed."),

    # IDX 85 — medium item_36, ACCEPT
    # Q: inventory management practice Xerox implemented. Correct=C (eliminated $700 million in inventory).
    # Chunk directly states this fact.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly states Xerox eliminated $700 million in inventory, directly grounding C. All other options are plausible financial improvements but are not attributed to Xerox in the chunk."),

    # IDX 86 — medium item_37, ACCEPT
    # Q: difference between SC planning and execution systems. Correct=A.
    # A: "Planning systems focus on forecasting and optimization of manufacturing plans, while execution systems manage product flow in distribution centers."
    # Chunk: "planning systems enable firms to model...generate forecasts...develop sourcing plans" vs "execution systems manage the flow of products through distribution centers."
    # A matches. B inverts (inventory vs production scheduling). C (long-term vs short-term) — not quite the distinction in chunk. D (demand forecasts vs correct location) — both somewhat true but imprecise.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk explicitly distinguishes planning systems (forecasting, optimization, sourcing plans) from execution systems (managing product flow in distribution centers), grounding A exactly. All distractors blur this distinction in plausible ways."),

    # IDX 87 — medium item_38, REVISE
    # Q: logistics strategic output KPIs — which is NOT mentioned. Correct=D (customer satisfaction).
    # Chunk lists: "delivery or service time, customization and breadth of product line or service, service level on inventory, and variation of service level or delivery time."
    # Customer satisfaction is NOT in this list. D is correct.
    # A, B, C are all in the list. This is a solid NOT question.
    (5, 4, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk explicitly lists the four strategic outputs (delivery time, customization/breadth, service level on inventory, variation of service level), confirming D (customer satisfaction) is not among them. All distractors are directly from the chunk. The reviewer's REVISE appears unnecessary — ACCEPT."),

    # IDX 88 — medium item_39, ACCEPT
    # Q: role of benchmarking. Correct=B. Similar to other benchmarking items.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk directly describes benchmarking as comparing with competitors, industry leaders, and customer expectations for continuous improvement, grounding B. A near-duplicate of other benchmarking items; the item itself is clean and well-grounded."),

    # IDX 89 — medium item_40, REVISE
    # Q: forecasting principles — which statement best reflects. Correct=B ("Aggregate forecasts are less accurate than disaggregated ones").
    # Wait — B says "Aggregate forecasts are LESS accurate than disaggregated ones." But the chunk says "Aggregate forecasts are MORE accurate than disaggregated ones." B contradicts the chunk.
    # If correct=B, this is a wrong correct key.
    # Unless the question is asking which statement is FALSE (doesn't apply) — but the stem says "best reflects the principles." So B should be a true statement, but it contradicts the chunk.
    # This appears to be another wrong correct key. Should be REJECT.
    (2, 2, 3, 3, "REJECT", False, True, True, False, False, False,
     "The correct_key B states 'aggregate forecasts are LESS accurate than disaggregated ones' — directly contradicting the chunk which states aggregate forecasts are MORE accurate. This appears to be a wrong answer key. The item has a fundamental correctness error and must be rejected."),

    # IDX 90 — medium item_41, REVISE
    # Q: additive demand model — given marginal cost > profit, which is true about p*. Correct=C (p* > formula).
    # Chunk: "stochastic optimal price p* = (a + bc + E[min(z*, ε)])/(2b)" and "p⁰ > p*" (deterministic price exceeds stochastic).
    # The question says "marginal cost of overstocking exceeds the profit from selling an additional unit" — this means Co > Cu, which would lower the optimal order quantity below mean demand. How does this affect p*?
    # The chunk gives p* as stated. The question asks whether p* is >, =, or < the formula.
    # But p* IS the formula. So asking p* > p* doesn't make sense unless they're comparing to p⁰.
    # The correct answer C says p* > (a + bc + E[min(z*, ε)]) / (2b). But that formula IS p*. So C says p* > p*, which is impossible.
    # This is a confused/flawed item. The question may intend to compare p* to p⁰ under the given overstocking condition.
    (2, 2, 2, 4, "REJECT", False, True, True, False, False, False,
     "The correct answer C states p* is greater than the formula (a + bc + E[min(z*, ε)])/(2b), but this formula IS the definition of p* per the chunk, making C logically self-contradictory. The item appears to confuse p* with p⁰ and the condition about overstocking costs is not connected to the answer through clear logic. Fundamental flaw requiring rejection."),

    # IDX 91 — medium item_42, REVISE
    # Q: order-up-to point calculation. Given: L=2, p=3 (moving average), mu=100, S=25, z=1.96. Correct=B (286).
    # Chunk formula for multi-stage: y^i_t = L_i * mu + z * sqrt(L_i * (1 + 2*L_i/p)) * S_t (approximately).
    # Actually chunk: "Var(q^i)/Var(D) = (1 + 2L_i/p)(1+2(L_1+...L_{i-1})/p)" for decentralized. For single stage (retailer): y_t = L*mu + z*sqrt(L)*S.
    # With L=2, mu=100, S=25, z=1.96: y = 2*100 + 1.96*sqrt(2)*25 = 200 + 1.96*1.414*25 = 200 + 69.3 = ~269. That's not 286.
    # Let me try: if using variance formula from chunk for one stage: Var(q)/Var(D) = 1 + 2L/p = 1 + 2*2/3 = 1 + 4/3 = 7/3. Then adjusted std = 25*sqrt(7/3) = 25*1.528 = 38.2. y = 2*100 + 1.96*38.2 = 200 + 74.9 = ~275. Still not 286.
    # Alternative: y = (L+1)*mu + z*sqrt(L+1)*S = 3*100 + 1.96*sqrt(3)*25 = 300 + 84.8 = ~385? No.
    # Or: y = L*mu + z*S_t where S_t already adjusted... Hard to verify exactly. The numeric calculation may not be verifiable from chunk.
    (3, 3, 4, 4, "REVISE", True, False, True, False, True, True,
     "The chunk provides the order-up-to formula but not the specific variance adjustment formula needed to compute 286 precisely from the given parameters (L=2, p=3, mu=100, S=25, z=1.96). The calculation is not fully verifiable from the retrieved chunk content alone, and the numeric answer requires working through intermediate steps not shown."),

    # IDX 92 — medium item_43, ACCEPT
    # Q: role of benchmarking. Near-duplicate. Correct=B.
    (5, 4, 5, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk directly describes benchmarking as comparing with industry leaders and competitors to drive continuous improvement, grounding B. This is a clean, well-grounded item (though a near-duplicate of other benchmarking items in this batch)."),

    # IDX 93 — medium item_44 (None difficulty), REVISE
    # Q=None. Options are full statements about ZICO. correct_key=None.
    # The difficulty is None and correct_key is None — this is a fundamentally broken item.
    (2, 2, 1, 1, "REJECT", False, True, True, False, False, False,
     "Both the question stem and correct_key are None, and the difficulty label is also None — this item is completely malformed with no functional MCQ structure. Must be rejected."),

    # IDX 94 — medium item_45, ACCEPT
    # Q: capacity-constrained production sequence definition. Correct=A.
    # Chunk: "at most one period k within the sequence has 0 < y_k < C_k while all other periods produce either zero or at full capacity." A matches exactly.
    # B (all periods at zero or full) — too restrictive (excludes the one intermediate period allowed). C (demand exactly equal capacity) — wrong. D (multiple periods with intermediate level) — wrong.
    (5, 4, 4, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk precisely defines a capacity-constrained sequence as having at most one period with intermediate production, matching A. Distractor B (no intermediate periods at all) is a subtle but distinct misstatement requiring careful reading."),

    # IDX 95 — medium item_46, ACCEPT
    # Q: variability at stage k, decentralized vs centralized. Correct=B (larger due to multiplicative amplification).
    # Near-duplicate of IDX 67 (medium item_18). Chunk supports B.
    (5, 4, 4, 5, "ACCEPT", True, False, True, True, True, True,
     "Chunk describes multiplicative amplification factors under decentralized information, grounding B. This is a near-duplicate of medium item_18 but the item is well-grounded and correct."),

    # IDX 96 — medium item_47, REVISE
    # Q: volume-process focus scenario. Correct=C (invests in Technology 1 for low volumes, switches to Technology 2 for higher volumes).
    # Chunk: describes technology scale curves and focus dimensions. C matches the technology switching concept.
    # A (single plant in Detroit) — that's focus "off." B (wide range across facilities) — not specific to volume-process focus. D (centralizes to reduce transport) — different concept.
    (5, 3, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk describes technology scale curves where different technologies are appropriate at different volume levels, grounding C as an illustration of volume-process focus. The reviewer's REVISE seems conservative — this is a reasonable, grounded item. ACCEPT."),

    # IDX 97 — medium item_48, REVISE
    # Q: SC strategy NOT mentioned as achieving total SC profit increase over sequential optimization. Correct=A (just-in-time inventory system).
    # Chunk: "supply contracts...revenue sharing, buyback contracts, direct business model" mentioned as achieving SC profit gains.
    # A (JIT) — not mentioned in this context as a profit-coordination contract mechanism. B (revenue sharing) — mentioned. C (buyback) — mentioned. D (direct business model/build-to-order) — mentioned (Dell).
    # A is the NOT item. JIT is a different strategy (operational, not contract-based coordination).
    (5, 4, 4, 5, "ACCEPT", False, False, True, True, True, True,
     "Chunk lists revenue sharing (B), buyback contracts (C), and Dell's direct model (D) as achieving SC profit improvements over sequential optimization. JIT (A) is not mentioned in this context, making it the correct NOT answer. ACCEPT over REVISE."),

    # IDX 98 — medium item_49, REVISE
    # Q: EOQ no-shortage assumption — how does it affect average cost per unit time. Correct=C (no effect on total ordering/holding costs, but affects optimal order quantity).
    # This is conceptually problematic: the EOQ model assumes no shortages, so shortages are excluded. Asking how the no-shortage assumption "affects" the cost is circular — you can't compare with and without shortages within the EOQ framework.
    # The EOQ with planned backorders (separate model) shows that allowing shortages DECREASES total cost. So if EOQ assumes no shortages, total cost is HIGHER than optimal.
    # C says "no effect on total ordering/holding costs but affects optimal order quantity" — this isn't quite right either. Shortages DO affect total cost (backorder model has lower cost).
    # The correct answer is debatable from the chunks. REVISE is appropriate.
    (3, 3, 3, 5, "REVISE", True, True, True, False, False, True,
     "The no-shortage assumption in EOQ and its cost implications are debatable: comparing EOQ with/without backorders (covered separately in chunk) shows shortages reduce total cost, contradicting option C's claim of 'no effect.' The question conflates two distinct models and the correct answer is not clearly verifiable from the chunks."),

    # IDX 99 — medium item_50, ACCEPT
    # Q: evaluating logistics strategy — what factors to consider for degree of dispersion. Correct=C (relative transportation costs and demand uncertainty).
    # Chunk: "degree of dispersion" and factors affecting it including transportation costs and demand uncertainty. C is grounded.
    # A (number of employees) — irrelevant. B (color scheme) — absurdly wrong. D (CEO preference) — irrelevant.
    # B is a trivial distractor, reducing DQ.
    (4, 2, 5, 5, "REVISE", False, False, True, True, False, True,
     "Chunk supports transportation costs and demand uncertainty as factors for supply chain dispersion decisions, grounding C. However, distractor B (company color scheme) is trivially absurd and immediately dismissible, substantially reducing distractor quality. REVISE to replace B with a substantive distractor."),
]

# Load data
WORKDIR = Path(__file__).resolve().parent

with open(WORKDIR / 'claude_review_input.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

slice_100 = data[0:100]

output = []
for i, (item, score) in enumerate(zip(slice_100, scores)):
    sa, dq, sc, dm, decision, agrees, ambig, chunks_support, verifiable, dist_wrong, rev_sa_acc, notes = score

    record = {
        "run_id": item["run_id"],
        "item_id": item["item_id"],
        "batch_label": item["batch_label"],
        "condition": item["condition"],
        "difficulty": item["difficulty"],
        "reviewer_decision": item["reviewer_decision"],
        "claude_source_alignment": sa,
        "claude_distractor_quality": dq,
        "claude_stem_clarity": sc,
        "claude_difficulty_match": dm,
        "claude_decision": decision,
        "agrees_with_reviewer": agrees,
        "flag_ambiguity": ambig,
        "chunks_support_question": chunks_support,
        "correct_answer_verifiable": verifiable,
        "distractors_clearly_wrong": dist_wrong,
        "reviewer_source_call_accurate": rev_sa_acc,
        "claude_notes": notes
    }
    output.append(record)

assert len(output) == 100, f"Expected 100 records, got {len(output)}"

with open(WORKDIR / 'batch_0000_0099.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Written {len(output)} records.")

# Summary stats
decisions = {}
for r in output:
    d = r["claude_decision"]
    decisions[d] = decisions.get(d, 0) + 1
print("Decision counts:", decisions)

agrees_count = sum(1 for r in output if r["agrees_with_reviewer"])
print(f"Agrees with reviewer: {agrees_count}/100")

ambig_count = sum(1 for r in output if r["flag_ambiguity"])
print(f"Flagged ambiguous: {ambig_count}")

reject_items = [r["item_id"] for r in output if r["claude_decision"] == "REJECT"]
print(f"Rejected items ({len(reject_items)}): {reject_items}")
