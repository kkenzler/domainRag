@echo off
setlocal
cd /d "%~dp0"

echo ======================================================
echo   ONE-OFF BATCH RUN  --  2026-03-18
echo.
echo   Step 1: Ingest example1    (Anthropic API / Sonnet)
echo   Step 2: Generate 150 items (agentFundamentals, local)
echo           easy x50 / medium x50 / hard x50
echo ======================================================
echo.

:: ── API key (needed for Step 1 only) ─────────────────────────────────────────
set /p LLM_API_KEY="  Anthropic API key (for example1 ingest): "
if "%LLM_API_KEY%"=="" (
    echo.
    echo   ERROR: API key required.
    pause
    exit /b 1
)

set RAG_ROOT=%~dp0_rag_testGen
set DB_DSN=postgresql://postgres:postgres@localhost:5435/kinaxis_ragtestdb
set LM_URL=http://localhost:1234
set EMBED_MODEL=text-embedding-nomic-embed-text-v1.5@q8_0
set CONTEXT_MODEL=qwen/qwen2.5-vl-7b
set GENERATOR_MODEL=qwen2.5-7b-instruct-uncensored
set REVIEW_MODEL=qwen2.5-7b-instruct-uncensored
set CHECKPOINT_CHUNKS=false
set CHECKPOINT_ITEMS=false
set CHECKPOINT_REVIEW=false


:: ════════════════════════════════════════════════════════════════════════════
:: STEP 1 — Ingest example1 via Anthropic API (Sonnet)
:: ════════════════════════════════════════════════════════════════════════════
echo ======================================================
echo   STEP 1/2  --  Ingest example1  (Sonnet API)
echo ======================================================
echo.

set DOMAIN_DIR=C:\Users\kadek\source\repos\domainRag\example1
set INGEST_PROVIDER=api
set GENERATE_PROVIDER=local
set REVIEW_PROVIDER=local
set API_PROVIDER=anthropic
set API_MODEL=claude-sonnet-4-6

python "%RAG_ROOT%\cli.py" pipeline --force-ingest --clear-first --ingest-only --no-checkpoint-chunks
if %errorlevel% neq 0 (
    echo.
    echo   ERROR: example1 ingest failed -- aborting.
    pause
    exit /b 1
)
echo.
echo   example1 ingest complete.
echo.


:: ════════════════════════════════════════════════════════════════════════════
:: STEP 2 — Generate agentFundamentals  easy / medium / hard x50  (all local)
:: ════════════════════════════════════════════════════════════════════════════
echo ======================================================
echo   STEP 2/2  --  Generate agentFundamentals  (local)
echo ======================================================
echo.

set DOMAIN_DIR=C:\Users\kadek\Desktop\agentFundamentals
set INGEST_PROVIDER=local
set GENERATE_PROVIDER=local
set REVIEW_PROVIDER=local
set API_PROVIDER=
set API_MODEL=
set N_ITEMS=50

set BATCH_DIR=%~dp0analytics\agentFundamentals_local-local
if not exist "%BATCH_DIR%" mkdir "%BATCH_DIR%"
echo   Output dir: %BATCH_DIR%
echo.

:: ── Easy ─────────────────────────────────────────────────────────────────────
echo ======== 1/3  EASY (50 items) ========
set DIFFICULTY_TARGET=easy
set RUN_ID=easy
set LOG_DIR=%BATCH_DIR%
python "%RAG_ROOT%\cli.py" generate
if %errorlevel% neq 0 goto :fail
echo.

:: ── Medium ───────────────────────────────────────────────────────────────────
echo ======== 2/3  MEDIUM (50 items) ========
set DIFFICULTY_TARGET=medium
set RUN_ID=medium
set LOG_DIR=%BATCH_DIR%
python "%RAG_ROOT%\cli.py" generate
if %errorlevel% neq 0 goto :fail
echo.

:: ── Hard ─────────────────────────────────────────────────────────────────────
echo ======== 3/3  HARD (50 items) ========
set DIFFICULTY_TARGET=hard
set RUN_ID=hard
set LOG_DIR=%BATCH_DIR%
python "%RAG_ROOT%\cli.py" generate
if %errorlevel% neq 0 goto :fail
echo.

:: ── Analytics ────────────────────────────────────────────────────────────────
echo ======== Analytics / Viz ========
python "%~dp0analytics\analyticsVizs.py" "%BATCH_DIR%"

echo.
echo ======================================================
echo   ALL DONE
echo   Results: %BATCH_DIR%
echo ======================================================
pause
endlocal
exit /b 0

:fail
echo.
echo ======================================================
echo   FAILED on %DIFFICULTY_TARGET% -- exit %errorlevel%
echo ======================================================
pause
endlocal
exit /b 1
