# domainRag — System Context

## What This Program Does

`_rag_testGen` is a Python pipeline that generates multiple-choice exam items grounded in domain
source material using a retrieval-augmented generation (RAG) architecture with a separate
critic/reviewer model. It ingests domain documents (PDF, PPTX, DOCX, TXT), extracts structured
knowledge chunks via a context model, embeds them into Postgres+pgvector, then uses a generator
LLM + reviewer LLM to produce structured MCQ items with quality scores. The system is designed
to answer two research questions: does a dual-model agentic RAG architecture produce measurably
higher-quality items than a single-model no-RAG baseline, and does agentic critique reduce human
review burden?

---

## Project Structure

```
_rag_testGen/
├── cli.py                  # Entrypoint; dispatches ingest / generate / baseline / pipeline subcommands
├── config.py               # Loads env vars into ResolvedConfig dataclass
├── pipeline.py             # Orchestrates ingest + generate phases; human-in-the-loop checkpoints; writes XLSX
├── ingest.py               # Loads docs, context model extracts knowledge chunks, embeds, upserts to pgvector
├── loaders.py              # Document loaders (PDF, PPTX, DOCX, TXT) + preprocess_text(); text extraction only
├── llm_client.py           # Unified LLM provider abstraction (lmstudio/openai/anthropic/gemini); text + vision
├── embed_lmstudio.py       # LM Studio /v1/embeddings client (embeddings remain local)
├── db_pgvector.py          # All Postgres/pgvector DB access (schema, upsert, search, snapshots)
├── text_utils.py           # Generator output cleaning, schema validation, reviewer hygiene
├── interactive_run.py               # Cross-platform launcher: config persistence, run mode, log capture, run-again loop
├── __init__.py             # Package marker
├── __main__.py             # Allows `python -m _rag_testGen`
├── _prompts/
│   ├── generator_system.txt
│   ├── generator_user.txt      # Contains {{CONTEXT}} placeholder
│   ├── reviewer_system.txt
│   ├── reviewer_user.txt       # Contains {{GEN_ITEM}} and {{CONTEXT}} placeholders
│   ├── context_system.txt      # Knowledge extraction instructions for context model
│   └── context_user.txt        # Contains {{DOCUMENT}} placeholder (text mode only)
├── runs/
│   └── logs_RUNID/
│       ├── console_pipeline.txt / console_generate.txt / console_baseline.txt
│       ├── run_info.txt
│       ├── run_RUNID.xlsx
│       ├── run_manifest_RUNID.json
│       ├── lmstudio.log
│       ├── llm_http.jsonl
│       └── docker_CONTAINERNAME.log
└── config.env              # Auto-written plain KEY=VALUE (no shell syntax)

_run_testGen.bat            # Windows thin shim — calls interactive_run.py
_run_testGen.sh             # Mac/Linux thin shim — calls interactive_run.py (chmod +x required)
```

---

## Launcher

Both `_run_testGen.bat` (Windows) and `_run_testGen.sh` (Mac/Linux) are thin shims that
simply call `python interactive_run.py` or `python3 interactive_run.py`. All orchestration logic lives in
`interactive_run.py`.

### `interactive_run.py`

- Loads and saves `config.env`
- Prompts user: update settings? (Y/N), shows current values
- Prompts user: run mode F / I / G / B
  - F = Full pipeline (ingest + generate, RAG mode)
  - I = Ingest only (extract knowledge chunks, write XLSX)
  - G = Generate only (use existing DB chunks, RAG mode)
  - B = Baseline (no-RAG, load docs directly)
- Generates RUN_ID (UTC timestamp)
- Creates `runs/logs_RUNID/` directory
- Sets environment variables for subprocess
- Calls `cli.py` via subprocess
- When checkpoints are disabled: tees stdout to console + log file
- When checkpoints are enabled: direct subprocess (stdin passes through for interactive prompts)
- Captures docker logs and LM Studio logs into run folder after completion
- Writes `run_info.txt` with config + timing
- Asks "Run again?" loop

---

## Pipeline Flow

```
_run_testGen.bat / _run_testGen.sh
  └── interactive_run.py
        └── cli.py  (pipeline / generate / ingest / baseline subcommand)
              ├── ingest phase:
              │     loaders.py → load_document()         [text extraction, all types]
              │     ingest.py → extract_knowledge_chunks()
              │       ├── PDFs: llm_client.py → call_llm_vision()
              │       │     lmstudio/openai/gemini: render pages → image_url blocks (batched)
              │       │     anthropic: raw PDF → document block (one call, native)
              │       └── PPTX/DOCX/TXT: llm_client.py → call_llm() [text mode]
              │     embed_lmstudio.py → embed_texts()
              │     db_pgvector.py → upsert_chunks()
              │     [CHECKPOINT 1] human reviews knowledge chunks (optional)
              │
              └── generate phase (per item):
                    db_pgvector.py → get_random_chunks() [seed]
                    embed_lmstudio.py → embed_texts() [seed embedding]
                    db_pgvector.py → similarity_search() [top-k retrieval]
                    llm_client.py → call_llm() [generator]
                    [CHECKPOINT 2] human reviews generated items (optional)
                    llm_client.py → call_llm() [reviewer]
                    [CHECKPOINT 3] human reviews flagged items (optional)
                    pipeline.py → write_run_xlsx()
```

---

## Key Modules

### `loaders.py`
- `load_document(path)` — dispatches by extension: `.pdf` → PyMuPDF + pypdf fallback,
  `.pptx` → python-pptx (text + speaker notes), `.docx` → python-docx, `.txt/.md` → plain read
- Returns `LoadedDoc(path, sha256, text, page_count)` — text extraction only, no chunking
- `preprocess_text(text, source_ext)` — normalizes whitespace, removes page number artifacts,
  de-hyphenates PDF line wraps, collapses repeated header/footer lines (freq ≥ 4),
  drops standalone integers (slide numbers), drops Wingdings 'z' artifacts
- `_is_spoken_math_transcript()` — detects and rejects audio transcript files with spoken math notation
- Note: PDF text extraction is used for identity/metadata only; knowledge extraction uses vision

### `ingest.py`
- `extract_knowledge_chunks(doc, cfg, ...)` — routes to vision or text based on file extension
  and LLM_PROVIDER; returns list of knowledge chunk strings
- `_extract_vision_lmstudio()` — renders PDF pages to base64 PNG, sends in batches of
  `vision_pages_per_batch` (default 4) to LM Studio vision endpoint
- `_extract_vision_anthropic()` — sends raw PDF bytes as native document block (one API call)
- `_split_knowledge_output()` — splits context model output (blank-line separated paragraphs)
  into individual chunks, merges short fragments, hard-splits overlong chunks
- `ingest_domain(cfg, prompts_dir)` — full ingest loop with batch embedding and upsert

### `llm_client.py`
- `call_llm(lm_url, model, system_prompt, user_prompt, ...)` — text-only call, all providers
- `call_llm_vision(lm_url, model, system_prompt, user_prompt, image_b64_list, pdf_path, ...)` —
  vision call; provider determines format:
  - lmstudio/openai/gemini: `image_url` blocks with base64 PNG data
  - anthropic: `document` block with raw PDF bytes (native PDF support, no rendering)
- `render_pdf_pages_b64(pdf_path, dpi)` — renders PDF pages to base64 PNG list (MuPDF warnings suppressed)
- `pdf_to_b64(pdf_path)` — raw PDF bytes as base64 (for Anthropic native PDF)
- All calls log to `runs/logs_RUNID/llm_http.jsonl` (provider, model, mode, elapsed_ms, token counts)
- `LLM_API_KEY` read from env only, never logged or written to config

### `embed_lmstudio.py`
- `embed_texts(cfg, texts)` — calls LM Studio `/v1/embeddings`
- Embeddings remain local regardless of LLM_PROVIDER setting

### `pipeline.py`
- Three human-in-the-loop checkpoints (all optional, controlled by config flags):
  - `_checkpoint_chunks()` — after ingest, review/edit/skip knowledge chunks before embedding
  - `_checkpoint_items()` — after generation, review/edit/skip items before reviewer
  - `_checkpoint_review()` — after review, override/correct flagged items
- `generate_from_db(cfg)` — RAG mode: retrieves top-k chunks, generates + reviews MCQ items
- `generate_baseline(cfg)` — baseline mode: loads docs directly, generates without pgvector
- `run_pipeline(cfg)` — orchestrates ingest + generate
- `write_run_xlsx()` — writes multi-sheet XLSX:
  Run Metadata, DB Snapshot, Chunk Preview, Items, Reviewer Decisions, Traceability, Quality Metrics
- Note: old context-rewrite-at-query-time agent removed; context model now runs at ingest time

### `config.py`
- `load_config_from_env()` — reads all settings from environment variables
- `ResolvedConfig` — frozen dataclass; `.with_overrides()` for CLI arg application
- Supports backward-compatible alias `SME_MODEL` → `GENERATOR_MODEL`
- New fields: `llm_provider`, `context_model`, `baseline_mode`, `checkpoint_chunks`,
  `checkpoint_items`, `checkpoint_review`

### `db_pgvector.py`
- Schema: `rag_chunks` (doc_path, doc_sha256, chunk_index, chunk_text, embedding vector(N), meta jsonb)
- Schema: `rag_meta` (k, v — stores embed_model, embedding_dim, source_root, context_model)
- `similarity_search()` — cosine distance via pgvector `<->` operator
- `get_db_snapshot_summary()` / `get_db_snapshot_per_doc()` — for XLSX DB Snapshot sheet

---

## Configuration (`config.env`)

Plain `KEY=VALUE` file, no shell syntax. Written by `interactive_run.py`. `LLM_API_KEY` is never
written here — entered at runtime via masked prompt, stored only in process environment.

```
RAG_ROOT=C:\Users\kadek\Documents\GitHub\KinaxisCapstone\_rag_testGen
DOMAIN_DIR=C:\Users\kadek\Documents\GitHub\KinaxisCapstone\example1
N_ITEMS=1
DB_DSN=postgresql://postgres:postgres@localhost:5435/kinaxis_ragtestdb
DOCKER_CONTAINER=pgvector17
LM_URL=http://localhost:1234
LLM_PROVIDER=lmstudio
EMBED_MODEL=text-embedding-nomic-embed-text-v1.5@q8_0
CONTEXT_MODEL=qwen/qwen2.5-vl-7b-instruct
GENERATOR_MODEL=qwen2.5-7b-instruct-uncensored
REVIEW_MODEL=qwen2.5-7b-instruct-uncensored
LMSTUDIO_LOGPATH=C:\Users\kadek\AppData\Roaming\LM Studio\logs\main.log
CHECKPOINT_CHUNKS=true
CHECKPOINT_ITEMS=true
CHECKPOINT_REVIEW=true
VISION_TIMEOUT_SECONDS=600
RENDER_DPI=96
```

Mac equivalent paths use `/Users/username/...` and `~/Library/Logs/LM Studio/main.log`.
The DB requires manual creation:
`docker exec -it pgvector17 psql -U postgres -c "CREATE DATABASE kinaxis_ragtestdb;"`

---

## Hardware Constraint — PDF Vision Ingest

The operator machine has a GTX 1650 (4GB VRAM). The `qwen2.5-vl-7b` vision model requires
~8GB VRAM and runs on CPU on this hardware. PDF page image encoding takes ~2 minutes per
4-page batch on CPU, making local vision ingest of large PDF corpora impractical (~12 hours
for 230 pages).

**Current recommended approach:**
- PDFs: route to Anthropic API (`LLM_PROVIDER=anthropic`) — native PDF support, no rendering,
  fast and accurate math extraction, pennies per document
- PPTX/DOCX/TXT: run locally via LM Studio text model (fast, no vision needed)
- A `PDF_PROVIDER` override config key to split providers by file type is a planned improvement

---

## Session 15 Plan — Comparative Batch Study + Claude Human Review

### Research Design

4 conditions × 3 difficulties × 50 items = **600 total items** across all batches.

| Batch | Label | Generate | Review | Status |
|-------|-------|----------|--------|--------|
| A | `3-16-26` | local Qwen 7B | local Qwen 7B | DONE — `analytics/3-16-26/` |
| B | `haiku-reviewer` | local Qwen 7B | Claude Haiku API | in progress |
| C | `haiku-generator` | Claude Haiku API | local Qwen 7B | pending |
| D | `haiku-both` | Claude Haiku API | Claude Haiku API | pending |

Each batch = easy + medium + hard × 50 items (9 total runs per session after batch A).
Checkpoints: all OFF (`CHECKPOINT_CHUNKS=false`, `CHECKPOINT_ITEMS=false`, `CHECKPOINT_REVIEW=false`) for unattended runs.

### Config per Batch

**Batch B (haiku-reviewer)** — current config.env state:
```
GENERATE_PROVIDER=local
REVIEW_PROVIDER=api
API_PROVIDER=anthropic
API_MODEL=claude-haiku-4-5-20251001
```

**Batch C (haiku-generator):**
```
GENERATE_PROVIDER=api
REVIEW_PROVIDER=local
```

**Batch D (haiku-both):**
```
GENERATE_PROVIDER=api
REVIEW_PROVIDER=api
```

### Per-Batch Workflow

1. Run easy (DIFFICULTY_TARGET=easy), then medium, then hard in sequence
2. Move completed runs folder to `analytics/[batch-label]/` (e.g. `analytics/haiku-reviewer/`)
3. Run `viz.py [batch-dir]` to generate that batch's snapshot charts + dashboard
4. Commit `analytics/[batch-label]/` to git

### Post-All-Batches Workflow

1. Run merge script (`analytics/merge_runs.py`) — combines all 4 batches' XLSX Items +
   Reviewer Decisions + Traceability + Quality Metrics into `analytics/merged_master.xlsx`
   with a `batch_label` column added to each row
2. Run `viz.py --merged analytics/merged_master.xlsx` — multi-condition comparison charts
3. Claude conducts "human review" (see below)

### Claude Human Review

Claude acts as the independent expert human reviewer. For each item across all batches:
- Reads: question stem, answer choices, correct key, stated difficulty
- Reads: source chunks from Traceability sheet (the actual retrieved context)
- Scores each quality dimension:
  - `source_alignment` (1-5): is the question answerable from the retrieved source material?
  - `distractor_quality` (1-5): are wrong answers plausible but unambiguously wrong?
  - `stem_clarity` (1-5): is the stem unambiguous, grammatically clean, no answer leaks?
  - `difficulty_match` (True/False): does stated difficulty match cognitive demand?
- Issues ACCEPT / REVISE / REJECT decision with written reasoning
- Output: new "Claude Review" sheet added to each run XLSX and to merged_master.xlsx

**Research value:** Claude review IS the human baseline for RQ2 (does agentic critique reduce
human review burden?). Comparing Claude's decisions against Haiku reviewer (Batch B/D) tells
us whether Haiku tracks human judgment. Comparing against local Qwen reviewer (Batch A/C)
quantifies the noise cost of non-independent review.

### viz.py — Required Extensions for Multi-Batch

`analytics/viz.py` currently reads 3 fixed XLSX files (easy/medium/hard) from one runs dir.
Extensions needed before or after merge:
- `--merged` flag: accept merged_master.xlsx, group by `batch_label` for condition comparison
- Additional charts: condition × quality metric, reviewer agreement rate vs Claude, cost comparison across all 4 conditions
- Output to `analytics/[batch-label]/charts/` per batch, or `analytics/merged/` for cross-batch

---

## Session 14 Findings — Scale Runs + Reviewer Architecture

### Scale Run Results (50 items each, local reviewer = qwen2.5-7b-uncensored)

| Difficulty | Schema OK | Difficulty Match | Auto-Accept | REVISE/REJECT |
|---|---|---|---|---|
| Easy ×50 | 49/50 (98%) | 49/50 (98%) | 26 (52%) | 24 |
| Medium ×50 | 50/50 (100%) | 50/50 (100%) | 20 (40%) | 30 |
| Hard ×50 | 50/50 (100%) | 50/50 (100%) | 6 (12%) | 44 |

### Root Cause — Local Reviewer Unreliable

qwen2.5-7b-uncensored reviewing its own output is not independent critique:
- Same model generates AND reviews → not independent
- Consistently flags `INCOMPLETE_CONTEXT` even for well-formed questions
- Inconsistent: some ACCEPT decisions contain REVISE-sounding reason codes
- Hard questions hit 12% accept — reviewer adds noise, not signal

### Fix — Route REVIEW_PROVIDER=api

`API_PROVIDER=anthropic`, `API_MODEL=claude-haiku-4-5-20251001` already configured.
Setting `REVIEW_PROVIDER=api` routes reviewer to Claude Haiku (~$0.10-0.15 per 150 items).
Generation stays local (free). Haiku reviewer will provide meaningful, independent assessment.
**Next session: change REVIEW_PROVIDER=local → api, re-run scale batches.**

### Difficulty Control — Validation Findings (2026-03-16 session 14)

- `DIFFICULTY_TARGET` env var injected into `generator_user.txt` via `{{DIFFICULTY}}` placeholder
- `TOP_K` and `MAX_CONTEXT_CHARS_GEN` are runtime-overridable via env/config.env
- Hard questions: `TOP_K=12`, `MAX_CONTEXT_CHARS_GEN=6000` used for scale runs
- Easy/medium: `TOP_K=6` (default), `MAX_CONTEXT_CHARS_GEN=3000` (default) — both PASS at 60% accept
- Hard: consistently ~0-40% auto-accept. Root cause: model drifts toward implied relationships between chunks rather than staying on explicit text. This is a known model limitation (qwen2.5-7b). Reviewer correctly catches these. Expected human review burden for hard: ~60% of items flagged for checkpoint 3.
- Assessor script: `assess_run.py` — auto-finds most recent XLSX, prints item/reviewer summary, PASS/FAIL verdict

---

## Current Known State

- `interactive_run.py` implemented and working; BAT/SH are thin shims
- `llm_client.py` replaces `lmstudio_client.py` — unified provider abstraction with vision support
- Context model runs at ingest time (not query time); old context-rewrite-at-query-time agent removed
- PDF ingest uses vision (rendered pages for lmstudio, native PDF for anthropic)
- PPTX/DOCX/TXT ingest uses text extraction via context model
- Three human-in-the-loop checkpoints implemented (chunks, items, review)
- Baseline (no-RAG) mode implemented as `generate_baseline()` and `baseline` CLI subcommand
- `chunking.py` is vestigial — character-based chunking replaced by context model output splitting
- Vision page batching implemented (`vision_pages_per_batch=4`) to respect LM Studio context limits
- LM Studio context window must be set to 32768+ for vision model to handle 4-page batches
- MuPDF structural warnings suppressed via `fitz.TOOLS.mupdf_display_errors(False)`
- XLSX output: Run Metadata, DB Snapshot, Chunk Preview, Items, Reviewer Decisions,
  Traceability, Quality Metrics sheets
- **58 chunks in DB** from prior ingest run (all 11 docs in example1, via Anthropic API) — confirmed 2026-03-16
- `config.env` paths updated to `C:\Users\kadek\source\repos\domainRag\` — were pointing to old KinaxisCapstone path
- Generator/reviewer output quality unvalidated end-to-end — first G mode run pending

---

## Still To Do — Priority Order

### IN PROGRESS: Comparative Batch Study (Session 15)

See Session 15 Plan above. Batch A done. Batches B/C/D running overnight.
- `REVIEW_PROVIDER=api` set in config.env — DONE
- All checkpoints disabled for unattended runs — DONE
- merge_runs.py not yet written — needed before Claude human review
- viz.py multi-batch extensions not yet written — needed before merged viz

### DONE: First G-Mode Scale Runs + REVIEW_PROVIDER Fix

Easy/medium/hard ×50 completed 2026-03-16 (Batch A, local/local). Chunks OK, difficulty control working.
Local reviewer unreliable — see Session 14 Findings. REVIEW_PROVIDER=api now set. Batch B running.

### HIGH: Competency / Section Tagging

Add `competency` and `source_section` fields to generator output schema, generator prompt, and XLSX Items sheet.
This is the foundation for coverage tracking and distribution control.
- Generator prompt: instruct model to tag each item with competency area drawn from context
- `text_utils.py`: add fields to schema validation
- `pipeline.py`: pass through to XLSX Items sheet

### MEDIUM: Knowledge Coverage Tracking

Ensure test items are distributed across logical sections of domain knowledge.
Depends on: competency tagging.
- Track which chunks have been used as retrieval seeds across items in a run
- Add Coverage sheet to XLSX (competency × chunk_count × items_generated)
- Flag under-represented competencies at checkpoint 2

### MEDIUM: Difficulty Proportion Control

Currently difficulty is declared by the generator but not controlled by the caller.
- Add `DIFFICULTY_TARGET` config param (easy | medium | hard | any; default: any)
- Inject target difficulty into generator_user.txt: "Generate a {difficulty} question…"
- Add `DIFFICULTY_DISTRIBUTION` param (e.g. "30/50/20") for multi-item runs
- Generation loop: rotate through difficulty targets to hit the requested distribution
- Coverage sheet: add difficulty × competency breakdown

### MEDIUM: Research Condition Comparison

Multiple condition runs for RQ1/RQ2:
- RAG + critic (current)
- RAG + no critic
- No-RAG + critic (baseline mode exists)
- No-RAG + no critic
Store `CONDITION_LABEL` in XLSX Run Metadata sheet for side-by-side analysis.

### LOW: Question Format Variants

Currently only standard 4-option MCQ (a/b/c/d). Planned variants:
- **Select-N-of-M** (e.g. "select 2 of 5"): requires different prompt contract and XLSX schema
- **Binned / categorization**: match concepts to categories; different prompt template entirely
- **Fill-in-the-blank**: gap-fill items; different output contract
Implementation: one prompt template file per format type; `FORMAT` config param; format-specific
schema validator in `text_utils.py`. Each format is independent — add one at a time.
Prerequisite: first run validated and competency tagging in place.

### LOW: User / LLM Interaction Layer

Currently completely absent — pipeline runs batch, no real-time dialogue.
Required for Kinaxis deliverables. Likely a new run mode (`C = Chat / interactive`).
Options: CLI REPL, minimal web UI (Flask/FastAPI), or structured chat loop.
Scope TBD — design after all other features validated.

---

## Research Design Context

**RQ1:** Does a dual-model agentic RAG architecture produce higher-quality MCQ items than
single-model generation?
- IV: generation approach (RAG+critic vs no-RAG, RAG+no-critic, no-RAG+no-critic)
- DVs: source alignment, distractor quality, stem clarity, difficulty calibration scores

**RQ2:** Can agentic critique meaningfully reduce human review burden?
- Measured by: proportion of items requiring substantive human revision after critic pass

**Quality dimensions:**
- Source alignment (1-5): grounded in retrieved chunks?
- Distractor quality (1-5): plausible but unambiguously wrong?
- Stem clarity (1-5): unambiguous, grammatically correct, no clues?
- Difficulty calibration (bool): stated difficulty matches cognitive demand?

---

## Constraints and Conventions

- Minimal diffs; full-file replacements preferred when changes are extensive
- Do NOT auto-load LM Studio models from Python
- Prompts do NOT control model selection — model is set in config
- All DB access via `psycopg.connect(dsn)`, no ORM
- Python files use dataclasses, psycopg3, openpyxl, requests — no heavy frameworks
- No f-strings or type annotations with `|` syntax — must support Python 3.9 for compatibility
- `LLM_API_KEY` must never appear in logs, XLSX output, or `config.env`
- When advising on code changes, always provide either:
  (a) full function replacement from the `def` line to the final return/end of function, or
  (b) full file replacement if changes span multiple functions or are extensive
  Do NOT provide surgical line-level snippets or partial function bodies
- When advising on prompt changes, provide full replacement text for the `.txt` file
