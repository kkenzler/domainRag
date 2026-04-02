from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


DIFF_COLORS = {"easy": "#4CAF50", "medium": "#FF9800", "hard": "#F44336"}
DEC_COLORS = {"ACCEPT": "#4CAF50", "REVISE": "#FF9800", "REJECT": "#F44336", "UNKNOWN": "#546e7a"}
BASE_COND_COLORS = ["#78909c", "#29b6f6", "#ab47bc", "#FFB300", "#ef5350", "#66bb6a", "#ffa726", "#26c6da"]

BG = "#0d1117"
AXIS_BG = "#161b22"
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
