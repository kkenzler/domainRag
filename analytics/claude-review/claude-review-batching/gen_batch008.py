"""Generate batch008.json — Claude review decisions for items 351-400."""
import json
from pathlib import Path

INPUT = Path("claude_review_input.json")
OUTPUT = Path("batch008.json")

with open(INPUT, encoding="utf-8") as f:
    items = json.load(f)

# (align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag, notes)
RAW = [
    # 351
    (3,2,4,False,"REVISE","True",False,False,False,True,False,
     "C (demand distribution F(y|p)) is correct: in newsboy+pricing, the demand distribution conditional on price is the central factor linking price and quantity decisions. However A (cost c) and B (price p) are also key factors in the critical fractile (p-c)/p. D (critical fractile formula) determines optimal y not p directly. Chunk mismatch: dist=0 chunk covers classical newsboy without pricing extension. dq=2: A and B are also correct in a narrower sense. Near-duplicate of Item 362 (which has conflicting KEY=B)."),
    # 352
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "A (phenomenon where order sizes amplify as they move upstream) is the correct bullwhip definition. B (reducing inventory levels = mischaracterizes direction). C (increase in customer demand leading to decrease in costs = wrong mechanism). D (reduction of lead times = wrong description). Near-duplicate of Items 332, 343, 348, 350—excessive repetition of basic bullwhip definition. Prefer Items 343 and 350 for better distractor sets."),
    # 353
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (order variability increases significantly due to forecasting processes) correctly identifies the bullwhip source. A (variability DECREASES as lead times increase = WRONG: longer lead times worsen bullwhip). B (variability unaffected by demand variability = WRONG). D (variability solely determined by current demand = WRONG: depends on forecasting history). Chunk directly shows the order formula demonstrating amplification from forecasting."),
    # 354
    (5,4,4,True,"REVISE","True",True,True,False,True,False,
     "C (rate of decrease in unit costs varies by manufacturing technology) is correct per scale analysis chunk. A (as volume decreases, unit costs increase at constant rate = wrong: costs DO increase as volume falls, but 'constant rate' contradicts the 'varies by technology' principle). B (at very high volumes, one technology will ALWAYS dominate = too absolute: chunk says 'may dominate'). D (subcontracting never more economical = WRONG: chunk says it 'may prove more economical' at lower volumes). B's 'always' qualifier makes it wrong—replace with 'typically' to create a better near-miss."),
    # 355
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "A (cumulative difference between supply and demand over time) correctly defines inventory. Near-duplicate of Item 346. B (cost of holding goods = carrying cost definition). C (number of products = SKU count). D (total amount supplied = confuses supply with inventory). Reviewer ACCEPT confirmed."),
    # 356
    (5,3,4,False,"REVISE","True",True,True,True,True,False,
     "B (independent optimization efforts by individual functions) correctly identifies the cause of sub-optimization, directly from the chunk. A (excessive communication between functions = obviously WRONG: it's the LACK of communication/coordination that causes sub-optimization). C (overly complex decision-making = not the specific cause). D (lack of strategic planning = secondary cause). dq=3: A is an obvious joke distractor. dm=False: this is very basic recall; should be classified 'very easy' not just 'easy'. distractors_wrong=True."),
    # 357
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (longer lead times correlate with higher inventory levels) correctly describes Little's Law relationship. A (inventory unrelated to lead times = WRONG). B (higher inventory → SHORTER lead times = WRONG direction). D (shorter lead times CAUSE lower inventory = partially correct but 'cause' is stronger than the bidirectional correlation; also duplicates C's meaning). Chunk directly states the cyclical relationship. Near-duplicate of Item 363."),
    # 358
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (increase in port congestion and higher fuel costs) correctly identifies 2021 ocean shipping rate drivers. A (decrease in global demand = WRONG: demand increased post-COVID). C (reduction in vessel capacity due to improved efficiency = WRONG: congestion reduced effective capacity, not efficiency gains). D (decline in energy prices = WRONG: energy prices rose). Near-duplicate of Items 345, 367."),
    # 359
    (3,2,4,False,"REVISE","True",False,False,False,True,False,
     "A (insurance, maintenance, opportunity cost) is correct. Near-duplicate of Items 321, 341—third version of the same carrying cost components question. Chunk mismatch: dist=0 chunk covers inventory model dimensions, NOT the carrying cost components specifically. dq=2: B (storage, handling, deterioration = subcategories of maintenance) is a near-miss. C and D contain no remotely plausible carrying cost components. Eliminate this version; keep Item 341 which has the best chunk alignment."),
    # 360
    (3,4,4,False,"REVISE","True",True,False,False,True,False,
     "D (longer lead times require more demand data to reduce bullwhip due to extended data accumulation period) is the KEY. The chunk shows bullwhip is an increasing function of both lead time L and smoothing parameter p—a larger p (more historical data) is needed to reduce variability, and longer L amplifies the effect. A (bullwhip completely eliminated by centralized sharing = too strong). B (decentralized forecasting errors don't propagate = WRONG). C (sophisticated forecasting reduces bullwhip = WRONG per chunk: more sophisticated order-up-to policy WORSENS bullwhip). D's claim is inferential and imprecisely stated. verifiable=False."),
    # 361
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "D (variation of service level or delivery time) is the NOT-output. The chunk lists strategic outputs for SC design; 'variation of service level or delivery time' is a performance metric/uncertainty measure, not a primary strategic output. A (delivery/service time), B (customization and breadth), C (service level on inventory) are all established strategic outputs. Well-constructed NOT-question."),
    # 362
    (2,4,3,False,"REJECT","Partial",False,False,False,False,True,
     "CRITICAL: KEY=B (selling price per unit p) is circular reasoning—'selling price is a key factor in determining the optimal selling price.' The correct key for this question should be C (demand distribution F(y|p)) as in the near-duplicate Item 351. Item 362's KEY=B conflicts with Item 351's KEY=C for the same question. B is tautological: p is 'a key factor' in determining p by definition. REJECT: wrong/circular key. reviewer_source_call_accurate=False. The question has no defensible correct answer as stated with KEY=B."),
    # 363
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (longer lead times result in higher inventory levels, and vice versa) correctly describes Little's Law bidirectional relationship. Near-duplicate of Item 357. A (inventory unrelated to lead times = WRONG). C (shorter lead times INCREASE inventory = WRONG: opposite). D (lead times have no impact = WRONG). Reviewer ACCEPT confirmed."),
    # 364
    (4,3,4,True,"REVISE","True",True,True,True,True,False,
     "B (raw material costs including invoice costs and freight) correctly identifies one key sourcing driver from the chunk. A (customer satisfaction ratings = not a primary sourcing driver). C (employee turnover rates = not mentioned). D (average customer order value = not a sourcing driver). dq=3: A, C, D are too obviously wrong—none are remotely related to strategic sourcing decisions. Replace with options that represent plausible sourcing factors (e.g., A: 'Proximity to customers to minimize shipping distances'; C: 'Carbon footprint of each potential production site'). distractors_wrong=True."),
    # 365
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (comparative performance against competitors and industry leaders) correctly identifies benchmarking's focus. A (internal productivity = that's what benchmarking moves AWAY from). C (only closest competitors in own sector = too narrow: benchmarking includes industry leaders and best-in-class outside your sector). D (purely internal efficiency = opposite of benchmarking). Well-constructed item with clear gradation from internal (A,D) to partially correct (C) to fully correct (B)."),
    # 366
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "A (increased demand from post-pandemic recovery, reduced vessel capacity from port congestion, higher fuel costs) correctly combines all three 2021 freight rate drivers. B reverses demand to 'decreased demand' (WRONG). C has increased vessel capacity (WRONG: port congestion reduced effective capacity). D reverses all factors (WRONG). Well-constructed all-or-none combination item."),
    # 367
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "C (higher energy prices and increased operational costs associated with shipping) correctly identifies 2021 freight rate cause. A (decrease in global demand = WRONG). B (increase in supply of shipping services due to REDUCED port congestion = WRONG: congestion INCREASED). D (reduction in number of available vessels = secondary factor; the primary driver was demand surge + congestion). Near-duplicate of Items 345, 358."),
    # 368
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "A (calculate l1 as maximum m such that sum of excess capacities from top m plants ≤ E) correctly identifies the determination step. Near-duplicate of Items 329, 369. B (rank plants and select first l1 with production cut = misses the calculation logic). C (determine l* as index of plant with highest cost multiplier = wrong step). D (calculate average cost multiplier until sum exceeds E = wrong procedure). Chunk directly supports A."),
    # 369
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (finding l1 as maximum m such that sum of excess capacity from m highest-cost plants ≤ total excess) correctly identifies the step. Near-duplicate of Items 329, 368. A (selecting all plants with excess capacity over demand = wrong criterion). C (choosing all but top-ranked plant with lowest cost multiplier = wrong selection logic). D (identifying plants with production capacities less than demand = wrong criterion). Chunk directly supports B."),
    # 370
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "A (SCOR emphasizes internal efficiency within organization, while GSCF focuses on inter-firm relationship management) is confirmed by SCOR chunk (standardized benchmarking framework vs GSCF's collaborative relationship emphasis). Near-duplicate of Items 145, 181, 277, 386. B (both prioritize internal efficiency = WRONG). C (SCOR concerned with IT/compliance = wrong characterization). D (both equally on relationship management = WRONG: SCOR is about standardized benchmarking, not relationships). Excessive duplication of SCOR/GSCF item."),
    # 371
    (4,3,5,True,"REVISE","True",True,True,False,True,False,
     "A (ZICO policy is extension of ZIO principle to problems with capacity constraints) is correct per chunk. Near-duplicate of Item 385 (which reviewer ACCEPTED). B (both policies state inventory×order_quantity=0 = describes ZIO's condition I_{t-1}·y_t=0 correctly for ZIO but ZICO adds the additional capacity constraint I_{t-1}·(C_t-y_t)·y_t=0). C (ZICO requires final production = remaining demand = describes ZICO's corollary, not the defining relationship). dq=3: B is a good trap but conflates the two conditions. Eliminate 371; keep 385."),
    # 372
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (more severe in decentralized systems due to propagation of forecasting errors across stages) correctly describes the decentralized bullwhip mechanism. A (less pronounced in decentralized = WRONG). C (mitigated by sophisticated forecasting = WRONG: more sophisticated order-up-to policy WORSENS decentralized bullwhip per the chunk formula). D (unaffected by information structure = WRONG). Well-constructed item with clear correct-direction wrong answers."),
    # 373
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (managing uncertainty across various sources such as demand fluctuations and supplier disruptions) correctly identifies the key SC management challenge. A (achieving perfect synchronization = a goal, not a challenge description). C (ensuring operations conducted independently = wrong approach that causes the problem). D (focusing solely on minimizing costs = wrong approach). Chunk directly supports B. Near-duplicate of Item 375."),
    # 374
    (5,3,4,True,"ACCEPT","True",True,True,False,True,False,
     "C (50 units—correctly using s = LT×AVG + z×STD×√LT but incorrectly estimating z) is correct. The base = LT×AVG = 5×10 = 50. With correct formula but assuming z=0 or STD=0, s=50. A (47 = wrong z=2 applied differently). B (63 = incorrectly calculated safety stock). D (42 = assumes LT=1 day). Each distractor explains its own error type, which helps diagnose student misconceptions. Novel format for a diagnostic item. Reviewer ACCEPT confirmed."),
    # 375
    (3,4,4,False,"REVISE","True",False,False,False,True,False,
     "B (balancing conflicting objectives between purchasing, manufacturing, warehousing, and customers) is correct but the dist=0 chunk describes a SC network definition (network of organizations, historically focused...) rather than the conflicting objectives challenge specifically. Near-duplicate of Item 373. A (all suppliers same country = obviously wrong simplification). C (solely minimizing production costs = too narrow). D (ignoring upstream raw material = opposite of SCM focus). Chunk mismatch for this specific claim about conflicting objectives."),
    # 376
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (demonstrates how small changes in customer demand trigger increasingly large order variations upstream) correctly describes bullwhip. A (customer demand fluctuations directly proportional to production orders = WRONG: production is amplified, not proportional). B (retailer orders LESS variable than customer demand = WRONG: retailer orders are MORE variable). D (production plans display SMALLER order size variations = WRONG: production planning is MOST volatile). Near-duplicate of bullwhip definition items."),
    # 377
    (5,4,5,True,"REVISE","True",True,True,False,True,True,
     "B (ocean shipments have higher threshold than air shipments, reflecting longer lead times) is correct: ocean lead times are longer → higher safety stock threshold needed. Flag: C (air shipments have lower threshold because more reliable) states the SAME relationship as B from the opposite direction—if ocean threshold > air threshold, then air threshold IS lower. Double-correct-answer issue between B and C. Both B and C describe the same empirical fact (ocean threshold > air threshold) using different framing. Revise C to make it clearly false (e.g., C: 'Air shipments require higher threshold because their cost per shipment is greater')."),
    # 378
    (3,4,4,False,"REVISE","True",False,True,False,True,False,
     "C (total cost includes both ordering costs and holding costs over a finite planning horizon) is correct for the Wagner-Whitin model. A (production quantity must always be at full capacity = WRONG: W-W is uncapacitated). B (inventory can never exceed demand = WRONG: inventory builds up between orders). D (initial inventory is non-zero = WRONG: W-W assumes zero initial inventory). Chunk mismatch: dist=0 chunk covers dynamic lot sizing WITH capacity constraints (ZICO model), not the W-W uncapacitated model. Remap to the W-W chunk. dm=False: W-W properties are medium-level content."),
    # 379
    (5,4,4,False,"REVISE","True",True,True,False,True,False,
     "B (inventory carrying costs increase due to larger order fluctuations at each stage) correctly describes bullwhip's impact on inventory. A (inventory levels DECREASE as orders move upstream = WRONG: they increase). C (inventory investment minimized because demand variability DECREASES = WRONG: variability increases). D (inventory turnover speeds up when lead times reduced = not directly about bullwhip effect on carrying costs). dm=False: reviewer says difficulty doesn't match—for medium classification this may be too straightforward (basic inference from bullwhip definition)."),
    # 380
    (3,4,4,False,"REVISE","True",True,False,False,True,False,
     "D (in decentralized SC, each stage estimates mean demand from orders received from downstream stage) correctly describes the decentralized information problem. A (decentralized stages forecast based on actual customer demand = WRONG: that's centralized). B (bullwhip less pronounced in decentralized = WRONG). C (centralized sharing can reduce bullwhip by allowing all stages to base decisions on same demand signal) is ALSO correct—this is a valid true statement about centralized info sharing. Double-correct concern between C and D. sa=3 given the chunk discusses the decentralized formula but not D's exact mechanism. verifiable=False."),
    # 381
    (3,2,4,False,"REVISE","True",True,False,True,True,False,
     "D (increased lead times) correctly is NOT mentioned as contributing to inventory turnover improvement. Near-duplicate of Item 388. The chunk mentions better management practices and technological advances. A (top management emphasis), B (number of SKUs), C (improved forecasting) are all plausible contributors. dq=2: D (increased lead times) as a NOT-contributor to improvement is obvious—longer lead times HURT inventory turnover, so it's trivially not a contributor to improvement. Replace D with something more subtle that sounds like it could contribute but isn't mentioned."),
    # 382
    (5,4,4,False,"REVISE","True",True,True,False,True,False,
     "B (strategic planning document translating insights into actionable KPIs aligned with business strategy) is directly supported by the chunk. Reviewer sa=3 seems inconsistent—the chunk directly says 'logistics scorecard framework translates benchmarking insights into actionable key performance indicators aligned with organizational strategy.' dm=False: this content is easier than medium level; the scorecard framework description is direct recall. A (operational tool for managing inventory = too operational). C (financial report for cost-to-serve = too narrow). D (solely internal efficiency measurement = misses market orientation). All wrong answers are too obviously wrong."),
    # 383
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (reorganizing around end-to-end processes with flat hierarchies and cross-functional teams) correctly describes horizontal process-driven organizations. A (maintaining functional departments but improving communication = incomplete—doesn't restructure). B (integrating logistics into existing vertical structures = doesn't address the structural barrier). D (single point of accountability within existing functional structure = still functional, not process-driven). Well-constructed item contrasting partial vs full SC integration solutions."),
    # 384
    (3,4,4,True,"REVISE","True",False,False,False,True,False,
     "B (relative transportation costs, demand uncertainty, and product variety for different locations) correctly identifies centralized vs dispersed network design factors. Chunk mismatch: dist=0 chunk is about scale analysis (unit costs vs volume) which argues FOR centralization/scale economies, not for the dispersed vs centralized trade-off framework. The relevant chunk would discuss network configuration factors explicitly. A (fixed costs = important but too narrow). C (linear cost structure of duties = very specific and narrow). D (Asian paradigm modeling = overly specific). Remap to a network configuration chunk."),
    # 385
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "A (ZICO policy is extension of ZIO principle that applies to capacity-constrained problems) is correct per chunk. Near-duplicate of Item 371 (which REVISE recommended). B (both policies state I_{t-1}·y_t=0 = describes ZIO but ZICO's condition is I_{t-1}·(C_t-y_t)·y_t=0—a different, extended condition). C (ZICO requires zero OR full capacity production, ZIO is different = partially correct but doesn't capture the full ZICO condition which also includes zero inventory). D (ZICO less effective than ZIO = WRONG: ZICO extends ZIO to handle capacity constraints). Reviewer ACCEPT confirmed."),
    # 386
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "A (SCOR emphasizes internal efficiency benchmarking, GSCF focuses on inter-firm relationship management) confirmed by the SCOR chunk. Near-duplicate of Items 145, 181, 277, 370. B (both prioritize internal efficiency = WRONG). C (SCOR concerned with IT/compliance = wrong characterization). D (both equally on SC relationship management = WRONG). Excessive duplication of SCOR/GSCF comparison item."),
    # 387
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "A (length of lead time between orders and deliveries) is the KEY factor contributing to demand variability amplification. The chunk formula shows Var(q) increases as function of L (lead time) and p (smoothing window). A is correct per the formula. B (number of historical observations = relates to smoothing parameter p, which is the other key variable—could be considered the SECOND most significant factor). REASON: sa=3 suggests the chunk supports the formula but the claim that L is MOST significant over p needs additional justification. dm=False: identifying the most significant factor among formula variables is hard-level analysis for medium classification."),
    # 388
    (3,2,4,False,"REVISE","True",True,False,True,True,False,
     "D (increased lead times) correctly is NOT mentioned as contributing to improved inventory turnover. Near-duplicate of Item 381. dq=2: D is obviously wrong as a contributor to improved inventory turnover (longer lead times HURT turnover). Replace D with something subtler (e.g., D: 'Expansion into new product categories' which is plausible but not mentioned as a driver). Also, A (top management emphasis), B (reduction in SKU proliferation), C (improved forecasting) need to be verified as explicitly mentioned in the chunk. distractors_wrong=True for D. rev_acc=True."),
    # 389
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (through ongoing comparison with competitors and industry leaders to identify breakthrough performance improvements) correctly describes benchmarking's impact. A (solely internal productivity = benchmarking moves AWAY from internal-only focus). C (benchmarking is ineffective = directly contradicts the chunk). D (only involves comparing direct competitors = too narrow: benchmarking includes industry leaders and best practices outside own sector). Chunk directly supports B."),
    # 390
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "B (strong global demand for agricultural commodities and pricing power) explains resilience in US ag equity valuations despite SC disruptions. The chunk documents substantial equity price increases (60%+ for some indices) since January 2020. A, C, D all make speculative forward-looking claims (freight rates will decrease, congestion will resolve, energy will stabilize) which are not supported by the chunk's retrospective equity analysis. B provides the fundamental economic driver."),
    # 391
    (4,4,4,False,"REVISE","True",True,True,False,True,False,
     "B (firm reduces operational costs AND enhances customer satisfaction through improved logistics performance) correctly captures the P&G example (saving retail customers $65M through logistics gains). A (increasing market share by expanding product line = different SC strategy, not P&G's mechanism). C (outsourcing manufacturing to reduce labor costs = different strategy). D (adopting direct sales model = different strategy, more like Dell). dm=False: this is a case study recall question that should be easy-medium, not medium. The P&G example is directly stated in the chunk."),
    # 392
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (bullwhip effect is likely at play) correctly diagnoses stable customer orders but fluctuating distributor orders. A (distributors have more accurate forecasts = WRONG: bullwhip implies distributors have LESS accurate demand info). C (customer demand is highly unpredictable = WRONG: the premise states customer orders are STABLE). D (lead times are very short = WRONG: shorter lead times would reduce, not cause, the described pattern). Well-constructed diagnostic scenario item."),
    # 393
    (4,3,4,True,"REVISE","True",True,True,False,True,True,
     "A (need for high flexibility versus achieving scale economies) is correct per the global strategies chunk. However B (local market presence versus centralized production efficiency) states essentially the SAME trade-off in different words. Double-correct-answer concern: A and B describe the same global SC tension (local responsiveness vs global efficiency). Revise B to describe a different tension (e.g., B: 'The cost of transportation versus the risk of foreign exchange fluctuations') to make A the unambiguously best answer. Flag: A and B overlap significantly."),
    # 394
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "B (company reduced supply chain complexity, leading to lower inventory levels) is a reasonable interpretation of PBG's results (inventory fell from $201M to $195M). A (increased production efficiency by 5% = not stated). C (outsourced more manufacturing = not mentioned). D (implemented JIT = not explicitly stated; outcomes resemble JIT benefits but mechanism was cross-functional coordination meetings). Chunk directly describes the inventory reduction. Reviewer ACCEPT confirmed."),
    # 395
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "A (direct business model with build-to-order strategy) correctly identifies Dell's approach per the competitive advantage examples in the chunk. B (indirect model with mass production = WRONG: Dell's advantage was the direct build-to-order model). C (hybrid combining direct and indirect = WRONG). D (centralized model focusing on internal operations = WRONG: Dell's advantage was customer-direct, not internal focus). Well-established business case example."),
    # 396
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (distributing production across multiple regions to serve local markets while maintaining scale economies) correctly balances both objectives. A (solely domestic production = avoids international complexity but sacrifices global market access). B (centralizing in single location = achieves scale economies but ignores transportation costs and regional market access). D (increasing exports without considering regional market demands = ignores market access). Chunk supports C's balance of global scale with regional presence."),
    # 397
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "A (s = LT × AVG + z × STD × √LT) correctly gives the (s,S) reorder point formula. B (LT - AVG = subtracts instead of multiplies—obviously wrong). C (LT × AVG - z × STD × √LT = subtracts safety stock instead of adding). D (LT + AVG = additive instead of multiplicative). dq=4: C is the best distractor—sign error on safety stock. B and D have more fundamental formula errors. Reviewer ACCEPT confirmed."),
    # 398
    (3,2,4,False,"REVISE","True",True,True,True,True,False,
     "B (difficulty in integrating SC processes due to functional silos and rigid departmental structures) correctly identifies the 21st century challenge. A (maintaining traditional hierarchical structures = describes the choice companies make, not the challenge itself). C (requirement for increased speed without regard for quality = wrong approach, not a business challenge). D (necessity of focusing solely on internal operations = opposite of the SC integration imperative). dq=2: A, C, D are too obviously wrong—none represent plausible business challenges. Replace with more nuanced wrong options. distractors_wrong=True."),
    # 399
    (3,4,4,False,"REVISE","True",False,False,False,True,False,
     "C (ratio of actual cost to optimal cost when ordering γ×EOQ is (γ+1/γ)/2) is the EOQ SENSITIVITY formula, but the question specifically asks about the 'EOQ model with planned backorders.' The (γ+1/γ)/2 formula holds for the STANDARD EOQ model, not specifically for the backorder model where Q*=√(2DK/h)·√((π+h)/π). The chunk shown is the standard EOQ total cost formula, not the backorder model chunk. A (both Q* and s* independent of π = WRONG). B (both Q* and s* increase as π increases = WRONG: Q* decreases and s* increases as π increases). D (ratio = 1 when Q = EOQ = trivially true). Chunk mismatch: wrong EOQ chunk for a backorder model question."),
    # 400
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (to coordinate SC, transport, finance, sales, and manufacturing functions to optimize sourcing and pre-build strategies) is directly supported by the PBG chunk. A (marketing strategies for new products = not the purpose). C (employee performance evaluation = not the purpose). D (negotiate with suppliers on price reductions = too narrow; the meetings involved a much broader set of functions and decisions). Chunk lists the exact functions involved in the cross-functional meetings."),
]

COLS = [
    "claude_source_alignment", "claude_distractor_quality", "claude_stem_clarity",
    "claude_difficulty_match", "claude_decision", "agrees_with_reviewer",
    "chunks_support_question", "correct_answer_verifiable", "distractors_clearly_wrong",
    "reviewer_source_call_accurate", "flag_ambiguity", "claude_notes",
]

decisions = []
for offset, row in enumerate(RAW):
    item = items[350 + offset]
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
print(f"Batch 8 written: {len(decisions)} items")
for k, v in sorted(decisions_count.items()):
    print(f"  {k}: {v}")
