from __future__ import annotations

import csv
import os
from pathlib import Path

STUDY_ROOT = Path(__file__).resolve().parents[1]
EXPORTS_DIR = STUDY_ROOT / "exports"
CHARTS_DIR = EXPORTS_DIR / "charts"
MPLCONFIGDIR = EXPORTS_DIR / ".mplconfig"
SUMMARY_CSV = EXPORTS_DIR / "first_pass_cost_model_condition_summary.csv"
OUTPUT_PNG = CHARTS_DIR / "first_pass_machine_cost_by_condition.png"

os.environ["MPLCONFIGDIR"] = str(MPLCONFIGDIR)

import matplotlib


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _style():
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.facecolor": "#0E1726",
            "axes.facecolor": "#0E1726",
            "savefig.facecolor": "#0E1726",
            "text.color": "#E8EEF7",
            "axes.labelcolor": "#D5DEEA",
            "axes.edgecolor": "#6D7A8C",
            "xtick.color": "#D5DEEA",
            "ytick.color": "#D5DEEA",
            "font.size": 10,
            "axes.titleweight": "bold",
            "axes.titlepad": 12,
        }
    )
    return plt


def main() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)

    rows = _read_rows(SUMMARY_CSV)
    if not rows:
        raise SystemExit(f"No rows found in {SUMMARY_CSV}")

    plt = _style()
    import numpy as np

    condition_order = ["local/local", "local/haiku", "haiku/local", "haiku/haiku"]
    rows_by_condition = {row["condition"]: row for row in rows}
    ordered = [rows_by_condition[c] for c in condition_order if c in rows_by_condition]

    labels = [row["condition"] for row in ordered]
    local_cost = [float(row["avg_local_compute_usd"]) for row in ordered]
    api_cost = [float(row["avg_api_cost_usd"]) for row in ordered]
    combined = [float(row["avg_combined_machine_cost_usd"]) for row in ordered]
    duration = [float(row["avg_duration_hours"]) for row in ordered]

    x = np.arange(len(labels))
    width = 0.62

    fig, ax = plt.subplots(figsize=(10.5, 6.0))

    local_bars = ax.bar(
        x,
        local_cost,
        width,
        color="#5BC0EB",
        label="Local compute estimate",
    )
    api_bars = ax.bar(
        x,
        api_cost,
        width,
        bottom=local_cost,
        color="#F6AE2D",
        label="Frontier API estimate",
    )

    ax2 = ax.twinx()
    ax2.plot(
        x,
        duration,
        color="#FF6B6B",
        marker="o",
        linewidth=2.2,
        label="Avg duration (hours)",
    )

    ax.set_title("First-Pass Machine Cost by Pipeline Condition", fontsize=14, color="#F3F7FB")
    ax.set_ylabel("Estimated machine cost (USD)")
    ax2.set_ylabel("Average duration (hours)", color="#FFD7D7")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, max(combined) * 1.35)
    ax2.set_ylim(0, max(duration) * 1.35)

    ax.grid(axis="y", linestyle="--", alpha=0.18, color="#D5DEEA")
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_color("#6D7A8C")
    for spine in ax2.spines.values():
        spine.set_color("#6D7A8C")

    for i, total in enumerate(combined):
        ax.text(
            x[i],
            total + max(combined) * 0.03,
            f"${total:.3f}",
            ha="center",
            va="bottom",
            fontsize=10,
            color="#F3F7FB",
            fontweight="bold",
        )
        ax2.text(
            x[i],
            duration[i] + max(duration) * 0.04,
            f"{duration[i]:.2f}h",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#FFD7D7",
        )

    legend_handles = [
        local_bars,
        api_bars,
        ax2.lines[0],
    ]
    legend_labels = [
        "Local compute estimate",
        "Frontier API estimate",
        "Avg duration (hours)",
    ]
    ax.legend(
        legend_handles,
        legend_labels,
        loc="upper left",
        frameon=False,
        fontsize=9,
    )

    fig.text(
        0.015,
        0.02,
        "First-pass model only: local = electricity estimate at $0.15/kWh and 350W; hardware amortization excluded.",
        color="#B8C4D1",
        fontsize=8.8,
    )

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(OUTPUT_PNG, dpi=180)
    print(f"Wrote {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
