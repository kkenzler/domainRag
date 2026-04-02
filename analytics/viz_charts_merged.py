from __future__ import annotations

from math import pi

import numpy as np

from viz_conditions import condition_color_map, condition_label, ordered_conditions
from viz_theme import AXIS_BG, DEC_COLORS, GRID_COL, TEXT_COL, TITLE_COL, style_ax


def _na_bar(ax, x, width, label="N/A\n(no reviewer)") -> None:
    """Draw a faint hatched placeholder bar at position x to signal absent data."""
    ax.bar(x, 1, width, color="#888888", alpha=0.18, hatch="//", zorder=2, edgecolor="#888888")
    ax.text(x, 0.5, label, ha="center", va="center", color=TEXT_COL,
            fontsize=7, style="italic", alpha=0.7)


def merged_accept_bar(ax, agg):
    style_ax(ax, "Accept Rate by Condition (all difficulties)", "Accept %")
    conds = [g["condition"] for g in agg]
    colors = condition_color_map(conds)
    for i, g in enumerate(agg):
        if not g.get("has_reviewer_metrics", True):
            _na_bar(ax, i, 0.6)
        else:
            n = len(g["items"])
            rate = sum(1 for it in g["items"] if it["decision"] == "ACCEPT") / n * 100 if n else 0
            bar = ax.bar(i, rate, 0.6, color=colors[g["condition"]], alpha=0.9, zorder=3)
            ax.text(i, rate + 1.5, f"{rate:.0f}%", ha="center", va="bottom",
                    color=TEXT_COL, fontsize=10, fontweight="bold")
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels([condition_label(c) for c in conds], color=TEXT_COL, fontsize=9)
    ax.set_ylim(0, 90)


def merged_decisions(ax, agg):
    style_ax(ax, "Reviewer Decisions by Condition", "Item Count")
    conds = [g["condition"] for g in agg]
    labels = [condition_label(c) for c in conds]
    bottoms = np.zeros(len(agg))
    for dk in ["ACCEPT", "REVISE", "REJECT"]:
        counts = [
            sum(1 for it in g["items"] if it["decision"] == dk)
            if g.get("has_reviewer_metrics", True) else 0
            for g in agg
        ]
        bars = ax.bar(range(len(conds)), counts, bottom=bottoms, color=DEC_COLORS[dk], alpha=0.9, label=dk, zorder=3, width=0.6)
        for bar, cnt, bot in zip(bars, counts, bottoms):
            if cnt > 10:
                ax.text(bar.get_x() + bar.get_width() / 2, bot + cnt / 2, str(cnt), ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        bottoms += np.array(counts, dtype=float)
    # Annotate no-reviewer conditions with N/A
    for i, g in enumerate(agg):
        if not g.get("has_reviewer_metrics", True):
            _na_bar(ax, i, 0.6)
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels(labels, color=TEXT_COL, fontsize=9)
    ax.set_ylim(0, max(max(bottoms), 1) * 1.15)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def merged_accept_heatmap(ax, groups):
    ax.set_facecolor(AXIS_BG)
    ax.set_title("Accept Rate %  (condition x difficulty)", color=TITLE_COL, fontsize=11, fontweight="bold", pad=8)
    diffs = ["easy", "medium", "hard"]
    conds = ordered_conditions([g["condition"] for g in groups])
    # Build a set of no-reviewer conditions for cell annotation
    no_rev_conds = {
        g["condition"] for g in groups if not g.get("has_reviewer_metrics", True)
    }
    matrix = np.full((len(conds), len(diffs)), np.nan)
    for g in groups:
        ci = conds.index(g["condition"]) if g["condition"] in conds else -1
        di = diffs.index(g["difficulty"]) if g["difficulty"] in diffs else -1
        if ci >= 0 and di >= 0 and g["items"] and g.get("has_reviewer_metrics", True):
            n_items = len(g["items"])
            matrix[ci, di] = sum(1 for it in g["items"] if it["decision"] == "ACCEPT") / n_items * 100
    cmap = __import__("matplotlib.cm", fromlist=["get_cmap"]).get_cmap("RdYlGn").copy()
    cmap.set_bad("#444444")
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=80)
    for i, cond in enumerate(conds):
        for j in range(len(diffs)):
            v = matrix[i, j]
            if np.isnan(v):
                lbl = "N/A" if cond in no_rev_conds else ""
                ax.text(j, i, lbl, ha="center", va="center", color=TEXT_COL, fontsize=10, style="italic")
            else:
                ax.text(j, i, f"{v:.0f}%", ha="center", va="center", color="black" if 20 < v < 65 else "white", fontsize=13, fontweight="bold")
    ax.set_xticks(range(len(diffs)))
    ax.set_xticklabels([d.capitalize() for d in diffs], color=TEXT_COL, fontsize=10)
    ax.set_yticks(range(len(conds)))
    ax.set_yticklabels([condition_label(c) for c in conds], color=TEXT_COL, fontsize=9)
    cbar = ax.get_figure().colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=TEXT_COL, labelsize=8)
    cbar.set_label("Accept %", color=TEXT_COL, fontsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)


def merged_quality_bar(ax, agg):
    style_ax(ax, "Mean Quality Scores by Condition", "Score (1-5)")
    metrics = ["mean_source_alignment", "mean_distractor_quality", "mean_stem_clarity"]
    m_labels = ["Source\nAlignment", "Distractor\nQuality", "Stem\nClarity"]
    x = np.arange(len(metrics))
    w = 0.18
    colors = condition_color_map([g["condition"] for g in agg])
    for i, g in enumerate(agg):
        color = colors[g["condition"]]
        if not g.get("has_reviewer_metrics", True):
            # Draw N/A placeholders for each metric group position
            for xi in x:
                _na_bar(ax, xi + i * w, w)
        else:
            vals = [g["qm"].get(m, 0) for m in metrics]
            bars = ax.bar(x + i * w, vals, w, label=g["condition"], color=color, alpha=0.9, zorder=3)
            for bar, v in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, f"{v:.2f}", ha="center", va="bottom", color=TEXT_COL, fontsize=6.5)
    ax.set_xticks(x + w * 1.5)
    ax.set_xticklabels(m_labels, fontsize=9, color=TEXT_COL)
    ax.set_ylim(0, 6)
    ax.legend(fontsize=7.5, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def merged_score_heatmap(ax, agg):
    ax.set_facecolor(AXIS_BG)
    ax.set_title("Mean Score Heatmap  (condition x metric)", color=TITLE_COL, fontsize=11, fontweight="bold", pad=8)
    metrics = ["mean_source_alignment", "mean_distractor_quality", "mean_stem_clarity"]
    m_labels = ["Source\nAlignment", "Distractor\nQuality", "Stem\nClarity"]
    conds = [g["condition"] for g in agg]
    # Use NaN for no-reviewer conditions so they render as gray (not as score=0=red)
    matrix = np.array([
        [g["qm"].get(m, 0) for m in metrics]
        if g.get("has_reviewer_metrics", True)
        else [np.nan] * len(metrics)
        for g in agg
    ], dtype=float)
    cmap = __import__("matplotlib.cm", fromlist=["get_cmap"]).get_cmap("RdYlGn").copy()
    cmap.set_bad("#444444")
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=1, vmax=5)
    for i, g in enumerate(agg):
        for j in range(len(metrics)):
            v = matrix[i, j]
            if np.isnan(v):
                ax.text(j, i, "N/A", ha="center", va="center", color=TEXT_COL, fontsize=10, style="italic")
            else:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", color="black" if 2 < v < 4.5 else "white", fontsize=12, fontweight="bold")
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(m_labels, color=TEXT_COL, fontsize=9)
    ax.set_yticks(range(len(conds)))
    ax.set_yticklabels([condition_label(c) for c in conds], color=TEXT_COL, fontsize=9)
    cbar = ax.get_figure().colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=TEXT_COL, labelsize=8)
    cbar.set_label("Score", color=TEXT_COL, fontsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)


def merged_radar(ax, agg):
    ax.set_facecolor(AXIS_BG)
    ax.set_title("Quality Radar by Condition", color=TITLE_COL, fontsize=11, fontweight="bold", pad=18)
    radar = [
        ("mean_source_alignment", "Src Align"),
        ("mean_distractor_quality", "Distractor"),
        ("mean_stem_clarity", "Stem\nClarity"),
        ("pct_difficulty_match_true", "Diff Match"),
        ("pct_source_alignment_gte_4", "Src >=4%"),
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
    colors = condition_color_map([g["condition"] for g in agg])
    for g in agg:
        if not g.get("has_reviewer_metrics", True):
            # Skip no-reviewer conditions — they have no valid QM data to plot
            continue
        color = colors[g["condition"]]
        vals = [norm(k, g["qm"].get(k, 0)) for k, _ in radar] + [norm(radar[0][0], g["qm"].get(radar[0][0], 0))]
        ax.plot(angles, vals, color=color, linewidth=2, label=g["condition"])
        ax.fill(angles, vals, color=color, alpha=0.1)
    ax.legend(loc="upper right", bbox_to_anchor=(1.45, 1.15), fontsize=7.5, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def merged_trend(ax, groups):
    style_ax(ax, "Accept Rate Trend: Easy -> Medium -> Hard", "Accept %")
    diffs = ["easy", "medium", "hard"]
    x = np.arange(len(diffs))
    conds = ordered_conditions([g["condition"] for g in groups])
    colors = condition_color_map(conds)
    # Build a no-reviewer set from group-level flag
    no_rev_conds = {
        g["condition"] for g in groups if not g.get("has_reviewer_metrics", True)
    }
    plotted = False
    for cond in conds:
        if cond in no_rev_conds:
            continue  # Skip — no valid accept-rate data for this condition
        color = colors[cond]
        rates = []
        for diff in diffs:
            match = [g for g in groups if g["condition"] == cond and g["difficulty"] == diff]
            if match and match[0]["items"]:
                n_items = len(match[0]["items"])
                rates.append(sum(1 for it in match[0]["items"] if it["decision"] == "ACCEPT") / n_items * 100)
            else:
                rates.append(None)
        valid = [(xi, r) for xi, r in zip(x, rates) if r is not None]
        if valid:
            xs, ys = zip(*valid)
            ax.plot(xs, ys, color=color, linewidth=2.5, marker="o", markersize=8, label=cond, zorder=3)
            for xi, yi in valid:
                ax.text(xi, yi + 2.5, f"{yi:.0f}%", ha="center", color=color, fontsize=8, fontweight="bold")
            plotted = True
    ax.set_xticks(x)
    ax.set_xticklabels(["Easy", "Medium", "Hard"], color=TEXT_COL, fontsize=10)
    ax.set_ylim(0, 90)
    if plotted:
        ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def merged_diff_match(ax, agg):
    style_ax(ax, "Difficulty Match % by Condition", "%")
    conds = [g["condition"] for g in agg]
    colors = condition_color_map(conds)
    for i, g in enumerate(agg):
        if not g.get("has_reviewer_metrics", True):
            _na_bar(ax, i, 0.6)
        else:
            v = g["qm"].get("pct_difficulty_match_true", 0)
            ax.bar(i, v, 0.6, color=colors[g["condition"]], alpha=0.9, zorder=3)
            ax.text(i, v + 1.5, f"{v:.0f}%", ha="center", va="bottom",
                    color=TEXT_COL, fontsize=10, fontweight="bold")
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels([condition_label(c) for c in conds], color=TEXT_COL, fontsize=9)
    ax.set_ylim(0, 110)
