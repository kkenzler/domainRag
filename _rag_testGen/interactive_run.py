#!/usr/bin/env python3
"""runner.py — Cross-platform launcher for RAG TestGen.

Replaces the orchestration logic formerly in _run_testGen.bat.
Called by thin platform shims (_run_testGen.bat / _run_testGen.sh).

Responsibilities:
  - Load and save config.env
  - Prompt user: update settings? show current values
  - Prompt user: run mode (F / I / G / B)
  - Generate RUN_ID (UTC timestamp)
  - Create runs/logs_RUNID/ directory
  - Set environment variables for subprocess
  - Call cli.py via subprocess, streaming stdout to console + log file
  - Capture docker logs and LM Studio logs into run folder
  - Write run_info.txt with config + timing
  - Ask "Run again?" loop
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Config persistence
# ---------------------------------------------------------------------------

CONFIG_KEYS = [
    "RAG_ROOT",
    "DOMAIN_DIR",
    "N_ITEMS",
    "DB_DSN",
    "DOCKER_CONTAINER",
    "LM_URL",
    "EMBED_MODEL",
    "CONTEXT_MODEL",
    "GENERATOR_MODEL",
    "REVIEW_MODEL",
    "API_PROVIDER",
    "API_MODEL",
    "INGEST_PROVIDER",
    "GENERATE_PROVIDER",
    "REVIEW_PROVIDER",
    "INGEST_DELAY_SECONDS",
    "DIFFICULTY_TARGET",
    "LMSTUDIO_LOGPATH",
    "CHECKPOINT_CHUNKS",
    "CHECKPOINT_ITEMS",
    "CHECKPOINT_REVIEW",
]
CONFIG_KEYS_SENSITIVE = ["LLM_API_KEY"]  # loaded from env only, never written to config.env

CONFIG_LABELS = {
    "RAG_ROOT":             "Program folder (contains .py files)",
    "DOMAIN_DIR":           "Domain folder (subject matter documents)",
    "N_ITEMS":              "Number of items to generate",
    "DB_DSN":               "Postgres DSN",
    "DOCKER_CONTAINER":     "Docker container name (for log capture)",
    "LM_URL":               "LM Studio URL",
    "EMBED_MODEL":          "LM Studio embedding model name",
    "CONTEXT_MODEL":        "LM Studio context model (for local text extraction of PPTX/DOCX)",
    "GENERATOR_MODEL":      "LM Studio generator model (generates exam items)",
    "REVIEW_MODEL":         "LM Studio review model (evaluates items; can match generator)",
    "API_PROVIDER":         "API provider (anthropic / openai / gemini)",
    "API_MODEL": (
        "API model name\n"
        "  anthropic: claude-haiku-4-5-20251001 | claude-sonnet-4-6-20250514\n"
        "  openai:    gpt-4o-mini | gpt-4o\n"
        "  gemini:    gemini-1.5-flash | gemini-1.5-pro"
    ),
    "INGEST_PROVIDER":      "Ingest provider: local or api",
    "GENERATE_PROVIDER":    "Generate provider: local or api",
    "REVIEW_PROVIDER":      "Review provider: local or api",
    "INGEST_DELAY_SECONDS": "Seconds to wait between documents during ingest (helps avoid API rate limits)",
    "DIFFICULTY_TARGET":    "Target difficulty for generated items: easy | medium | hard | any",
    "LMSTUDIO_LOGPATH":     "LM Studio log file path",
    "CHECKPOINT_CHUNKS":    "Pause to review knowledge chunks? (true/false)",
    "CHECKPOINT_ITEMS":     "Pause to review generated items? (true/false)",
    "CHECKPOINT_REVIEW":    "Pause to review flagged items? (true/false)",
}


DEFAULTS = {
    "N_ITEMS":              "5",
    "DB_DSN":               "postgresql://username:password@localhost:5435/your_database",
    "LM_URL":               "http://localhost:1234",
    "DOCKER_CONTAINER":     "pgvector17",
    "API_PROVIDER":         "",
    "API_MODEL":            "",
    "INGEST_PROVIDER":      "local",
    "GENERATE_PROVIDER":    "local",
    "REVIEW_PROVIDER":      "local",
    "INGEST_DELAY_SECONDS": "10",
    "CHECKPOINT_CHUNKS":    "true",
    "CHECKPOINT_ITEMS":     "true",
    "CHECKPOINT_REVIEW":    "true",
}

if platform.system() == "Windows":
    DEFAULTS["LMSTUDIO_LOGPATH"] = str(
        Path(os.environ.get("APPDATA", "C:\\Users\\user\\AppData\\Roaming"))
        / "LM Studio" / "logs" / "main.log"
    )
else:
    DEFAULTS["LMSTUDIO_LOGPATH"] = str(
        Path.home() / "Library" / "Logs" / "LM Studio" / "main.log"
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _legacy_config_env(rag_root: Path) -> Path:
    return rag_root / "config.env"


def _default_config_env() -> Path:
    return Path.home() / "secrets" / "domainRag" / "config.env"


def _default_run_root() -> Path:
    return Path.home() / "secrets" / "domainRag" / "runs"


def _find_secrets_config_candidate(default_path: Path) -> Path:
    if default_path.exists():
        return default_path

    parent = default_path.parent
    if not parent.exists():
        return default_path

    matches = sorted(
        [
            candidate for candidate in parent.iterdir()
            if candidate.is_file() and candidate.name.startswith("config.env")
        ],
        key=lambda candidate: candidate.stat().st_mtime,
        reverse=True,
    )
    if len(matches) == 1:
        return matches[0]
    return default_path


def _find_config_env(rag_root: Path) -> Path:
    override = os.environ.get("DOMAINRAG_CONFIG_ENV", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return _find_secrets_config_candidate(_default_config_env())


def load_config_env(path: Path) -> dict[str, str]:
    """Loads KEY=VALUE pairs from config.env into a dict."""
    cfg: dict[str, str] = {}
    if not path.exists():
        legacy = _legacy_config_env(Path(__file__).resolve().parent)
        if legacy.exists() and legacy != path:
            path = legacy
        else:
            return cfg
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            cfg[k.strip()] = v.strip()
    return cfg


def save_config_env(path: Path, values: dict[str, str]) -> None:
    """Writes KEY=VALUE pairs to config.env. Never writes sensitive keys."""
    lines = []
    for k in CONFIG_KEYS:
        v = values.get(k, "")
        lines.append(f"{k}={v}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _prompt(label: str, current: str, secret: bool = False) -> str:
    """Prompts user for a new value; returns current if user presses Enter."""
    print(f"\n  {label}")
    print(f"  Current:  {'[hidden]' if secret else current}")
    try:
        if secret:
            val = getpass.getpass("  New value (Enter to keep): ")
        else:
            val = input("  New value (Enter to keep): ")
    except (EOFError, KeyboardInterrupt):
        return current
    return val.strip() if val.strip() else current


def _masked_input(prompt):
    """Shows * for each character on Windows; falls back to getpass on Mac/Linux."""
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
            elif ch == "\x08":  # backspace
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":  # ctrl+c
                raise KeyboardInterrupt
            else:
                chars.append(ch)
                sys.stdout.write("*")
                sys.stdout.flush()
        return "".join(chars)
    else:
        import getpass
        return getpass.getpass(prompt)


def configure(values: dict[str, str], rag_root: Path) -> dict[str, str]:
    """Interactive settings update. Returns updated values dict."""
    print("\nEnter new values or press Enter to keep current.\n")

    updated = dict(values)

    # RAG_ROOT first — affects config.env path
    new_root = _prompt(CONFIG_LABELS["RAG_ROOT"], updated.get("RAG_ROOT", str(rag_root)))
    updated["RAG_ROOT"] = new_root

    for key in CONFIG_KEYS:
        if key == "RAG_ROOT":
            continue
        current = updated.get(key, DEFAULTS.get(key, ""))
        updated[key] = _prompt(CONFIG_LABELS.get(key, key), current)

    # Sensitive: LLM_API_KEY
    # Prompt if any step routes to an API provider
    api_prov = updated.get("API_PROVIDER", "").strip().lower()
    ingest_p = updated.get("INGEST_PROVIDER", "local").strip().lower()
    generate_p = updated.get("GENERATE_PROVIDER", "local").strip().lower()
    review_p = updated.get("REVIEW_PROVIDER", "local").strip().lower()
    needs_key = bool(api_prov) and (ingest_p == "api" or generate_p == "api" or review_p == "api")
    current_key = os.environ.get("LLM_API_KEY", "")
    if needs_key or not current_key:
        print("")
        new_key = _masked_input("  LLM API key (not saved to config.env)\n  Current: %s\n  New value (Enter to keep): " % ("[set]" if current_key else "[not set]"))
        if new_key and new_key.strip():
            os.environ["LLM_API_KEY"] = new_key.strip()
    else:
        print("\n  LLM API key: [not required for lmstudio]")

    return updated


# ---------------------------------------------------------------------------
# Subprocess runner with tee
# ---------------------------------------------------------------------------

def _run_tee(cmd: list[str], log_path: Path, env: dict[str, str]) -> int:
    """Runs cmd, streaming stdout to both console and log_path."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as log_f:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=None,   # inherit: goes direct to terminal so \r progress bars work
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            log_f.write(line)
        proc.wait()
    return proc.returncode


# ---------------------------------------------------------------------------
# Log capture helpers
# ---------------------------------------------------------------------------

def _capture_docker_logs(container: str, dest: Path) -> None:
    if not container:
        return
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", "5000", container],
            capture_output=True, text=True, timeout=30,
        )
        dest.write_text(result.stdout + result.stderr, encoding="utf-8")
    except Exception as e:
        dest.write_text(f"docker logs capture failed: {e}\n", encoding="utf-8")


def _capture_lmstudio_logs(log_path_str: str, dest: Path) -> None:
    if not log_path_str:
        return
    src = Path(log_path_str)
    if not src.exists():
        return
    try:
        # Read last 5000 lines
        lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
        dest.write_text("\n".join(lines[-5000:]), encoding="utf-8")
    except Exception as e:
        dest.write_text(f"LM Studio log capture failed: {e}\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def _build_env(values: dict[str, str], log_dir: Path, run_id: str) -> dict[str, str]:
    """Builds the subprocess environment from current os.environ + config values."""
    env = dict(os.environ)
    for k, v in values.items():
        if v:
            env[k] = v
    env["RUN_ID"] = run_id
    env["LOG_DIR"] = str(log_dir)
    # Never inherit LLM_API_KEY from config — only from os.environ (set in configure())
    # It's already in env if the user entered it above
    return env


def _write_run_info(path: Path, values: dict[str, str], run_id: str, extra: dict | None = None) -> None:
    lines = [f"RUN_ID={run_id}"]
    for k in CONFIG_KEYS:
        v = values.get(k, "")
        lines.append(f"{k}={v}")
    if extra:
        for k, v in extra.items():
            lines.append(f"{k}={v}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Q mode — SQL agent chat (corpus exploration)
# ---------------------------------------------------------------------------

_SCHEMA_Q = """
Tables in this PostgreSQL database:

rag_chunks (
    id          BIGSERIAL PRIMARY KEY,
    doc_path    TEXT NOT NULL,        -- file path/name of source document
    doc_sha256  TEXT NOT NULL,        -- SHA-256 hash of source file
    chunk_index INT NOT NULL,         -- 0-based order within document
    chunk_text  TEXT NOT NULL,        -- extracted knowledge chunk text
    meta        JSONB NOT NULL,       -- arbitrary metadata (page numbers, etc.)
    created_at  TIMESTAMPTZ,
    updated_at  TIMESTAMPTZ
)

rag_meta (
    k           TEXT PRIMARY KEY,     -- metadata key (e.g. embedding_dim, corpus_label, ingest_date)
    v           TEXT NOT NULL,        -- metadata value
    updated_at  TIMESTAMPTZ
)

Useful query patterns:
- Count all chunks:            SELECT COUNT(*) AS total FROM rag_chunks
- List source documents:       SELECT DISTINCT doc_path FROM rag_chunks ORDER BY doc_path
- Chunks per document:         SELECT doc_path, COUNT(*) AS chunk_count FROM rag_chunks GROUP BY doc_path ORDER BY chunk_count DESC
- Search chunk text:           SELECT id, doc_path, chunk_index, chunk_text FROM rag_chunks WHERE chunk_text ILIKE '%keyword%' LIMIT 20
- Show all corpus metadata:    SELECT k, v FROM rag_meta ORDER BY k
- Longest chunks:              SELECT id, doc_path, chunk_index, LENGTH(chunk_text) AS chars FROM rag_chunks ORDER BY chars DESC LIMIT 20
- Chunks from one document:    SELECT chunk_index, chunk_text FROM rag_chunks WHERE doc_path ILIKE '%filename%' ORDER BY chunk_index
""".strip()

_SQL_GEN_SYSTEM_Q = f"""You are a PostgreSQL query generator for a RAG (Retrieval-Augmented Generation) corpus database.

DATABASE SCHEMA:
{_SCHEMA_Q}

Your job: given a user question about the corpus, generate a SQL SELECT query.

ALWAYS respond with exactly one JSON object — no markdown, no explanation, no extra text.

If answerable with SQL:
{{"sql": "SELECT ..."}}

If the question is off-topic or unanswerable:
{{"sql": null, "reply": "brief explanation"}}

SQL RULES:
- Only SELECT — never INSERT, UPDATE, DELETE, DROP, or DDL
- Always use LIMIT 100 unless the user asks for more, or the query is a COUNT/aggregate
- For text searches use ILIKE with % on both sides: chunk_text ILIKE '%keyword%'
- For doc_path searches: doc_path ILIKE '%filename%'
- Never use SELECT * — always name specific columns
- Prefer informative column aliases: LENGTH(chunk_text) AS chars
""".strip()

_FORMATTER_SYSTEM_Q = """You are a helpful assistant summarizing database query results about a RAG corpus.

You will receive a user question and the SQL result.

RULES:
- Be concise and direct.
- Never invent information not present in the data.
- If the result is a single number or small list, state it plainly.
- If there are many rows, give a brief summary rather than listing all of them.
- If the data is empty, say so.
""".strip()


def _call_lm(lm_url: str, model: str, system: str, user: str, timeout: int = 60) -> str:
    """Single LM Studio chat completion call. Returns content string."""
    import requests as _req
    url = lm_url.rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "temperature": 0.1,
        "stream": False,
    }
    resp = _req.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _parse_sql_response(raw: str) -> dict:
    """Parse SQL gen JSON response. Returns dict with 'sql' key (may be None)."""
    import json as _json, re as _re
    cleaned = _re.sub(r"```(?:json)?|```", "", raw).strip()
    try:
        return _json.loads(cleaned)
    except Exception:
        m = _re.search(r'\{.*\}', cleaned, _re.DOTALL)
        if m:
            try:
                return _json.loads(m.group())
            except Exception:
                pass
    return {"sql": None, "reply": "Could not parse model response."}


def _execute_sql_q(conn, sql: str) -> tuple[list[dict], str]:
    """Execute a SELECT query against the corpus DB. Returns (rows, error_msg)."""
    first_word = sql.strip().split()[0].upper() if sql.strip() else ""
    if first_word != "SELECT":
        return [], f"Rejected: only SELECT is allowed (got {first_word!r})"
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [d.name for d in cur.description] if cur.description else []
            rows = [dict(zip(cols, row)) for row in (cur.fetchall() or [])]
        return rows, ""
    except Exception as e:
        return [], str(e)


def _format_rows_q(rows: list[dict], max_rows: int = 50) -> str:
    """Format query result rows as a plain-text table."""
    if not rows:
        return "(no rows)"
    cols = list(rows[0].keys())
    lines = ["  ".join(str(c) for c in cols)]
    lines.append("-" * min(100, sum(len(str(c)) + 2 for c in cols)))
    for r in rows[:max_rows]:
        lines.append("  ".join(str(r.get(c, "")) for c in cols))
    if len(rows) > max_rows:
        lines.append(f"... ({len(rows) - max_rows} more rows not shown)")
    return "\n".join(lines)


def _run_chat_mode(values: dict[str, str]) -> None:
    """Interactive two-call SQL agent chat loop for corpus exploration."""
    import psycopg as _pg

    dsn   = values.get("DB_DSN", "")
    lm_url = values.get("LM_URL", "http://localhost:1234")
    model  = values.get("GENERATOR_MODEL", "") or values.get("CONTEXT_MODEL", "")

    if not dsn:
        print("\nERROR: DB_DSN not set. Update settings (Y) and configure it.")
        return
    if not model:
        print("\nERROR: GENERATOR_MODEL not set. Update settings (Y) and configure it.")
        return

    print(f"\nConnecting to {dsn} ...")
    try:
        conn = _pg.connect(dsn)
    except Exception as e:
        print(f"ERROR: Could not connect: {e}")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM rag_chunks;")
            n_chunks = int((cur.fetchone() or [0])[0])
        print(f"Connected. {n_chunks} chunk(s) in corpus.")
    except Exception as e:
        print(f"WARNING: Could not query rag_chunks ({e}). DB may be empty.")
        n_chunks = 0

    print(f"\nCorpus Chat  |  model: {model}")
    print(f"  exit / back = return to menu   Ctrl+C = quit\n")

    while True:
        try:
            question = input("Q> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q", "back"}:
            break

        # ── Call 1: generate SQL ──────────────────────────────────────────
        print("  [generating SQL...]", end="", flush=True)
        try:
            raw1 = _call_lm(lm_url, model, _SQL_GEN_SYSTEM_Q, question, timeout=60)
            parsed = _parse_sql_response(raw1)
        except Exception as e:
            print(f"\r  [error calling LM Studio: {e}]\n")
            continue

        print("\r" + " " * 25 + "\r", end="", flush=True)

        sql = parsed.get("sql")
        if not sql:
            reply = parsed.get("reply", "I can't answer that with this database.")
            print(f"  {reply}\n")
            continue

        print(f"  SQL: {sql}")

        # ── Execute ───────────────────────────────────────────────────────
        rows, err = _execute_sql_q(conn, sql)
        if err:
            print(f"  SQL error: {err}\n")
            continue
        if not rows:
            print("  No results.\n")
            continue

        rows_text = _format_rows_q(rows)

        # ── Call 2: format result ─────────────────────────────────────────
        user_prompt = (
            f"Question: {question}\n\n"
            f"SQL RESULT ({len(rows)} row(s)):\n{rows_text}"
        )
        try:
            reply = _call_lm(lm_url, model, _FORMATTER_SYSTEM_Q, user_prompt, timeout=90)
            print(f"\n{reply}\n")
        except Exception:
            print(f"\n{rows_text}\n")

    conn.close()


# ---------------------------------------------------------------------------
# Multi-domain batch helpers
# ---------------------------------------------------------------------------

def _dsn_with_db(base_dsn: str, db_name: str) -> str:
    """Replace the database name in a DSN."""
    import re as _re
    return _re.sub(r"/[^/]*$", f"/{db_name}", base_dsn)


def _folder_to_db_name(folder_name: str) -> str:
    """Derive a safe Postgres DB name from a folder name."""
    import re as _re
    safe = _re.sub(r"[^a-z0-9]", "_", folder_name.lower()).strip("_")
    return f"{safe}_ragtestdb"


def _ensure_db(dsn: str, db_name: str) -> bool:
    """Create DB + enable pgvector if the DB doesn't already exist."""
    try:
        import psycopg as _pg
    except ImportError:
        print("  [db] ERROR: psycopg not installed.")
        return False

    maintenance_dsn = _dsn_with_db(dsn, "postgres")
    try:
        conn = _pg.connect(maintenance_dsn, autocommit=True)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cur.fetchone():
                print(f"  [db] Exists: {db_name}")
            else:
                cur.execute(f'CREATE DATABASE "{db_name}"')
                print(f"  [db] Created: {db_name}")
        conn.close()
    except Exception as e:
        print(f"  [db] ERROR connecting to maintenance DB: {e}")
        return False

    try:
        conn = _pg.connect(dsn)
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        conn.close()
        print(f"  [db] pgvector ready.")
    except Exception as e:
        print(f"  [db] WARNING: could not enable pgvector: {e}")

    return True


def _run_multi_domain(values: dict[str, str], rag_root_val: Path, cli_path: Path) -> None:
    """Run ingest (or full pipeline) across multiple domain/DB pairs."""
    _W2 = 54

    # ── Choose mode ───────────────────────────────────────────────────────
    print()
    print("  Mode to run for each domain:")
    print("    I  Ingest only")
    print("    P  Pipeline  (ingest + generate)")
    print("    F  Full      (ingest + generate + analytics)")
    print("    Enter = cancel")
    try:
        mode = input("  > ").strip().upper()
    except (EOFError, KeyboardInterrupt):
        return
    if mode not in {"I", "P", "F"}:
        print("  Cancelled.")
        return

    # ── Collect domain entries ────────────────────────────────────────────
    base_dsn = values.get("DB_DSN", "")
    print()
    print("  Enter domain folders one at a time.")
    print("  For each, confirm or override the suggested DB name.")
    print("  Empty folder path = done.\n")

    entries: list[tuple[Path, str]] = []  # (domain_dir, dsn)
    idx = 1
    while True:
        try:
            raw = input(f"  Folder {idx}: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            break
        folder = Path(raw)
        if not folder.exists():
            print(f"  [!] Not found — skipping: {raw}")
            continue

        suggested_db = _folder_to_db_name(folder.name)
        suggested_dsn = _dsn_with_db(base_dsn, suggested_db)
        print(f"      DB suggestion: {suggested_db}")
        try:
            override = input(f"      DB name (Enter to accept): ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        db_name = override if override else suggested_db
        dsn = _dsn_with_db(base_dsn, db_name)
        entries.append((folder, dsn))
        print(f"      -> {folder.name}  |  {dsn}\n")
        idx += 1

    if not entries:
        print("  No domains entered.")
        return

    # ── Confirm ───────────────────────────────────────────────────────────
    print(f"\n  {len(entries)} domain(s) queued  |  mode: {mode}")
    for i, (d, dsn) in enumerate(entries, 1):
        print(f"    {i}.  {d.name}  ->  {dsn.split('/')[-1]}")
    try:
        confirm = input("\n  Proceed? (Y/N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return
    if confirm not in {"y", "yes"}:
        print("  Cancelled.")
        return

    # ── Run each domain ───────────────────────────────────────────────────
    run_id = _utc_now()
    log_dir_base = _default_run_root() / f"logs_{run_id}_multi"
    log_dir_base.mkdir(parents=True, exist_ok=True)

    results: list[tuple[str, int, str]] = []  # (folder_name, returncode, duration)

    _hdr(f"MULTI-DOMAIN  —  {len(entries)} domain(s)  |  mode: {mode}")
    print(f"  run_id  : {run_id}")
    print(f"  log dir : {log_dir_base}")

    for i, (domain_dir, dsn) in enumerate(entries, 1):
        _sub(f"Domain {i}/{len(entries)}  —  {domain_dir.name}")
        print(f"  path : {domain_dir}")
        print(f"  db   : {dsn.split('/')[-1]}")
        print()

        # Ensure DB + pgvector exist
        db_name = dsn.split("/")[-1]
        if not _ensure_db(dsn, db_name):
            print(f"  [!] Skipping — could not prepare DB.")
            results.append((domain_dir.name, -1, "skipped"))
            continue

        # Build env for this domain
        env = dict(os.environ)
        for k, v in values.items():
            if v:
                env[k] = v
        env["DOMAIN_DIR"] = str(domain_dir)
        env["DB_DSN"] = dsn
        env["RUN_ID"] = f"{run_id}_{i:02}"
        env["LOG_DIR"] = str(log_dir_base)

        # Build command
        if mode in {"P", "F"}:
            cmd = [sys.executable, str(cli_path), "pipeline", "--force-ingest", "--clear-first"]
        else:  # I
            cmd = [sys.executable, str(cli_path), "pipeline", "--force-ingest", "--clear-first", "--ingest-only"]

        for flag, env_key in [
            ("--no-checkpoint-chunks", "CHECKPOINT_CHUNKS"),
            ("--no-checkpoint-items", "CHECKPOINT_ITEMS"),
            ("--no-checkpoint-review", "CHECKPOINT_REVIEW"),
        ]:
            if values.get(env_key, "true").lower() in {"0", "false", "no", "n"}:
                if flag == "--no-checkpoint-chunks" and mode in {"P", "F", "I"}:
                    cmd.append(flag)
                elif flag in ("--no-checkpoint-items", "--no-checkpoint-review") and mode in {"P", "F"}:
                    cmd.append(flag)

        log_file = log_dir_base / f"{i:02}_{domain_dir.name}.txt"
        t0 = time.perf_counter()
        returncode = _run_tee(cmd, log_file, env)
        elapsed = time.perf_counter() - t0
        m_e, s_e = int(elapsed // 60), int(elapsed % 60)
        dur = f"{m_e}m {s_e}s"

        status = "OK" if returncode == 0 else f"FAILED (exit {returncode})"
        print(f"\n  [{i}/{len(entries)}] {domain_dir.name}: {status} — {dur}")
        results.append((domain_dir.name, returncode, dur))

        if mode == "F" and returncode == 0:
            _sub("ANALYTICS")
            print()
            _run_analytics(log_dir_base, rag_root_val)

    # ── Summary ───────────────────────────────────────────────────────────
    _hdr("MULTI-DOMAIN COMPLETE")
    for i, (name, rc, dur) in enumerate(results, 1):
        status = "OK" if rc == 0 else ("skipped" if rc == -1 else f"exit {rc}")
        print(f"  {i}.  {name:<30}  {status:<10}  {dur}")
    print(f"\n  log dir: {log_dir_base}")


# ---------------------------------------------------------------------------
# Analytics helpers
# ---------------------------------------------------------------------------

def _analytics_script(rag_root: Path) -> Path:
    return rag_root.parent / "analytics" / "analyticsVizs.py"


def _run_analytics(log_dir: Path, rag_root: Path) -> None:
    """Run analyticsVizs.py on a completed run's log directory."""
    script = _analytics_script(rag_root)
    if not script.exists():
        print(f"\n[analytics] analyticsVizs.py not found at {script} — skipping.")
        print("[analytics] (analytics/ is local-only; copy scripts there to enable viz)")
        return
    print(f"\n[analytics] Running viz on {log_dir.name} ...")
    result = subprocess.run([sys.executable, str(script), str(log_dir)])
    if result.returncode != 0:
        print(f"[analytics] Exited with code {result.returncode}")
    else:
        print(f"[analytics] Done.")


def _run_analytics_latest(rag_root: Path) -> None:
    """Find the most recent run and run analytics on it."""
    script = _analytics_script(rag_root)
    if not script.exists():
        print(f"\n[analytics] analyticsVizs.py not found at {script}")
        print("[analytics] (analytics/ is local-only; copy scripts there to enable viz)")
        return
    runs_dir = _default_run_root()
    candidates = sorted(runs_dir.glob("logs_*"), key=lambda p: p.name) if runs_dir.exists() else []
    if not candidates:
        print(f"\n[analytics] No run directories found in {runs_dir}. Run F or P first.")
        return
    latest = candidates[-1]
    print(f"\n[analytics] Most recent run: {latest.name}")
    _run_analytics(latest, rag_root)


_W = 54  # banner width

def _hdr(label: str) -> None:
    """Print a top-level ===== section banner."""
    inner = f"  {label}  "
    pad = max(0, _W - len(inner))
    left = pad // 2
    right = pad - left
    print(f"\n{'=' * _W}")
    print(f"{'=' * left}{inner}{'=' * right}")
    print(f"{'=' * _W}")


def _sub(label: str) -> None:
    """Print a -------- sub-section label."""
    dashes = max(4, _W - len(label) - 3)
    print(f"\n-------- {label} " + "-" * dashes)


def main() -> None:
    # Determine rag_root: the directory containing runner.py
    rag_root = Path(__file__).resolve().parent
    config_path = _find_config_env(rag_root)

    _hdr("RAG TestGen")
    print(f"  rag_root : {rag_root}")
    print(f"  config   : {config_path}")

    # Load persisted config, fill defaults
    values: dict[str, str] = {**DEFAULTS}
    values["RAG_ROOT"] = str(rag_root)
    persisted = load_config_env(config_path)
    values.update(persisted)

    _SEP = "=" * 52

    while True:
        print(f"\n{_SEP}")
        try:
            update = input("  Update settings?  Y = yes   X = quit   Enter = skip\n  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if update == "x":
            print("\nExiting.")
            break

        if update in {"y", "yes"}:
            values = configure(values, rag_root)
            save_config_env(config_path, values)
            print(f"\nSettings saved to {config_path}")
        else:
            # Even when skipping settings, ensure API key is set if needed
            api_prov = values.get("API_PROVIDER", "").strip().lower()
            ingest_p = values.get("INGEST_PROVIDER", "local").strip().lower()
            generate_p = values.get("GENERATE_PROVIDER", "local").strip().lower()
            review_p = values.get("REVIEW_PROVIDER", "local").strip().lower()
            needs_key = bool(api_prov) and (ingest_p == "api" or generate_p == "api" or review_p == "api")
            current_key = os.environ.get("LLM_API_KEY", "")
            if needs_key and not current_key:
                print("\n  API key required for API_PROVIDER=%s" % api_prov)
                new_key = _masked_input("  LLM API key (not saved to config.env)\n  New value: ")
                if new_key and new_key.strip():
                    os.environ["LLM_API_KEY"] = new_key.strip()

        print(f"\n{_SEP}")
        print("  Run mode\n")
        print("  ── Batch / Pipeline " + "─" * 31)
        print("  B  Batch run    generate (from db) + analytics")
        print("  P  Pipeline     ingest + generate")
        print("  F  Full         ingest + generate + analytics")
        print()
        print("  ── Step by step " + "─" * 35)
        print("  I  Ingest only  extract knowledge chunks, write XLSX")
        print("  G  Generate     use existing db chunks")
        print("  A  Analytics    viz on most recent run")
        print()
        print("  ── Tools " + "─" * 42)
        print("  Q  Query        interactive SQL chat, explore corpus db")
        print("  M  Multi-domain run pipeline across multiple domain/DB pairs")
        print()
        print("  Enter = back to settings   X = quit")
        print(_SEP)

        try:
            run_choice = input("  > ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not run_choice:
            continue  # back to settings prompt

        if run_choice == "X":
            print("\nExiting.")
            break

        if run_choice not in {"B", "F", "P", "I", "G", "A", "Q", "M"}:
            print("  Invalid choice. Try again.")
            continue

        if run_choice == "Q":
            _run_chat_mode(values)
            continue

        if run_choice == "M":
            rag_root_val_m = Path(values.get("RAG_ROOT", str(rag_root)))
            cli_path_m = rag_root_val_m / "cli.py"
            if not cli_path_m.exists():
                print(f"\nERROR: cli.py not found at {cli_path_m}")
                continue
            _run_multi_domain(values, rag_root_val_m, cli_path_m)
            continue

        # Validate required paths
        rag_root_val = Path(values.get("RAG_ROOT", str(rag_root)))
        cli_path = rag_root_val / "cli.py"
        if not cli_path.exists():
            print(f"\nERROR: cli.py not found at {cli_path}")
            print("Update RAG_ROOT in settings.")
            continue

        if run_choice == "A":
            _run_analytics_latest(rag_root_val)
            continue

        domain_dir = values.get("DOMAIN_DIR", "")
        if not domain_dir or not Path(domain_dir).exists():
            print(f"\nERROR: DOMAIN_DIR not found: {domain_dir}")
            continue

        run_id = _utc_now()
        log_dir = rag_root_val / "runs" / f"logs_{run_id}"
        log_dir.mkdir(parents=True, exist_ok=True)

        env = _build_env(values, log_dir, run_id)

        python = sys.executable
        cli = str(cli_path)

        if run_choice in {"F", "P"}:
            cmd = [python, cli, "pipeline", "--force-ingest", "--clear-first"]
            log_file = log_dir / "console_pipeline.txt"
        elif run_choice == "I":
            cmd = [python, cli, "pipeline", "--force-ingest", "--clear-first", "--ingest-only"]
            log_file = log_dir / "console_pipeline.txt"
        else:  # B or G
            cmd = [python, cli, "generate"]
            log_file = log_dir / "console_generate.txt"

        # Handle checkpoint flags from config
        for flag, env_key in [
            ("--no-checkpoint-chunks", "CHECKPOINT_CHUNKS"),
            ("--no-checkpoint-items", "CHECKPOINT_ITEMS"),
            ("--no-checkpoint-review", "CHECKPOINT_REVIEW"),
        ]:
            if values.get(env_key, "true").lower() in {"0", "false", "no", "n"}:
                if flag in ("--no-checkpoint-items", "--no-checkpoint-review"):
                    if run_choice in {"F", "P", "B", "G"}:
                        cmd.append(flag)
                elif flag == "--no-checkpoint-chunks":
                    if run_choice in {"F", "P", "I"}:
                        cmd.append(flag)

        _write_run_info(log_dir / "run_info.txt", values, run_id, {"RUN_START": _utc_iso()})

        _run_labels = {
            "F": "FULL  —  ingest + generate + analytics",
            "P": "PIPELINE  —  ingest + generate",
            "B": "BATCH  —  generate + analytics",
            "I": "INGEST ONLY",
            "G": "GENERATE ONLY",
        }
        _hdr(_run_labels.get(run_choice, run_choice))
        print(f"  RUN_ID  : {run_id}")
        print(f"  log dir : {log_dir}")
        print(f"  started : {_utc_iso()}")

        t0 = time.perf_counter()

        # Note: pipeline/generate handle checkpoints interactively themselves.
        # We can't tee + interact at the same time, so for checkpoint-enabled
        # runs we use direct subprocess (no tee) so stdin passes through.
        checkpoint_enabled = any(
            values.get(k, "true").lower() not in {"0", "false", "no", "n"}
            for k in ["CHECKPOINT_CHUNKS", "CHECKPOINT_ITEMS", "CHECKPOINT_REVIEW"]
        ) and run_choice in {"F", "P", "B", "G", "I"}

        if run_choice in {"F", "P", "I"}:
            _sub("INGEST")
        elif run_choice in {"B", "G"}:
            _sub("GENERATE")
        print()

        if checkpoint_enabled:
            # Direct run — stdin passes through for interactive checkpoints
            result = subprocess.run(cmd, env=env)
            returncode = result.returncode
            # Capture stdout separately after the fact is not possible here;
            # pipeline writes to stderr for progress, stdout for summaries.
            # For now, note this in run_info.
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"[interactive run — stdout not captured when checkpoints enabled]\n")
                f.write(f"returncode={returncode}\n")
        else:
            returncode = _run_tee(cmd, log_file, env)

        elapsed = time.perf_counter() - t0
        h = int(elapsed // 3600)
        m = int((elapsed % 3600) // 60)
        s = int(elapsed % 60)
        duration_str = f"{h}h {m}m {s}s"

        status = "DONE" if returncode == 0 else f"DONE  (exit {returncode})"
        _hdr(status)
        print(f"  finished : {_utc_iso()}")
        print(f"  duration : {duration_str}")
        print(f"  exit     : {returncode}")

        _write_run_info(
            log_dir / "run_info.txt", values, run_id,
            {"RUN_END": _utc_iso(), "RUN_DURATION": duration_str, "EXIT_CODE": str(returncode)},
        )

        # Capture external logs
        docker_container = values.get("DOCKER_CONTAINER", "")
        if docker_container:
            _capture_docker_logs(docker_container, log_dir / f"docker_{docker_container}.log")

        lmstudio_log = values.get("LMSTUDIO_LOGPATH", "")
        if lmstudio_log:
            _capture_lmstudio_logs(lmstudio_log, log_dir / "lmstudio.log")

        if run_choice in {"F", "B"} and returncode == 0:
            _sub("ANALYTICS")
            print()
            _run_analytics(log_dir, rag_root_val)

        try:
            again = input("\nRun again? (Y/N, default N): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if again not in {"y", "yes"}:
            break

    print("\nDone.")


if __name__ == "__main__":
    main()
