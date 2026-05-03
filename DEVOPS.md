# domainRag

## Purpose

`domainRag` is a document-grounded MCQ generation and study workspace.

The repo supports:
- RAG vs baseline item generation
- local vs API routing by pipeline step
- dual review lanes over merged study outputs
- unattended comparative studies
- smaller repeatable studies
- local-only handling for confidential corpora

The source of truth is the codebase. This file exists to describe:
- the current repo layout
- the canonical operator flows
- the architectural boundaries
- the storage and secrecy constraints that matter during maintenance

It is not a session diary.

---

## Repo Layout

```text
domainRag/
├── _rag_testGen/
│   ├── cli.py
│   ├── config.py
│   ├── ingest.py
│   ├── loaders.py
│   ├── chunking.py
│   ├── embed_lmstudio.py
│   ├── db_pgvector.py
│   ├── llm_client.py
│   ├── pipeline.py
│   ├── interactive_run.py
│   ├── assess_run.py
│   ├── transcribe_corpus.py
│   ├── DEVOPS.md
│   └── README.txt
├── analytics/
│   ├── run_batches.py
│   ├── run_full_study.py
│   ├── create_study.py
│   ├── merge_runs.py
│   ├── review_export.py
│   ├── human_review_cycle.py
│   ├── finalize_study.py
│   ├── build_review_analysis_exports.py
│   ├── analyticsVizs.py
│   ├── review_lanes.py
│   ├── review_paths.py
│   ├── review_workflow.py
│   ├── viz_*.py
│   ├── example1_*/
│   ├── claude_aigenticHumanReview/
│   ├── codex_aigenticHumanReview/
│   ├── merged/
│   └── studies/
├── example1/
├── _run_testGen.bat
├── _run_testGen.sh
├── README.txt
├── DEVOPS.md
├── EVALUATION_METHODOLOGY.md
└── LAST_PHASE_PLAN.md
```

---

## Canonical Entry Points

### Main launcher

Preferred operator surface:
- `_run_testGen.bat`
- `_run_testGen.sh`

Both launch:
- `_rag_testGen\interactive_run.py`

### Programmatic CLI

Stable package entrypoint:

```powershell
python -m _rag_testGen <command>
```

Supported commands:
- `ingest`
- `generate`
- `baseline`
- `pipeline`

### Analytics study surface

Canonical study orchestration lives under `analytics\`.

Key scripts:
- `run_batches.py`
- `run_full_study.py`
- `create_study.py`
- `merge_runs.py`
- `review_export.py`
- `human_review_cycle.py`
- `finalize_study.py`

---

## Current Operator Flows

### Single-run pipeline

Use the launcher when running interactively.

Interactive menu includes:
- `B` batch generate + analytics
- `C` baseline generate directly from docs
- `P` pipeline ingest + generate
- `F` full ingest + generate + analytics
- `I` ingest only
- `G` generate only from existing DB chunks
- `A` analytics
- `Q` corpus/DB exploration
- `M` multi-domain pipeline runner

High-level flow:
1. load persisted config
2. choose run mode
3. create a run folder
4. execute ingest, generation, review, or analytics
5. write workbook, manifests, and logs into the run folder

### Comparative-study flow

The current study model is:
1. generate and archive condition runs
2. merge archived runs into `analytics\merged_master.xlsx`
3. export shared review input
4. complete both review lanes:
   - Claude
   - Codex
5. finalize the study
6. inspect:
   - `analytics\merged_master.xlsx`
   - `analytics\merged\review_analysis\charts`

### Small-study flow

Canonical root:
- `analytics\studies\<study_id>\`

Scaffold commands:

```powershell
python analytics\create_study.py my-study
python analytics\create_study.py my-confidential-study --local-only
```

Use this path when the study should not pollute the large `example1_*` roots.

---

## Architecture

### `_rag_testGen`

This package owns the document-to-item pipeline.

Core responsibilities:
- config resolution
- document loading
- chunk extraction
- embedding
- retrieval
- generation
- review
- workbook output
- run-folder logging

Main modules:
- `config.py`
  - loads env into `ResolvedConfig`
  - defines routing and runtime settings
- `interactive_run.py`
  - interactive launcher
  - config persistence
  - run-folder creation
  - subprocess orchestration
- `ingest.py`
  - corpus ingestion into pgvector
- `loaders.py`
  - raw document loading and normalization
- `chunking.py`
  - text-to-chunk splitting logic
- `embed_lmstudio.py`
  - LM Studio embeddings wrapper
- `db_pgvector.py`
  - raw Postgres + pgvector access
- `llm_client.py`
  - unified LM Studio / Anthropic / OpenAI / Gemini client
- `pipeline.py`
  - generation, review, checkpoints, XLSX writing
- `assess_run.py`
  - completed-run quality gate
- `transcribe_corpus.py`
  - batch `.mp4` transcript sidecar generation

### `analytics`

This folder owns the study and review workflow after run generation.

Responsibilities:
- archive-aware batch execution
- merged workbook construction
- shared review export
- dual review-lane coordination
- finalization
- review-analysis exports
- chart rendering
- small-study scaffolding

Key architectural surfaces:
- `example1_local-local`
  - archived source runs for the `local/local` slice
- `example1_haikuPermutations`
  - archived source runs for mixed/local permutations
- `example1_gptBaseline`
  - GPT baseline source inputs
- `claude_aigenticHumanReview`
  - Claude review workflow and lane-local workdir
- `codex_aigenticHumanReview`
  - Codex review workflow and lane-local workdir
- `merged`
  - derived merged outputs and review-analysis exports
- `studies`
  - canonical home for smaller repeatable or confidential study roots

Historical/non-canonical:
- `_custom_batch_studies`
  - older study-control output
  - not part of the primary current end-to-end path

---

## Storage Rules

### Config and secrets

Default persisted config path:
- `C:\Users\kadek\secrets\domainRag\config.env`

Override:
- `DOMAINRAG_CONFIG_ENV`

Rules:
- never store live secrets in the repo
- never persist `LLM_API_KEY` into tracked files

### Run outputs

Default run root:
- `C:\Users\kadek\secrets\domainRag\runs`

Default per-run folder:
- `C:\Users\kadek\secrets\domainRag\runs\logs_<RUN_ID>\`

Typical artifacts:
- `run_<RUN_ID>.xlsx`
- `run_manifest_<RUN_ID>.json`
- `run_info.txt`
- `console_*.txt`
- `llm_http.jsonl`
- `lmstudio.log`
- `docker_<container>.log`

### Analytics outputs

Canonical shared artifacts:
- `analytics\merged_master.xlsx`
- `analytics\review_input.json`
- `analytics\merged\review_analysis\`
- `analytics\merged\review_analysis\charts\`

Semantics:
- archived `example1_*` roots are durable tracked study source material
- `merged\` is derived output
- transient runtime state should not be mistaken for durable study archives

---

## Routing Model

Embeddings:
- always local via LM Studio

Per-step routing:
- `INGEST_PROVIDER=local|api`
- `GENERATE_PROVIDER=local|api`
- `REVIEW_PROVIDER=local|api`

Implications:
- ingest can be local while generation/review are API-backed
- generation and review can be split independently
- confidential corpora should stay entirely on local routing

---

## Database

Engine:
- PostgreSQL 17 + pgvector

Typical container:
- `pgvector17`

Typical port:
- `5435`

Access style:
- raw `psycopg.connect(dsn)`
- no ORM

The DB layer is intentionally simple and direct.

---

## Local-Only / Confidential Mode

Use local-only routing when corpus text must not leave local boundaries.

Required posture:
- `INGEST_PROVIDER=local`
- `GENERATE_PROVIDER=local`
- `REVIEW_PROVIDER=local`

Operator guidance:
- keep corpus inputs in local folders, preferably under secrets-backed storage
- keep machine-local config untracked
- start confidential work under `analytics\studies\`
- do not put corpus-bearing files in tracked archive roots unless they are explicitly scrubbed and intended as durable artifacts

Hard rule:
- private client corpus content must not be exposed to hosted APIs or browser workflows

---

## Source-Of-Truth Boundaries

Durable source material:
- code
- prompt files
- tracked archive roots in `analytics\example1_*`
- lane decision files when intentionally kept as study source artifacts

Derived or reproducible material:
- merged workbooks
- review-analysis exports
- charts
- runtime logs

This distinction matters during cleanup:
- do not treat every generated artifact as canonical
- do preserve tracked study archives and decision data that the final analysis depends on

---

## Editing Rules

- prefer minimal coherent diffs
- keep root docs aligned with actual launcher and workflow behavior
- keep analytics docs aligned with the real study/finalization path
- do not introduce ORM layers
- do not auto-load LM Studio models from Python
- keep comments sparse and structural
- preserve existing compatibility constraints in older modules when touching them

---

## Maintenance Pressure Points

- keep `README.txt` lightweight and operator-facing
- keep `DEVOPS.md` architectural and operational
- keep `analytics\studies` as the canonical small-study path
- keep local-only/confidential handling explicit
- avoid letting historical artifacts blur the canonical study flow
