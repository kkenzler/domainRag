param(
    [int]$TargetCount = 1200,
    [int]$TickSeconds = 60,
    [int]$MaxCycles = 0
)

$ErrorActionPreference = "Stop"

$Supervisor = Join-Path (Split-Path -Parent $PSCommandPath) "supervise_codex_review_queue.ps1"
if (-not (Test-Path -LiteralPath $Supervisor)) {
    throw "Missing supervisor script: $Supervisor"
}

$cycle = 0
while ($true) {
    $cycle += 1
    & $Supervisor -TargetCount $TargetCount -SinglePass
    if ($MaxCycles -gt 0 -and $cycle -ge $MaxCycles) {
        break
    }
    Start-Sleep -Seconds $TickSeconds
}
