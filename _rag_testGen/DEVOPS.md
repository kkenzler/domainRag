# _rag_testGen

Core package for domainRag. See the repo-root DEVOPS.md for the full
pipeline overview, storage paths, and analytics workflow.
This file documents the internals specific to this package.

---

## Package Entry Points

`__main__.py` re-exports `cli.main`, enabling `python -m _rag_testGen <cmd>`.

`interactive_run.py` is the primary operator surface. It wraps `cli.py` as a
subprocess and handles config persistence, run-folder creation, and log capture.
It is invoked by the repo-root `_run_testGen.bat` / `_run_testGen.sh` shims.

`cli.py` is the stable programmatic entry point. It builds an argparse
dispatcher and routes to the four sub-commands below.

---

## Sub-Commands

| Command    | Function called        | Source         |
|------------|------------------------|----------------|
| `ingest`   | `ingest_domain()`      | `ingest.py`    |
| `generate` | `generate_from_db()`   | `pipeline.py`  |
| `baseline` | `generate_baseline()`  | `pipeline.py`  |
| `pipeline` | `run_pipeline()`       | `pipeline.py`  |

All sub-commands load `ResolvedConfig` from env first, then apply CLI overrides
via `cfg.with_overrides(...)`. `corpus_label` is always derived from the
`DOMAIN_DIR` basename, not from a CLI flag.

---

## Module Inventory

### `config.py`

Loads env vars into `ResolvedConfig`. All pipeline config flows through this
dataclass — nothing reads env vars directly in other modules.

Key routing env vars:
- `INGEST_PROVIDER=local|api`
- `GENERATE_PROVIDER=local|api`
- `REVIEW_PROVIDER=local|api`

Embeddings always come from LM Studio regardless of provider routing.

### `interactive_run.py`

Config persistence, interactive menu, subprocess orchestration, and log capture.

- Persisted config default: `C:\Users\kadek\secrets\domainRag\config.env`
- Override: `DOMAINRAG_CONFIG_ENV`
- Per-run folder: `<RAG_ROOT>\runs\logs_<RUN_ID>\`
- `run_info.txt`, `console_*.txt`, `llm_http.jsonl`, `lmstudio.log`,
  and docker logs all land in the run folder.
- Run modes: `B` (batch), `C` (custom batch), `F` (full), `P` (pipeline),
  `I` (ingest), `G` (generate), `A` (analytics), `Q` (SQL query), `M` (multi-domain).

### `ingest.py`

Owns corpus ingestion via `IngestConfig` + `ingest_domain()`.

- Iterates domain files with `iter_domain_files()`.
- Routes PDF extraction to vision API or local text depending on
  `INGEST_PROVIDER`.
- Calls `llm_client` for context extraction, `embed_lmstudio` for embedding,
  `db_pgvector` for upsert.
- `corpus_label` is stored per-chunk so multi-corpus DBs stay separable.
- `clear_first=True` drops all chunks for the corpus label before ingest.

### `loaders.py`

Owns raw document loading for all supported formats.

- `LoadedDoc(path, text, sha256)` is the output type.
- `load_document()` dispatches on extension: `.pdf`, `.pptx`, `.docx`,
  `.txt`/`.md`, `.mp4` (sidecar transcript workflow).
- `preprocess_text()` normalizes whitespace and strips common slide/OCR
  artifacts before chunking.
- `_is_spoken_math_transcript()` detects transcripts that need special handling
  for math notation.

### `chunking.py`

Owns text-to-chunk splitting. Separated from `loaders.py` so chunking
parameters can be changed without touching document loading.

- `Chunk(index, text)` is the unit of embedding and retrieval.
- `chunk_text(text, chunk_chars=1600, overlap_chars=200)` splits by
  paragraph blocks (blank-line separated), packs into ~`chunk_chars`, and
  appends sentence-aware tail overlap from the previous chunk.
- Single blocks larger than `chunk_chars` are hard-split to prevent stalls.
- Overlap is boundary-aware: `_tail_overlap()` takes up to 3 sentences from
  the end of the prior chunk, capped at `overlap_chars`.

### `embed_lmstudio.py`

Thin wrapper around the LM Studio embedding endpoint.

- `embed_texts(texts, model, lm_url)` returns a list of float vectors.
- Always used for embeddings regardless of `INGEST_PROVIDER` / `GENERATE_PROVIDER`.

### `db_pgvector.py`

Owns all Postgres access. No ORM. Raw `psycopg.connect(dsn)`.

- `ensure_schema()` creates the `chunks` table and pgvector index if absent.
- `upsert_chunks()` inserts or updates by `chunk_id` (sha256-derived).
- `similarity_search()` returns top-K chunks by cosine distance.
- `corpus_label` column enables filtering by corpus within a shared DB.
- `migrate_corpus_label()` handles the one-time schema migration for the
  multi-corpus column.

### `llm_client.py`

Unified client across LM Studio (local), Anthropic, OpenAI, and Gemini.

- `validate_provider_and_key()` and `validate_model_name()` gate startup.
- `_post_with_retry()` handles transient HTTP failures with backoff.
- `_append_http_log()` writes JSONL traces to `llm_http.jsonl` in the run folder.
- Image block helpers (`_image_block_openai`, `_image_block_anthropic`) wrap
  base64 image payloads for vision-mode PDF extraction.

### `pipeline.py`

Owns generation, review, checkpoints, and XLSX output.

Three config dataclasses:
- `GenerateConfig` — RAG generation from existing DB chunks
- `BaselineConfig` — direct generation from source docs (no retrieval)
- `PipelineConfig` — ingest + generate combined

Checkpoint stages (each interactive, requiring operator confirmation to continue):
1. `_checkpoint_chunks`: after ingest, review extracted chunks
2. `_checkpoint_items`: after generation, review raw items
3. `_checkpoint_review`: after reviewer pass, review flagged items

`write_run_xlsx()` writes the run XLSX with sheets: Run Metadata, DB Snapshot,
Chunk Preview, Items, Reviewer Decisions, Traceability, Quality Metrics.

`XLSX_SAFE_CELL_LIMIT = 32767` chars — cells are truncated to that limit.

### `text_utils.py`

Shared text helpers used by `pipeline.py` and `ingest.py`.

- `extract_first_json_obj()`: extracts the first `{...}` block from LLM output.
- `normalize_decision()`: maps reviewer output strings to canonical
  `ACCEPT/REVISE/REJECT`.
- `clean_generator_text()` / `hard_trim_after_difficulty()`: strip LLM preamble
  and trim after the `difficulty:` field.
- `validate_generator_schema()`: checks that all required fields are present.
- `enforce_hygiene_on_review()`: removes forbidden phrases from reviewer output.

### `transcribe_corpus.py`

Standalone batch transcriber. Walks the corpus folder, transcribes all `.mp4`
files using local Whisper, writes `.txt` sidecars.

### `assess_run.py`

Standalone quality checker for a completed run XLSX.

Pass thresholds:
- `>= 80%` schema-valid items
- `>= 60%` reviewer ACCEPT rate
- `>= 60%` difficulty labels matching `DIFFICULTY_TARGET`

Exits 0 (pass) or 1 (fail). Used for post-run validation before archiving.

---

## Prompt Contract

`_prompts/` holds six plain-text templates:

| File                    | Purpose                                        |
|-------------------------|------------------------------------------------|
| `context_system.txt`    | System role for context/chunk extraction       |
| `context_user.txt`      | User template for context/chunk extraction     |
| `generator_system.txt`  | System role for MCQ generation                 |
| `generator_user.txt`    | User template for MCQ generation               |
| `reviewer_system.txt`   | System role for item review                    |
| `reviewer_user.txt`     | User template for item review                  |

Generator output contract (from `generator_system.txt`):

```
question:
a) ...
b) ...
c) ...
d) ...
correct_key: A|B|C|D
difficulty: easy|medium|hard
```

Plain text only — no code fences. `text_utils.py` parses this format.
When replacing prompt content, replace the full file rather than making
partial edits.

---

## Configuration Keys

Full list of supported env vars (see `config.env.example` for defaults):

```
RAG_ROOT              base path for run output folders
DOMAIN_DIR            path to corpus folder
N_ITEMS               items to generate per run
DB_DSN                psycopg connection string
DOCKER_CONTAINER      container name for log capture
LM_URL                LM Studio endpoint (default http://localhost:1234)
EMBED_MODEL           embedding model name
CONTEXT_MODEL         model for chunk extraction
GENERATOR_MODEL       model for item generation
REVIEW_MODEL          model for item review
API_PROVIDER          api provider name (anthropic|openai|gemini)
API_MODEL             model name for API provider
INGEST_PROVIDER       local|api
GENERATE_PROVIDER     local|api
REVIEW_PROVIDER       local|api
DIFFICULTY_TARGET     easy|medium|hard
LMSTUDIO_LOGPATH      path to LM Studio log for capture
CHECKPOINT_CHUNKS     0|1 enable chunk checkpoint
CHECKPOINT_ITEMS      0|1 enable items checkpoint
CHECKPOINT_REVIEW     0|1 enable reviewer checkpoint
RUN_ID                (runtime) set by interactive_run.py or caller
LOG_DIR               (runtime) run log folder path
OUT_DIR               (runtime) XLSX output folder path
TOP_K                 chunks retrieved per generation call
SLEEP_SECONDS         delay between LLM calls
MAX_CONTEXT_CHARS_GEN max chars of chunk context for generation
MAX_CONTEXT_CHARS_REV max chars of chunk context for review
INGEST_DELAY_SECONDS  delay between ingest API calls
FORCE_INGEST          skip ingest-skip check and always re-ingest
INGEST_ONLY           stop pipeline after ingest
```

`LLM_API_KEY` is read from env at runtime and never written to the
persisted config file.

---

## Design Constraints

- No ORM. Use raw `psycopg.connect(dsn)` throughout.
- No auto-load of LM Studio models from Python.
- Do not introduce framework-heavy abstractions.
- Keep comments sparse and structural.
- Preserve Python 3.9-compatible syntax when touching older modules.
- Prompt files are full-file replacements — do not make partial edits.
- Run artifacts belong in secrets-backed storage, not inside the repo tree.
- Client corpus content under `_client_corpus/` and `_private_corpus/` must
  never be read or exposed. All stages must remain local for those paths.
