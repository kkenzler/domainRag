from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

sys.path.insert(0, str(Path(__file__).parent / "claude_aigenticHumanReview"))
sys.path.insert(0, str(Path(__file__).parent / "codex_aigenticHumanReview"))

from viz_charts_batch import (
    boxplot,
    chart_accept_vs_match,
    chart_api_cost,
    chart_decisions,
    chart_heatmap,
    chart_mean_quality,
    chart_radar,
    chart_thresholds,
)
from viz_charts_claude_review import (
    accept_vs_match as cr_accept_vs_match,
    agreement_bar as cr_agreement_bar,
    decision_heatmap as cr_decision_heatmap,
    decisions_bar as cr_decisions_bar,
    flag_bar as cr_flag_bar,
    qc_flags_bar as cr_qc_flags_bar,
    radar_by_condition as cr_radar_by_condition,
    reject_breakdown as cr_reject_breakdown,
    score_bars as cr_score_bars,
    score_boxplot as cr_score_boxplot,
    score_heatmap as cr_score_heatmap,
)
from viz_charts_codex_review import (
    accept_vs_match as cx_accept_vs_match,
    agreement_bar as cx_agreement_bar,
    decision_heatmap as cx_decision_heatmap,
    decisions_bar as cx_decisions_bar,
    flag_bar as cx_flag_bar,
    qc_flags_bar as cx_qc_flags_bar,
    radar_by_condition as cx_radar_by_condition,
    reject_breakdown as cx_reject_breakdown,
    score_bars as cx_score_bars,
    score_boxplot as cx_score_boxplot,
    score_heatmap as cx_score_heatmap,
)
from viz_charts_merged import (
    merged_accept_bar,
    merged_accept_heatmap,
    merged_decisions,
    merged_diff_match,
    merged_quality_bar,
    merged_radar,
    merged_score_heatmap,
    merged_trend,
)
from viz_charts_metrics import (
    batch_answer_key_distribution,
    batch_document_coverage,
    batch_pathology_summary,
    merged_answer_key_distribution,
    merged_document_coverage,
    merged_pathology_summary,
)
from viz_charts_review_analysis import (
    anomaly_counts,
    answer_key_distribution as review_analysis_answer_key_distribution,
    coverage_heatmap as review_analysis_coverage_heatmap,
    failure_modes as review_analysis_failure_modes,
    lane_accept_heatmap as review_analysis_lane_accept_heatmap,
    lane_completion as review_analysis_lane_completion,
    lane_decision_mix as review_analysis_lane_decision_mix,
    lane_score_heatmap as review_analysis_lane_score_heatmap,
    lane_score_comparison as review_analysis_lane_score_comparison,
    load_review_analysis_bundle,
    reviewer_agreement_rates as review_analysis_reviewer_agreement_rates,
    reviewer_alignment_heatmap as review_analysis_reviewer_alignment_heatmap,
    reviewer_vs_lane_nonaccept as review_analysis_reviewer_vs_lane_nonaccept,
    time_cost_bars as review_analysis_time_cost_bars,
)
from viz_io import aggregate_by_condition, claude_review_by_condition, codex_review_by_condition, find_runs, load_batch_run, load_claude_review, load_codex_review, load_merged
from viz_io import load_claude_review_sheet
from viz_metrics import batch_metrics_summary, merged_metrics_summary, write_metrics_summary
from viz_theme import BG, TEXT_COL, TITLE_COL


def _reset_png_dir(path: Path, prefixes: tuple[str, ...] | None = None) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for png in path.glob("*.png"):
        if prefixes is None or png.name.startswith(prefixes):
            png.unlink()


def run_batch_mode(runs_dir: Path, out_dir: Path) -> None:
    charts_dir = out_dir / "charts"
    _reset_png_dir(charts_dir)

    run_files = find_runs(runs_dir)
    if not run_files:
        print(f"No easy/medium/hard run XLSXs found in {runs_dir}")
        return

    data = [load_batch_run(label, path) for label, path in run_files]
    labels = [d["label"] for d in data]
    metrics_summary = batch_metrics_summary(data)
    write_metrics_summary(out_dir / "metrics_summary.json", {"mode": "batch", "metrics": metrics_summary})

    chart_specs = [
        ("01_mean_quality_scores", lambda ax: chart_mean_quality(ax, data, labels), 8, 5.5, False),
        ("02_decision_distribution", lambda ax: chart_decisions(ax, data, labels), 7, 5.5, False),
        ("03_threshold_pass_rates", lambda ax: chart_thresholds(ax, data, labels), 9, 5.5, False),
        ("04_source_alignment_box", lambda ax: boxplot(ax, data, labels, "source_alignment", "Source Alignment Distribution"), 7, 5.5, False),
        ("05_distractor_quality_box", lambda ax: boxplot(ax, data, labels, "distractor_quality", "Distractor Quality Distribution"), 7, 5.5, False),
        ("06_stem_clarity_box", lambda ax: boxplot(ax, data, labels, "stem_clarity", "Stem Clarity Distribution"), 7, 5.5, False),
        ("07_radar", lambda ax: chart_radar(ax, data, labels), 7, 6.0, True),
        ("08_accept_vs_match", lambda ax: chart_accept_vs_match(ax, data, labels), 7, 5.5, False),
        ("09_score_heatmap", lambda ax: chart_heatmap(ax, data, labels), 7, 4.5, False),
        ("10_api_cost_comparison", chart_api_cost, 10, 5.5, False),
        ("11_answer_key_distribution", lambda ax: batch_answer_key_distribution(ax, data, labels), 8, 5.5, False),
        ("12_document_coverage", lambda ax: batch_document_coverage(ax, data, labels), 8, 5.5, False),
        ("13_pathology_summary", lambda ax: batch_pathology_summary(ax, data, labels), 8, 5.5, False),
    ]

    for slug, fn, w, h, polar in chart_specs:
        fig, ax = plt.subplots(figsize=(w, h), subplot_kw={"polar": True} if polar else {})
        fig.patch.set_facecolor(BG)
        fn(ax)
        path = charts_dir / f"{slug}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"  chart: {path.name}")

    fig = plt.figure(figsize=(22, 22))
    fig.patch.set_facecolor(BG)
    gs = gridspec.GridSpec(4, 3, figure=fig, hspace=0.52, wspace=0.38, left=0.06, right=0.97, top=0.94, bottom=0.04, height_ratios=[1, 1, 1, 1.1])
    chart_mean_quality(fig.add_subplot(gs[0, 0]), data, labels)
    chart_decisions(fig.add_subplot(gs[0, 1]), data, labels)
    chart_thresholds(fig.add_subplot(gs[0, 2]), data, labels)
    boxplot(fig.add_subplot(gs[1, 0]), data, labels, "source_alignment", "Source Alignment Distribution")
    boxplot(fig.add_subplot(gs[1, 1]), data, labels, "distractor_quality", "Distractor Quality Distribution")
    boxplot(fig.add_subplot(gs[1, 2]), data, labels, "stem_clarity", "Stem Clarity Distribution")
    chart_radar(fig.add_subplot(gs[2, 0], polar=True), data, labels)
    chart_accept_vs_match(fig.add_subplot(gs[2, 1]), data, labels)
    chart_heatmap(fig.add_subplot(gs[2, 2]), data, labels)
    chart_api_cost(fig.add_subplot(gs[3, :]))
    fig.suptitle("domainRag  —  RAG TestGen Quality & Cost Dashboard  (easy | medium | hard)", color=TITLE_COL, fontsize=14, fontweight="bold", y=0.965)
    dash = out_dir / "dashboard.png"
    fig.savefig(dash, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"\ndashboard: {dash}")


def run_merged_mode(master_path: Path, out_dir: Path) -> None:
    charts_dir = out_dir / "charts"
    _reset_png_dir(charts_dir)

    print(f"Loading merged data from {master_path}")
    groups = load_merged(master_path)
    agg = aggregate_by_condition(groups)
    metrics_summary = merged_metrics_summary(groups, agg)
    write_metrics_summary(out_dir / "metrics_summary.json", {"mode": "merged", "metrics": metrics_summary})
    print(f"  {len(groups)} condition/difficulty groups, {len(agg)} conditions")
    claude_items = load_claude_review_sheet(master_path)
    claude_by_cond = claude_review_by_condition(claude_items) if claude_items else {}
    if claude_items:
        print(f"  Claude review rows available: {len(claude_items)} across {len(claude_by_cond)} conditions")

    chart_specs = [
        ("01_accept_by_condition", lambda ax: merged_accept_bar(ax, agg), 8, 5.5, False),
        ("02_decisions_by_condition", lambda ax: merged_decisions(ax, agg), 8, 5.5, False),
        ("03_accept_heatmap", lambda ax: merged_accept_heatmap(ax, groups), 9, 5.0, False),
        ("04_quality_by_condition", lambda ax: merged_quality_bar(ax, agg), 10, 5.5, False),
        ("05_score_heatmap", lambda ax: merged_score_heatmap(ax, agg), 8, 4.5, False),
        ("06_radar", lambda ax: merged_radar(ax, agg), 7, 6.0, True),
        ("07_accept_trend", lambda ax: merged_trend(ax, groups), 9, 5.5, False),
        ("08_difficulty_match", lambda ax: merged_diff_match(ax, agg), 7, 5.5, False),
        ("09_api_cost_comparison", chart_api_cost, 10, 5.5, False),
        ("10_answer_key_balance", lambda ax: merged_answer_key_distribution(ax, agg), 8, 5.5, False),
        ("11_document_coverage", lambda ax: merged_document_coverage(ax, agg), 8, 5.5, False),
        ("12_pathology_summary", lambda ax: merged_pathology_summary(ax, agg), 9, 5.5, False),
    ]

    for slug, fn, w, h, polar in chart_specs:
        fig, ax = plt.subplots(figsize=(w, h), subplot_kw={"polar": True} if polar else {})
        fig.patch.set_facecolor(BG)
        fn(ax)
        path = charts_dir / f"{slug}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"  chart: {path.name}")

    if claude_items:
        final_chart_specs = [
            ("13_claude_decisions_by_condition", lambda ax: cr_decisions_bar(ax, claude_by_cond), 8, 5.5, False),
            ("14_claude_scores_by_condition", lambda ax: cr_score_bars(ax, claude_by_cond), 9, 5.5, False),
            ("15_claude_accept_heatmap", lambda ax: cr_decision_heatmap(ax, claude_items), 7, 4.5, False),
            ("16_claude_score_heatmap", lambda ax: cr_score_heatmap(ax, claude_by_cond), 7, 4.5, False),
            ("17_claude_qc_flags", lambda ax: cr_qc_flags_bar(ax, claude_by_cond), 10, 5.5, False),
            ("18_claude_radar", lambda ax: cr_radar_by_condition(ax, claude_by_cond), 7, 6.0, True),
            ("19_claude_accept_vs_match", lambda ax: cr_accept_vs_match(ax, claude_by_cond), 8, 5.5, False),
        ]
        for slug, fn, w, h, polar in final_chart_specs:
            fig, ax = plt.subplots(figsize=(w, h), subplot_kw={"polar": True} if polar else {})
            fig.patch.set_facecolor(BG)
            fn(ax)
            path = charts_dir / f"{slug}.png"
            fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
            plt.close(fig)
            print(f"  chart: {path.name}")

    fig = plt.figure(figsize=(22, 20))
    fig.patch.set_facecolor(BG)
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.52, wspace=0.38, left=0.06, right=0.97, top=0.94, bottom=0.05)
    merged_accept_bar(fig.add_subplot(gs[0, 0]), agg)
    merged_decisions(fig.add_subplot(gs[0, 1]), agg)
    merged_accept_heatmap(fig.add_subplot(gs[0, 2]), groups)
    merged_quality_bar(fig.add_subplot(gs[1, 0]), agg)
    merged_score_heatmap(fig.add_subplot(gs[1, 1]), agg)
    merged_radar(fig.add_subplot(gs[1, 2], polar=True), agg)
    merged_trend(fig.add_subplot(gs[2, 0]), groups)
    merged_diff_match(fig.add_subplot(gs[2, 1]), agg)
    chart_api_cost(fig.add_subplot(gs[2, 2]))
    cond_labels = " | ".join([g["condition"] for g in agg])
    total_items = sum(len(g["items"]) for g in agg)
    fig.suptitle(f"domainRag  —  Generation Condition Comparison  ({total_items} items  ·  {cond_labels})", color=TITLE_COL, fontsize=13, fontweight="bold", y=0.965)
    dash = out_dir / "dashboard.png"
    fig.savefig(dash, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"\ndashboard: {dash}")

    if claude_items:
        fig = plt.figure(figsize=(22, 20))
        fig.patch.set_facecolor(BG)
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.52, wspace=0.38, left=0.06, right=0.97, top=0.94, bottom=0.05)
        cr_decisions_bar(fig.add_subplot(gs[0, 0]), claude_by_cond)
        cr_score_bars(fig.add_subplot(gs[0, 1]), claude_by_cond)
        cr_agreement_bar(fig.add_subplot(gs[0, 2]), claude_by_cond)
        cr_decision_heatmap(fig.add_subplot(gs[1, 0]), claude_items)
        cr_score_heatmap(fig.add_subplot(gs[1, 1]), claude_by_cond)
        cr_qc_flags_bar(fig.add_subplot(gs[1, 2]), claude_by_cond)
        cr_reject_breakdown(fig.add_subplot(gs[2, 0]), claude_by_cond)
        cr_radar_by_condition(fig.add_subplot(gs[2, 1], polar=True), claude_by_cond)
        cr_accept_vs_match(fig.add_subplot(gs[2, 2]), claude_by_cond)
        cond_labels = " | ".join(list(claude_by_cond.keys()))
        fig.suptitle(
            f"domainRag  —  Final Claude Review Comparison  ({len(claude_items)} items  ·  {cond_labels})",
            color=TITLE_COL,
            fontsize=13,
            fontweight="bold",
            y=0.965,
        )
        final_dash = out_dir / "dashboard_claude_final.png"
        fig.savefig(final_dash, dpi=150, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"final dashboard: {final_dash}")


def run_claude_review_mode(decisions_json: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _reset_png_dir(out_dir, prefixes=("claude_", "dashboard_claude_"))

    print(f"Loading Claude review data from {decisions_json}")
    items = load_claude_review(decisions_json)
    by_cond = claude_review_by_condition(items)
    print(f"  {len(items)} items across {len(by_cond)} conditions")

    chart_specs = [
        ("01_decisions_by_condition", lambda ax: cr_decisions_bar(ax, by_cond), 8, 5.5, False),
        ("02_scores_by_condition", lambda ax: cr_score_bars(ax, by_cond), 9, 5.5, False),
        ("03_agreement_with_reviewer", lambda ax: cr_agreement_bar(ax, by_cond), 8, 5.5, False),
        ("04_decision_heatmap", lambda ax: cr_decision_heatmap(ax, items), 7, 4.5, False),
        ("05_score_heatmap", lambda ax: cr_score_heatmap(ax, by_cond), 7, 4.5, False),
        ("06_qc_flags", lambda ax: cr_qc_flags_bar(ax, by_cond), 10, 5.5, False),
        ("07_radar_by_condition", lambda ax: cr_radar_by_condition(ax, by_cond), 7, 6.0, True),
    ]

    for slug, fn, w, h, polar in chart_specs:
        fig, ax = plt.subplots(figsize=(w, h), subplot_kw={"polar": True} if polar else {})
        fig.patch.set_facecolor(BG)
        fn(ax)
        path = out_dir / f"claude_{slug}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"  chart: {path.name}")

    fig = plt.figure(figsize=(22, 14))
    fig.patch.set_facecolor(BG)
    gs = gridspec.GridSpec(2, 4, figure=fig, hspace=0.55, wspace=0.40, left=0.05, right=0.97, top=0.92, bottom=0.06)
    cr_decisions_bar(fig.add_subplot(gs[0, 0]), by_cond)
    cr_score_bars(fig.add_subplot(gs[0, 1]), by_cond)
    cr_agreement_bar(fig.add_subplot(gs[0, 2]), by_cond)
    cr_decision_heatmap(fig.add_subplot(gs[0, 3]), items)
    cr_score_heatmap(fig.add_subplot(gs[1, 0]), by_cond)
    cr_qc_flags_bar(fig.add_subplot(gs[1, 1]), by_cond)
    cr_radar_by_condition(fig.add_subplot(gs[1, 2], polar=True), by_cond)
    cr_flag_bar(fig.add_subplot(gs[1, 3]), by_cond)
    total_items = len(items)
    fig.suptitle(f"domainRag  —  Agentic Human Review  ({total_items} items  ·  {len(by_cond)} conditions)", color=TITLE_COL, fontsize=13, fontweight="bold", y=0.965)
    dash = out_dir / "dashboard_claude_review.png"
    fig.savefig(dash, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"\ndashboard: {dash}")


def run_codex_review_mode(decisions_json: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _reset_png_dir(out_dir, prefixes=("codex_", "dashboard_codex_"))

    print(f"Loading Codex review data from {decisions_json}")
    items = load_codex_review(decisions_json)
    by_cond = codex_review_by_condition(items)
    print(f"  {len(items)} items across {len(by_cond)} conditions")

    chart_specs = [
        ("01_decisions_by_condition", lambda ax: cx_decisions_bar(ax, by_cond), 8, 5.5, False),
        ("02_scores_by_condition", lambda ax: cx_score_bars(ax, by_cond), 9, 5.5, False),
        ("03_agreement_with_reviewer", lambda ax: cx_agreement_bar(ax, by_cond), 8, 5.5, False),
        ("04_decision_heatmap", lambda ax: cx_decision_heatmap(ax, items), 7, 4.5, False),
        ("05_score_heatmap", lambda ax: cx_score_heatmap(ax, by_cond), 7, 4.5, False),
        ("06_qc_flags", lambda ax: cx_qc_flags_bar(ax, by_cond), 10, 5.5, False),
        ("07_radar_by_condition", lambda ax: cx_radar_by_condition(ax, by_cond), 7, 6.0, True),
    ]

    for slug, fn, w, h, polar in chart_specs:
        fig, ax = plt.subplots(figsize=(w, h), subplot_kw={"polar": True} if polar else {})
        fig.patch.set_facecolor(BG)
        fn(ax)
        path = out_dir / f"codex_{slug}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"  chart: {path.name}")

    fig = plt.figure(figsize=(22, 14))
    fig.patch.set_facecolor(BG)
    gs = gridspec.GridSpec(2, 4, figure=fig, hspace=0.55, wspace=0.40, left=0.05, right=0.97, top=0.92, bottom=0.06)
    cx_decisions_bar(fig.add_subplot(gs[0, 0]), by_cond)
    cx_score_bars(fig.add_subplot(gs[0, 1]), by_cond)
    cx_agreement_bar(fig.add_subplot(gs[0, 2]), by_cond)
    cx_decision_heatmap(fig.add_subplot(gs[0, 3]), items)
    cx_score_heatmap(fig.add_subplot(gs[1, 0]), by_cond)
    cx_qc_flags_bar(fig.add_subplot(gs[1, 1]), by_cond)
    cx_radar_by_condition(fig.add_subplot(gs[1, 2], polar=True), by_cond)
    cx_flag_bar(fig.add_subplot(gs[1, 3]), by_cond)
    total_items = len(items)
    fig.suptitle(f"domainRag  —  Codex Agentic Review  ({total_items} items  ·  {len(by_cond)} conditions)", color=TITLE_COL, fontsize=13, fontweight="bold", y=0.965)
    dash = out_dir / "dashboard_codex_review.png"
    fig.savefig(dash, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"\ndashboard: {dash}")


def run_review_analysis_mode(analysis_dir: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _reset_png_dir(out_dir, prefixes=("shared_", "dashboard_review_analysis"))

    print(f"Loading review analysis exports from {analysis_dir}")
    bundle = load_review_analysis_bundle(analysis_dir)

    chart_specs = [
        ("01_answer_key_distribution", lambda ax: review_analysis_answer_key_distribution(ax, bundle), 8, 5.5, False),
        ("02_failure_modes", lambda ax: review_analysis_failure_modes(ax, bundle), 10, 5.5, False),
        ("03_lane_decision_mix", lambda ax: review_analysis_lane_decision_mix(ax, bundle), 7, 5.5, False),
        ("04_reviewer_agreement", lambda ax: review_analysis_reviewer_agreement_rates(ax, bundle), 8, 5.5, False),
        ("05_lane_score_comparison", lambda ax: review_analysis_lane_score_comparison(ax, bundle), 8, 5.5, False),
        ("06_claude_accept_heatmap", lambda ax: review_analysis_lane_accept_heatmap(ax, bundle, "claude", "Claude"), 10, 5.5, False),
        ("07_codex_accept_heatmap", lambda ax: review_analysis_lane_accept_heatmap(ax, bundle, "codex", "Codex"), 10, 5.5, False),
        ("08_claude_score_heatmap", lambda ax: review_analysis_lane_score_heatmap(ax, bundle, "claude", "Claude"), 10, 5.5, False),
        ("09_codex_score_heatmap", lambda ax: review_analysis_lane_score_heatmap(ax, bundle, "codex", "Codex"), 10, 5.5, False),
        ("10_reviewer_alignment_heatmap", lambda ax: review_analysis_reviewer_alignment_heatmap(ax, bundle), 10, 5.5, False),
        ("11_time_cost", lambda ax: review_analysis_time_cost_bars(ax, bundle), 7, 5.5, False),
    ]

    for slug, fn, w, h, polar in chart_specs:
        fig, ax = plt.subplots(figsize=(w, h), subplot_kw={"polar": True} if polar else {})
        fig.patch.set_facecolor(BG)
        fn(ax)
        path = out_dir / f"shared_{slug}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"  chart: {path.name}")

    fig = plt.figure(figsize=(22, 18))
    fig.patch.set_facecolor(BG)
    gs = gridspec.GridSpec(4, 3, figure=fig, hspace=0.60, wspace=0.42, left=0.05, right=0.97, top=0.94, bottom=0.06)
    review_analysis_answer_key_distribution(fig.add_subplot(gs[0, 0]), bundle)
    review_analysis_failure_modes(fig.add_subplot(gs[0, 1:]), bundle)
    review_analysis_lane_decision_mix(fig.add_subplot(gs[1, 0]), bundle)
    review_analysis_reviewer_agreement_rates(fig.add_subplot(gs[1, 1]), bundle)
    review_analysis_lane_score_comparison(fig.add_subplot(gs[1, 2]), bundle)
    review_analysis_lane_accept_heatmap(fig.add_subplot(gs[2, 0]), bundle, "claude", "Claude")
    review_analysis_lane_accept_heatmap(fig.add_subplot(gs[2, 1]), bundle, "codex", "Codex")
    review_analysis_time_cost_bars(fig.add_subplot(gs[2, 2]), bundle)
    review_analysis_lane_score_heatmap(fig.add_subplot(gs[3, 0]), bundle, "claude", "Claude")
    review_analysis_lane_score_heatmap(fig.add_subplot(gs[3, 1]), bundle, "codex", "Codex")
    review_analysis_reviewer_alignment_heatmap(fig.add_subplot(gs[3, 2]), bundle)
    fig.suptitle("domainRag  —  Review Analysis Dashboard", color=TITLE_COL, fontsize=13, fontweight="bold", y=0.965)
    dash = out_dir / "dashboard_review_analysis.png"
    fig.savefig(dash, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"\ndashboard: {dash}")
