from __future__ import annotations

import sys
from math import pi
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))  # analytics root — for viz_conditions, viz_theme

from viz_conditions import condition_color_map, ordered_conditions, review_condition_label
from viz_theme import AXIS_BG, DEC_COLORS, DIFF_COLORS, GRID_COL, TEXT_COL, TITLE_COL, style_ax


CR_AGREE_COLORS = {"True": "#4CAF50", "Partial": "#FF9800", "False": "#F44336"}


def _review_labels(conds: list[str]) -> list[str]:
    return [review_condition_label(cond, "claude") for cond in conds]


def decisions_bar(ax, by_cond: dict):
    conds = list(by_cond.keys())
    labels = _review_labels(conds)
    bottoms = np.zeros(len(conds))
    for dec in ["ACCEPT", "REVISE", "REJECT"]:
        pcts = [sum(1 for it in by_cond[c] if it["claude_decision"] == dec) / len(by_cond[c]) * 100 for c in conds]
        bars = ax.bar(labels, pcts, bottom=bottoms, color=DEC_COLORS[dec], label=dec, width=0.55)
        for bar, pct in zip(bars, pcts):
            if pct > 6:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, f"{pct:.0f}%", ha="center", va="center", color="white", fontsize=8, fontweight="bold")
        bottoms += np.array(pcts)
    style_ax(ax, "Claude Decisions by Generation Condition", "% of items")
    ax.set_ylim(0, 110)
    ax.legend(fontsize=8, labelcolor=TEXT_COL, framealpha=0.2, loc="upper right")


def score_bars(ax, by_cond: dict):
    conds = list(by_cond.keys())
    metrics = ["claude_source_alignment", "claude_distractor_quality", "claude_stem_clarity"]
    labels = ["Alignment", "Distractor", "Clarity"]
    colors = ["#29b6f6", "#ab47bc", "#FFB300"]
    x = np.arange(len(conds))
    w = 0.24
    for i, (m, lab, col) in enumerate(zip(metrics, labels, colors)):
        means = [np.mean([it[m] for it in by_cond[c] if it[m] is not None]) for c in conds]
        bars = ax.bar(x + (i - 1) * w, means, w, label=lab, color=col)
        for bar, v in zip(bars, means):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, f"{v:.2f}", ha="center", va="bottom", color=TEXT_COL, fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(_review_labels(conds), fontsize=8)
    ax.set_ylim(1, 5.5)
    style_ax(ax, "Mean Claude Scores by Generation Condition", "Score (1–5)")
    ax.legend(fontsize=8, labelcolor=TEXT_COL, framealpha=0.2)


def agreement_bar(ax, by_cond: dict):
    conds = [c for c in by_cond.keys() if any(it.get("reviewer_decision") not in {None, ""} for it in by_cond[c])]
    label_map = [("True", "Agrees"), ("Partial", "Partial"), ("False", "Disagrees")]
    x = np.arange(len(conds))
    w = 0.24
    for i, (val, lab) in enumerate(label_map):
        pcts = [sum(1 for it in by_cond[c] if str(it.get("agrees_with_reviewer", "")) == val) / len(by_cond[c]) * 100 for c in conds]
        bars = ax.bar(x + (i - 1) * w, pcts, w, label=lab, color=CR_AGREE_COLORS[val])
        for bar, pct in zip(bars, pcts):
            if pct > 5:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4, f"{pct:.0f}%", ha="center", va="bottom", color=TEXT_COL, fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(_review_labels(conds), fontsize=8)
    style_ax(ax, "Claude Agreement with Human Reviewer Baseline (non-GPT rows)", "% of items with reviewer baseline")
    ax.legend(fontsize=8, labelcolor=TEXT_COL, framealpha=0.2)


def flag_bar(ax, by_cond: dict):
    conds = list(by_cond.keys())
    colors = condition_color_map(conds)
    rates = [sum(1 for it in by_cond[c] if it.get("flag_ambiguity") is True) / len(by_cond[c]) * 100 for c in conds]
    bars = ax.bar(_review_labels(conds), rates, color=[colors[c] for c in conds], width=0.55)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, f"{rate:.1f}%", ha="center", va="bottom", color=TEXT_COL, fontsize=9)
    style_ax(ax, "Ambiguity Flag Rate by Generation Condition", "% flagged")
    ax.set_ylim(0, max(rates) * 1.35 + 2)


def decision_heatmap(ax, items: list):
    diffs = ["easy", "medium", "hard"]
    conds = ordered_conditions([it["condition"] for it in items])
    matrix = np.zeros((len(conds), len(diffs)))
    for i, cond in enumerate(conds):
        for j, diff in enumerate(diffs):
            sub = [it for it in items if it["condition"] == cond and it["difficulty"] == diff]
            matrix[i, j] = (sum(1 for it in sub if it["claude_decision"] == "ACCEPT") / len(sub) * 100) if sub else 0
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(diffs)))
    ax.set_xticklabels(diffs, color=TEXT_COL, fontsize=9)
    ax.set_yticks(range(len(conds)))
    ax.set_yticklabels([review_condition_label(c, "claude") for c in conds], color=TEXT_COL, fontsize=9)
    for i in range(len(conds)):
        for j in range(len(diffs)):
            ax.text(j, i, f"{matrix[i,j]:.0f}%", ha="center", va="center", color="black", fontsize=10, fontweight="bold")
    ax.set_title("Claude ACCEPT Rate  (generation condition x difficulty)", color=TITLE_COL, fontsize=11, fontweight="bold", pad=8)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.yaxis.set_tick_params(color=TEXT_COL)


def score_heatmap(ax, by_cond: dict):
    conds = list(by_cond.keys())
    metrics = ["claude_source_alignment", "claude_distractor_quality", "claude_stem_clarity"]
    mlabels = ["Alignment", "Distractor", "Clarity"]
    matrix = np.zeros((len(conds), len(metrics)))
    for i, cond in enumerate(conds):
        for j, metric in enumerate(metrics):
            vals = [it[metric] for it in by_cond[cond] if it[metric] is not None]
            matrix[i, j] = np.mean(vals) if vals else 0
    im = ax.imshow(matrix, cmap="Blues", vmin=1, vmax=5, aspect="auto")
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(mlabels, color=TEXT_COL, fontsize=9)
    ax.set_yticks(range(len(conds)))
    ax.set_yticklabels([review_condition_label(c, "claude") for c in conds], color=TEXT_COL, fontsize=9)
    for i in range(len(conds)):
        for j in range(len(metrics)):
            ax.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", color="black", fontsize=10, fontweight="bold")
    ax.set_title("Mean Claude Score  (generation condition x metric)", color=TITLE_COL, fontsize=11, fontweight="bold", pad=8)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.yaxis.set_tick_params(color=TEXT_COL)


def qc_flags_bar(ax, by_cond: dict):
    conds = list(by_cond.keys())
    qc_fields = [
        ("chunks_support_question", "Chunks support Q"),
        ("correct_answer_verifiable", "Answer verifiable"),
        ("distractors_clearly_wrong", "Distractors clear"),
        ("reviewer_source_call_accurate", "Rev. source OK"),
    ]
    qc_colors = ["#29b6f6", "#4CAF50", "#ab47bc", "#FF9800"]
    x = np.arange(len(conds))
    w = 0.18
    for i, ((field, lab), col) in enumerate(zip(qc_fields, qc_colors)):
        pcts = [sum(1 for it in by_cond[c] if it.get(field) is True) / len(by_cond[c]) * 100 for c in conds]
        bars = ax.bar(x + (i - 1.5) * w, pcts, w, label=lab, color=col)
        for bar, pct in zip(bars, pcts):
            if pct > 5:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{pct:.0f}", ha="center", va="bottom", color=TEXT_COL, fontsize=6)
    ax.set_xticks(x)
    ax.set_xticklabels(_review_labels(conds), fontsize=8)
    ax.set_ylim(0, 115)
    style_ax(ax, "Claude QC Traceability  (% items passing each flag)", "% True")
    ax.legend(fontsize=7, labelcolor=TEXT_COL, framealpha=0.2, ncol=2)


def reject_breakdown(ax, by_cond: dict):
    conds = list(by_cond.keys())
    diffs = ["easy", "medium", "hard", "unknown"]
    dcols = [DIFF_COLORS.get(d, "#546e7a") for d in diffs]
    x = np.arange(len(conds))
    w = 0.2
    shown = set()
    for j, (diff, col) in enumerate(zip(diffs, dcols)):
        counts = [sum(1 for it in by_cond[c] if it["claude_decision"] == "REJECT" and it["difficulty"] == diff) for c in conds]
        if all(v == 0 for v in counts):
            continue
        lab = diff if diff not in shown else "_nolegend_"
        shown.add(diff)
        bars = ax.bar(x + (j - 1.5) * w, counts, w, label=lab, color=col)
        for bar, cnt in zip(bars, counts):
            if cnt > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, str(cnt), ha="center", va="bottom", color=TEXT_COL, fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(_review_labels(conds), fontsize=8)
    style_ax(ax, "Claude REJECT Count by Review Condition x Difficulty", "# rejected")
    ax.legend(fontsize=8, labelcolor=TEXT_COL, framealpha=0.2, title="Difficulty", title_fontsize=8)


def score_boxplot(ax, by_cond: dict, metric: str, title: str):
    conds = list(by_cond.keys())
    colors = condition_color_map(conds)
    data = [[it[metric] for it in by_cond[c] if it[metric] is not None] for c in conds]
    bp = ax.boxplot(data, patch_artist=True, medianprops={"color": "#FFB300", "linewidth": 2})
    for patch, cond in zip(bp["boxes"], conds):
        patch.set_facecolor(colors[cond])
        patch.set_alpha(0.7)
    for element in ("whiskers", "caps", "fliers"):
        for item in bp[element]:
            item.set_color(TEXT_COL)
    ax.set_xticks(range(1, len(conds) + 1))
    ax.set_xticklabels(_review_labels(conds), fontsize=8)
    ax.set_ylim(0.5, 5.5)
    ax.set_yticks([1, 2, 3, 4, 5])
    style_ax(ax, title, "Score (1–5)")


def radar_by_condition(ax, by_cond: dict):
    metrics = [
        ("claude_source_alignment", "Alignment\n(1–5)"),
        ("claude_distractor_quality", "Distractor\n(1–5)"),
        ("claude_stem_clarity", "Clarity\n(1–5)"),
    ]
    conds = list(by_cond.keys())
    cats = [lab for _, lab in metrics]
    n_points = len(cats)
    angles = [n / n_points * 2 * pi for n in range(n_points)] + [0]

    ax.set_facecolor(AXIS_BG)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(cats, color=TEXT_COL, fontsize=8)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["1.5", "2.5", "3.5", "4.5"], color=TEXT_COL, fontsize=6)
    ax.set_ylim(0, 1)
    ax.grid(color=GRID_COL, linewidth=0.6)
    ax.spines["polar"].set_edgecolor(GRID_COL)

    colors = condition_color_map(conds)
    for cond in conds:
        vals = []
        for field, _ in metrics:
            raw = [it[field] for it in by_cond[cond] if it[field] is not None]
            vals.append((np.mean(raw) - 1) / 4 if raw else 0)
        vals += [vals[0]]
        ax.plot(angles, vals, linewidth=2, color=colors[cond], label=review_condition_label(cond, "claude"))
        ax.fill(angles, vals, alpha=0.15, color=colors[cond])
    ax.set_title("Claude Score Radar by Generation Condition", color=TITLE_COL, fontsize=11, fontweight="bold", pad=18)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.25, -0.12), fontsize=7, labelcolor=TEXT_COL, framealpha=0.2)


def accept_vs_match(ax, by_cond: dict):
    conds = list(by_cond.keys())
    x = np.arange(len(conds))
    w = 0.32
    accept_rates = [sum(1 for it in by_cond[c] if it["claude_decision"] == "ACCEPT") / len(by_cond[c]) * 100 for c in conds]
    match_rates = []
    for c in conds:
        matched = 0
        for it in by_cond[c]:
            val = it.get("claude_difficulty_match")
            if val is True:
                matched += 1
            elif isinstance(val, (int, float)) and val >= 4:
                matched += 1
        match_rates.append(matched / len(by_cond[c]) * 100 if by_cond[c] else 0)
    bars1 = ax.bar(x - w / 2, accept_rates, w, label="ACCEPT %", color="#4CAF50")
    bars2 = ax.bar(x + w / 2, match_rates, w, label="Difficulty Match %", color="#29b6f6")
    for bars, vals in [(bars1, accept_rates), (bars2, match_rates)]:
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8, f"{v:.0f}%", ha="center", va="bottom", color=TEXT_COL, fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(_review_labels(conds), fontsize=8)
    ax.set_ylim(0, 115)
    style_ax(ax, "Claude ACCEPT Rate vs Difficulty Match", "% of items")
    ax.legend(fontsize=8, labelcolor=TEXT_COL, framealpha=0.2)
