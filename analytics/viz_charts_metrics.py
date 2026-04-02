from __future__ import annotations

import numpy as np

from viz_conditions import condition_color_map, condition_label
from viz_metrics import ANSWER_BUCKETS, answer_key_summary, doc_coverage_summary, pathology_summary
from viz_theme import AXIS_BG, GRID_COL, TEXT_COL, style_ax


def batch_answer_key_distribution(ax, data, labels):
    style_ax(ax, "Answer Key Distribution", "Item Count")
    x = np.arange(len(ANSWER_BUCKETS))
    w = 0.18
    colors = ["#4caf50", "#29b6f6", "#ffb300", "#ab47bc", "#ef5350"]
    for i, d in enumerate(data):
        counts = answer_key_summary(d["items"])["counts"]
        vals = [counts[k] for k in ANSWER_BUCKETS]
        bars = ax.bar(x + i * w, vals, w, label=d["label"].capitalize(), color=colors[i % len(colors)], alpha=0.9, zorder=3)
        for bar, v in zip(bars, vals):
            if v:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, str(v), ha="center", va="bottom", color=TEXT_COL, fontsize=7)
    ax.set_xticks(x + w)
    ax.set_xticklabels(ANSWER_BUCKETS, color=TEXT_COL)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def batch_document_coverage(ax, data, labels):
    style_ax(ax, "Document Coverage Summary", "Value")
    metrics = ["represented_docs", "missing_seed_doc_count", "max_doc_share_pct"]
    metric_labels = ["Docs\nRepresented", "Missing\nSeed Doc", "Max Doc\nShare %"]
    x = np.arange(len(metrics))
    w = 0.25
    for i, d in enumerate(data):
        cov = doc_coverage_summary(d["items"])
        vals = [cov["represented_docs"], cov["missing_seed_doc_count"], cov["max_doc_share_pct"]]
        bars = ax.bar(x + i * w, vals, w, label=d["label"].capitalize(), alpha=0.9, zorder=3)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, f"{v:.0f}", ha="center", va="bottom", color=TEXT_COL, fontsize=7)
    ax.set_xticks(x + w)
    ax.set_xticklabels(metric_labels, color=TEXT_COL)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def batch_pathology_summary(ax, data, labels):
    style_ax(ax, "AI Testing Pathology Checks", "Count / %")
    metrics = ["invalid_answer_key_count", "duplicate_question_instances", "correct_is_uniquely_longest_rate_pct"]
    metric_labels = ["Invalid\nAnswer Key", "Duplicate\nQuestions", "Correct Longest\nRate %"]
    x = np.arange(len(metrics))
    w = 0.25
    for i, d in enumerate(data):
        p = pathology_summary(d["items"])
        vals = [p["invalid_answer_key_count"], p["duplicate_question_instances"], p["correct_is_uniquely_longest_rate_pct"]]
        bars = ax.bar(x + i * w, vals, w, label=d["label"].capitalize(), alpha=0.9, zorder=3)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, f"{v:.0f}", ha="center", va="bottom", color=TEXT_COL, fontsize=7)
    ax.set_xticks(x + w)
    ax.set_xticklabels(metric_labels, color=TEXT_COL)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)


def merged_answer_key_distribution(ax, agg):
    style_ax(ax, "Answer Key Balance by Condition", "Max Letter Share %")
    conds = [g["condition"] for g in agg]
    colors = condition_color_map(conds)
    vals = [answer_key_summary(g["items"])["max_letter_share_pct"] for g in agg]
    bars = ax.bar(range(len(conds)), vals, color=[colors[c] for c in conds], alpha=0.9, zorder=3, width=0.6)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6, f"{v:.0f}%", ha="center", va="bottom", color=TEXT_COL, fontsize=9)
    ax.axhline(40, color="#ffb300", linestyle="--", linewidth=1)
    ax.axhline(50, color="#ef5350", linestyle="--", linewidth=1)
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels([condition_label(c) for c in conds], color=TEXT_COL, fontsize=9)
    ax.set_ylim(0, 100)


def merged_document_coverage(ax, agg):
    style_ax(ax, "Document Coverage by Condition", "Docs Represented")
    conds = [g["condition"] for g in agg]
    colors = condition_color_map(conds)
    vals = [doc_coverage_summary(g["items"])["represented_docs"] for g in agg]
    bars = ax.bar(range(len(conds)), vals, color=[colors[c] for c in conds], alpha=0.9, zorder=3, width=0.6)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f"{v:.0f}", ha="center", va="bottom", color=TEXT_COL, fontsize=9)
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels([condition_label(c) for c in conds], color=TEXT_COL, fontsize=9)


def merged_pathology_summary(ax, agg):
    style_ax(ax, "Pathology Summary by Condition", "Count / %")
    conds = [g["condition"] for g in agg]
    x = np.arange(len(conds))
    w = 0.25
    dupes = [pathology_summary(g["items"])["duplicate_question_instances"] for g in agg]
    invalid = [pathology_summary(g["items"])["invalid_answer_key_count"] for g in agg]
    longest = [pathology_summary(g["items"])["correct_is_uniquely_longest_rate_pct"] for g in agg]
    b1 = ax.bar(x - w, dupes, w, label="Duplicates", color="#ffb300")
    b2 = ax.bar(x, invalid, w, label="Invalid Keys", color="#ef5350")
    b3 = ax.bar(x + w, longest, w, label="Correct Longest %", color="#29b6f6")
    for bars in (b1, b2, b3):
        for bar in bars:
            v = bar.get_height()
            if v:
                ax.text(bar.get_x() + bar.get_width() / 2, v + 0.05, f"{v:.0f}", ha="center", va="bottom", color=TEXT_COL, fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([condition_label(c) for c in conds], color=TEXT_COL, fontsize=9)
    ax.legend(fontsize=8, framealpha=0.2, labelcolor=TEXT_COL, facecolor=AXIS_BG, edgecolor=GRID_COL)
