from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import openpyxl

from viz_conditions import ordered_conditions


def find_runs(runs_dir: Path):
    found = {}
    for xlsx in sorted(runs_dir.glob("run_*.xlsx")):
        try:
            wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
            ws = wb["Items"]
            hdrs = [c.value for c in next(ws.iter_rows(max_row=1))]
            if "difficulty" not in hdrs:
                wb.close()
                continue
            di = hdrs.index("difficulty")
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] and row[di]:
                    found[str(row[di])] = xlsx
                    break
            wb.close()
        except Exception:
            pass
    order = ["easy", "medium", "hard"]
    return [(d, found[d]) for d in order if d in found]


def load_batch_run(label: str, xlsx_path: Path) -> dict:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)

    qm = {}
    for row in wb["Quality Metrics"].iter_rows(min_row=2, values_only=True):
        if row[0]:
            qm[row[0].replace("quality.", "")] = row[1]

    hdrs = [c.value for c in next(wb["Items"].iter_rows(max_row=1))]
    idx = {h: i for i, h in enumerate(hdrs)}
    items = []
    for row in wb["Items"].iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        items.append(
            {
                "question": row[idx["question"]] if "question" in idx else None,
                "a": row[idx["a"]] if "a" in idx else None,
                "b": row[idx["b"]] if "b" in idx else None,
                "c": row[idx["c"]] if "c" in idx else None,
                "d": row[idx["d"]] if "d" in idx else None,
                "correct_key": row[idx["correct_key"]] if "correct_key" in idx else None,
                "seed_doc_path": row[idx["seed_doc_path"]] if "seed_doc_path" in idx else None,
                "decision": row[idx["decision"]],
                "source_alignment": row[idx["source_alignment"]],
                "distractor_quality": row[idx["distractor_quality"]],
                "stem_clarity": row[idx["stem_clarity"]],
                "difficulty_match": row[idx["difficulty_match"]],
            }
        )

    chunks = []
    if "Chunk Preview" in wb.sheetnames:
        for row in wb["Chunk Preview"].iter_rows(min_row=2, values_only=True):
            if row[2]:
                chunks.append(row[2])

    return {"label": label, "qm": qm, "items": items, "chunks": chunks}


def load_merged(master_path: Path) -> list:
    wb = openpyxl.load_workbook(master_path, data_only=True)
    ws = wb["Items"]
    hdrs = [c.value for c in next(ws.iter_rows(max_row=1))]
    idx = {h: i for i, h in enumerate(hdrs)}
    groups = {}

    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        cond = row[idx.get("condition", 0)] or "unknown"
        diff = row[idx.get("difficulty", 0)] or "unknown"
        key = (cond, diff)
        if key not in groups:
            groups[key] = {"condition": cond, "difficulty": diff, "items": [], "qm": {}}
        groups[key]["items"].append(
            {
                "question": row[idx["question"]] if "question" in idx else None,
                "a": row[idx["a"]] if "a" in idx else None,
                "b": row[idx["b"]] if "b" in idx else None,
                "c": row[idx["c"]] if "c" in idx else None,
                "d": row[idx["d"]] if "d" in idx else None,
                "correct_key": row[idx["correct_key"]] if "correct_key" in idx else None,
                "seed_doc_path": row[idx["seed_doc_path"]] if "seed_doc_path" in idx else None,
                "decision": row[idx["decision"]],
                "source_alignment": row[idx["source_alignment"]],
                "distractor_quality": row[idx["distractor_quality"]],
                "stem_clarity": row[idx["stem_clarity"]],
                "difficulty_match": row[idx["difficulty_match"]],
            }
        )

    ws_qm = wb["Quality Metrics"]
    qm_hdrs = [c.value for c in next(ws_qm.iter_rows(max_row=1))]
    qi = {h: i for i, h in enumerate(qm_hdrs)}
    for row in ws_qm.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        cond = row[qi.get("condition", 0)] or "unknown"
        diff = row[qi.get("difficulty", 0)] or "unknown"
        key = (cond, diff)
        metric = str(row[qi["metric"]]).replace("quality.", "")
        val = row[qi["value"]]
        if key in groups and val is not None:
            prev = groups[key]["qm"].get(metric)
            groups[key]["qm"][metric] = (prev + val) / 2 if prev is not None else val

    diff_order = {"easy": 0, "medium": 1, "hard": 2}
    return sorted(
        groups.values(),
        key=lambda g: (ordered_conditions([item["condition"] for item in groups.values()]).index(g["condition"]), diff_order.get(g["difficulty"], 99)),
    )


def aggregate_by_condition(groups: list) -> list:
    cond_map = defaultdict(lambda: {"items": [], "qm_lists": {}})
    for g in groups:
        c = g["condition"]
        cond_map[c]["condition"] = c
        cond_map[c]["items"].extend(g["items"])
        for k, v in g["qm"].items():
            cond_map[c]["qm_lists"].setdefault(k, []).append(v)

    result = []
    for c in ordered_conditions(cond_map.keys()):
        if c not in cond_map:
            continue
        entry = cond_map[c]
        qm = {k: float(np.mean(vs)) for k, vs in entry["qm_lists"].items()}
        # has_reviewer_metrics is True only when at least one item in this
        # condition has a non-None decision (i.e. was run through the
        # domainRag automated reviewer).  GPT baseline items have
        # decision=None and are explicitly flagged False so that downstream
        # charts can distinguish "no reviewer data" from "score = 0".
        has_rev = any(it.get("decision") is not None for it in entry["items"])
        result.append({
            "condition": c,
            "items": entry["items"],
            "qm": qm,
            "has_reviewer_metrics": has_rev,
        })
    return result


def load_claude_review(decisions_json: Path) -> list:
    with open(decisions_json, encoding="utf-8") as f:
        raw = json.load(f)
    return [_normalize_claude_review_item(item) for item in raw]


def load_claude_review_sheet(master_path: Path) -> list:
    wb = openpyxl.load_workbook(master_path, read_only=True, data_only=True)
    if "Claude Review" not in wb.sheetnames:
        wb.close()
        return []
    ws = wb["Claude Review"]
    headers = [c.value for c in next(ws.iter_rows(max_row=1))]
    items = [dict(zip(headers, row)) for row in ws.iter_rows(min_row=2, values_only=True) if row[0] is not None]
    wb.close()
    return [_normalize_claude_review_item(item) for item in items]


def _normalize_claude_review_item(item: dict) -> dict:
    item["condition"] = item.get("condition") or "unknown"
    item["difficulty"] = item.get("difficulty") or "unknown"
    for bfield in (
        "agrees_with_reviewer",
        "flag_ambiguity",
        "chunks_support_question",
        "correct_answer_verifiable",
        "distractors_clearly_wrong",
        "reviewer_source_call_accurate",
    ):
        v = item.get(bfield)
        if isinstance(v, str):
            item[bfield] = True if v.lower() == "true" else (False if v.lower() == "false" else v)
    for sfield in (
        "claude_source_alignment",
        "claude_distractor_quality",
        "claude_stem_clarity",
        "claude_difficulty_match",
    ):
        v = item.get(sfield)
        if isinstance(v, str) and v.strip().isdigit():
            item[sfield] = int(v.strip())
    return item


def claude_review_by_condition(items: list) -> dict:
    out = defaultdict(list)
    for it in items:
        out[it["condition"]].append(it)
    return {c: out[c] for c in ordered_conditions(out.keys())}


def load_codex_review(decisions_json: Path) -> list:
    with open(decisions_json, encoding="utf-8") as f:
        raw = json.load(f)
    return [_normalize_codex_review_item(item) for item in raw]


def _normalize_codex_review_item(item: dict) -> dict:
    item["condition"] = item.get("condition") or "unknown"
    item["difficulty"] = item.get("difficulty") or "unknown"
    for bfield in (
        "agrees_with_reviewer",
        "flag_ambiguity",
        "chunks_support_question",
        "correct_answer_verifiable",
        "distractors_clearly_wrong",
        "reviewer_source_call_accurate",
    ):
        v = item.get(bfield)
        if isinstance(v, str):
            item[bfield] = True if v.lower() == "true" else (False if v.lower() == "false" else v)
    for sfield in (
        "review_source_alignment",
        "review_distractor_quality",
        "review_stem_clarity",
        "review_difficulty_match",
    ):
        v = item.get(sfield)
        if isinstance(v, str) and v.strip().isdigit():
            item[sfield] = int(v.strip())
    return item


def codex_review_by_condition(items: list) -> dict:
    out = defaultdict(list)
    for it in items:
        out[it["condition"]].append(it)
    return {c: out[c] for c in ordered_conditions(out.keys())}
