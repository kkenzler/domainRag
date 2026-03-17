"""
merge_runs.py — Merge all batch XLSX runs into a single master file.

Scans analytics/<batch-label>/run_*.xlsx across all 4 batches,
combines Items + Reviewer Decisions + Traceability + Quality Metrics,
adds batch_label column, writes analytics/merged_master.xlsx.

Also runs viz.py --merged to generate cross-condition comparison charts.

Usage:
    python merge_runs.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import openpyxl
from openpyxl import Workbook

SCRIPT_DIR = Path(__file__).resolve().parent

# Ordered batch labels — determines sheet ordering and comparison axis
BATCH_ORDER = ["local-local", "haiku-reviewer", "haiku-generator", "haiku-both"]

# Map folder name → human-readable condition label
BATCH_LABELS = {
    "local-local":      "local/local",
    "haiku-reviewer":   "local/haiku",
    "haiku-generator":  "haiku/local",
    "haiku-both":       "haiku/haiku",
}

# Sheets to merge (source sheet name → dest sheet name)
MERGE_SHEETS = ["Items", "Reviewer Decisions", "Traceability"]

# Quality Metrics: aggregate separately (one row per run)
QM_SHEET = "Quality Metrics"


def find_run_files() -> list[tuple[str, str, Path]]:
    """Returns list of (batch_label, difficulty, xlsx_path)."""
    runs = []
    for batch_dir in sorted(SCRIPT_DIR.iterdir()):
        if not batch_dir.is_dir():
            continue
        label = batch_dir.name
        if label not in BATCH_ORDER:
            continue
        for xlsx in sorted(batch_dir.glob("run_*.xlsx")):
            # Determine difficulty from the Items sheet
            try:
                wb   = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
                ws   = wb["Items"]
                hdrs = [c.value for c in next(ws.iter_rows(max_row=1))]
                diff_idx = hdrs.index("difficulty") if "difficulty" in hdrs else None
                difficulty = "unknown"
                if diff_idx is not None:
                    for row in ws.iter_rows(min_row=2, values_only=True):
                        if row[0] and row[diff_idx]:
                            difficulty = str(row[diff_idx])
                            break
                wb.close()
            except Exception:
                difficulty = "unknown"
            runs.append((label, difficulty, xlsx))
    return runs


def merge_sheet(dest_ws, src_ws, batch_label: str, condition_label: str,
                difficulty: str, first: bool) -> None:
    """Append rows from src_ws into dest_ws. Writes header on first call."""
    rows = list(src_ws.iter_rows(values_only=True))
    if not rows:
        return

    header = list(rows[0])
    if first:
        dest_ws.append(["batch_label", "condition", "difficulty"] + header)

    for row in rows[1:]:
        if row[0] is None:
            continue
        dest_ws.append([batch_label, condition_label, difficulty] + list(row))


def merge_quality_metrics(dest_ws, src_ws, batch_label: str,
                           condition_label: str, difficulty: str,
                           run_id: str, first: bool) -> None:
    rows = list(src_ws.iter_rows(values_only=True))
    if not rows:
        return
    if first:
        dest_ws.append(["batch_label", "condition", "difficulty", "run_id", "metric", "value"])
    for row in rows[1:]:
        if row[0]:
            dest_ws.append([batch_label, condition_label, difficulty, run_id] + list(row))


def main() -> None:
    print("merge_runs.py — scanning batch folders\n")

    run_files = find_run_files()
    if not run_files:
        print("No run files found. Check that analytics/<batch>/ folders exist.")
        sys.exit(1)

    print(f"Found {len(run_files)} run files:")
    for label, diff, path in run_files:
        print(f"  [{BATCH_LABELS.get(label, label)}]  {diff:8s}  {path.name}")

    out_wb = Workbook()
    out_wb.remove(out_wb.active)   # remove default sheet

    # Create destination sheets
    sheet_map = {}
    for sheet_name in MERGE_SHEETS:
        ws = out_wb.create_sheet(sheet_name)
        sheet_map[sheet_name] = {"ws": ws, "first": True}

    qm_ws = out_wb.create_sheet("Quality Metrics")
    qm_first = True

    for label, difficulty, xlsx_path in run_files:
        condition = BATCH_LABELS.get(label, label)
        print(f"\n  merging [{condition}] {difficulty} <- {xlsx_path.name}")
        try:
            src_wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        except Exception as e:
            print(f"    ERROR loading {xlsx_path}: {e}")
            continue

        # Extract run_id from filename
        run_id = xlsx_path.stem.replace("run_", "")

        for sheet_name, state in sheet_map.items():
            if sheet_name in src_wb.sheetnames:
                merge_sheet(
                    state["ws"], src_wb[sheet_name],
                    label, condition, difficulty, state["first"],
                )
                state["first"] = False

        if QM_SHEET in src_wb.sheetnames:
            merge_quality_metrics(
                qm_ws, src_wb[QM_SHEET],
                label, condition, difficulty, run_id, qm_first,
            )
            qm_first = False

        src_wb.close()

    out_path = SCRIPT_DIR / "merged_master.xlsx"
    out_wb.save(str(out_path))
    print(f"\nSaved: {out_path}")
    print(f"  Sheets: {out_wb.sheetnames}")

    # Trigger merged viz if viz.py supports it
    viz_py = SCRIPT_DIR / "viz.py"
    if viz_py.exists():
        print("\nRunning viz.py --merged ...")
        rc = subprocess.run(
            [sys.executable, str(viz_py), "--merged", str(out_path)],
            cwd=str(SCRIPT_DIR),
        ).returncode
        if rc != 0:
            print(f"  viz.py --merged returned {rc} (may not be implemented yet)")

    print("\nMerge complete.")


if __name__ == "__main__":
    main()
