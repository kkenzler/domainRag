domainRag
=========

Generates multiple-choice items grounded in source documents.

The system:
- ingests PDF, PPTX, DOCX, TXT, and MD source material
- extracts structured knowledge chunks
- embeds those chunks into PostgreSQL + pgvector
- generates MCQ items with or without retrieval
- reviews generated items with a second pass
- writes XLSX outputs for downstream study and analysis


HOW TO START
------------
Preferred launcher:

  Windows:   _run_testGen.bat
  Mac/Linux: ./_run_testGen.sh

Both launch `_rag_testGen/interactive_run.py`.

First run:
- when prompted to update settings, enter `Y`
- point the config at the correct corpus, database, and model settings

Persisted config default:
- `C:\Users\kadek\secrets\domainRag\config.env`

Override:
- set `DOMAINRAG_CONFIG_ENV` to use a different local config path

Tracked template:
- `_rag_testGen/config.env.example`


PREREQUISITES
-------------
1. Python 3.10+

2. PostgreSQL 17 + pgvector

   Example Docker bootstrap:

     docker run --name pgvector17 --restart unless-stopped ^
       -e POSTGRES_PASSWORD=postgres -p 5435:5432 -d pgvector/pgvector:pg17

     docker exec -it pgvector17 psql -U postgres -c "CREATE DATABASE kinaxis_ragtestdb;"

3. LM Studio running on port `1234`

   Typical roles:
- embeddings: `text-embedding-nomic-embed-text-v1.5`
- local context / ingest model: vision-capable model for PDFs when using local ingest
- local generator and reviewer: instruction-tuned text models

4. Optional API access for non-local ingest/review/generation

   Notes:
- `LLM_API_KEY` is read at runtime only
- it is never written to the persisted config file
- API routing is optional and can be disabled for local-only runs

5. Python dependencies

     pip install requests psycopg pgvector python-docx pypdf python-pptx pymupdf openpyxl


RUN MODES
---------
Interactive launcher menu:

  B  Batch run    generate (from db) + analytics
  C  Baseline     generate directly from docs, no retrieval
  P  Pipeline     ingest + generate
  F  Full         ingest + generate + analytics
  I  Ingest only  extract knowledge chunks, write XLSX
  G  Generate     use existing db chunks
  A  Analytics    visualize the most recent run/finalization surface
  Q  Query        interactive corpus/DB exploration
  M  Multi-domain run pipeline across multiple domain/DB pairs

Programmatic entrypoint:

  python -m _rag_testGen <command>

Commands:
- `ingest`
- `generate`
- `baseline`
- `pipeline`


OPERATOR FLOW
-------------
Single pipeline run:
1. launch `_run_testGen.bat` or `_run_testGen.sh`
2. choose `P`, `F`, `I`, `G`, or `C`
3. complete any enabled checkpoints
4. inspect the run workbook and logs in the run folder

Comparative study flow:
1. generate/archive study runs
2. merge archived runs into `analytics\merged_master.xlsx`
3. export shared review input
4. complete both review lanes:
   - Claude
   - Codex
5. finalize the study
6. inspect:
   - `analytics\merged_master.xlsx`
   - `analytics\merged\review_analysis\charts`


CONFIGURATION
-------------
Important config behavior:
- `DOMAIN_DIR` points at the corpus folder
- `RAG_ROOT` controls run-output storage
- embeddings always stay on LM Studio
- ingest, generation, and review can each route independently via:
  - `INGEST_PROVIDER=local|api`
  - `GENERATE_PROVIDER=local|api`
  - `REVIEW_PROVIDER=local|api`

Default storage expectation:
- config in `C:\Users\kadek\secrets\domainRag\config.env`
- run outputs in `C:\Users\kadek\secrets\domainRag\runs`


OUTPUT
------
Default per-run folder:
- `C:\Users\kadek\secrets\domainRag\runs\logs_<RUN_ID>\`

Typical run artifacts:
- `run_<RUN_ID>.xlsx`
- `run_manifest_<RUN_ID>.json`
- `run_info.txt`
- `console_*.txt`
- `llm_http.jsonl`
- `lmstudio.log`
- `docker_<container>.log`

Typical workbook sheets:
- Run Metadata
- DB Snapshot
- Chunk Preview
- Items
- Reviewer Decisions
- Traceability
- Quality Metrics


ANALYTICS
---------
`analytics\` is the study workspace.

Key surfaces:
- `example1_local-local`
- `example1_haikuPermutations`
- `example1_gptBaseline`
- `claude_aigenticHumanReview`
- `codex_aigenticHumanReview`
- `merged`
- `studies`

Important artifacts:
- `analytics\merged_master.xlsx`
- `analytics\review_input.json`
- `analytics\merged\review_analysis\charts`

For smaller repeatable studies:

  python analytics\create_study.py my-study

For confidential local-only scaffolds:

  python analytics\create_study.py my-confidential-study --local-only


LOCAL-ONLY / CONFIDENTIAL MODE
------------------------------
Use local-only routing when corpus content must never leave local boundaries:
- `INGEST_PROVIDER=local`
- `GENERATE_PROVIDER=local`
- `REVIEW_PROVIDER=local`

Recommended shape:
- keep corpus material in secrets-backed local folders
- keep local config files untracked
- start confidential studies under `analytics\studies\`
- do not place corpus-bearing material in tracked repo roots


TROUBLESHOOTING
---------------
pgvector connection error:
- confirm the Docker container is running:
  `docker ps --filter "name=pgvector17"`

No chunks in DB:
- run `I`, `P`, or `F` before `G`

LM Studio timeout on local PDF ingest:
- local vision is slow on weaker hardware
- use API ingest for non-sensitive corpora if needed

Checkpoint prompts not appearing:
- run from an interactive terminal

Unexpected config/path behavior:
- update settings at startup and verify `DOMAIN_DIR`, `DB_DSN`, and `RAG_ROOT`


MORE DETAIL
-----------
- repo architecture and workflow rules: `DEVOPS.md`
- analytics-specific workflow: `analytics\README.txt`
- core package internals: `_rag_testGen\DEVOPS.md`
