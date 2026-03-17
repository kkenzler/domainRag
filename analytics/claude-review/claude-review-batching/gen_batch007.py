"""Generate batch007.json — Claude review decisions for items 301-350."""
import json
from pathlib import Path

INPUT = Path("claude_review_input.json")
OUTPUT = Path("batch007.json")

with open(INPUT, encoding="utf-8") as f:
    items = json.load(f)

# (align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag, notes)
RAW = [
    # 301
    (3,2,3,False,"REVISE","True",True,False,False,True,False,
     "B (4 plants) per multi-plant algorithm: l*=l1+fractional adjustment. With 5 plants at 133 1/3 each and total excess=250, 40% fractional adjustment gives l*≈1.4, so 2 plants cut back → 4 operate. Chunk provides the algorithm but B=4 requires full cost distribution computation. dq=2: A:3 and D:6 are too extreme given 5 plants total. Replace with options representing different l* values. dm=False: difficulty mismatch (not straightforward calculation from provided data)."),
    # 302
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "A correctly identifies logistics as central driver aligning planning with execution in the order-to-delivery transformation. B (administrative function = old view of logistics). C (maintains functional barriers = directly contradicts COMS integration). D (no significant role = most obviously wrong). Well-constructed item with clear gradation of wrong answers. Near-duplicate of Items 261, 299."),
    # 303
    (4,3,5,False,"REVISE","True",True,True,False,True,False,
     "B correctly captures that optimal Q balances marginal profit vs cost AND that risk increases as Q increases—a counterintuitive but important newsboy insight. A (maximizing profit also minimizes risk = WRONG per chunk: higher Q increases probability of both gains and losses). D (higher Q always reduces probability of large losses = WRONG: chunk says risk increases with Q). dm=False: the counterintuitive risk property is medium-level analysis. dq=3: C ('solely dependent on average forecast demand') is too obviously wrong; replace with something more subtle."),
    # 304
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "A (global demand for ag commodities increased, offsetting freight rate effects) is the primary mechanism. Chunk confirms statistical analysis shows no measurable negative effects on US ag export levels despite substantial freight rate increases. B (government subsidies) and C (flawed methods) are implausible. D (simulation overestimated competitive position) mischaracterizes the methodology. Strong item with direct chunk support."),
    # 305
    (4,3,5,False,"REVISE","True",True,True,False,True,False,
     "B (regular cross-functional meetings facilitating communication) correctly identifies the method. A (increasing raw material inventory = WRONG: reduced from $201M to $195M). C (outsourcing to lower-cost countries = not mentioned). D (JIT system = not explicitly stated; outcomes described resemble JIT but mechanism was cross-functional coordination). MULTIPLE_CORRECT_ANSWERS concern: D's JIT framing overlaps with actual outcomes. dm=False: easy-to-medium case recall, not hard."),
    # 306
    (2,4,2,False,"REVISE","True",False,False,False,True,True,
     "D (cannot be determined without knowing specific values) is correct: multiplicative vs additive optimal prices depend on specific elasticity and demand distribution parameters not provided. A, B, C all make specific directional claims without required parameters. The dist=0 chunk covers only the additive demand model formula—the multiplicative model comparison requires a different chunk. Flag: stem asks about comparison between two model types when only one is covered by available chunks."),
    # 307
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "B (balancing internal and external KPIs while promoting market orientation, collaboration, flexibility) confirmed by scorecard framework chunk (4-step process). A (equally weighted KPIs = wrong: strategic importance dictates weighting). C (solely cost reduction = too narrow). D (ignoring operational realities = describes a failure mode, not a challenge). Well-constructed item."),
    # 308
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "B (multiple products, stochastic demand, multiple locations, limited capacity) combines most complexity dimensions. A (single product, deterministic, single location = simplest EOQ-type). D (durable, constant rate, periodic review = classical simple). C (perishable, endogenous demand = complex but lacks the network complexity of B's multiple locations). Good complexity spectrum item."),
    # 309
    (2,4,2,False,"REVISE","True",False,False,False,True,False,
     "B (introduces complexities like lower-scale higher-skill manufacturing and JIT from dispersed locations) makes a specific claim about globalization's SC strategy impact. The dist=0 chunk is about outsourcing trends 1993-1996 purchasing-as-%-of-sales data, NOT about globalization's strategic impact on manufacturing scale. The 'lower-scale, higher-skill' claim is not supported by outsourcing trends data. Remap to an appropriate globalization and SC strategy chunk. dm=False: hard level for essentially a definitional question."),
    # 310
    (3,4,4,False,"REVISE","True",False,False,False,True,False,
     "D (global flexibility, market access, research capabilities) correctly identifies dispersed network design drivers. A (minimize transportation = centralization driver). B (stable predictable demand = centralization driver). C (high volume, standardized, single location = centralized). Chunk mismatch: dist=0 chunk is about scale analysis/economies of scale which actually argues FOR centralization, not dispersal. Remap to a dispersed network rationale chunk."),
    # 311
    (3,4,4,False,"REVISE","True",True,False,False,True,True,
     "D (long-term forecasts, while less accurate, provide better basis for production planning) is ambiguous: long-term forecasts ARE necessary for production planning due to lead times, but 'better basis' implies higher accuracy which is false. B (inventory can be accurately predicted by aggregating individual forecasts) is partially correct (aggregation reduces variability) but 'accurately' is too strong. Flag: D conflates necessity (must use long-term for production planning) with accuracy (long-term is less accurate). Revise D to distinguish between 'necessary for' vs 'more accurate than' short-term forecasts."),
    # 312
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (rigid departmental silos prioritizing local budget control over cross-functional collaboration) correctly identifies structural AND incentive mechanism. A (flat hierarchy lacking accountability = wrong: silos create VERTICAL hierarchies). C (vertical processes focused on individual dept performance) is also accurate but B specifies the incentive mechanism (budget control) more precisely. D (end-to-end process teams = describes the DESIRED integrated state). Near-duplicate of prior functional org items."),
    # 313
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (wide range of factors including raw material, manufacturing costs, etc.) correctly captures the multi-factor nature of strategic sourcing. A, C, D all make overly narrow claims (freight costs alone, yield loss alone, duties alone). Chunk directly supports the comprehensive factor list."),
    # 314
    (2,4,4,False,"REVISE","True",False,False,False,True,False,
     "B (ABC provides detailed cost by tracing to specific activities and products, revealing true costs) is correct from general SCM knowledge. However the dist=0 chunk is about functional silos causing sub-optimization—NOT about Activity-Based Costing. Chunk mismatch: ABC content belongs to a cost accounting chunk not available at dist=0. A (simplifies transactions = opposite: ABC adds complexity). C (tracks inputs rather than outcomes = wrong description). D (eliminates traditional accounting = wrong). Remap to appropriate ABC chunk. dm=False: ABC basics are introductory accounting."),
    # 315
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "A (helps determine optimal facility sizes by identifying where economies of scale are most significant) is directly supported by the scale analysis chunk. B (routing within a single plant = too narrow). C (flexibility for demand uncertainty = scale curves are about cost efficiency, not flexibility). D (centralized vs dispersed based on product value = not explicitly about product value per chunk). Solid item."),
    # 316
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "C (unit costs initially decrease but level off or even increase) is correct per scale curve concept. A (increase linearly = opposite). D (unchanged = obviously wrong). B ('decrease at constant rate' = wrong: rate of decrease varies by technology). dq=3: B is the only interesting distractor; A and D too easily eliminated. Replace A and D with more nuanced wrong options (e.g., A: 'decrease only at low volumes then increase exponentially'; D: 'always decrease regardless of technology')."),
    # 317
    (5,3,4,True,"REVISE","True",True,True,True,True,False,
     "B (minimizing total system cost while achieving service requirements) is directly supported. A (maximizing number of suppliers) and C (increasing product variety at all costs) are joke distractors—no SCM-aware student would choose them. D (solely manufacturing efficiency) is too narrow but at least relevant-sounding. dq=3: A and C are too obviously wrong. Replace with plausible wrong answers (e.g., A: 'Optimizing each supply chain stage independently to maximize local efficiency'; C: 'Prioritizing customer service levels without regard for cost trade-offs')."),
    # 318
    (5,4,5,True,"REVISE","True",True,True,False,True,False,
     "A (orders placed only when inventory reaches zero, each order covers demand for several consecutive periods) correctly describes ZIO. D (orders based on remaining capacity or demand, whichever smaller = describes ZICO's final-period corollary, not ZIO) is a good near-miss trap. REASON: CORRECT_ANSWER_VAGUE—A's 'covers demand for several consecutive periods' is imprecise (number of periods isn't fixed by ZIO). Revise A to: 'Orders are placed only when ending inventory from the previous period is zero, and the order quantity satisfies all demand until the next order.'"),
    # 319
    (4,3,5,False,"REVISE","True",True,True,False,True,False,
     "B (optimal Q determined by balancing marginal profit against marginal cost) is correct and directly supported. A (too high Q always results in higher profits = WRONG). C (optimal Q independent of average forecast demand = WRONG: Q* depends on demand distribution which includes the mean). D (as production increases, risk decreases = WRONG: chunk says risk increases with production). dm=False: marginal profit/cost balancing is newsboy theory—medium level, not easy. dq=3: C is subtle but 'independent of average forecast demand' is too strong."),
    # 320
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (KD/Q + hQ/2 + cD) correctly represents the per-unit-time total cost in the EOQ model. A (K + cQ + hQ/2 = gives per-cycle ordering cost instead of per-unit-time). C (K + cQ + hQ = doubles holding cost). D (KD/Q + hQ + cD = doubles holding cost). Chunk directly states the formula. Note: B is technically the annual average cost rate, not per-cycle cost as the question states, but reviewer confirmed this as intended formula."),
    # 321
    (3,2,4,False,"REVISE","True",False,False,False,True,False,
     "A (insurance, maintenance, opportunity cost) correctly identifies the three components. Near-duplicate of Item 341. The dist=0 chunk is about inventory model dimensions, NOT the carrying cost components chunk. Chunk mismatch. dq=2: B (storage, handling, deterioration = subcategories of maintenance) is a near-miss that a knowledgeable student might not clearly eliminate. Eliminate Item 321; prefer Item 341 which has better chunk alignment for the carrying cost components."),
    # 322
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (cost function remains relatively flat even when quantities significantly different from Q*) confirmed by (γ+1/γ)/2 sensitivity analysis result. A (increases rapidly = opposite). C (decreases sharply beyond optimal = wrong direction). D (highly sensitive = opposite of the EOQ robustness property). Near-duplicate of Item 340."),
    # 323
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (implementation of sophisticated inventory management software) aligns with the chunk's 'technological advances' factor for 30%+27% inventory turnover increase 1995-2000. A (decrease in SKUs = not mentioned as primary driver). B (improved forecasting accuracy = secondary). D (enhanced top management focus = vague). Reviewer ACCEPT confirmed."),
    # 324
    (5,3,4,True,"REVISE","True",True,True,False,True,False,
     "B ('production can be zero or at full capacity, but not both simultaneously') is roughly correct but imprecise: ZICO says EITHER inventory=0 OR production=0 OR production=full capacity. B implies only zero or full are possible, but ZICO also allows production=0 with any inventory level. Near-duplicate of Item 334 which is more precise ('not between these two extremes'). dq=3: C ('must equal remaining demand' = ZICO's final-period corollary) is a good near-miss. Eliminate 324; keep 334."),
    # 325
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (all-units discounts apply to entire order if threshold met or exceeded) is correct per the chunk. C (incremental applies to ALL units regardless of quantity = WRONG: applies only to units BEYOND threshold). D (lower price with incremental applies to quantities BELOW threshold = WRONG: it applies to quantities ABOVE threshold). Good discrimination between all-units vs incremental discount structures."),
    # 326
    (3,2,4,False,"REVISE","True",True,False,False,True,True,
     "C (increased safety stock levels) is the KEY, but standard bullwhip mechanism cites demand signal processing as the primary cause. The chunk shows the order-up-to formula (q_t = demand estimate + safety stock - inventory) where higher safety factor k·σ̂ can amplify orders when σ̂ increases. However, 'increased safety stock' is a RESPONSE to demand uncertainty rather than a direct driver of order amplification. REASON: FACTOR_NOT_EXPLICITLY_MENTIONED. Flag: verify whether C is precisely correct per the chunk formula. Revise C to 'higher safety stock requirements due to increased demand uncertainty' for precision. dq=2: A (shorter lead times) and D (decreased demand variability) obviously REDUCE bullwhip."),
    # 327
    (2,3,3,False,"REJECT","Partial",True,False,False,False,True,
     "CRITICAL: KEY=C states 'Aggregate forecasts are less reliable than disaggregate forecasts.' This directly contradicts the fundamental SCM principle that aggregating across products/locations INCREASES forecast reliability (law of large numbers, risk pooling). Standard teaching: aggregate > disaggregate in reliability. D ('forecasting individual items separately produces more reliable predictions') makes the same wrong claim as C. Neither B ('longer horizon = better' = WRONG: longer horizon reduces accuracy) nor A ('always perfectly accurate' = WRONG) is correct. REJECT: C has wrong key contradicting SCM theory. reviewer_source_call_accurate=False."),
    # 328
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (estimated mean demand plus safety factor adjusted by lead time and standard deviation) correctly describes the order-up-to formula: (L+1)·mean(D) + k·σ̂·√(L+1). A (ordering exactly last period's sales = no lead time or safety stock). B (fixed percentage above mean = not lead-time or σ adjusted). D (ordering only when below threshold = describes (s,Q) policy). Well-constructed item with clear formula support."),
    # 329
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (finding l1 as maximum m such that sum of excess capacity from m highest-cost plants ≤ total excess capacity) identifies the key determination step. A (calculating total excess capacity = prerequisite step). C (determining j(l) as index = ranking setup, not the key determination). D (applying fractional adjustment = final step AFTER l1 is found). Chunk directly states this algorithm. Good procedural knowledge item."),
    # 330
    (5,3,4,False,"REVISE","True",True,True,True,True,False,
     "B (each department handoffs orders to the next, creating delays and disconnects) is directly supported by the chunk ('sequential relay race... separate handoffs... delays and disconnects'). Reviewer sa=2 is inconsistent with the clear chunk support—likely saw a different top chunk in their review tool. A (seamless with no delays = opposite), D (cross-functional teams collaborate = describes the integrated org). dq=3: A and D are obviously wrong. dm=False: basic recall should be 'very easy' not just 'easy'. distractors_wrong=True."),
    # 331
    (5,3,4,False,"REVISE","True",True,False,False,True,False,
     "A (-cg + g(p)(p-c) + p·E[min(z,ε)]) represents expected revenue in additive model where z=y-g(p) is the safety stock above deterministic component. This requires knowing the z=y-g(p) substitution. D (multiplicative model formula notation: ap^(-b-1)) is a good trap for students who confuse the two models. dm=False: formula derivation in z-substituted form is hard-level content classified as easy. Replace with the standard r(y,p)=-cy+p·E[min(y,D)] form or reclassify as hard."),
    # 332
    (5,3,4,False,"REVISE","True",True,True,True,True,False,
     "C (small changes in customer demand lead to large fluctuations in orders at each stage) is correct. Near-duplicate of Items 343, 348, 350—excessive repetition of basic bullwhip definition. B ('order sizes decrease as they move upstream' = obviously WRONG: they increase). D ('less pronounced with longer lead times' = obviously WRONG). dq=3: B and D are obviously wrong distractors. Eliminate this version; retain Items 343 and 350 which have better distractor sets."),
    # 333
    (3,4,4,False,"REVISE","True",True,False,False,True,False,
     "C (in multi-stage SC with centralized information, each stage's order-up-to policy is based on actual demand data) is correct per the centralized bullwhip theory. B ('sophisticated forecasting reduces bullwhip' = WRONG per chunk: more sophisticated demand models like order-up-to WORSEN decentralized bullwhip). A ('completely eliminated by centralized sharing' = too strong). D ('depends SOLELY on individual stage lead times' = WRONG). sa=3: chunk covers the decentralized math; C's claim about centralized case needs a different chunk section. verifiable=False for C without seeing the centralized case formula. dm=False: hard content not easy level."),
    # 334
    (4,3,5,True,"REVISE","True",True,True,True,True,False,
     "B ('production can be zero or at full capacity, but NOT between the two extremes') is the more precise ZICO policy statement compared to Item 324. A (always at full capacity = WRONG), C (must be exactly half = WRONG), D (never zero = WRONG). Near-duplicate of 324 but preferred version for precision. dq=3: A, C, D are all very obviously wrong. Replace with options like 'Production must equal minimum of capacity and remaining demand' (ZICO corollary) to create better near-miss options. Eliminate 324; keep 334."),
    # 335
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (increased cycle times and inventory build-up) directly stated in the chunk. A (improved coordination = opposite). C (enhanced responsiveness = opposite). D (reduced capital in excess inventory = opposite). Good discrimination: all wrong answers describe BENEFITS of integration, not consequences of silos."),
    # 336
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (decreasing administrative costs) is the NOT-factor. Chunk discusses rising logistics costs 1984-2007 including transportation, inventory carrying, energy. Administrative costs not mentioned as rising. A, B, D all mentioned as rising cost contributors. Well-constructed NOT-question."),
    # 337
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "D (physical flow and information flow) correctly identifies the two critical SC linking mechanisms. A (financial + information = wrong: financial is not the primary SC linking mechanism). B (physical + financial = missing information flow). C (information + strategic planning = wrong: strategic planning is a decision level, not a linking mechanism). Good discrimination between the three types of flows."),
    # 338
    (3,4,5,False,"REVISE","True",False,False,False,True,True,
     "A ('maintain market presence through competitive positioning') as the TRANSACTION MOTIVE is problematic: transaction motive traditionally describes holding inventory to service regular demand transactions (smoothing supply-demand flows). 'Competitive positioning' is more strategic, not transactional. B (buffer against uncertainty = PRECAUTIONARY). C (price fluctuations = SPECULATIVE). D (reduce transportation costs = ordering motive). Flag: A may be wrong key if 'transaction motive' follows standard SCM taxonomy. Chunk (inventory = cumulative supply-demand difference) doesn't explicitly define the three holding motives. Verify source text's definition of transaction motive before accepting A."),
    # 339
    (5,4,5,True,"ACCEPT","True",True,True,False,True,True,
     "B (-cy + p∫₀ʸ(1-F(x))dx) is correct using the integration form. Chunk states r(y,p) = -cy + p·E[min(y,D)]. Flag: mathematically E[min(y,D)] = ∫₀ʸ(1-F(x))dx, so B and C are equivalent representations. The question presumably intends B as the 'explicit leftover inventory' integral form, distinguishing it from the expectation form in C. Reviewer ACCEPT with sa=5 indicates the source distinguishes between these representations. Retain B as preferred form showing the integration connection."),
    # 340
    (5,4,5,True,"REVISE","True",True,True,False,True,False,
     "B (cost function remains relatively flat even when order quantities significantly differ from Q*) is correct per the (γ+1/γ)/2 formula. Near-duplicate of Item 322—both items ask the identical question with very similar options. Eliminate 340; prefer Item 322 which has slightly cleaner distractor phrasing."),
    # 341
    (5,4,5,True,"REVISE","True",True,True,False,True,False,
     "A (insurance, maintenance, opportunity cost) correctly identifies the three carrying cost components. Near-duplicate of Item 321. Item 341 has better chunk alignment (dist=0 chunk explicitly lists the three components with percentages). dq=4: B (storage, handling, deterioration = subcategories of maintenance) is a good near-miss trap. C (production, transportation, purchasing = supply chain costs, not carrying costs) and D (risk preferences = model structure) are clearly wrong. Eliminate Item 321; keep Item 341."),
    # 342
    (4,3,5,False,"REVISE","True",False,False,False,True,False,
     "B (integrates order entry, forecasting, inventory management, production, procurement, delivery into unified system) correctly describes COMS. Near-duplicate of Items 299, 344. The dist=0 chunk is the logistics scorecard framework chunk (NOT the COMS chunk)—chunk mismatch. A (sequential with functional barriers = pre-COMS state). C (solely internal efficiency = misses market-oriented integration). D (relay race = the old metaphor COMS replaces). dm=False: COMS structure is medium-level, not easy. Eliminate this version; prefer 299 or 344."),
    # 343
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "A (small changes in customer demand lead to large fluctuations in orders as they move upstream) correct and directly supported. B (production planning more stable than retailer orders = WRONG: customer demand is MOST stable; production planning is MOST volatile). C (customer demand is highly variable = WRONG: opposite). D (lead times have no significant impact = WRONG). Near-duplicate of Items 332, 348, 350—excessive repetition, but keep 343 and 350 as preferred versions."),
    # 344
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (integrates various functions into unified system responding to market signals) correctly describes COMS operational structure. Near-duplicate of Items 299, 342. A (sequential with functional barriers = opposite). C (solely internal efficiency = wrong). D (organized around individual departments = opposite). Reviewer ACCEPT with sa=5. Eliminate duplicate versions; keep 344 as the ACCEPT version."),
    # 345
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (increased operational costs due to higher energy prices and port congestion) correctly identifies 2021 freight rate drivers. A (significant decrease in global demand = WRONG: demand increased sharply post-COVID). C (reduced vessel capacity due to shipbuilding decline = WRONG: congestion reduced effective capacity, not new shipbuilding). D (decreased labor issues = WRONG: labor issues INCREASED). Chunk directly supports B."),
    # 346
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "A (cumulative difference between supply and demand over time) correctly defines inventory. B (cost of holding goods = carrying cost definition, not inventory). C (number of products managed = SKU count). D (total amount supplied to customers = confuses supply with inventory level). Straightforward definition item with chunk support."),
    # 347
    (4,3,5,True,"REVISE","True",True,True,False,True,False,
     "C (as π increases, s* approaches Q) is correct: from s*=√(2DK/h)·√(π/(π+h)), as π→∞, s*→√(2DK/h)=Q*. However D (as π decreases, s* approaches zero) is ALSO correct: as π→0, π/(π+h)→0, so s*→0. Double-correct-answer issue between C and D. Revise D to make it false (e.g., D: 'As π decreases, Q* increases significantly' which is false since Q*=√(2DK/h)·√((π+h)/π) increases as π→0). Or replace D with 'As π increases, s* approaches zero' (directly wrong—opposite of C)."),
    # 348
    (5,4,3,False,"REVISE","True",True,True,False,True,False,
     "B (small changes in customer demand lead to large order fluctuations upstream) is correct. Near-duplicate of Items 332, 343, 350—fourth version of the basic bullwhip definition question. sc=3: stem is vague compared to Items 343 and 350. Eliminate 348; retain 343 and 350."),
    # 349
    (5,3,4,True,"REVISE","True",True,True,True,True,False,
     "B (enable firms to reduce costs associated with inventory, transportation, and warehousing) is directly supported by the chunk. A (allow firms to IGNORE customer demand = obviously wrong joke distractor). C (make it easier to increase prices = obviously wrong joke distractor). D (help firms focus solely on INTERNAL operations = wrong: SC systems involve external partners). dq=3: A and C are joke distractors. Replace A and C with plausible wrong options (e.g., A: 'They automate replenishment decisions, removing the need for demand forecasting'; C: 'They enable firms to optimize each supply chain stage independently without coordination')."),
    # 350
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (small fluctuations in customer demand cause increasingly large variations in orders upstream) is correct and well-supported. A (order sizes DECREASE as they move upstream = obviously WRONG: opposite). C (lead times decrease when inventory high = wrong description entirely). D (production plans display relatively STABLE fluctuations = WRONG: production planning is the MOST volatile stage). Near-duplicate of 332, 343, 348—keep 343 and 350 as preferred versions with better distractor discrimination."),
]

COLS = [
    "claude_source_alignment", "claude_distractor_quality", "claude_stem_clarity",
    "claude_difficulty_match", "claude_decision", "agrees_with_reviewer",
    "chunks_support_question", "correct_answer_verifiable", "distractors_clearly_wrong",
    "reviewer_source_call_accurate", "flag_ambiguity", "claude_notes",
]

decisions = []
for offset, row in enumerate(RAW):
    item = items[300 + offset]
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
print(f"Batch 7 written: {len(decisions)} items")
for k, v in sorted(decisions_count.items()):
    print(f"  {k}: {v}")
