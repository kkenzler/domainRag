@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "POWERSHELL_EXE=C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

if not exist "%POWERSHELL_EXE%" set "POWERSHELL_EXE=powershell.exe"

set "TARGET_COUNT=%~1"
if "%TARGET_COUNT%"=="" set "TARGET_COUNT=1200"

set "TICK_SECONDS=%~2"
if "%TICK_SECONDS%"=="" set "TICK_SECONDS=60"

"%POWERSHELL_EXE%" -NoExit -ExecutionPolicy Bypass -File "%SCRIPT_DIR%watch_codex_review_supervisor.ps1" -TargetCount %TARGET_COUNT% -TickSeconds %TICK_SECONDS%
