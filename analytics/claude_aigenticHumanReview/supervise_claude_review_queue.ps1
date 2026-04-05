param(
    [int]$TargetCount = 1200,
    [int]$PollSeconds = 5,
    [int]$QuietSeconds = 20,
    [int]$RetryWithoutProgressSeconds = 45,
    [int]$MaxNoProgressQueues = 12,
    [int]$MaxCycles = 500,
    [switch]$StatusOnly
)

$ErrorActionPreference = "Stop"

$AnalyticsRoot = Split-Path -Parent $PSCommandPath
$Workdir = Join-Path $AnalyticsRoot "claude_review_workdir"
$InputJson = Join-Path (Split-Path -Parent $AnalyticsRoot) "review_input.json"
$DecisionsJson = Join-Path $Workdir "claude_review_decisions.json"
$QueueRoot = "C:\Users\kadek\source\.cogark\agent_infra\agent_sync\queues\claude"
$Inbox = Join-Path $QueueRoot "inbox"
$StatePath = Join-Path $QueueRoot "state.json"
$QueueWriter = Join-Path $AnalyticsRoot "queue_claude_review_resume.ps1"
$SupervisorStatePath = Join-Path $AnalyticsRoot "claude_review_supervisor_state.json"

function Get-JsonCount {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return 0 }
    $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    if ([string]::IsNullOrWhiteSpace($raw)) { return 0 }
    $parsed = ConvertFrom-Json -InputObject $raw
    if ($null -eq $parsed) { return 0 }
    if ($parsed -is [System.Array]) { return $parsed.Count }
    if ($parsed -is [System.Collections.IList]) { return $parsed.Count }
    if ($parsed -is [System.Collections.IEnumerable] -and -not ($parsed -is [string]) -and -not ($parsed -is [pscustomobject])) {
        return @($parsed).Count
    }
    return 1
}

function Get-QueueState {
    if (-not (Test-Path -LiteralPath $StatePath)) { return $null }
    try {
        return Get-Content -LiteralPath $StatePath -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-InboxCount {
    if (-not (Test-Path -LiteralPath $Inbox)) { return 0 }
    return @(Get-ChildItem -LiteralPath $Inbox -Filter *.json -ErrorAction SilentlyContinue).Count
}

function Write-SupervisorState {
    param(
        [string]$Action,
        [int]$Count,
        [int]$InboxCount,
        [double]$QuietFor,
        [object]$ListenerState,
        [string]$LastQueueResult,
        [string]$LastQueueReason,
        [int]$NoProgressQueueCount
    )

    $payload = [ordered]@{
        updated_at = (Get-Date).ToString("o")
        action = $Action
        count = $Count
        target_count = $TargetCount
        inbox_count = $InboxCount
        quiet_seconds = [math]::Round($QuietFor, 1)
        listener_status = if ($ListenerState) { [string]$ListenerState.status } else { "" }
        listener_note = if ($ListenerState) { [string]$ListenerState.note } else { "" }
        listener_last_message_id = if ($ListenerState) { [string]$ListenerState.last_message_id } else { "" }
        last_queue_result = $LastQueueResult
        last_queue_reason = $LastQueueReason
        no_progress_queue_count = $NoProgressQueueCount
    }
    $payload | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $SupervisorStatePath -Encoding UTF8
}

if (-not (Test-Path -LiteralPath $InputJson)) {
    throw "Missing review input: $InputJson"
}

if (-not (Test-Path -LiteralPath $QueueWriter)) {
    throw "Missing queue writer: $QueueWriter"
}

$inputCount = Get-JsonCount -Path $InputJson
if ($TargetCount -le 0) {
    $TargetCount = $inputCount
}

$lastCount = Get-JsonCount -Path $DecisionsJson
$lastProgressAt = (Get-Date).AddSeconds(-$QuietSeconds)
$queuedThisCycle = $false
$lastQueueAt = [datetime]::MinValue
$lastQueueReason = ""
$lastQueueResult = ""
$noProgressQueueCount = 0

for ($cycle = 1; $cycle -le $MaxCycles; $cycle++) {
    $count = Get-JsonCount -Path $DecisionsJson
    if ($count -gt $lastCount) {
        $lastCount = $count
        $lastProgressAt = Get-Date
        $queuedThisCycle = $false
        $noProgressQueueCount = 0
        $lastQueueReason = "progress_reset"
        $lastQueueResult = ""
        Write-Host ("Progress: {0}/{1}" -f $count, $TargetCount)
    }

    if ($count -ge $TargetCount) {
        Write-SupervisorState -Action "complete" -Count $count -InboxCount (Get-InboxCount) -QuietFor 0 -ListenerState (Get-QueueState) -LastQueueResult $lastQueueResult -LastQueueReason $lastQueueReason -NoProgressQueueCount $noProgressQueueCount
        Write-Host ("Complete: {0}/{1}" -f $count, $TargetCount)
        break
    }

    $state = Get-QueueState
    $listenerStatus = if ($state) { [string]$state.status } else { "" }
    $inboxCount = Get-InboxCount
    $quietFor = ((Get-Date) - $lastProgressAt).TotalSeconds

    if ($StatusOnly) {
        Write-SupervisorState -Action "status_only" -Count $count -InboxCount $inboxCount -QuietFor $quietFor -ListenerState $state -LastQueueResult $lastQueueResult -LastQueueReason $lastQueueReason -NoProgressQueueCount $noProgressQueueCount
        $lastMessageId = if ($state) { [string]$state.last_message_id } else { "" }
        Write-Host ("StatusOnly: count={0}/{1} listener={2} inbox={3} quiet={4:n1}s last_reason={5} last_message={6}" -f $count, $TargetCount, $listenerStatus, $inboxCount, $quietFor, $lastQueueReason, $lastMessageId)
        break
    }

    $shouldQueue = $false
    $queueReason = ""
    if ($inboxCount -eq 0 -and $quietFor -ge $QuietSeconds) {
        if (-not $queuedThisCycle) {
            $shouldQueue = $true
            $queueReason = "initial_quiet_queue"
        } elseif ($RetryWithoutProgressSeconds -gt 0 -and $noProgressQueueCount -lt $MaxNoProgressQueues) {
            $sinceLastQueue = ((Get-Date) - $lastQueueAt).TotalSeconds
            if ($sinceLastQueue -ge $RetryWithoutProgressSeconds) {
                $shouldQueue = $true
                $queueReason = "retry_without_progress"
            }
        }
    }

    if ($shouldQueue) {
        $queueResult = & powershell -NoProfile -ExecutionPolicy Bypass -File $QueueWriter
        $queuedThisCycle = $true
        $lastQueueAt = Get-Date
        $lastQueueReason = $queueReason
        $lastQueueResult = [string]$queueResult
        if ($queueReason -eq "retry_without_progress") {
            $noProgressQueueCount += 1
        }
        Write-SupervisorState -Action "queued" -Count $count -InboxCount (Get-InboxCount) -QuietFor $quietFor -ListenerState (Get-QueueState) -LastQueueResult $lastQueueResult -LastQueueReason $lastQueueReason -NoProgressQueueCount $noProgressQueueCount
        Write-Host ("Queued resume prompt at count {0} (listener={1}, reason={2}, attempt={3}) -> {4}" -f $count, $listenerStatus, $queueReason, $noProgressQueueCount, $lastQueueResult)
    } else {
        Write-SupervisorState -Action "waiting" -Count $count -InboxCount $inboxCount -QuietFor $quietFor -ListenerState $state -LastQueueResult $lastQueueResult -LastQueueReason $lastQueueReason -NoProgressQueueCount $noProgressQueueCount
        $lastMessageId = if ($state) { [string]$state.last_message_id } else { "" }
        Write-Host ("Waiting: count={0}/{1} listener={2} inbox={3} quiet={4:n1}s last_reason={5} last_message={6}" -f $count, $TargetCount, $listenerStatus, $inboxCount, $quietFor, $lastQueueReason, $lastMessageId)
    }

    Start-Sleep -Seconds $PollSeconds
}
