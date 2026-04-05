"""
run_batches.py — Unattended batch orchestrator for domainRag comparative study.

Runs batches B, C, D (3 difficulties × 50 items each) back-to-back.
Requires API key once at startup, then runs completely unattended.

Batch conditions:
  B  [MODEL]-reviewer   generate=local   review=api
  C  [MODEL]-generator  generate=api     review=local
  D  [MODEL]-both       generate=api     review=api

Set MODEL (below) to switch the API model for a new study run.
Output lands in:
  analytics/example1_local-local/
  analytics/example1_[MODEL]Permutations/

After each batch:  moves runs → study archive folder  →  viz snapshot
After all batches: merge_runs.py

Usage (from repo root or analytics/):
    python analytics/run_batches.py
    python analytics/run_batches.py --start-batch [MODEL]-generator   # resume from C
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent          # analytics/
REPO_DIR   = SCRIPT_DIR.parent                        # domainRag/
RAG_DIR    = REPO_DIR / "_rag_testGen"                # domainRag/_rag_testGen/
RUNS_DIR   = SCRIPT_DIR / "runs"
CONFIG_ENV = Path(
    os.environ.get("DOMAINRAG_CONFIG_ENV", str(Path.home() / "secrets" / "domainRag" / "config.env"))
)
CLI_PY     = RAG_DIR / "cli.py"
VIZ_PY     = SCRIPT_DIR / "analyticsVizs.py"

sys.path.insert(0, str(RAG_DIR))   # for importing runner helpers

# ── Model selection ────────────────────────────────────────────────────────────
# Change this to switch the API model for a new study run.
# Labels and output folder (analytics/[MODEL]Permutations/) update automatically.

MODEL = "haiku"   # e.g. "haiku", "sonnet", "opus"

# ── Batch definitions ─────────────────────────────────────────────────────────

BATCHES = [
    {"label": f"{MODEL}-reviewer",  "GENERATE_PROVIDER": "local", "REVIEW_PROVIDER": "api"},
    {"label": f"{MODEL}-generator", "GENERATE_PROVIDER": "api",   "REVIEW_PROVIDER": "local"},
    {"label": f"{MODEL}-both",      "GENERATE_PROVIDER": "api",   "REVIEW_PROVIDER": "api"},
]

DIFFICULTIES = [
    {"DIFFICULTY_TARGET": "easy",   "TOP_K": "6"},
    {"DIFFICULTY_TARGET": "medium", "TOP_K": "6"},
    {"DIFFICULTY_TARGET": "hard",   "TOP_K": "12"},
]

# ── Config helpers (mirrors interactive_run.py — avoids import side-effects) ──

CONFIG_KEYS = [
    "RAG_ROOT", "DOMAIN_DIR", "N_ITEMS", "DB_DSN", "DOCKER_CONTAINER",
    "LM_URL", "EMBED_MODEL", "CONTEXT_MODEL", "GENERATOR_MODEL", "REVIEW_MODEL",
    "API_PROVIDER", "API_MODEL", "INGEST_PROVIDER", "GENERATE_PROVIDER",
    "REVIEW_PROVIDER", "INGEST_DELAY_SECONDS", "DIFFICULTY_TARGET",
    "LMSTUDIO_LOGPATH", "CHECKPOINT_CHUNKS", "CHECKPOINT_ITEMS", "CHECKPOINT_REVIEW",
]


def load_config() -> dict:
    cfg = {}
    if not CONFIG_ENV.exists():
        return cfg
    for line in CONFIG_ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            cfg[k.strip()] = v.strip()
    return cfg


def save_config(cfg: dict) -> None:
    lines = [f"{k}={cfg.get(k, '')}" for k in CONFIG_KEYS]
    CONFIG_ENV.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_ENV.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _masked_input(prompt: str) -> str:
    if sys.platform == "win32":
        import msvcrt
        sys.stdout.write(prompt)
        sys.stdout.flush()
        chars = []
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            elif ch == "\x08":
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":
                raise KeyboardInterrupt
            else:
                chars.append(ch)
                sys.stdout.write("*")
                sys.stdout.flush()
        return "".join(chars)
    else:
        import getpass
        return getpass.getpass(prompt)


# ── Subprocess helpers ────────────────────────────────────────────────────────

def _run_tee(cmd: list, log_path: Path, env: dict) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as lf:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=env, text=True, encoding="utf-8", errors="replace",
        )
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            lf.write(line)
        proc.wait()
    return proc.returncode


def _capture_docker_logs(container: str, dest: Path) -> None:
    if not container:
        return
    try:
        r = subprocess.run(
            ["docker", "logs", "--tail", "5000", container],
            capture_output=True, text=True, timeout=30,
        )
        dest.write_text(r.stdout + r.stderr, encoding="utf-8")
    except Exception as e:
        dest.write_text(f"docker logs capture failed: {e}\n", encoding="utf-8")


def _capture_lmstudio_logs(log_path_str: str, dest: Path) -> None:
    src = Path(log_path_str) if log_path_str else None
    if not src or not src.exists():
        return
    try:
        lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
        dest.write_text("\n".join(lines[-5000:]), encoding="utf-8")
    except Exception as e:
        dest.write_text(f"LM Studio log capture failed: {e}\n", encoding="utf-8")


def _write_run_info(path: Path, cfg: dict, run_id: str, extra: dict = None) -> None:
    lines = [f"RUN_ID={run_id}"]
    for k in CONFIG_KEYS:
        lines.append(f"{k}={cfg.get(k, '')}")
    if extra:
        for k, v in extra.items():
            lines.append(f"{k}={v}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── Single run ────────────────────────────────────────────────────────────────

def run_one(cfg: dict, batch_label: str, difficulty: str, top_k: str) -> dict:
    """Run cli.py generate for one difficulty. Returns info dict."""
    run_id  = _utc_now()
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    log_dir = RUNS_DIR / f"logs_{run_id}"
    log_dir.mkdir(parents=True, exist_ok=True)

    env = {**os.environ}
    for k, v in cfg.items():
        if v:
            env[k] = v
    env["RUN_ID"]          = run_id
    env["LOG_DIR"]         = str(log_dir)
    env["OUT_DIR"]         = str(log_dir)
    env["DIFFICULTY_TARGET"] = difficulty
    env["TOP_K"]           = top_k
    env["CONDITION_LABEL"] = batch_label

    _write_run_info(log_dir / "run_info.txt", {**cfg, "TOP_K": top_k}, run_id,
                    {"BATCH_LABEL": batch_label, "RUN_START": _utc_iso()})

    cmd = [
        sys.executable, str(CLI_PY), "generate",
        "--no-checkpoint-items", "--no-checkpoint-review",
    ]

    banner = f"\n{'='*60}\n  BATCH: {batch_label}  |  DIFFICULTY: {difficulty}  |  TOP_K: {top_k}\n  RUN_ID: {run_id}\n{'='*60}\n"
    print(banner)

    t0 = time.perf_counter()
    rc = _run_tee(cmd, log_dir / "console_generate.txt", env)
    elapsed = time.perf_counter() - t0

    h, rem = divmod(int(elapsed), 3600)
    m, s   = divmod(rem, 60)
    duration = f"{h}h {m}m {s}s"

    _write_run_info(log_dir / "run_info.txt", {**cfg, "TOP_K": top_k}, run_id, {
        "BATCH_LABEL": batch_label,
        "RUN_END": _utc_iso(),
        "RUN_DURATION": duration,
        "EXIT_CODE": str(rc),
    })

    _capture_docker_logs(cfg.get("DOCKER_CONTAINER", ""), log_dir / f"docker_{cfg.get('DOCKER_CONTAINER','pgvector17')}.log")
    _capture_lmstudio_logs(cfg.get("LMSTUDIO_LOGPATH", ""), log_dir / "lmstudio.log")

    print(f"\n  Finished: {_utc_iso()}  |  Duration: {duration}  |  Exit: {rc}\n")
    return {"run_id": run_id, "log_dir": log_dir, "rc": rc, "duration": duration}


# ── Post-batch: move, viz, commit ─────────────────────────────────────────────

def _batch_dest(batch_label: str, corpus: str) -> Path:
    """Returns the archive folder for a batch run.

    local-local  → analytics/{corpus}_local-local/
    model-*      → analytics/{corpus}_{MODEL}Permutations/{corpus}_{batch_label}/
    """
    if batch_label == "local-local":
        return SCRIPT_DIR / f"{corpus}_local-local"
    model_dir = SCRIPT_DIR / f"{corpus}_{MODEL}Permutations"
    model_dir.mkdir(exist_ok=True)
    return model_dir / f"{corpus}_{batch_label}"


def post_batch(batch_label: str, corpus: str) -> None:
    dest = _batch_dest(batch_label, corpus)
    rel  = dest.relative_to(SCRIPT_DIR.parent)

    print(f"\n[post-batch] Moving runs/ -> {rel}/")
    if dest.exists():
        print(f"  WARNING: {dest} already exists — merging into it")
    dest.mkdir(exist_ok=True)

    moved = 0
    for item in RUNS_DIR.iterdir():
        target = dest / item.name
        if target.exists():
            print(f"  skip (exists): {item.name}")
        else:
            shutil.move(str(item), str(target))
            moved += 1
    print(f"  Moved {moved} items")

    print(f"\n[post-batch] Running analyticsVizs.py on {rel}/")
    viz_rc = subprocess.run(
        [sys.executable, str(VIZ_PY), str(dest)],
        cwd=str(SCRIPT_DIR),
    ).returncode
    if viz_rc != 0:
        print(f"  WARNING: analyticsVizs.py returned {viz_rc}")

    print(f"\n[post-batch] Committing {rel}/")
    subprocess.run(["git", "add", str(dest)], cwd=str(REPO_DIR))
    subprocess.run([
        "git", "commit", "-m",
        f"add batch {batch_label}: easy/medium/hard x50 runs + viz snapshot\n\nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>",
    ], cwd=str(REPO_DIR))


# ── Post-all: merge ───────────────────────────────────────────────────────────

def post_all() -> None:
    merge_py = SCRIPT_DIR / "merge_runs.py"
    if not merge_py.exists():
        print("\n[post-all] merge_runs.py not found — skipping merge")
        return

    print("\n[post-all] Running merge_runs.py")
    rc = subprocess.run([sys.executable, str(merge_py)], cwd=str(SCRIPT_DIR)).returncode
    if rc != 0:
        print(f"  WARNING: merge_runs.py returned {rc}")
        return

    print("\n[post-all] Committing merged master")
    subprocess.run(["git", "add", "analytics/merged_master.xlsx",
                    f"analytics/example1_{MODEL}Permutations/"], cwd=str(REPO_DIR))
    subprocess.run([
        "git", "commit", "-m",
        "add merged_master.xlsx and merged viz across all 4 conditions\n\nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>",
    ], cwd=str(REPO_DIR))


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Unattended domainRag batch runner")
    parser.add_argument("--start-batch", default=None,
                        help="Resume from this batch label (e.g. haiku-generator)")
    args = parser.parse_args()

    print("\ndomainRag Batch Runner — Comparative Study")
    print(f"  Repo:     {REPO_DIR}")
    print(f"  RAG dir:  {RAG_DIR}")
    print(f"  Batches:  {[b['label'] for b in BATCHES]}")

    # API key — needed for any batch that uses api provider
    api_key = os.environ.get("LLM_API_KEY", "")
    if not api_key:
        api_key = _masked_input("\nLLM API key (not saved to disk): ")
        if api_key:
            os.environ["LLM_API_KEY"] = api_key
        else:
            print("No API key provided — runs requiring api provider will fail.")

    # Determine start index
    start_idx = 0
    if args.start_batch:
        labels = [b["label"] for b in BATCHES]
        if args.start_batch in labels:
            start_idx = labels.index(args.start_batch)
        else:
            print(f"Unknown batch '{args.start_batch}'. Valid: {labels}")
            sys.exit(1)

    cfg = load_config()

    # Derive corpus name from DOMAIN_DIR basename (e.g. "example1", "clientA")
    corpus = Path(cfg.get("DOMAIN_DIR", "unknown")).name or "unknown"
    print(f"  Corpus:   {corpus}  (from DOMAIN_DIR basename)")

    for batch in BATCHES[start_idx:]:
        label = batch["label"]

        # Skip if already done
        dest = _batch_dest(label, corpus)
        if dest.exists():
            existing = list(dest.glob("run_*.xlsx"))
            if len(existing) >= 3:
                print(f"\n[skip] {dest.relative_to(SCRIPT_DIR.parent)}/ already has {len(existing)} run files — skipping batch")
                continue

        print(f"\n{'#'*60}")
        print(f"# STARTING BATCH: {label}  (corpus: {corpus})")
        print(f"# GENERATE_PROVIDER={batch['GENERATE_PROVIDER']}  REVIEW_PROVIDER={batch['REVIEW_PROVIDER']}")
        print(f"{'#'*60}")

        # Update config for this batch
        cfg["GENERATE_PROVIDER"] = batch["GENERATE_PROVIDER"]
        cfg["REVIEW_PROVIDER"]   = batch["REVIEW_PROVIDER"]
        save_config(cfg)

        results = []
        for diff in DIFFICULTIES:
            info = run_one(cfg, label, diff["DIFFICULTY_TARGET"], diff["TOP_K"])
            results.append(info)
            if info["rc"] != 0:
                print(f"\n  ERROR: run exited {info['rc']} — continuing to next difficulty")

        print(f"\n[batch {label}] All 3 difficulties complete:")
        for r, d in zip(results, DIFFICULTIES):
            status = "OK" if r["rc"] == 0 else f"ERROR({r['rc']})"
            print(f"  {d['DIFFICULTY_TARGET']:8s}  {r['run_id']}  {r['duration']}  {status}")

        post_batch(label, corpus)

    post_all()

    print("\n" + "="*60)
    print("All batches complete.")
    print("Required next step: dual human review must be completed before final analytics.")
    print("Use: python analytics\\human_review_cycle.py --bootstrap")
    print("Then queue both agents with: python analytics\\human_review_cycle.py --queue-both")
    print("Check both lanes with: python analytics\\human_review_cycle.py --status")
    print("Validate the gate with: python analytics\\human_review_cycle.py --require-complete")
    print("="*60)


if __name__ == "__main__":
    main()
