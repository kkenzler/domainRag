# domainRag

---

## Purpose

`domainRag` generates multiple-choice items grounded in source documents.

The core system:
- ingests domain documents
- extracts knowledge chunks with an LLM
- embeds those chunks into Postgres + pgvector
- retrieves relevant chunks during generation
- generates items
- reviews items with a second pass
- writes structured XLSX outputs for analysis

Primary use cases:
- RAG vs no-RAG comparison
- local vs API review/generation comparison
- unattended batch studies
- human or Claude follow-up review over generated runs

---

## Repo Layout

```text
domainRag/
├── _rag_testGen/
│   ├── cli.py
│   ├── config.py
│   ├── pipeline.py
│   ├── ingest.py
│   ├── loaders.py
│   ├── llm_client.py
│   ├── embed_lmstudio.py
│   ├── db_pgvector.py
│   ├── text_utils.py
│   ├── interactive_run.py
│   ├── transcribe_corpus.py
│   ├── assess_run.py
│   └── _prompts/
├── analytics/
│   ├── analyticsVizs.py
│   ├── run_batches.py
│   ├── merge_runs.py
│   └── aigenticHumanReview.py
├── example1/
├── _run_testGen.bat
├── _run_testGen.sh
├── README.txt
└── DEVOPS.md
```

---

## Runtime Surfaces

### Main Launcher

`_run_testGen.bat` and `_run_testGen.sh` are thin shims into `_rag_testGen/interactive_run.py`.

`interactive_run.py` is the primary operator surface. It:
- loads and saves persisted config
- prompts for run mode
- prepares run folders
- passes env vars to `cli.py`
- captures logs
- optionally runs analytics

Current launcher menu:
- `B`: batch generate + analytics
- `P`: pipeline ingest + generate
- `F`: full ingest + generate + analytics
- `I`: ingest only
- `G`: generate only
- `A`: analytics on most recent run
- `Q`: SQL-style corpus exploration against the pgvector DB
- `M`: multi-domain pipeline runner

### CLI Dispatcher

`_rag_testGen/cli.py` dispatches to:
- `ingest`
- `generate`
- `baseline`
- `pipeline`

This is the stable programmatic entrypoint for automation.

---

## Core Flow

```text
interactive_run.py
  -> cli.py
     -> pipeline / generate / ingest / baseline

pipeline
  -> ingest.py
     -> loaders.py
     -> llm_client.py
     -> embed_lmstudio.py
     -> db_pgvector.py
  -> pipeline.py generation path
     -> db_pgvector.py retrieval
     -> llm_client.py generator
     -> llm_client.py reviewer
  -> write_run_xlsx()
```

High-level behavior:
- PDFs use vision-style extraction
- PPTX/DOCX/TXT use text extraction
- embeddings always come from LM Studio
- retrieval comes from pgvector
- generation and review can each route to local or API

---

## Module Roles

### `_rag_testGen/config.py`

Loads environment variables into `ResolvedConfig`.

Important behavior:
- config is environment-driven
- local lane and API lane are separate
- routing is per step: ingest, generate, review
- embeddings remain local regardless of provider routing

### `_rag_testGen/interactive_run.py`

Interactive operator launcher.

Important behavior:
- persisted config defaults to `C:\Users\kadek\secrets\domainRag\config.env`
- default run root is `C:\Users\kadek\secrets\domainRag\runs`
- per-run folder is `runs\logs_<RUN_ID>\`
- `OUT_DIR` is pointed at the same run folder so XLSX, manifest, logs, and console output stay together

### `_rag_testGen/ingest.py`

Owns corpus ingestion.

Important behavior:
- extracts knowledge chunks
- uses vision for PDFs
- uses text-mode extraction for PPTX/DOCX/TXT
- writes chunks into pgvector
- supports `clear_first`

### `_rag_testGen/loaders.py`

Owns raw document loading and preprocessing.

Supported types:
- PDF
- PPTX
- DOCX
- TXT / MD
- MP4 sidecar transcript workflow is also present

### `_rag_testGen/pipeline.py`

Owns generation, review, checkpoints, and XLSX output.

Primary functions:
- `generate_from_db()`
- `generate_baseline()`
- `run_pipeline()`
- `write_run_xlsx()`

Checkpoint stages:
- chunk review
- item review
- reviewer-flag review

### `_rag_testGen/db_pgvector.py`

Owns all Postgres access.

This repo does not use an ORM.

### `_rag_testGen/llm_client.py`

Unified LLM client across:
- LM Studio
- Anthropic
- OpenAI
- Gemini

### `analytics/analyticsVizs.py`

Current chart renderer for:
- one 3-run batch directory
- merged comparison workbook
- Claude review decision JSON

This file was historically the messiest surface because it accumulated one-off study assumptions.
Current expectation: it should stay generic and derive conditions from the provided data, not from hardcoded historic batch names.

### `analytics/run_batches.py`

Unattended comparative-study runner.

Current behavior:
- reads persisted config from secrets path
- writes runs into secrets-backed run folders first
- archives completed runs into `analytics/`
- invokes `analyticsVizs.py`
- invokes `merge_runs.py` at the end

### `analytics/create_study.py`

Small-study scaffold helper.

Current behavior:
- creates `analytics\studies\<study_id>\...`
- writes a per-study `.gitignore`
- writes a local-only config template
- separates smaller or confidential studies from the tracked `example1_*` large-study roots

### `analytics/merge_runs.py`

Builds a merged master workbook from archived batch folders.

### `analytics/aigenticHumanReview.py`

Exports items for human/Claude review and writes review decisions back into a workbook.

---

## Configuration

Persisted config path:
- `C:\Users\kadek\secrets\domainRag\config.env`

Override path:
- `DOMAINRAG_CONFIG_ENV`

Tracked template:
- `_rag_testGen/config.env.example`

Secrets rule:
- `LLM_API_KEY` is never written to the persisted config file

Common keys:

```text
RAG_ROOT
DOMAIN_DIR
N_ITEMS
DB_DSN
DOCKER_CONTAINER
LM_URL
EMBED_MODEL
CONTEXT_MODEL
GENERATOR_MODEL
REVIEW_MODEL
API_PROVIDER
API_MODEL
INGEST_PROVIDER
GENERATE_PROVIDER
REVIEW_PROVIDER
DIFFICULTY_TARGET
LMSTUDIO_LOGPATH
CHECKPOINT_CHUNKS
CHECKPOINT_ITEMS
CHECKPOINT_REVIEW
```

Important routing rules:
- `INGEST_PROVIDER=local|api`
- `GENERATE_PROVIDER=local|api`
- `REVIEW_PROVIDER=local|api`

Important runtime variables:
- `RUN_ID`
- `LOG_DIR`
- `OUT_DIR`
- `TOP_K`
- `CONDITION_LABEL`
- `MAX_CONTEXT_CHARS_GEN`
- `MAX_CONTEXT_CHARS_REV`

---

## Storage And Outputs

Default run root:
- `C:\Users\kadek\secrets\domainRag\runs`

Default per-run folder:
- `C:\Users\kadek\secrets\domainRag\runs\logs_<RUN_ID>\`

Expected run artifacts:
- `run_<RUN_ID>.xlsx`
- `run_manifest_<RUN_ID>.json`
- `run_info.txt`
- `console_pipeline.txt` or `console_generate.txt`
- `llm_http.jsonl`
- `lmstudio.log`
- `docker_<container>.log`

XLSX sheets can include:
- Run Metadata
- DB Snapshot
- Chunk Preview
- Items
- Reviewer Decisions
- Traceability
- Quality Metrics

---

## Database

Database engine:
- PostgreSQL 17 with pgvector

Expected local container:
- `pgvector17`

Typical port:
- `5435`

Manual bootstrap example:

```powershell
docker run --name pgvector17 --restart unless-stopped -e POSTGRES_PASSWORD=postgres -p 5435:5432 -d pgvector/pgvector:pg17
docker exec -it pgvector17 psql -U postgres -c "CREATE DATABASE kinaxis_ragtestdb;"
```

The repo expects direct `psycopg.connect(dsn)` usage.

---

## Analytics Workflow

### Single Run Folder

Use:

```powershell
python analytics\analyticsVizs.py "C:\path\to\logs_YYYYMMDD_HHMMSSZ"
```

This expects one batch folder containing three `run_*.xlsx` files representing:
- easy
- medium
- hard

### Unattended Multi-Condition Study

Use:

```powershell
python analytics\run_batches.py
```

Expected pattern:
- run batch condition
- archive generated run folders into `analytics\...`
- render charts for each batch
- merge all batches
- render merged charts

### Merge Archived Batches

Use:

```powershell
python analytics\merge_runs.py
```

### Claude / Human Review

Use:

```powershell
python analytics\aigenticHumanReview.py --export
python analytics\aigenticHumanReview.py --status
python analytics\aigenticHumanReview.py --require-complete
python analytics\aigenticHumanReview.py --write
python analytics\analyticsVizs.py --claude-review "<path-to-decisions-json>"
```

Claude / human review is a required stage before final analytics sign-off.

### Analytics Expectations

`analyticsVizs.py` should remain:
- data-driven
- batch-name agnostic where possible
- able to render from current workbook schema

It should not rely on:
- one hardcoded model family
- one historical item count
- one historical folder name

### Small-Study Mode

Canonical root:
- `analytics\studies\<study_id>\`

Purpose:
- isolate smaller repeatable studies from the current large `example1_*` archives
- keep per-study review workdirs and outputs together
- provide a safe starting point for confidential corpora

Scaffold command:

```powershell
python analytics\create_study.py my-study
python analytics\create_study.py my-confidential-study --local-only
```

---

## Local vs API Guidance

### Local-Only Safe Lane

Use local-only routing when corpus content must remain private:
- `INGEST_PROVIDER=local`
- `GENERATE_PROVIDER=local`
- `REVIEW_PROVIDER=local`

Recommended operator shape:
- scaffold a study with `python analytics\create_study.py <study-id> --local-only`
- point `DOMAIN_DIR` at a secrets-backed local corpus path
- keep any machine-local `.env` file untracked
- do not place corpus-bearing review exports in tracked large-study roots

### Mixed Lane

Useful when:
- PDFs are large
- local vision is too slow
- review independence matters

Typical mixed pattern:
- ingest via API for PDFs
- generate locally
- review via API

### Hardware Constraint

This machine’s GTX 1650 class hardware is weak for sustained local PDF vision ingest.

Operational consequence:
- local PDF vision can be very slow
- Anthropic native PDF ingest is often the practical route for non-sensitive corpora

---

## Current Operational Assumptions

- Python 3.10+ is expected by the operator docs
- LM Studio should be running on port `1234`
- embeddings use LM Studio
- run artifacts belong in secrets-backed storage, not repo-local folders
- archived analytics bundles belong in `analytics/`
- generated analytics images and merged study artifacts are reproducible outputs, not canonical source material

---

## Known Weak Spots

- `analytics/analyticsVizs.py` has historically accreted one-off study logic
- `DEVOPS.md` was previously polluted with session history and stale plans
- archived analytics outputs are recoverable only if they still exist locally; the code is the durable asset, generated study outputs are not
- study reproduction is straightforward, but exact historic outputs are not guaranteed unless the artifacts were preserved

---

## Rules For Editing

- Prefer minimal, coherent diffs
- If a change spans many functions, replace the full file rather than leaving fragmented edits
- Keep comments sparse and structural
- Do not introduce framework-heavy abstractions
- Do not add ORM layers
- Do not auto-load LM Studio models from Python
- Keep prompt files as full-text replacements when changing them
- Preserve Python 3.9-compatible syntax if touching older modules that rely on that compatibility

---

## Hard Constraints

### Secret Handling

- Never write live secrets into the repo
- Never persist `LLM_API_KEY` into tracked files

### Client Corpus Protection

Do not inspect private corpus contents under:
- `_client_corpus/`
- `_private_corpus/`

If working against a private client corpus:
- all stages must remain local
- no cloud APIs

### Source Of Truth

The codebase is the source of truth for behavior.

This file should describe:
- what exists now
- how to run it
- what constraints matter
- what an agent must preserve

It should not function as a session diary.

---

## Recovery Notes

If generated study artifacts are missing:
- recover code from git if possible
- check `C:\Users\kadek\secrets\domainRag` for surviving run folders
- if artifacts are gone, regenerate the study rather than trying to reverse-engineer the exact outputs from chart images

Recommended regeneration order:
1. validate config and paths
2. run a small pilot batch
3. run full study batches
4. merge outputs
5. regenerate dashboards

---

## Immediate Maintenance Targets

- keep `analyticsVizs.py` generic
- keep launcher paths aligned with secrets-backed storage
- keep `README.txt` lightweight and operator-facing
- keep this file architectural and operational, not historical
