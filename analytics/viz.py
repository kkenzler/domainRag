"""
domainRag Run Quality + Cost Dashboard
========================================
Reads domainRag XLSX run files and produces:
  - 10 individual chart PNGs  →  analytics/charts/
  - 1 combined dashboard PNG  →  analytics/dashboard.png

Usage:
    python viz.py                          # default: ../_rag_testGen/runs
    python viz.py C:/path/to/runs          # explicit runs directory

Cost estimates are derived from actual char counts logged in llm_http.jsonl
(hard run only has logs; easy/medium estimated proportionally from timing).
"""

import os
import sys
import json
import openpyxl
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from math import pi
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
RUNS_DIR   = Path(sys.argv[1]) if len(sys.argv) > 1 else SCRIPT_DIR / "../_rag_testGen/runs"
OUT_DIR    = SCRIPT_DIR
CHARTS_DIR = SCRIPT_DIR / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

# ── Run files ─────────────────────────────────────────────────────────────────

RUNS = [
    ("easy",   "run_20260317_015354Z.xlsx"),
    ("medium", "run_20260317_024849Z.xlsx"),
    ("hard",   "run_20260317_035048Z.xlsx"),
]

# ── Colors & theme ────────────────────────────────────────────────────────────

DIFF_COLORS = {"easy": "#4CAF50", "medium": "#FF9800", "hard": "#F44336"}
DECISION_COLORS = {"ACCEPT": "#4CAF50", "REVISE": "#FF9800", "REJECT": "#F44336"}

BG       = "#0d1117"
AXIS_BG  = "#161b22"
GRID_COL = "#30363d"
TEXT_COL = "#c9d1d9"
TITLE_COL = "#e6edf3"

plt.style.use("dark_background")


def style_ax(ax, title, ylabel=None):
    ax.set_facecolor(AXIS_BG)
    ax.tick_params(colors=TEXT_COL, labelsize=9)
    ax.xaxis.label.set_color(TEXT_COL)
    ax.yaxis.label.set_color(TEXT_COL)
    ax.set_title(title, color=TITLE_COL, fontsize=11, fontweight="bold", pad=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.grid(axis="y", color=GRID_COL, linewidth=0.6, linestyle="--", alpha=0.7)
    if ylabel:
        ax.set_ylabel(ylabel, color=TEXT_COL)


def make_fig(w=8, h=5.5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    return fig, ax


# ── Data loading ──────────────────────────────────────────────────────────────

def load_run(label, fname):
    wb = openpyxl.load_workbook(RUNS_DIR / fname)

    qm = {}
    for row in wb["Quality Metrics"].iter_rows(min_row=2, values_only=True):
        if row[0]:
            qm[row[0].replace("quality.", "")] = row[1]

    headers = [c.value for c in next(wb["Items"].iter_rows(max_row=1))]
    idx = {h: i for i, h in enumerate(headers)}
    items = []
    for row in wb["Items"].iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        items.append({
            "decision":           row[idx["decision"]],
            "source_alignment":   row[idx["source_alignment"]],
            "distractor_quality": row[idx["distractor_quality"]],
            "stem_clarity":       row[idx["stem_clarity"]],
            "difficulty_match":   row[idx["difficulty_match"]],
        })

    meta = {}
    for row in wb["Run Metadata"].iter_rows(values_only=True):
        if row[0]:
            meta[row[0]] = row[1]

    chunks = []
    for row in wb["Chunk Preview"].iter_rows(min_row=2, values_only=True):
        if row[2]:
            chunks.append(row[2])

    return {
        "label":  label,
        "qm":     qm,
        "items":  items,
        "meta":   meta,
        "chunks": chunks,
    }


data   = [load_run(label, fname) for label, fname in RUNS]
labels = [d["label"] for d in data]


# ─────────────────────────────────────────────────────────────────────────────
# Cost estimation
# ─────────────────────────────────────────────────────────────────────────────
# Source: llm_http.jsonl from hard run (50 items, 100 calls).
# Chars/4 ≈ tokens. Other runs estimated by scale factor from timing metadata.

_LOG_FILE = RUNS_DIR.parent.parent / "analytics" / "../.." / "Downloads/runs/logs_20260317_035048Z/llm_http.jsonl"
# Prefer embedded constants derived once from actual logs
# Hard run (50 items): gen in=59475 tok, gen out=9496 tok; rev in=54690 tok, rev out=5367 tok
_HARD_GEN_IN  = 59_475
_HARD_GEN_OUT =  9_496
_HARD_REV_IN  = 54_690
_HARD_REV_OUT =  5_367

# Ingest: 58 chunks, avg ~1218 chars each.
# Estimated prompt: ~1000 chars system + chunk text; output: ~500 chars of JSON
_INGEST_IN_TOK  = 58 * (1_000 + 1_218) // 4   # ~32_189
_INGEST_OUT_TOK = 58 * 500 // 4                # ~7_250

# Model pricing  ($ per 1M tokens, input / output)
MODELS = {
    "Local\n(Qwen 7B)": (0.0,   0.0,   "#78909c"),
    "Haiku 4.5":         (0.80,  4.00,  "#29b6f6"),
    "Sonnet 4.6":        (3.00,  15.00, "#ab47bc"),
    "Opus 4.6":          (15.00, 75.00, "#ef5350"),
}


def stage_cost(in_tok, out_tok, price_in, price_out):
    return in_tok / 1e6 * price_in + out_tok / 1e6 * price_out


def pipeline_costs():
    """Return dict: model → {ingest, generate, review, total}"""
    costs = {}
    for model, (pi, po, _) in MODELS.items():
        ingest   = stage_cost(_INGEST_IN_TOK,  _INGEST_OUT_TOK,  pi, po)
        generate = stage_cost(_HARD_GEN_IN,    _HARD_GEN_OUT,    pi, po)
        review   = stage_cost(_HARD_REV_IN,    _HARD_REV_OUT,    pi, po)
        costs[model] = {
            "ingest":   ingest,
            "generate": generate,
            "review":   review,
            "total":    ingest + generate + review,
        }
    return costs


# ─────────────────────────────────────────────────────────────────────────────
# Individual chart functions  (each takes an ax and populates it)
# ─────────────────────────────────────────────────────────────────────────────

def chart_mean_quality(ax):
    style_ax(ax, "Mean Quality Scores by Difficulty", "Score (1-5)")
    metrics  = ["mean_source_alignment", "mean_distractor_quality", "mean_stem_clarity"]
    m_labels = ["Source\nAlignment", "Distractor\nQuality", "Stem\nClarity"]
    x = np.arange(len(metrics))
    w = 0.25
    for i, d in enumerate(data):
        vals = [d["qm"].get(m, 0) for m in metrics]
        bars = ax.bar(x + i * w, vals, w, label=d["label"].capitalize(),
                      color=DIFF_COLORS[d["label"]], alpha=0.9, zorder=3)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.06,
                    f"{v:.2f}", ha="center", va="bottom", color=TEXT_COL, fontsize=7.5)
    ax.set_xticks(x + w)
    ax.set_xticklabels(m_labels, fontsize=9, color=TEXT_COL)
    ax.set_ylim(0, 6)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL,
              facecolor=AXIS_BG, edgecolor=GRID_COL)


def chart_decisions(ax):
    style_ax(ax, "Reviewer Decisions by Difficulty", "Item Count")
    bottoms = np.zeros(len(data))
    for dk in ["ACCEPT", "REVISE", "REJECT"]:
        counts = [sum(1 for it in d["items"] if it["decision"] == dk) for d in data]
        bars = ax.bar(labels, counts, bottom=bottoms,
                      color=DECISION_COLORS[dk], alpha=0.9, label=dk, zorder=3)
        for bar, cnt, bot in zip(bars, counts, bottoms):
            if cnt > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bot + cnt / 2,
                        str(cnt), ha="center", va="center",
                        color="white", fontsize=9, fontweight="bold")
        bottoms += np.array(counts, dtype=float)
    ax.set_ylim(0, 60)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([l.capitalize() for l in labels], color=TEXT_COL)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL,
              facecolor=AXIS_BG, edgecolor=GRID_COL)


def chart_thresholds(ax):
    style_ax(ax, "Threshold Pass Rates (%)", "Pass Rate (%)")
    thresh = [
        ("pct_source_alignment_gte_4",  "Src Align\n>=4"),
        ("pct_distractor_quality_gte_3","Distractor\n>=3"),
        ("pct_stem_clarity_gte_4",      "Stem Clarity\n>=4"),
        ("pct_difficulty_match_true",   "Difficulty\nMatch"),
    ]
    x = np.arange(len(thresh))
    w = 0.25
    for i, d in enumerate(data):
        vals = [d["qm"].get(k, 0) for k, _ in thresh]
        bars = ax.bar(x + i * w, vals, w, label=d["label"].capitalize(),
                      color=DIFF_COLORS[d["label"]], alpha=0.9, zorder=3)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{v:.0f}%", ha="center", va="bottom", color=TEXT_COL, fontsize=7)
    ax.set_xticks(x + w)
    ax.set_xticklabels([lbl for _, lbl in thresh], fontsize=8, color=TEXT_COL)
    ax.set_ylim(0, 120)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL,
              facecolor=AXIS_BG, edgecolor=GRID_COL)


def _boxplot(ax, metric_key, title):
    style_ax(ax, title, "Score (1-5)")
    bp_data = [[it[metric_key] for it in d["items"] if it[metric_key] is not None]
               for d in data]
    bp = ax.boxplot(bp_data, patch_artist=True, widths=0.45,
                    medianprops=dict(color="white", linewidth=2),
                    whiskerprops=dict(color=GRID_COL),
                    capprops=dict(color=GRID_COL),
                    flierprops=dict(marker="o", markerfacecolor=GRID_COL,
                                   markersize=4, linestyle="none"))
    for patch, lbl in zip(bp["boxes"], labels):
        patch.set_facecolor(DIFF_COLORS[lbl])
        patch.set_alpha(0.8)
    ax.set_xticklabels([l.capitalize() for l in labels], color=TEXT_COL)
    ax.set_ylim(0, 6)


def chart_box_source(ax):
    _boxplot(ax, "source_alignment", "Source Alignment Distribution")


def chart_box_distractor(ax):
    _boxplot(ax, "distractor_quality", "Distractor Quality Distribution")


def chart_box_stem(ax):
    _boxplot(ax, "stem_clarity", "Stem Clarity Distribution")


def chart_radar(ax):
    ax.set_facecolor(AXIS_BG)
    ax.set_title("Quality Radar", color=TITLE_COL, fontsize=11,
                 fontweight="bold", pad=18)
    radar = [
        ("mean_source_alignment",      "Src Align"),
        ("mean_distractor_quality",    "Distractor\nQuality"),
        ("mean_stem_clarity",          "Stem\nClarity"),
        ("pct_difficulty_match_true",  "Difficulty\nMatch"),
        ("pct_source_alignment_gte_4", "Src >=4 %"),
    ]

    def norm(key, val):
        return val / 100 if "pct" in key else (val - 1) / 4

    N = len(radar)
    angles = [n / N * 2 * pi for n in range(N)] + [0]
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
        vals = [norm(k, d["qm"].get(k, 0)) for k, _ in radar] + \
               [norm(radar[0][0], d["qm"].get(radar[0][0], 0))]
        ax.plot(angles, vals, color=DIFF_COLORS[d["label"]], linewidth=2,
                label=d["label"].capitalize())
        ax.fill(angles, vals, color=DIFF_COLORS[d["label"]], alpha=0.15)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15),
              fontsize=8, framealpha=0.2, labelcolor=TEXT_COL,
              facecolor=AXIS_BG, edgecolor=GRID_COL)


def chart_accept_vs_match(ax):
    style_ax(ax, "Accept Rate vs Difficulty Match (%)", "%")
    accept_pct = [
        sum(1 for it in d["items"] if it["decision"] == "ACCEPT") / len(d["items"]) * 100
        for d in data
    ]
    diff_match = [d["qm"].get("pct_difficulty_match_true", 0) for d in data]
    x = np.arange(len(labels))
    w = 0.35
    b1 = ax.bar(x - w / 2, accept_pct,  w, color="#29b6f6", alpha=0.9,
                label="Accept Rate %", zorder=3)
    b2 = ax.bar(x + w / 2, diff_match,  w, color="#ce93d8", alpha=0.9,
                label="Difficulty Match %", zorder=3)
    for bar, v in list(zip(b1, accept_pct)) + list(zip(b2, diff_match)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                f"{v:.0f}%", ha="center", va="bottom", color=TEXT_COL, fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([l.capitalize() for l in labels], color=TEXT_COL)
    ax.set_ylim(0, 115)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL,
              facecolor=AXIS_BG, edgecolor=GRID_COL)


def chart_heatmap(ax):
    ax.set_facecolor(AXIS_BG)
    ax.set_title("Mean Scores Heatmap", color=TITLE_COL, fontsize=11,
                 fontweight="bold", pad=8)
    hm_metrics = ["mean_source_alignment", "mean_distractor_quality", "mean_stem_clarity"]
    hm_labels  = ["Source\nAlignment", "Distractor\nQuality", "Stem\nClarity"]
    matrix = np.array([[d["qm"].get(m, 0) for m in hm_metrics] for d in data])
    im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=1, vmax=5)
    for i in range(len(data)):
        for j in range(len(hm_metrics)):
            v = matrix[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    color="black" if 2 < v < 4.5 else "white",
                    fontsize=12, fontweight="bold")
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
    """
    Stacked bar: ingest / generate / review cost per model tier (50 items, hard run).
    Based on actual token counts from llm_http.jsonl logs.
    """
    ax.set_facecolor(AXIS_BG)
    ax.set_title(
        "Estimated API Cost — 50 Items (Hard)  |  Based on actual token logs",
        color=TITLE_COL, fontsize=10, fontweight="bold", pad=8,
    )
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.grid(axis="y", color=GRID_COL, linewidth=0.6, linestyle="--", alpha=0.7)

    costs  = pipeline_costs()
    mnames = list(costs.keys())
    mcolors = [MODELS[m][2] for m in mnames]

    stage_colors = {"ingest": "#546e7a", "generate": "#1565c0", "review": "#4a148c"}
    stage_labels = {"ingest": "Ingest (58 chunks)", "generate": "Generate (50 items)", "review": "Review (50 items)"}

    bottoms = np.zeros(len(mnames))
    x = np.arange(len(mnames))

    for stage in ["ingest", "generate", "review"]:
        vals = np.array([costs[m][stage] for m in mnames])
        bars = ax.bar(x, vals, bottom=bottoms, color=stage_colors[stage],
                      alpha=0.9, label=stage_labels[stage], zorder=3, width=0.55)
        for bar, v, bot in zip(bars, vals, bottoms):
            if v >= 0.005:
                ax.text(bar.get_x() + bar.get_width() / 2, bot + v / 2,
                        f"${v:.3f}", ha="center", va="center",
                        color="white", fontsize=8, fontweight="bold")
        bottoms += vals

    # Total label on top
    for i, (m, bot) in enumerate(zip(mnames, bottoms)):
        label = "$0.00\n(local)" if bot == 0 else f"${bot:.3f}"
        ax.text(i, bot + ax.get_ylim()[1] * 0.015 if bot > 0 else 0.003,
                label, ha="center", va="bottom",
                color=TEXT_COL, fontsize=8.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(mnames, color=TEXT_COL, fontsize=9)
    ax.set_ylabel("Estimated Cost (USD)", color=TEXT_COL)
    ax.tick_params(colors=TEXT_COL, labelsize=9)
    ax.set_ylim(0, max(bottoms) * 1.2 + 0.1)

    # Annotation
    ax.annotate(
        "Token counts from actual llm_http.jsonl logs (hard run).\n"
        "Ingest estimated: 58 chunks x ~555 in / ~125 out tokens.\n"
        "Local = $0 API cost; runtime ~70 min on Qwen 7B.",
        xy=(0.98, 0.97), xycoords="axes fraction",
        ha="right", va="top", fontsize=7.5, color="#8b949e",
        bbox=dict(boxstyle="round,pad=0.4", facecolor=AXIS_BG,
                  edgecolor=GRID_COL, alpha=0.8),
    )
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL,
              facecolor=AXIS_BG, edgecolor=GRID_COL, loc="upper left")


# ─────────────────────────────────────────────────────────────────────────────
# Save individual charts
# ─────────────────────────────────────────────────────────────────────────────

CHART_SPECS = [
    ("01_mean_quality_scores",    chart_mean_quality,    8,   5.5, False),
    ("02_decision_distribution",  chart_decisions,       7,   5.5, False),
    ("03_threshold_pass_rates",   chart_thresholds,      9,   5.5, False),
    ("04_source_alignment_box",   chart_box_source,      7,   5.5, False),
    ("05_distractor_quality_box", chart_box_distractor,  7,   5.5, False),
    ("06_stem_clarity_box",       chart_box_stem,        7,   5.5, False),
    ("07_radar",                  chart_radar,           7,   6.0, True),
    ("08_accept_vs_match",        chart_accept_vs_match, 7,   5.5, False),
    ("09_score_heatmap",          chart_heatmap,         7,   4.5, False),
    ("10_api_cost_comparison",    chart_api_cost,        10,  5.5, False),
]

for slug, fn, w, h, polar in CHART_SPECS:
    fig, ax = plt.subplots(figsize=(w, h),
                           subplot_kw={"polar": True} if polar else {})
    fig.patch.set_facecolor(BG)
    fn(ax)
    path = CHARTS_DIR / f"{slug}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  chart: {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard (3x3 grid + full-width cost chart)
# ─────────────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(22, 22))
fig.patch.set_facecolor(BG)

gs = gridspec.GridSpec(
    4, 3,
    figure=fig,
    hspace=0.52, wspace=0.38,
    left=0.06, right=0.97,
    top=0.94,   bottom=0.04,
    height_ratios=[1, 1, 1, 1.1],
)

chart_mean_quality(fig.add_subplot(gs[0, 0]))
chart_decisions(fig.add_subplot(gs[0, 1]))
chart_thresholds(fig.add_subplot(gs[0, 2]))
chart_box_source(fig.add_subplot(gs[1, 0]))
chart_box_distractor(fig.add_subplot(gs[1, 1]))
chart_box_stem(fig.add_subplot(gs[1, 2]))
chart_radar(fig.add_subplot(gs[2, 0], polar=True))
chart_accept_vs_match(fig.add_subplot(gs[2, 1]))
chart_heatmap(fig.add_subplot(gs[2, 2]))

ax_cost = fig.add_subplot(gs[3, :])   # full width
chart_api_cost(ax_cost)

fig.suptitle(
    "domainRag  —  RAG TestGen Quality & Cost Dashboard  (easy  |  medium  |  hard)",
    color=TITLE_COL, fontsize=14, fontweight="bold", y=0.965,
)

dash_path = OUT_DIR / "dashboard.png"
fig.savefig(dash_path, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close(fig)
print(f"\ndashboard: {dash_path}")
