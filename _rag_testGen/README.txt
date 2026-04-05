_rag_testGen
============

Core Python package for domainRag. Ingests domain documents into pgvector,
generates multiple-choice items via RAG or baseline (no-RAG), and reviews
them with a second LLM pass.

Running
-------

Preferred: use the repo-root launchers.

  Windows:  _run_testGen.bat
  Other:    _run_testGen.sh

Both drop into interactive_run.py, which prompts for settings and run mode.

Direct (automation or headless):

  python -m _rag_testGen <command> [options]

Commands:

  ingest     Ingest domain folder into pgvector
  generate   Generate items from existing pgvector chunks (RAG)
  baseline   Generate directly from source docs (no-RAG)
  pipeline   Full ingest + generate in one step

Run modes in the interactive launcher:

  F   Full: ingest + generate + analytics
  P   Pipeline: ingest + generate (no analytics)
  I   Ingest only
  G   Generate only (requires prior ingest)
  B   Batch generate + analytics
  A   Analytics on most recent run
  Q   SQL-style corpus exploration (Q mode)
  M   Multi-domain pipeline runner

Config
------

Settings are loaded from a persisted config.env file. The launcher prompts to
update settings on each run.

Default config path: C:\Users\kadek\secrets\domainRag\config.env
Override: set DOMAINRAG_CONFIG_ENV to point at a different file

The config.env.example file in this folder lists all supported keys.
LLM_API_KEY is never written to a persisted config file.

Prerequisites
-------------

- Python 3.10+
- PostgreSQL 17 + pgvector running (see parent DEVOPS.md for docker bootstrap)
- LM Studio running on port 1234 (for local embeddings and local generation)
- openpyxl, psycopg, requests, python-docx, python-pptx (see requirements)

Checking a completed run
------------------------

  python assess_run.py <path_to_run_xlsx>

Exits 0 (pass) or 1 (fail). Pass criteria: >=80% schema-valid items,
>=60% reviewer ACCEPT, >=60% difficulty labels matching DIFFICULTY_TARGET.

Transcribing MP4 corpus files
------------------------------

  python transcribe_corpus.py

Batch-transcribes all MP4 files in the corpus folder to sidecar .txt files
for ingestion.

Troubleshooting
---------------

- "No chunks in DB": run ingest before generate, or use pipeline/full mode.
- LM Studio timeout: reduce N_ITEMS or lower SLEEP_SECONDS between requests.
- PDF vision slow: set INGEST_PROVIDER=api to use the Anthropic PDF route.
- Encoding errors on Windows: ensure PYTHONIOENCODING=utf-8 is set.
