@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py "%SCRIPT_DIR%_rag_testGen\interactive_run.py"
) else (
  python "%SCRIPT_DIR%_rag_testGen\interactive_run.py"
)
pause
