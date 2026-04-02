from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path


ANSWER_BUCKETS = ["A", "B", "C", "D", "INVALID"]


def normalize_answer_key(value) -> str:
    raw = str(value or "").strip().upper()
    return raw if raw in {"A", "B", "C", "D"} else "INVALID"


def normalize_question(text) -> str:
    cleaned = re.sub(r"\s+", " ", str(text or "").strip().lower())
    return cleaned


def answer_key_counts(items: list[dict]) -> dict[str, int]:
    counts = Counter(normalize_answer_key(it.get("correct_key")) for it in items)
    return {k: int(counts.get(k, 0)) for k in ANSWER_BUCKETS}


def answer_key_entropy(counts: dict[str, int]) -> float:
    valid_total = sum(counts.get(k, 0) for k in ["A", "B", "C", "D"])
    if valid_total <= 0:
        return 0.0
    entropy = 0.0
    for k in ["A", "B", "C", "D"]:
        p = counts.get(k, 0) / valid_total
        if p > 0:
            entropy -= p * math.log2(p)
    return float(entropy)


def answer_key_summary(items: list[dict]) -> dict[str, object]:
    counts = answer_key_counts(items)
    total = len(items)
    valid_total = sum(counts[k] for k in ["A", "B", "C", "D"])
    max_letter_count = max((counts[k] for k in ["A", "B", "C", "D"]), default=0)
    max_letter_share = (max_letter_count / valid_total * 100.0) if valid_total else 0.0
    return {
        "counts": counts,
        "total_items": total,
        "valid_answer_keys": valid_total,
        "invalid_answer_keys": counts["INVALID"],
        "max_letter_share_pct": max_letter_share,
        "entropy_bits": answer_key_entropy(counts),
        "warn_imbalance": max_letter_share > 40.0,
        "critical_imbalance": max_letter_share > 50.0,
    }


def doc_coverage_summary(items: list[dict]) -> dict[str, object]:
    docs = [Path(str(it.get("seed_doc_path"))).name for it in items if str(it.get("seed_doc_path") or "").strip()]
    counts = Counter(docs)
    represented = len(counts)
    missing = sum(1 for it in items if not str(it.get("seed_doc_path") or "").strip())
    total = len(items)
    max_doc_share = (max(counts.values()) / total * 100.0) if counts and total else 0.0
    top_docs = [{"doc": doc, "count": cnt} for doc, cnt in counts.most_common(5)]
    return {
        "represented_docs": represented,
        "missing_seed_doc_count": missing,
        "max_doc_share_pct": max_doc_share,
        "top_docs": top_docs,
        "topic_coverage_available": False,
        "topic_coverage_note": "Current workbook schema has no topic/subtopic columns; only document coverage can be measured directly.",
    }


def pathology_summary(items: list[dict]) -> dict[str, object]:
    normalized_questions = [normalize_question(it.get("question")) for it in items if normalize_question(it.get("question"))]
    question_counts = Counter(normalized_questions)
    duplicate_question_instances = sum(cnt - 1 for cnt in question_counts.values() if cnt > 1)

    invalid_answer_keys = sum(1 for it in items if normalize_answer_key(it.get("correct_key")) == "INVALID")
    missing_seed_docs = sum(1 for it in items if not str(it.get("seed_doc_path") or "").strip())

    correct_is_longest = 0
    valid_for_length = 0
    for it in items:
        key = normalize_answer_key(it.get("correct_key"))
        if key == "INVALID":
            continue
        options = {
            "A": str(it.get("a") or ""),
            "B": str(it.get("b") or ""),
            "C": str(it.get("c") or ""),
            "D": str(it.get("d") or ""),
        }
        lengths = {k: len(v.strip()) for k, v in options.items()}
        max_len = max(lengths.values())
        winners = [k for k, v in lengths.items() if v == max_len]
        valid_for_length += 1
        if len(winners) == 1 and winners[0] == key:
            correct_is_longest += 1

    return {
        "duplicate_question_instances": duplicate_question_instances,
        "duplicate_question_rate_pct": (duplicate_question_instances / len(items) * 100.0) if items else 0.0,
        "invalid_answer_key_count": invalid_answer_keys,
        "missing_seed_doc_count": missing_seed_docs,
        "correct_is_uniquely_longest_count": correct_is_longest,
        "correct_is_uniquely_longest_rate_pct": (correct_is_longest / valid_for_length * 100.0) if valid_for_length else 0.0,
    }


def batch_metrics_summary(data: list[dict]) -> dict[str, object]:
    out = {}
    for d in data:
        label = d["label"]
        items = d["items"]
        out[label] = {
            "answer_keys": answer_key_summary(items),
            "document_coverage": doc_coverage_summary(items),
            "pathologies": pathology_summary(items),
        }
    return out


def merged_metrics_summary(groups: list[dict], agg: list[dict]) -> dict[str, object]:
    by_condition = {}
    for g in agg:
        by_condition[g["condition"]] = {
            "answer_keys": answer_key_summary(g["items"]),
            "document_coverage": doc_coverage_summary(g["items"]),
            "pathologies": pathology_summary(g["items"]),
        }
    by_condition_difficulty = {}
    for g in groups:
        by_condition_difficulty[f"{g['condition']}::{g['difficulty']}"] = {
            "answer_keys": answer_key_summary(g["items"]),
            "document_coverage": doc_coverage_summary(g["items"]),
            "pathologies": pathology_summary(g["items"]),
        }
    return {"by_condition": by_condition, "by_condition_difficulty": by_condition_difficulty}


def write_metrics_summary(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
