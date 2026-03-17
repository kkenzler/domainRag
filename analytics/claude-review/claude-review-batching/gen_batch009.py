"""Generate batch009.json — Claude review decisions for items 401-450."""
import json
from pathlib import Path

INPUT = Path("claude_review_input.json")
OUTPUT = Path("batch009.json")

with open(INPUT, encoding="utf-8") as f:
    items = json.load(f)

# (align, dist, clarity, dm, decision, agrees, chunks_ok, verifiable, distractors_wrong, rev_acc, flag, notes)
RAW = [
    # 401
    (4,4,4,False,"REVISE","True",True,True,False,True,False,
     "A (customer satisfaction levels) is correctly NOT a direct strategic sourcing driver in the chunk (which lists raw material costs, manufacturing costs, freight, duties, yield losses, technical constraints). B, C, D are all mentioned. Near-duplicate of Item 408. dm=False: medium label for a medium-level NOT-question. sa=3 inconsistent with fairly direct chunk support; A is not listed while B, C, D are. Eliminate one of the near-duplicate versions."),
    # 402
    (4,4,4,False,"REVISE","True",True,True,False,True,False,
     "B (ZICO is more general policy extending ZIO by incorporating capacity constraints) is correct per chunk. A (both applicable to capacity-constrained = WRONG: ZIO is NOT for capacity-constrained problems). C (ZIO and ZICO equivalent = WRONG). D (ZICO simplifies by allowing only full-capacity or zero-production = mischaracterizes: ZICO allows zero inventory OR zero production OR full capacity—three states, not two). Near-duplicate of Items 371, 385. Eliminate excess versions; keep Item 385."),
    # 403
    (4,3,4,True,"REVISE","True",True,True,False,True,False,
     "B (optimal Q determined by balancing marginal profit against marginal cost) is correct per the newsboy chunk. A (Q always increases → profit always increases = WRONG). C (Q has no impact on risk = WRONG: chunk explicitly says risk increases with Q). D (profit maximized when inventory lowest = WRONG: zero inventory means no sales). Near-duplicate of Items 303, 319. dq=3: C and D are somewhat obviously wrong. Eliminate excess versions."),
    # 404
    (5,3,4,False,"REVISE","True",True,True,True,True,False,
     "D (transportation costs) is correctly NOT a holding cost. A (insurance ~2%), B (maintenance ~6%), C (opportunity cost 7-10%) are all standard holding cost components per the chunk. Near-duplicate of Items 169, 173, 259, 264. dq=3: D is too obviously wrong as a 'holding cost'—transportation is clearly a movement cost. Replace D with something more subtle (e.g., D: 'depreciation of inventory management software licenses' which sounds like an overhead holding cost but is an IT expense). distractors_wrong=True."),
    # 405
    (4,4,4,True,"ACCEPT","True",False,True,False,True,False,
     "D (includes fixed AND variable ordering costs as well as holding costs per unit of inventory) correctly describes W-W model components. A (balances production levels with holding costs = too vague; W-W doesn't set production levels per se). B (requires initial inventory to be non-zero = WRONG: W-W assumes zero initial inventory). C (can ALWAYS be found using shortest path in O(T²) = too strong; more sophisticated algorithms achieve O(T ln T)). Reviewer ACCEPT confirmed with sa=5. Note: dist=0 chunk covers capacity-constrained lot sizing (ZICO), not W-W—but reviewer confirmed alignment."),
    # 406
    (3,4,4,False,"REVISE","True",True,False,False,True,False,
     "D (reducing order batching) correctly mitigates bullwhip by reducing lead times. A (increasing inventory = WRONG: increases lead times via Little's Law). B (smaller and more frequent orders = also correct—this IS essentially the same as reducing order batching). C (sharing POS data = reduces bullwhip but through information, not lead time reduction). Double-correct-answer concern: B and D describe the same strategy (smaller more frequent orders = reduced order batching). Revise B to describe a different approach (e.g., B: 'Increasing safety stock at each stage to absorb demand shocks') to make D unambiguously correct. chunks_ok=True but verifiable=False due to B=D equivalence."),
    # 407
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (managing uncertainty across various sources including production disruptions and supplier risks) correctly identifies the key SC challenge beyond supply-demand matching. A (ensuring procurement conducted independently = wrong approach that causes problems). C (focusing solely on reducing transportation delays = too narrow). D (ignoring quality issues = obviously wrong). Chunk directly supports B. Near-duplicate of Items 373, 415."),
    # 408
    (3,2,4,False,"REVISE","True",True,True,False,True,False,
     "D (customer satisfaction levels) is correctly NOT a key strategic sourcing driver. Near-duplicate of Item 401. The chunk lists A (freight costs for existing lanes), B (duties), C (variable manufacturing costs) as explicit sourcing drivers. D (customer satisfaction) is an outcome goal, not a direct sourcing input. dq=2: D is too obviously wrong as a strategic sourcing driver. Replace with something that sounds like a sourcing driver but isn't in the chunk (e.g., D: 'CEO personal preferences for domestic suppliers'). Eliminate one version; keep Item 401."),
    # 409
    (4,4,4,False,"REVISE","True",True,True,False,True,False,
     "C (strong commodity demand and pricing power) correctly identifies the factor that compensated for elevated logistics costs per the equity price data in the chunk. A (substantial increase in ocean freight rates = not compensating for anything—causes the problem). B (reduction in global SC pressure since 2020 = WRONG: pressure increased). D (decrease in export volumes = WRONG: exports remained robust). Near-duplicate of Items 390, 421, 437. dm=False: medium label; this is straightforward reading comprehension from the equity price data."),
    # 410
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (tactical decisions) correctly identifies the SC management level that deploys resources to match supply with demand. A (strategic = long-term policies and objectives). C (operational = daily execution tasks). D (none of above = WRONG). The three-level framework is directly described in the chunk context. Clear distinction between strategic (what), tactical (how/when), operational (do)."),
    # 411
    (3,2,4,False,"REVISE","True",True,True,True,True,False,
     "B (variance of order quantities relative to demand variance increases significantly due to forecasting) correctly describes two-stage bullwhip manifestation. A (order quantities more STABLE than demand = WRONG: opposite). C (retailers can perfectly predict demand = WRONG: opposite). D (safety stock adjustments REDUCE impact of lead times = WRONG per the formula). dq=2: A, C, D are all too obviously wrong. Replace with options that test specific aspects of the bullwhip formula. distractors_wrong=True."),
    # 412
    (4,3,4,False,"REVISE","True",True,True,True,True,False,
     "B (inventory models can be designed for multiple products or perishable items and may involve stochastic demand and multiple objectives) is correct—reflecting the multi-dimensional inventory model framework. A (solely single product with deterministic demand = WRONG). C (only finite horizons without stochastic demand = WRONG). D (exclusively minimize costs = WRONG: can maximize profit). dm=False: medium label for a medium-level multi-dimensional description. dq=3: A, C, D are too obviously wrong—they all make absolute claims that contradict the chunk. distractors_wrong=True."),
    # 413
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (through joint business planning with manufacturers and suppliers, eliminating wasteful practices) correctly describes P&G's approach per the chunk. A (increasing prices on retail customers = WRONG: P&G SAVED customers $65M). C (reducing suppliers to single source = WRONG). D (outsourcing to lower-cost countries = WRONG). Chunk directly states P&G had manufacturers and suppliers work together. Clear, well-supported item."),
    # 414
    (4,3,4,False,"REVISE","True",True,True,False,True,False,
     "B (bullwhip exacerbated by longer lead times and smoothing parameter p) correctly identifies the mathematical drivers. A (retailers unable to accurately predict demand, leading to larger order fluctuations = partially correct mechanism but lacks the specific L and p factors). C (production planning more efficient than distributors = WRONG: production planning is MOST volatile). D (customer demand inherently unstable = WRONG: customer demand is stable; upstream amplification is the issue). dm=False: identifying the specific mathematical parameters of the bullwhip formula is hard-level content, not medium. Align=4 (chunk shows amplification dynamics but not the explicit L and p parameter language)."),
    # 415
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (balancing competing objectives across different functional areas such as purchasing, manufacturing) correctly identifies the key SCM challenge. A (ensuring all suppliers in same country = wrong simplification). C (focusing solely on cost minimization = wrong approach). D (ignoring SC integration = opposite of SCM goal). Chunk directly supports B. Near-duplicate of Items 373, 407."),
    # 416
    (3,4,4,False,"REVISE","True",False,True,False,True,False,
     "B (relay race with separate handoffs creating delays) correctly describes the functionally-organized order-to-delivery analogy. A (rugby team = the INTEGRATED organization's metaphor). C (integrated system responding to market signals = describes COMS, the goal). D (cross-functional team = describes the process-driven organization). Chunk mismatch: dist=0 chunk is the COMS integration chunk, not the relay race/functionally-organized chunk. Remap to the order-to-delivery relay race chunk. dm=False: hard label for a basic recall question about an analogy."),
    # 417
    (4,4,4,False,"REVISE","True",True,True,False,True,False,
     "B (multiple products, stochastic demand, multiple locations) correctly identifies the most complex combination. A (single product, deterministic, single location = simplest). C (perishable, endogenous demand, continuous review = complex but lacks the network complexity of multiple locations). D (durable, exogenous constant demand, periodic review = classical simple). Near-duplicate of Items 308, 417. dm=False: hard label for what is a medium-level complexity spectrum question."),
    # 418
    (4,3,4,False,"REVISE","True",True,False,False,True,False,
     "D (improves customer service by reducing delays through integrated processes, but also increases complexity in managing cross-functional coordination) attempts a nuanced answer. A (enhances customer service by creating single point of accountability = also partially correct per the chunk). Double-correct-answer concern: A and D both describe real benefits of horizontal orgs. D's 'but also increases complexity' is a caveat not explicitly supported by the chunk. verifiable=False for D's full claim. Revise D to remove the unsupported complexity claim, or revise A to add a limitation to distinguish them clearly."),
    # 419
    (1,3,4,False,"REVISE","True",False,False,False,True,False,
     "C (optimal Q may increase due to reduced risk, but still determined by marginal profit/cost balance) correctly captures the buyback contract effect. A (Q will ALWAYS be higher = too strong). B (Q remains unchanged = WRONG: buyback does affect Q). D (Q will decrease because manufacturer's repurchase obligation limits over-ordering incentive = WRONG: buyback REDUCES over-ordering risk → MORE is ordered). Massive chunk mismatch: dist=0 chunk is about quantity discounts (incremental vs all-units discounts), NOT buyback agreements. sa=1 is appropriate. Remap to the buyback/revenue sharing supply contracts chunk."),
    # 420
    (1,3,4,False,"REVISE","True",False,False,False,True,False,
     "D (safety stock decreases AND average inventory decreases) correctly describes the effect of centralization via risk pooling. A (safety stock increases, avg decreases = WRONG: safety stock decreases under centralization). B (both increase = WRONG). C (safety stock decreases, avg unchanged = WRONG: avg also decreases). Massive chunk mismatch: dist=0 chunk is the Xerox/Walmart competitive advantage examples, NOT the risk pooling theory. sa=1 is appropriate. Remap to the centralization/risk-pooling formula chunk. Near-duplicate of Items 115, 278, 284."),
    # 421
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "A (global demand for ag commodities remained strong despite increased shipping costs) correctly explains the resilience of US ag export levels. B (time series methods failed to account for SC = WRONG: methods were valid). C (simulation model overestimated = WRONG). D (statistical analysis flawed = WRONG: analysis was robust). Chunk directly states 'no measurable negative effects on U.S. maritime agricultural export levels.' Near-duplicate of Items 304, 409, 437."),
    # 422
    (3,4,4,False,"REVISE","True",False,False,False,True,False,
     "D (push manages inventory based on forecasts of future demand; pull replenishment triggered by actual demand) is the KEY but B (pull more responsive to actual demand because bases production on actual demand) ALSO describes the same push/pull distinction. Double-correct-answer issue: B and D both correctly contrast push (forecast-driven) with pull (demand-triggered). A (push relies on actual customer orders = WRONG: that's pull). Chunk mismatch: dist=0 chunk is about information systems for SC, not the push/pull theory. Remap to push/pull strategy chunk. Revise B to be clearly wrong."),
    # 423
    (2,3,4,False,"REVISE","True",False,False,False,True,False,
     "B (higher shipping costs and increased demand resulted in elevated logistical uncertainty and pressures) is vague and doesn't capture the key finding: US ag EXPORTS REMAINED ROBUST despite these pressures. B merely describes the pressures without noting the surprising resilience. A (increased demand led to surplus, shipping reduced transportation efficiency = wrong interpretation). C (led to decrease in aggregate demand = WRONG). D (no significant impact = wrong: there WAS supply chain pressure). Chunk mismatch: dist=0 chunk is generic SC environment challenges, not the 2021 ag export resilience finding."),
    # 424
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "B (inventory policies shaped by combination of demand characteristics, lead time duration, cost structures, and organizational objectives) correctly describes the multidimensional nature of inventory policy. A (solely determined by number of products = WRONG). C (dictated exclusively by SC complexity and external market forces = WRONG: internal objectives also matter). D (fixed once established = WRONG: policies adapt to changing conditions). Well-constructed item that captures the multi-dimensional inventory policy concept."),
    # 425
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "D (rank plants by cost multipliers, determine l1 as maximum m such that sum of excess capacity from m highest-cost plants ≤ total excess capacity, then apply fractional adjustment) correctly describes the multi-plant production cut-back algorithm. Near-duplicate of Items 329, 368, 369, 440. A (equal allocation regardless of cost multiplier = WRONG). B (cut back only the single highest-cost plant = WRONG: cut back multiple). C (rank by cost multiplier and cut back from LOWEST ranked = WRONG: from HIGHEST-cost). Excessive near-duplication of this algorithm question."),
    # 426
    (5,4,4,False,"REVISE","True",True,True,False,True,False,
     "D (decrease in number of production lines required, thereby reducing capital expenditure) is correctly NOT achieved: the chunk explicitly states the optimization EFFECTIVELY ADDED one and a half production lines worth of capacity without capital expenditure (not decreased lines). A, B, C are all directly stated in the chunk. dm=False: hard label for a factual recall NOT-question about PBG outcomes. This is easier than hard level."),
    # 427
    (5,3,4,False,"REVISE","True",True,True,True,True,False,
     "B (by positioning logistics at core, organizations can align planning with execution, ensuring integration of all SC activities) correctly describes logistics as organizational transformation driver. A (logistics as administrative function supporting sequential processes = WRONG: old view). C (logistics irrelevant in modern business = WRONG). D (role limited to shipping and delivery = WRONG). Chunk directly supports B. dq=3: A, C, D are too obviously wrong. Replace with more nuanced wrong options. dm=False: hard label for a medium-level logistics concept. distractors_wrong=True."),
    # 428
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (reorganize around end-to-end processes with flat hierarchies and cross-functional teams) correctly describes horizontal process-driven organizations. A (horizontal orgs maintain functional silos but integrate through cross-functional meetings = incomplete structural change). B (integrate logistics into existing vertical structures = doesn't address the structural barrier). D (rely solely on traditional functional departments = opposite). Near-duplicate of Item 383. Reviewer ACCEPT confirmed."),
    # 429
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "B (variability in order quantities increases at each stage due to amplification of demand signals) correctly describes decentralized multi-stage bullwhip. A (bullwhip mitigated as lead times increase = WRONG: longer lead times WORSEN bullwhip). C (variance DECREASES significantly from distributor to manufacturer = WRONG). D (safety stock adjustments have NO impact on order variability = WRONG: safety factor k·σ̂ affects the order quantity formula). dm=False: hard label for medium-level bullwhip concept. Near-duplicate of Items 372, 434, 443."),
    # 430
    (4,3,4,False,"REVISE","True",True,False,False,True,False,
     "B (firm implements efficient inventory policy that reduces parts inventory by 26% annually, achieving cost leadership) is the positive illustrative example. A (holding more inventory than necessary = obviously negative). C (decentralized inventory across multiple warehouses leading to increased costs = depends on context, not necessarily negative). D (speculative inventory strategy capitalizing on price fluctuations = risky, not necessarily wrong). The '26% annual reduction' figure needs chunk verification—the chunk mentions Xerox $700M and Walmart success but not a specific 26% figure. verifiable=False (specific % not confirmed in chunk preview)."),
    # 431
    (5,5,4,True,"ACCEPT","True",True,True,False,True,False,
     "B (63) is accepted by reviewer with sa=5, dq=5. Using s = LT × AVG + z × STD × √LT with LT=10, AVG=5, and 95% service level. B=63 implies: 63 = 10×5 + z×STD×√10 → safety stock = 63-50 = 13 = z×STD×√10. With z=1.65 for 95%, STD ≈ 2.5. This is consistent with the formula. Reviewer confirmed the calculation. The (s,S) policy chunk directly provides the formula. Well-constructed numerical calculation item."),
    # 432
    (3,4,4,False,"REVISE","True",True,False,False,True,False,
     "C (redundancy and safety stock can help manage both demand and supply-side uncertainties) is the KEY. A (bullwhip easily mitigated by accurate demand forecasting = WRONG: not easily). B (strategic decisions primarily focused on short-term adjustments = WRONG: strategic = long-term). D (operational decisions solely concerned with physical flow = WRONG: information flow is also operational). sa=3: the chunk discusses the fundamental challenge of global optimization but doesn't specifically state redundancy/safety stock as the recommended response. verifiable=False for C's specific claim. dm=False: hard label for a medium-level concept."),
    # 433
    (2,4,4,False,"REJECT","Partial",True,False,False,False,True,
     "CRITICAL: KEY=C states 'Aggregate forecasts are less reliable than disaggregate forecasts, making it better to focus on individual product forecasts.' This directly contradicts the fundamental SCM principle: aggregate forecasts are MORE reliable (law of large numbers, risk pooling). D ('Companies can eliminate demand uncertainty by using advanced forecasting techniques' = also WRONG but obviously so). A (inventory at constant level = WRONG). B (accuracy improves as forecast horizon extends = WRONG). Same wrong key as Item 327. REJECT: C has wrong key contradicting established SCM theory. reviewer_source_call_accurate=False."),
    # 434
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "B (in decentralized systems, variability amplification compounds across stages due to forecasting errors) correctly contrasts with centralized systems. A (less pronounced in decentralized = WRONG). C (centralized info sharing eliminates bullwhip ENTIRELY = too strong: 'eliminates entirely' is wrong). D (bullwhip exacerbated in CENTRALIZED because of complicated demand models = WRONG: centralized info reduces bullwhip). Near-duplicate of Items 372, 429, 443. Reviewer ACCEPT confirmed."),
    # 435
    (2,3,4,False,"REVISE","True",False,False,False,False,True,
     "C (complexity introduced by duties and taxes in different countries) is the KEY for 'which factor most likely influences choice between subcontracting vs alternative technologies at lower volumes.' However A (fixed costs) and B (variable costs per unit) are MORE directly relevant to the subcontracting vs own-technology choice at lower volumes—per scale curve analysis, the crossover point where subcontracting becomes economical depends on the fixed vs variable cost structure. C (duties and taxes) is a global SC factor that applies broadly, not specifically to the lower-volume technology choice. Chunk mismatch: Asian Paradigm chunk is about dual-mode transportation, not technology scale analysis. Flag: C may be wrong key; A and B are more directly relevant."),
    # 436
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "A (minimize total cost per unit time by balancing ordering, holding, and shortage costs) correctly identifies the objective for perishable goods with uncertain demand over infinite horizon. B (maximize profit by selling as much perishable goods as possible ignoring costs = incomplete: ignores cost trade-offs). C (minimize average number of orders = wrong objective: doesn't address holding or shortage costs). D (maximize service level ignoring ordering and shortage costs = wrong: ignores key cost components). dm=False: hard label for a medium-level objective identification question. Chunk (model dimensions) provides general framework but not perishable-infinite horizon specific guidance."),
    # 437
    (4,3,4,False,"REVISE","True",True,True,False,True,False,
     "A (increased demand for ag commodities and strong global pricing power more than compensated for higher logistics costs) correctly explains the resilience. B (had a surplus of goods = not mentioned in chunk). C (ocean freight rates not as high due to government subsidies = WRONG: rates did increase substantially). D (found alternative modes of transportation = not mentioned as the explanation). Near-duplicate of Items 304, 409, 421. dm=False: hard label for an inference question that is medium-level difficulty."),
    # 438
    (3,2,4,False,"REVISE","True",True,True,True,True,False,
     "B (shorter lead times reduce variability in customer orders as they move upstream) correctly explains the lean SC bullwhip mitigation mechanism. A (shorter lead times increase accuracy of demand forecasting = partially true mechanism but not the direct explanation for bullwhip reduction). C (shorter lead times decrease bullwhip by reducing NUMBER OF STAGES in SC = WRONG: stages don't change). D (shorter lead times enable MORE FREQUENT ORDER BATCHING = WRONG: shorter lead times REDUCE order batching). dq=2: C and D are obviously wrong. distractors_wrong=True. Replace C and D with more nuanced wrong options."),
    # 439
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "D (balancing the need for safety stock against the risk of overstocking inventory) correctly identifies the SC uncertainty challenge. A (ensuring all suppliers in same country = obviously wrong—irrelevant to uncertainty challenge). B (maintaining consistent production schedules despite varying demand = plausible but too operationally narrow). C (guaranteeing 100% recycled materials = obviously wrong—sustainability goal, not uncertainty challenge). Near-duplicate of Items 407, 415, 432. Reviewer ACCEPT confirmed."),
    # 440
    (5,4,5,True,"ACCEPT","True",True,True,False,True,False,
     "C (largest m such that sum of excess capacity from m highest-cost plants does not exceed total excess capacity E) correctly defines l1 in the multi-plant production algorithm. A (sum of all plant capacities divided by E = wrong formula). B (index j(l) of plant with highest cost multiplier = describes the ranking setup, not l1). D (l1 plus a fractional adjustment = describes l*, not l1). Near-duplicate of Items 329, 368, 369, 425. Chunk directly supports C. Reviewer ACCEPT confirmed."),
    # 441
    (2,2,1,False,"REJECT","Partial",False,False,False,False,True,
     "CRITICAL: Malformed item with empty question stem. Options A, B, C, D each contain a different MCQ sub-question rather than answer options: A='In EOQ model, if actual Q is 150% of optimal, what percentage over-cost?', B='EPQ model differs from EOQ primarily because:', C='What does s represent in EOQ backorders?', D='In EOQ model, which factor is NOT considered?' (KEY=D). This item cannot function as a MCQ—the question stem is absent. REJECT: structurally defective item requiring complete reconstruction as a proper MCQ."),
    # 442
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "B (strong global demand for ag commodities has more than offset negative impacts of SC disruptions and rising freight rates) correctly explains the resilience of US ag equity valuations. A (high commodity prices not sufficient to compensate = WRONG: equity prices ROSE substantially). C (lack of measurable export declines indicates alternative routes = too narrow interpretation). D (overall profitability declined despite no export decline = contradicts the equity price increase data). Chunk directly shows substantial equity price increases. Near-duplicate of Items 390, 409, 421."),
    # 443
    (2,3,4,False,"REVISE","True",True,True,False,True,False,
     "B (bullwhip more pronounced due to distortion of demand signals as they propagate upstream) correctly contrasts decentralized vs centralized. A (less pronounced in decentralized = WRONG). C (mitigated by moving average with FEWER observations = WRONG: fewer obs = smaller p = WORSE bullwhip, not better). D (doesn't exist in decentralized because orders are based on... = WRONG). sa=2: chunk shows the order formula which implies the decentralized amplification, but the chunk preview doesn't explicitly state the centralized vs decentralized contrast. Near-duplicate of Items 372, 429, 434."),
    # 444
    (3,4,4,False,"REVISE","True",False,False,False,True,False,
     "A (supply contracts increase order quantities by reducing risk associated with unsold inventory) correctly describes the buyback/revenue sharing effect. B (decrease Q because align incentives for higher sales = WRONG direction: incentivizing higher sales → MORE orders, not fewer). C (no effect on quantities = WRONG). D (reduce Q by increasing cost of ordering too much = WRONG: contracts REDUCE the downside risk of over-ordering, incentivizing MORE). Chunk mismatch: dist=0 chunk is the single-period uncertain demand/newsboy chunk, not the supply contracts chunk. Remap to supply contracts chunk."),
    # 445
    (3,3,3,False,"REJECT","Partial",True,False,False,False,True,
     "CRITICAL: KEY=D states (a + bc - 2bp + E[min(z*, ε)]) / (2b) which is circular (contains p, the variable being solved for). The correct optimal price formula from dR/dp=0 in the additive newsboy+pricing model is: a - bp - bp + bc + E[min(z*,ε)] = 0 → 2bp* = a + bc + E[min(z*,ε)] → p* = (a + bc + E[min(z*,ε)]) / (2b), which equals Option A. KEY=D contains -2bp which would make the formula self-referential without a valid closed-form solution. REJECT: wrong key (A is correct, not D). reviewer_source_call_accurate=False."),
    # 446
    (2,3,4,False,"REVISE","True",False,False,False,True,False,
     "B (centralization allows for better risk pooling through reduced demand variability when aggregated) correctly explains why centralization reduces safety stock and average inventory. A (eliminates ALL forms of uncertainty = WRONG: reduces but doesn't eliminate). C (increases TRANSACTION MOTIVE by enhancing production scale = wrong reasoning: transaction motive is about servicing regular orders, not about safety stock reduction). D (reduces PRECAUTIONARY MOTIVE by eliminating need for inventory buffers = WRONG: precautionary motive remains, just requires less safety stock due to pooling). Chunk mismatch: dist=0 chunk is competitive advantage examples (Xerox, Walmart), not risk pooling theory. sa=2 is appropriate. Remap to risk pooling math chunk."),
    # 447
    (5,4,4,True,"ACCEPT","True",True,True,False,True,False,
     "B (shortage cost π; as π increases, s* approaches Q*) correctly identifies the primary influence. From s*=√(2DK/h)·√(π/(π+h)): as π→∞, s*→√(2DK/h)=Q*. A (ordering cost K; as K increases, s* DECREASES = WRONG: s* increases with K since s*=√(2DK/h)·√(π/(π+h))). C (holding cost h; as h increases, s* INCREASES = WRONG: s* decreases with h). D (demand rate D; s* remains unchanged = WRONG: s* scales with √D). Note: item was not reviewed by human reviewer (rev=UNKNOWN). Claude assessment: B is clearly correct per the backorder formula."),
    # 448
    (3,4,4,False,"REVISE","True",True,True,False,True,False,
     "C (supplier selection based on lowest cost alone) is correctly NOT a typical strategic output alignment consideration—SC strategy balances cost, service, quality, and flexibility across strategic outputs. A (delivery or service time), B (inventory levels and positioning), D (service level on inventory availability) are all legitimate strategic outputs that logistics policies align with. dm=False: hard label for a medium-level strategic outputs question. align=3: chunk discusses SC strategy inputs/outputs but may not explicitly list these as strategic outputs."),
    # 449
    (1,2,1,False,"REJECT","Partial",False,False,False,False,True,
     "CRITICAL: Malformed item with empty question stem. Same structural defect as Item 441. Options A, B, C, D each contain a different MCQ sub-question: A='In EOQ model, if actual Q is 150% of optimal, how much more cost?', B='EPQ model differs from EOQ in that:', C='Which statement about EOQ model with planned backorders is true?', D='In EOQ model, which factor does NOT affect optimal order quantity?' (KEY=D). REJECT: structurally defective item requiring complete reconstruction."),
    # 450
    (3,4,4,False,"REVISE","True",False,False,False,True,False,
     "B (pull-based models more responsive to actual demand, whereas push-based focus on forecast-driven production and inventory pre-positioning) correctly contrasts push vs pull. A (push relies on actual customer orders = WRONG: that's pull). C (both use same methods; difference only in timing = WRONG). D (push prioritizes rapid fulfillment over accurate forecasting = WRONG characterization of push; push IS forecast-driven). Chunk mismatch: dist=0 chunk is about information systems for SC management, not push/pull strategies. Near-duplicate of Item 422. Remap to push/pull strategy chunk."),
]

COLS = [
    "claude_source_alignment", "claude_distractor_quality", "claude_stem_clarity",
    "claude_difficulty_match", "claude_decision", "agrees_with_reviewer",
    "chunks_support_question", "correct_answer_verifiable", "distractors_clearly_wrong",
    "reviewer_source_call_accurate", "flag_ambiguity", "claude_notes",
]

decisions = []
for offset, row in enumerate(RAW):
    item = items[400 + offset]
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
print(f"Batch 9 written: {len(decisions)} items")
for k, v in sorted(decisions_count.items()):
    print(f"  {k}: {v}")
