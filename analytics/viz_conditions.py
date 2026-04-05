from __future__ import annotations

from viz_theme import BASE_COND_COLORS


BASE_COND_ORDER = ["local/local", "local/haiku", "haiku/local", "haiku/haiku"]


def ordered_conditions(conditions):
    unique = []
    seen = set()
    for cond in conditions:
        if cond in seen:
            continue
        seen.add(cond)
        unique.append(cond)
    known = [c for c in BASE_COND_ORDER if c in seen]
    extra = sorted(c for c in unique if c not in BASE_COND_ORDER)
    return known + extra


def condition_color_map(conditions):
    ordered = ordered_conditions(conditions)
    color_map = {}
    for i, cond in enumerate(ordered):
        color_map[cond] = BASE_COND_COLORS[i % len(BASE_COND_COLORS)]
    return color_map


def condition_label(cond):
    return str(cond).replace("/", "/\n")


def review_condition_label(cond, lane_key: str | None = None):
    raw = str(cond)
    if raw == "gpt/baseline":
        if lane_key == "claude":
            return "gpt/\nclaude"
        if lane_key == "codex":
            return "gpt/\ncodex"
    return condition_label(raw)
