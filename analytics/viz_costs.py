from __future__ import annotations


_HARD_GEN_IN = 59_475
_HARD_GEN_OUT = 9_496
_HARD_REV_IN = 54_690
_HARD_REV_OUT = 5_367
_INGEST_IN = 58 * (1_000 + 1_218) // 4
_INGEST_OUT = 58 * 500 // 4

MODELS = {
    "Local\n(Qwen 7B)": (0.0, 0.0, "#78909c"),
    "Haiku 4.5": (0.80, 4.00, "#29b6f6"),
    "Sonnet 4.6": (3.00, 15.00, "#ab47bc"),
    "Opus 4.6": (15.00, 75.00, "#ef5350"),
}


def stage_cost(in_tok, out_tok, pi, po):
    return in_tok / 1e6 * pi + out_tok / 1e6 * po


def pipeline_costs():
    costs = {}
    for model, (pi, po, _) in MODELS.items():
        i = stage_cost(_INGEST_IN, _INGEST_OUT, pi, po)
        g = stage_cost(_HARD_GEN_IN, _HARD_GEN_OUT, pi, po)
        r = stage_cost(_HARD_REV_IN, _HARD_REV_OUT, pi, po)
        costs[model] = {"ingest": i, "generate": g, "review": r, "total": i + g + r}
    return costs
