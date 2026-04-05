from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from viz_conditions import condition_color_map, condition_label, ordered_conditions, review_condition_label
from viz_theme import DEC_COLORS, TEXT_COL, TITLE_COL, style_ax


def _read_csv(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_review_analysis_bundle(analysis_dir: Path) -> dict[str, list[dict]]:
    return {
        "answer_keys": _read_csv(analysis_dir / "review_summary_answer_keys.csv"),
        "condition_difficulty": _read_csv(analysis_dir / "review_summary_condition_difficulty.csv"),
        "failure_modes": _read_csv(analysis_dir / "review_summary_failure_modes.csv"),
        "time_cost": _read_csv(analysis_dir / "review_summary_time_cost.csv"),
        "duplicates": _read_csv(analysis_dir / "review_summary_lane_duplicates.csv"),
        "key_anomalies": _read_csv(analysis_dir / "review_summary_correct_key_anomalies.csv"),
        "lane_long": _read_csv(analysis_dir / "review_item_lane_long.csv"),
    }


def _lane_rows(bundle: dict[str, list[dict]], lane: str | None = None, reviewer_required: bool = False) -> list[dict]:
    rows = bundle["lane_long"]
    if lane is not None:
        rows = [row for row in rows if row["lane"] == lane]
    if reviewer_required:
        rows = [
            row for row in rows
            if row.get("reviewer_decision") not in {"", "None", None}
        ]
    return rows


def answer_key_distribution(ax, bundle: dict[str, list[dict]]):
    rows = [
        row for row in bundle["answer_keys"]
        if row["scope"] == "all_items" and row["slice_type"] == "overall"
    ]
    labels = [row["correct_key"] for row in rows]
    values = [int(row["item_count"]) for row in rows]
    colors = []
    for label in labels:
        if label in {"A", "B", "C", "D"}:
            colors.append({"A": "#4CAF50", "B": "#29B6F6", "C": "#FFB300", "D": "#AB47BC"}[label])
        elif label == "MULTI":
            colors.append("#F44336")
        else:
            colors.append("#78909C")
    bars = ax.bar(labels, values, color=colors, width=0.65)
    for bar, value in zip(bars, values):
        if value:
            ax.text(bar.get_x() + bar.get_width() / 2, value + 4, str(value), ha="center", va="bottom", color=TEXT_COL, fontsize=9)
    style_ax(ax, "Correct Answer Key Distribution (All Items)", "Item Count")


def coverage_heatmap(ax, bundle: dict[str, list[dict]]):
    rows = [row for row in bundle["condition_difficulty"] if row["condition"] != "gpt/baseline"]
    conds = ordered_conditions({row["condition"] for row in rows})
    diffs = ["easy", "medium", "hard"]
    raw_value_map = {(row["condition"], row["difficulty"]): int(row["item_count"]) for row in rows}
    matrix = np.zeros((len(conds), len(diffs)), dtype=float)
    raw_matrix = np.zeros((len(conds), len(diffs)), dtype=int)
    for i, cond in enumerate(conds):
        raw_vals = [raw_value_map.get((cond, diff), 0) for diff in diffs]
        row_max = max(raw_vals) if raw_vals else 0
        for j, diff in enumerate(diffs):
            raw_matrix[i, j] = raw_vals[j]
            matrix[i, j] = (raw_vals[j] / row_max * 100.0) if row_max else 0.0
    im = ax.imshow(matrix, cmap="Blues", aspect="auto", vmin=0, vmax=100)
    for i, cond in enumerate(conds):
        for j, diff in enumerate(diffs):
            pct = matrix[i, j]
            raw = raw_matrix[i, j]
            text = f"{raw}\n({pct:.0f}%)"
            ax.text(j, i, text, ha="center", va="center", color="black", fontsize=9, fontweight="bold")
    ax.set_xticks(range(len(diffs)))
    ax.set_xticklabels([d.capitalize() for d in diffs], color=TEXT_COL)
    ax.set_yticks(range(len(conds)))
    ax.set_yticklabels([condition_label(cond) for cond in conds], color=TEXT_COL)
    ax.set_title("Coverage Completeness by Non-GPT Condition × Difficulty", color=TITLE_COL, fontsize=11, fontweight="bold", pad=8)
    ax.get_figure().colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(colors=TEXT_COL)


def lane_completion(ax, bundle: dict[str, list[dict]]):
    rows = bundle["time_cost"]
    labels = [f"{row['lane_label']} review" for row in rows]
    values = [float(row["completion_percent"]) for row in rows]
    bars = ax.bar(labels, values, color=["#1F77B4", "#FF7F0E"], width=0.6)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 1, f"{value:.1f}%", ha="center", va="bottom", color=TEXT_COL, fontsize=10, fontweight="bold")
    style_ax(ax, "Review Lane Completion", "Percent of Item Set")
    ax.set_ylim(0, 110)


def time_cost_bars(ax, bundle: dict[str, list[dict]]):
    rows = bundle["time_cost"]
    labels = [f"{row['lane_label']} review" for row in rows]
    review_hours = [float(row["estimated_review_hours"]) for row in rows]
    x = np.arange(len(labels))
    bars = ax.bar(x, review_hours, color=["#66BB6A", "#FFA726"], width=0.55)
    for bar, value in zip(bars, review_hours):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.7, f"{value:.1f}h", ha="center", va="bottom", color=TEXT_COL, fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=TEXT_COL)
    style_ax(ax, "Estimated Review Time by Lane", "Estimated Hours")


def failure_modes(ax, bundle: dict[str, list[dict]]):
    order = ["non_accept", "ambiguity_flagged", "low_source_alignment", "difficulty_mismatch", "disagrees_with_reviewer"]
    label_map = {
        "non_accept": "Non-accept",
        "ambiguity_flagged": "Ambiguity",
        "low_source_alignment": "Low align",
        "difficulty_mismatch": "Diff mismatch",
        "disagrees_with_reviewer": "Reviewer disagreement\n(reviewer rows only)",
    }
    lanes = ["claude", "codex"]
    x = np.arange(len(order))
    width = 0.36
    lane_colors = {"claude": "#4CAF50", "codex": "#29B6F6"}
    for i, lane in enumerate(lanes):
        lane_rows = _lane_rows(bundle, lane=lane, reviewer_required=False)
        reviewer_rows = _lane_rows(bundle, lane=lane, reviewer_required=True)
        vals = []
        for mode in order:
            if mode == "non_accept":
                denom_rows = lane_rows
                count = sum(1 for row in denom_rows if row.get("lane_decision") in {"REVISE", "REJECT"})
            elif mode == "ambiguity_flagged":
                denom_rows = lane_rows
                count = sum(1 for row in denom_rows if row.get("flag_ambiguity") == "True")
            elif mode == "low_source_alignment":
                denom_rows = lane_rows
                count = sum(1 for row in denom_rows if row.get("lane_source_alignment") not in {"", None} and float(row["lane_source_alignment"]) <= 3)
            elif mode == "difficulty_mismatch":
                denom_rows = lane_rows
                count = sum(1 for row in denom_rows if row.get("lane_difficulty_match_pass") == "False")
            else:
                denom_rows = reviewer_rows
                count = sum(1 for row in denom_rows if row.get("agrees_with_reviewer") == "False")
            denom = len(denom_rows)
            vals.append(count / denom * 100.0 if denom else np.nan)
        bars = ax.bar(x + (i - 0.5) * width, vals, width, label=f"{lane.capitalize()} review", color=lane_colors[lane])
        for bar, value in zip(bars, vals):
            if np.isnan(value):
                ax.text(bar.get_x() + bar.get_width() / 2, 1.0, "N/A", ha="center", va="bottom", color=TEXT_COL, fontsize=7, style="italic")
            elif value > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, value + 0.5, f"{value:.1f}", ha="center", va="bottom", color=TEXT_COL, fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels([label_map[mode] for mode in order], color=TEXT_COL, fontsize=8)
    style_ax(ax, "Failure Mode Rates by Review Lane", "Percent of applicable items")
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL)


def lane_decision_mix(ax, bundle: dict[str, list[dict]]):
    rows = [
        row for row in bundle["failure_modes"]
        if row["slice_type"] == "overall" and row["failure_mode"] in {"reject", "revise"}
    ]
    time_rows = {row["lane"]: row for row in bundle["time_cost"]}
    lanes = ["claude", "codex"]
    accept = []
    revise = []
    reject = []
    for lane in lanes:
        revise_rate = 0.0
        reject_rate = 0.0
        for row in rows:
            if row["lane"] == lane:
                if row["failure_mode"] == "revise":
                    revise_rate = float(row["rate_percent"])
                elif row["failure_mode"] == "reject":
                    reject_rate = float(row["rate_percent"])
        accept_rate = max(0.0, float(time_rows[lane]["completion_percent"]) * 0 + 100.0 - revise_rate - reject_rate)
        accept.append(accept_rate)
        revise.append(revise_rate)
        reject.append(reject_rate)
    x = np.arange(len(lanes))
    b1 = ax.bar(x, accept, color=DEC_COLORS["ACCEPT"], width=0.6, label="ACCEPT")
    b2 = ax.bar(x, revise, bottom=accept, color=DEC_COLORS["REVISE"], width=0.6, label="REVISE")
    b3 = ax.bar(x, reject, bottom=np.array(accept) + np.array(revise), color=DEC_COLORS["REJECT"], width=0.6, label="REJECT")
    for bars, vals, bottoms in [(b1, accept, np.zeros(len(accept))), (b2, revise, np.array(accept)), (b3, reject, np.array(accept) + np.array(revise))]:
        for bar, value, bottom in zip(bars, vals, bottoms):
            if value > 4:
                ax.text(bar.get_x() + bar.get_width() / 2, bottom + value / 2, f"{value:.0f}%", ha="center", va="center", color="white", fontsize=8, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{lane.capitalize()} review" for lane in lanes], color=TEXT_COL)
    style_ax(ax, "Decision Mix by Review Lane", "Percent of Reviewed Items")
    ax.set_ylim(0, 110)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL)


def anomaly_counts(ax, bundle: dict[str, list[dict]]):
    duplicate_count = len(bundle["duplicates"])
    key_anomaly_rows = bundle["key_anomalies"]
    multi_count = sum(1 for row in key_anomaly_rows if row["correct_key_normalized"] == "MULTI")
    unknown_count = sum(1 for row in key_anomaly_rows if row["correct_key_normalized"] == "UNKNOWN")
    labels = ["Lane duplicates", "Multi-key items", "Unknown keys"]
    values = [duplicate_count, multi_count, unknown_count]
    colors = ["#FF7043", "#AB47BC", "#78909C"]
    bars = ax.bar(labels, values, color=colors, width=0.6)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.3, str(value), ha="center", va="bottom", color=TEXT_COL, fontsize=10, fontweight="bold")
    style_ax(ax, "Exported Data Anomalies", "Count")


def reviewer_agreement_rates(ax, bundle: dict[str, list[dict]]):
    lanes = ["claude", "codex"]
    states = [("True", "Agree", "#4CAF50"), ("False", "Disagree", "#F44336"), ("UNKNOWN", "Unknown", "#78909C")]
    x = np.arange(len(lanes))
    bottom = np.zeros(len(lanes))
    for raw_state, label, color in states:
        vals = []
        for lane in lanes:
            lane_rows = _lane_rows(bundle, lane=lane, reviewer_required=True)
            denom = len(lane_rows) or 1
            if raw_state == "UNKNOWN":
                count = sum(1 for row in lane_rows if row.get("agrees_with_reviewer", "") in {"", "None", None})
            else:
                count = sum(1 for row in lane_rows if row.get("agrees_with_reviewer") == raw_state)
            vals.append(count / denom * 100.0)
        bars = ax.bar(x, vals, bottom=bottom, color=color, width=0.58, label=label)
        for bar, value, bot in zip(bars, vals, bottom):
            if value > 5:
                ax.text(bar.get_x() + bar.get_width() / 2, bot + value / 2, f"{value:.0f}%", ha="center", va="center", color="white", fontsize=8, fontweight="bold")
        bottom += np.array(vals)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{lane.capitalize()} review" for lane in lanes], color=TEXT_COL)
    style_ax(ax, "Agreement With Reviewer Baseline (non-GPT rows)", "Percent of items with reviewer baseline")
    ax.set_ylim(0, 110)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL)


def reviewer_vs_lane_nonaccept(ax, bundle: dict[str, list[dict]]):
    lanes = ["claude", "codex"]
    labels = [f"{lane.capitalize()} review" for lane in lanes]
    reviewer_nonaccept = []
    lane_nonaccept = []
    matched_nonaccept = []
    for lane in lanes:
        lane_rows = _lane_rows(bundle, lane=lane, reviewer_required=True)
        denom = len(lane_rows) or 1
        reviewer_nonaccept.append(sum(1 for row in lane_rows if row.get("reviewer_decision") in {"REVISE", "REJECT"}) / denom * 100.0)
        lane_nonaccept.append(sum(1 for row in lane_rows if row.get("lane_decision") in {"REVISE", "REJECT"}) / denom * 100.0)
        matched_nonaccept.append(sum(1 for row in lane_rows if row.get("reviewer_decision") in {"REVISE", "REJECT"} and row.get("lane_decision") in {"REVISE", "REJECT"}) / denom * 100.0)
    x = np.arange(len(lanes))
    width = 0.24
    specs = [
        (reviewer_nonaccept, "Reviewer baseline", "#AB47BC"),
        (lane_nonaccept, "Lane non-accept", "#29B6F6"),
        (matched_nonaccept, "Both non-accept", "#FF9800"),
    ]
    for i, (vals, label, color) in enumerate(specs):
        bars = ax.bar(x + (i - 1) * width, vals, width, label=label, color=color)
        for bar, value in zip(bars, vals):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, value + 0.5, f"{value:.1f}", ha="center", va="bottom", color=TEXT_COL, fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=TEXT_COL)
    style_ax(ax, "Reviewer vs Lane Non-Accept Rates (non-GPT rows)", "Percent of items with reviewer baseline")
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL)


def lane_score_comparison(ax, bundle: dict[str, list[dict]]):
    rows = bundle["lane_long"]
    lanes = ["claude", "codex"]
    metrics = [
        ("lane_source_alignment", "Alignment"),
        ("lane_distractor_quality", "Distractor"),
        ("lane_stem_clarity", "Clarity"),
    ]
    x = np.arange(len(metrics))
    width = 0.34
    colors = {"claude": "#4CAF50", "codex": "#29B6F6"}
    for i, lane in enumerate(lanes):
        vals = []
        lane_rows = [row for row in rows if row["lane"] == lane]
        for field, _label in metrics:
            metric_vals = [float(row[field]) for row in lane_rows if row.get(field) not in {"", None}]
            vals.append(sum(metric_vals) / len(metric_vals) if metric_vals else 0.0)
        bars = ax.bar(x + (i - 0.5) * width, vals, width, label=f"{lane.capitalize()} review", color=colors[lane])
        for bar, value in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.05, f"{value:.2f}", ha="center", va="bottom", color=TEXT_COL, fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels([label for _field, label in metrics], color=TEXT_COL)
    style_ax(ax, "Review Lane Score Comparison", "Mean Score (1-5)")
    ax.set_ylim(0, 5.5)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL)


def reviewer_alignment_heatmap(ax, bundle: dict[str, list[dict]]):
    lanes = ["claude", "codex"]
    rows = _lane_rows(bundle, reviewer_required=True)
    conds = ordered_conditions({row["condition"] for row in rows})
    matrix = np.zeros((len(lanes), len(conds)), dtype=float)
    for i, lane in enumerate(lanes):
        for j, cond in enumerate(conds):
            subset = [row for row in rows if row["lane"] == lane and row["condition"] == cond]
            denom = len(subset)
            agree = sum(1 for row in subset if row.get("agrees_with_reviewer") == "True")
            matrix[i, j] = agree / denom * 100.0 if denom else np.nan
    cmap = __import__("matplotlib.cm", fromlist=["get_cmap"]).get_cmap("RdYlGn").copy()
    cmap.set_bad("#444444")
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    for i in range(len(lanes)):
        for j in range(len(conds)):
            value = matrix[i, j]
            if np.isnan(value):
                ax.text(j, i, "N/A", ha="center", va="center", color=TEXT_COL, fontsize=9, style="italic")
            else:
                ax.text(j, i, f"{value:.0f}%", ha="center", va="center", color="black", fontsize=9, fontweight="bold")
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels([condition_label(cond) for cond in conds], color=TEXT_COL, fontsize=8)
    ax.set_yticks(range(len(lanes)))
    ax.set_yticklabels([f"{lane.capitalize()} review" for lane in lanes], color=TEXT_COL)
    ax.set_title("Agreement With Reviewer by Condition (non-GPT rows)", color=TITLE_COL, fontsize=11, fontweight="bold", pad=8)
    ax.get_figure().colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(colors=TEXT_COL)


def lane_accept_heatmap(ax, bundle: dict[str, list[dict]], lane_key: str, lane_label: str):
    rows = bundle["lane_long"]
    conds = ordered_conditions({row["condition"] for row in rows if row["lane"] == lane_key})
    diffs = ["easy", "medium", "hard"]
    matrix = np.zeros((len(conds), len(diffs)), dtype=float)
    for i, cond in enumerate(conds):
        for j, diff in enumerate(diffs):
            subset = [
                row for row in rows
                if row["lane"] == lane_key and row["condition"] == cond and row["difficulty"] == diff
            ]
            denom = len(subset)
            accept = sum(1 for row in subset if row.get("lane_decision") == "ACCEPT")
            matrix[i, j] = accept / denom * 100.0 if denom else np.nan
    cmap = __import__("matplotlib.cm", fromlist=["get_cmap"]).get_cmap("RdYlGn").copy()
    cmap.set_bad("#444444")
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    for i in range(len(conds)):
        for j in range(len(diffs)):
            value = matrix[i, j]
            if np.isnan(value):
                ax.text(j, i, "N/A", ha="center", va="center", color=TEXT_COL, fontsize=9, style="italic")
            else:
                ax.text(j, i, f"{value:.0f}%", ha="center", va="center", color="black", fontsize=9, fontweight="bold")
    ax.set_xticks(range(len(diffs)))
    ax.set_xticklabels([d.capitalize() for d in diffs], color=TEXT_COL, fontsize=8)
    ax.set_yticks(range(len(conds)))
    ax.set_yticklabels([review_condition_label(cond, lane_key) for cond in conds], color=TEXT_COL, fontsize=8)
    ax.set_title(f"{lane_label} Review Accept Rate by Generation Condition", color=TITLE_COL, fontsize=11, fontweight="bold", pad=8)
    ax.get_figure().colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(colors=TEXT_COL)


def lane_score_heatmap(ax, bundle: dict[str, list[dict]], lane_key: str, lane_label: str):
    rows = _lane_rows(bundle, lane=lane_key)
    conds = ordered_conditions({row["condition"] for row in rows})
    metrics = [
        ("lane_source_alignment", "Alignment"),
        ("lane_distractor_quality", "Distractor"),
        ("lane_stem_clarity", "Clarity"),
    ]
    matrix = np.zeros((len(conds), len(metrics)), dtype=float)
    for i, cond in enumerate(conds):
        cond_rows = [row for row in rows if row["condition"] == cond]
        for j, (field, _label) in enumerate(metrics):
            vals = [float(row[field]) for row in cond_rows if row.get(field) not in {"", None}]
            matrix[i, j] = sum(vals) / len(vals) if vals else np.nan
    cmap = __import__("matplotlib.cm", fromlist=["get_cmap"]).get_cmap("Blues").copy()
    cmap.set_bad("#444444")
    im = ax.imshow(matrix, cmap=cmap, vmin=1, vmax=5, aspect="auto")
    for i in range(len(conds)):
        for j in range(len(metrics)):
            value = matrix[i, j]
            if np.isnan(value):
                ax.text(j, i, "N/A", ha="center", va="center", color=TEXT_COL, fontsize=9, style="italic")
            else:
                ax.text(j, i, f"{value:.2f}", ha="center", va="center", color="black", fontsize=9, fontweight="bold")
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels([label for _field, label in metrics], color=TEXT_COL, fontsize=8)
    ax.set_yticks(range(len(conds)))
    ax.set_yticklabels([review_condition_label(cond, lane_key) for cond in conds], color=TEXT_COL, fontsize=8)
    ax.set_title(f"{lane_label} Review Score Heatmap by Generation Condition", color=TITLE_COL, fontsize=11, fontweight="bold", pad=8)
    ax.get_figure().colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(colors=TEXT_COL)
