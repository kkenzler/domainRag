domainRag (RAG TestGen)
=======================
Generates multiple-choice exam items grounded in domain source material.
Ingests PDF, PPTX, DOCX, and TXT documents, extracts structured knowledge
chunks via a local or cloud LLM, embeds them into a vector database, then
generates and reviews MCQ items with three human-in-the-loop checkpoints.


HOW TO START
------------
Windows:   Double-click  _run_testGen.bat
Mac/Linux: ./_run_testGen.sh  (chmod +x required on first use)
           OR: python3 _rag_testGen/interactive_run.py

First run: when prompted "Update settings?" enter Y and set all paths and
model names. Settings are saved to `C:\Users\kadek\secrets\domainRag\config.env`
by default. Set `DOMAINRAG_CONFIG_ENV` if you want a different local path.
The repo includes `_rag_testGen/config.env.example` as a safe template only.


PREREQUISITES
-------------
1. Python 3.10+

2. Docker Desktop (Linux containers mode):
   Start the pgvector container (run once, container restarts automatically):

     docker run --name pgvector17 --restart unless-stopped ^
       -e POSTGRES_PASSWORD=postgres -p 5435:5432 -d pgvector/pgvector:pg17

   Initialize the database (run once):

     docker exec -it pgvector17 psql -U postgres -c "CREATE DATABASE kinaxis_ragtestdb;"

3. LM Studio  (https://lmstudio.ai)  -- required for embeddings and local
   generation/review. Server must be running (green icon, port 1234).
   Minimum required model:  text-embedding-nomic-embed-text-v1.5@q8_0
   Context model (PDF vision ingest):  qwen2.5-vl-7b-instruct
   Generator and reviewer:  qwen2.5-7b-instruct-uncensored (or equivalent)
   Set LM Studio context window to 32768+ when using the vision model.

4. API key (optional but recommended for PDF-heavy corpora on low-VRAM hardware).
   Entering an API key at runtime routes PDF ingest to Anthropic or another
   cloud provider. The key is never saved to the persisted config file.

5. Python dependencies:

     pip install requests psycopg pgvector python-docx pypdf python-pptx pymupdf openpyxl


USAGE
-----
On startup, interactive_run.py asks:
  - Update settings? (Y/N) -- review and edit the persisted config values
  - Run mode:
      F = Full pipeline    ingest domain folder + generate items (RAG mode)
      I = Ingest only      extract knowledge chunks, embed, write XLSX preview
      G = Generate only    use existing DB chunks to generate + review items
      B = Baseline         no-RAG mode -- load docs directly, no pgvector

Human-in-the-loop checkpoints (each can be disabled in the persisted config):
  After ingest:      review extracted knowledge chunks, edit or skip any
  After generation:  review generated items, edit or skip before critic pass
  After review:      see flagged items, override or correct before final output

When checkpoints are enabled, the terminal must remain interactive.

Source documents go in the folder set as DOMAIN_DIR in the persisted config. Supported
formats: PDF, PPTX, DOCX, TXT.

Hardware note: PDF vision ingest requires ~8GB VRAM for full GPU speed. On
hardware with less VRAM (e.g. GTX 1650 4GB), local vision runs on CPU at
roughly 2 minutes per 4-page batch. For PDF-heavy corpora, routing PDF ingest
to the Anthropic API is strongly recommended (fast, accurate, low cost).
PPTX/DOCX/TXT ingest runs fast on any hardware via the local text model.


OUTPUT
------
Each run writes to the secrets-backed run root under
`C:\Users\kadek\secrets\domainRag\runs\logs_<RUNID>\` by default:

  run_<RUNID>.xlsx           Multi-sheet workbook:
                               Run Metadata, DB Snapshot, Chunk Preview,
                               Items, Reviewer Decisions, Traceability,
                               Quality Metrics
  run_manifest_<RUNID>.json  Config snapshot for this run
  run_info.txt               Settings and timing summary
  console_pipeline.txt       Captured stdout (when checkpoints disabled)
  llm_http.jsonl             Per-request LLM log (provider, model, elapsed_ms)
  lmstudio.log               LM Studio log tail
  docker_<container>.log     Docker container log tail


TROUBLESHOOTING
---------------
"Update settings?" -- type Y if this is a new machine or DOMAIN_DIR has moved.

pgvector connection error           Confirm Docker container is running:
                                    docker ps --filter "name=pgvector17"

LM Studio timeout on PDF ingest     Vision model is running on CPU. Route
                                    PDFs to Anthropic API instead by setting
                                    API_PROVIDER=anthropic in the persisted
                                    config and entering your API key at the
                                    runtime prompt.

Embeddings fail                     Confirm LM Studio is running and
                                    nomic-embed-text-v1.5 is loaded. Embeddings
                                    always use LM Studio regardless of provider.

Checkpoint prompts not appearing    Run from a terminal, not piped to a file.
