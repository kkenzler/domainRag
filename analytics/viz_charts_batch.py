from __future__ import annotations

from math import pi

import numpy as np

from viz_costs import pipeline_costs
from viz_theme import AXIS_BG, BG, DEC_COLORS, DIFF_COLORS, GRID_COL, TEXT_COL, TITLE_COL, style_ax


def chart_mean_quality(ax, data, labels):
    style_ax(ax, "Mean Quality Scores by Difficulty", "Score (1-5)")
    metrics = ["mean_source_alignment", "mean_distractor_quality", "mean_stem_clarity"]
    m_labels = ["Source\nAlignment", "Distractor\nQuality", "Stem\nClarity"]
    x = np.arange(len(metrics))
    w = 0.25
    for i, d in enumerate(data):
        vals = [d["qm"].get(m, 0) for m in metrics]
        bars = ax.bar(x + i * w, vals, w, label=d["label"].capitalize(), color=DIFF_COLORS[d["label"]], alpha=0.9, zorder=3)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.06, f"{v:.2f}", ha="center", va="bottom", color=TEXT_COL, fontsize=7.5)
    ax.set_xticks(x + w)
    ax.set_xticklabels(m_labels, fontsize=9, color=TEXT_COL)
    ax.set_ylim(0, 6)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def chart_decisions(ax, data, labels):
    style_ax(ax, "Reviewer Decisions by Difficulty", "Item Count")
    bottoms = np.zeros(len(data))
    for dk in ["ACCEPT", "REVISE", "REJECT"]:
        counts = [sum(1 for it in d["items"] if it["decision"] == dk) for d in data]
        bars = ax.bar(labels, counts, bottom=bottoms, color=DEC_COLORS[dk], alpha=0.9, label=dk, zorder=3)
        for bar, cnt, bot in zip(bars, counts, bottoms):
            if cnt > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bot + cnt / 2, str(cnt), ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        bottoms += np.array(counts, dtype=float)
    ax.set_ylim(0, 60)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([l.capitalize() for l in labels], color=TEXT_COL)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def chart_thresholds(ax, data, labels):
    style_ax(ax, "Threshold Pass Rates (%)", "Pass Rate (%)")
    thresh = [
        ("pct_source_alignment_gte_4", "Src Align\n>=4"),
        ("pct_distractor_quality_gte_3", "Distractor\n>=3"),
        ("pct_stem_clarity_gte_4", "Stem Clarity\n>=4"),
        ("pct_difficulty_match_true", "Difficulty\nMatch"),
    ]
    x = np.arange(len(thresh))
    w = 0.25
    for i, d in enumerate(data):
        vals = [d["qm"].get(k, 0) for k, _ in thresh]
        bars = ax.bar(x + i * w, vals, w, label=d["label"].capitalize(), color=DIFF_COLORS[d["label"]], alpha=0.9, zorder=3)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{v:.0f}%", ha="center", va="bottom", color=TEXT_COL, fontsize=7)
    ax.set_xticks(x + w)
    ax.set_xticklabels([lbl for _, lbl in thresh], fontsize=8, color=TEXT_COL)
    ax.set_ylim(0, 120)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def boxplot(ax, data, labels, metric_key, title):
    style_ax(ax, title, "Score (1-5)")
    bp_data = [[it[metric_key] for it in d["items"] if it[metric_key] is not None] for d in data]
    bp = ax.boxplot(
        bp_data,
        patch_artist=True,
        widths=0.45,
        medianprops=dict(color="white", linewidth=2),
        whiskerprops=dict(color=GRID_COL),
        capprops=dict(color=GRID_COL),
        flierprops=dict(marker="o", markerfacecolor=GRID_COL, markersize=4, linestyle="none"),
    )
    for patch, lbl in zip(bp["boxes"], labels):
        patch.set_facecolor(DIFF_COLORS[lbl])
        patch.set_alpha(0.8)
    ax.set_xticklabels([l.capitalize() for l in labels], color=TEXT_COL)
    ax.set_ylim(0, 6)


def chart_radar(ax, data, labels):
    ax.set_facecolor(AXIS_BG)
    ax.set_title("Quality Radar", color=TITLE_COL, fontsize=11, fontweight="bold", pad=18)
    radar = [
        ("mean_source_alignment", "Src Align"),
        ("mean_distractor_quality", "Distractor\nQuality"),
        ("mean_stem_clarity", "Stem\nClarity"),
        ("pct_difficulty_match_true", "Difficulty\nMatch"),
        ("pct_source_alignment_gte_4", "Src >=4 %"),
    ]

    def norm(key, val):
        return val / 100 if "pct" in key else (val - 1) / 4

    n_points = len(radar)
    angles = [n / n_points * 2 * pi for n in range(n_points)] + [0]
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlim(0, 1)
    ax.set_rticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], color=TEXT_COL, fontsize=7)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([lbl for _, lbl in radar], color=TEXT_COL, fontsize=8)
    ax.yaxis.grid(color=GRID_COL, linestyle="--", alpha=0.5)
    ax.xaxis.grid(color=GRID_COL, linestyle="--", alpha=0.5)
    ax.spines["polar"].set_color(GRID_COL)
    for d in data:
        vals = [norm(k, d["qm"].get(k, 0)) for k, _ in radar] + [norm(radar[0][0], d["qm"].get(radar[0][0], 0))]
        ax.plot(angles, vals, color=DIFF_COLORS[d["label"]], linewidth=2, label=d["label"].capitalize())
        ax.fill(angles, vals, color=DIFF_COLORS[d["label"]], alpha=0.15)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def chart_accept_vs_match(ax, data, labels):
    style_ax(ax, "Accept Rate vs Difficulty Match (%)", "%")
    accept_pct = [sum(1 for it in d["items"] if it["decision"] == "ACCEPT") / len(d["items"]) * 100 for d in data]
    diff_match = [d["qm"].get("pct_difficulty_match_true", 0) for d in data]
    x = np.arange(len(labels))
    w = 0.35
    b1 = ax.bar(x - w / 2, accept_pct, w, color="#29b6f6", alpha=0.9, label="Accept Rate %", zorder=3)
    b2 = ax.bar(x + w / 2, diff_match, w, color="#ce93d8", alpha=0.9, label="Difficulty Match %", zorder=3)
    for bar, v in list(zip(b1, accept_pct)) + list(zip(b2, diff_match)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5, f"{v:.0f}%", ha="center", va="bottom", color=TEXT_COL, fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([l.capitalize() for l in labels], color=TEXT_COL)
    ax.set_ylim(0, 115)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def chart_heatmap(ax, data, labels):
    ax.set_facecolor(AXIS_BG)
    ax.set_title("Mean Scores Heatmap", color=TITLE_COL, fontsize=11, fontweight="bold", pad=8)
    hm_metrics = ["mean_source_alignment", "mean_distractor_quality", "mean_stem_clarity"]
    hm_labels = ["Source\nAlignment", "Distractor\nQuality", "Stem\nClarity"]
    matrix = np.array([[d["qm"].get(m, 0) for m in hm_metrics] for d in data])
    im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=1, vmax=5)
    for i in range(len(data)):
        for j in range(len(hm_metrics)):
            v = matrix[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", color="black" if 2 < v < 4.5 else "white", fontsize=12, fontweight="bold")
    ax.set_xticks(range(len(hm_metrics)))
    ax.set_xticklabels(hm_labels, color=TEXT_COL, fontsize=9)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels([l.capitalize() for l in labels], color=TEXT_COL, fontsize=10)
    cbar = ax.get_figure().colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=TEXT_COL, labelsize=8)
    cbar.set_label("Score", color=TEXT_COL, fontsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)


def chart_api_cost(ax):
    ax.set_facecolor(AXIS_BG)
    ax.set_title("Estimated API Cost — 50 Items (Hard)  |  Actual token logs", color=TITLE_COL, fontsize=10, fontweight="bold", pad=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.grid(axis="y", color=GRID_COL, linewidth=0.6, linestyle="--", alpha=0.7)
    costs = pipeline_costs()
    mnames = list(costs.keys())
    stage_colors = {"ingest": "#546e7a", "generate": "#1565c0", "review": "#4a148c"}
    stage_labels = {"ingest": "Ingest (58 chunks)", "generate": "Generate (50 items)", "review": "Review (50 items)"}
    bottoms = np.zeros(len(mnames))
    x = np.arange(len(mnames))
    for stage in ["ingest", "generate", "review"]:
        vals = np.array([costs[m][stage] for m in mnames])
        bars = ax.bar(x, vals, bottom=bottoms, color=stage_colors[stage], alpha=0.9, label=stage_labels[stage], zorder=3, width=0.55)
        for bar, v, bot in zip(bars, vals, bottoms):
            if v >= 0.005:
                ax.text(bar.get_x() + bar.get_width() / 2, bot + v / 2, f"${v:.3f}", ha="center", va="center", color="white", fontsize=8, fontweight="bold")
        bottoms += vals
    for i, (mname, bot) in enumerate(zip(mnames, bottoms)):
        lbl = "$0.00\n(local)" if bot == 0 else f"${bot:.3f}"
        ax.text(i, bot + 0.01, lbl, ha="center", va="bottom", color=TEXT_COL, fontsize=8.5, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(mnames, color=TEXT_COL, fontsize=9)
    ax.set_ylabel("Estimated Cost (USD)", color=TEXT_COL)
    ax.tick_params(colors=TEXT_COL, labelsize=9)
    ax.set_ylim(0, max(bottoms) * 1.25 + 0.1)
    ax.annotate(
        "Token counts from actual llm_http.jsonl logs (hard run).\n"
        "Ingest estimated: 58 chunks x ~555 in / ~125 out tokens.\n"
        "Local = $0 API cost; runtime ~70 min on Qwen 7B.",
        xy=(0.98, 0.97),
        xycoords="axes fraction",
        ha="right",
        va="top",
        fontsize=7.5,
        color="#8b949e",
        bbox=dict(boxstyle="round,pad=0.4", facecolor=AXIS_BG, edgecolor=GRID_COL, alpha=0.8),
    )
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL, loc="upper left")
