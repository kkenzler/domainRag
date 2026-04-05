param(
    [int]$TargetCount = 1200,
    [int]$PollSeconds = 5,
    [int]$QuietSeconds = 90,
    [int]$RetryWithoutProgressSeconds = 180,
    [int]$MaxNoProgressQueues = 12,
    [int]$MaxCycles = 500,
    [switch]$StatusOnly,
    [switch]$SinglePass
)

$ErrorActionPreference = "Stop"

$AnalyticsRoot = Split-Path -Parent $PSCommandPath
$Workdir = Join-Path $AnalyticsRoot "codex_review_workdir"
$InputJson = Join-Path (Split-Path -Parent $AnalyticsRoot) "review_input.json"
$DecisionsJson = Join-Path $Workdir "codex_review_decisions.json"
$QueueRoot = "C:\Users\kadek\source\.cogark\control_plane\agent_sync\queues\codex"
$Inbox = Join-Path $QueueRoot "inbox"
$ListenerStatePath = Join-Path $QueueRoot "state.json"
$QueueWriter = Join-Path $AnalyticsRoot "queue_codex_review_resume.ps1"
$SupervisorStatePath = Join-Path $AnalyticsRoot "codex_review_supervisor_state.json"
$RuntimeStatePath = Join-Path $AnalyticsRoot "codex_review_supervisor_runtime.json"
$LockPath = Join-Path $QueueRoot "codex_review_supervisor.lock.json"

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

function Get-DecisionsMeta {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return [pscustomobject]@{
            count = 0
            last_run_id = ""
            last_item_id = ""
        }
    }

    $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return [pscustomobject]@{
            count = 0
            last_run_id = ""
            last_item_id = ""
        }
    }

    $parsed = ConvertFrom-Json -InputObject $raw
    $count = Get-JsonCount -Path $Path
    if ($count -le 0) {
        return [pscustomobject]@{
            count = 0
            last_run_id = ""
            last_item_id = ""
        }
    }

    $last = if ($parsed -is [System.Array]) { $parsed[-1] } else { @($parsed)[-1] }
    return [pscustomobject]@{
        count = $count
        last_run_id = [string]$last.run_id
        last_item_id = [string]$last.item_id
    }
}

function Get-JsonObject {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-InboxCount {
    if (-not (Test-Path -LiteralPath $Inbox)) { return 0 }
    return @(Get-ChildItem -LiteralPath $Inbox -Filter *.json -ErrorAction SilentlyContinue).Count
}

function ConvertTo-HashtableSafe {
    param([object]$InputObject)

    if ($null -eq $InputObject) { return @{} }
    if ($InputObject -is [hashtable]) { return $InputObject }

    $result = @{}
    foreach ($property in $InputObject.PSObject.Properties) {
        $result[$property.Name] = $property.Value
    }
    return $result
}

function Test-AliveProcess {
    param([int]$ProcessId)
    if ($ProcessId -le 0) { return $false }
    return $null -ne (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue)
}

function Acquire-SupervisorLock {
    param([switch]$SinglePassMode)

    $payload = [ordered]@{
        pid = $PID
        mode = if ($SinglePassMode) { "single_pass" } else { "loop" }
        started_at = (Get-Date).ToString("o")
        host = $Host.Name
        script = $PSCommandPath
    }

    for ($attempt = 0; $attempt -lt 2; $attempt++) {
        $existing = Get-JsonObject -Path $LockPath
        if ($existing) {
            $existingPid = 0
            try { $existingPid = [int]$existing.pid } catch {}
            if ($existingPid -gt 0 -and $existingPid -ne $PID -and (Test-AliveProcess -ProcessId $existingPid)) {
                return [pscustomobject]@{
                    acquired = $false
                    owner_pid = $existingPid
                    owner_mode = [string]$existing.mode
                    owner_started_at = [string]$existing.started_at
                }
            }
            Remove-Item -LiteralPath $LockPath -Force -ErrorAction SilentlyContinue
        }

        try {
            $json = $payload | ConvertTo-Json -Depth 4
            $stream = [System.IO.File]::Open($LockPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
            try {
                $writer = New-Object System.IO.StreamWriter($stream, [System.Text.UTF8Encoding]::new($false))
                $writer.Write($json)
                $writer.Flush()
            } finally {
                if ($writer) { $writer.Dispose() }
                $stream.Dispose()
            }

            return [pscustomobject]@{
                acquired = $true
                owner_pid = $PID
                owner_mode = $payload.mode
                owner_started_at = $payload.started_at
            }
        } catch [System.IO.IOException] {
            Start-Sleep -Milliseconds 100
        }
    }

    $existing = Get-JsonObject -Path $LockPath
    return [pscustomobject]@{
        acquired = $false
        owner_pid = if ($existing) { [int]$existing.pid } else { 0 }
        owner_mode = if ($existing) { [string]$existing.mode } else { "" }
        owner_started_at = if ($existing) { [string]$existing.started_at } else { "" }
    }
}

function Release-SupervisorLock {
    if (-not (Test-Path -LiteralPath $LockPath)) { return }
    $existing = Get-JsonObject -Path $LockPath
    $existingPid = 0
    try { $existingPid = [int]$existing.pid } catch {}
    if ($existingPid -eq $PID) {
        Remove-Item -LiteralPath $LockPath -Force -ErrorAction SilentlyContinue
    }
}

function Write-SupervisorState {
    param(
        [string]$Action,
        [object]$Meta,
        [int]$InboxCount,
        [double]$QuietFor,
        [object]$ListenerState,
        [object]$RuntimeState,
        [string]$QueueBlocker,
        [string]$LastError,
        [object]$LockInfo
    )

    $payload = [ordered]@{
        updated_at = (Get-Date).ToString("o")
        action = $Action
        mode = if ($SinglePass) { "single_pass" } else { "loop" }
        count = [int]$Meta.count
        target_count = [int]$TargetCount
        last_completed_run_id = [string]$Meta.last_run_id
        last_completed_item_id = [string]$Meta.last_item_id
        inbox_count = [int]$InboxCount
        quiet_seconds = [math]::Round($QuietFor, 1)
        listener_status = if ($ListenerState) { [string]$ListenerState.status } else { "" }
        listener_note = if ($ListenerState) { [string]$ListenerState.note } else { "" }
        listener_last_message_id = if ($ListenerState) { [string]$ListenerState.last_message_id } else { "" }
        last_queue_result = if ($RuntimeState) { [string]$RuntimeState.last_queue_result } else { "" }
        last_queue_reason = if ($RuntimeState) { [string]$RuntimeState.last_queue_reason } else { "" }
        no_progress_queue_count = if ($RuntimeState) { [int]$RuntimeState.no_progress_queue_count } else { 0 }
        last_progress_at = if ($RuntimeState) { [string]$RuntimeState.last_progress_at } else { "" }
        last_queue_at = if ($RuntimeState) { [string]$RuntimeState.last_queue_at } else { "" }
        queue_blocker = [string]$QueueBlocker
        last_error = [string]$LastError
        lock_status = if ($LockInfo -and $LockInfo.acquired) { "held" } elseif ($LockInfo) { "busy" } else { "" }
        lock_owner_pid = if ($LockInfo) { [int]$LockInfo.owner_pid } else { 0 }
        lock_owner_mode = if ($LockInfo) { [string]$LockInfo.owner_mode } else { "" }
        runtime_state_path = $RuntimeStatePath
    }
    $payload | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $SupervisorStatePath -Encoding UTF8
}

function New-RuntimeState {
    param(
        [object]$Meta,
        [object]$SeedState
    )

    $now = Get-Date
    $seedProgressAt = $now.AddSeconds(-$QuietSeconds)
    $seedQueueAt = ""
    $seedQueueReason = ""
    $seedQueueResult = ""
    $seedNoProgress = 0

    if ($SeedState) {
        if ($SeedState.updated_at -and $SeedState.quiet_seconds -ne $null) {
            try {
                $seedProgressAt = ([datetime]$SeedState.updated_at).AddSeconds(-1 * [double]$SeedState.quiet_seconds)
            } catch {}
        }
        if ($SeedState.last_queue_reason) {
            $seedQueueReason = [string]$SeedState.last_queue_reason
            $seedQueueResult = [string]$SeedState.last_queue_result
            try { $seedNoProgress = [int]$SeedState.no_progress_queue_count } catch {}
            if ($SeedState.updated_at) {
                try { $seedQueueAt = ([datetime]$SeedState.updated_at).ToString("o") } catch {}
            }
        }
    }

    return [ordered]@{
        last_observed_count = [int]$Meta.count
        last_completed_run_id = [string]$Meta.last_run_id
        last_completed_item_id = [string]$Meta.last_item_id
        last_progress_at = $seedProgressAt.ToString("o")
        last_queue_at = $seedQueueAt
        last_queue_reason = $seedQueueReason
        last_queue_result = $seedQueueResult
        no_progress_queue_count = $seedNoProgress
        last_queued_count = if ($seedQueueReason) { [int]$Meta.count } else { 0 }
        last_queued_run_id = if ($seedQueueReason) { [string]$Meta.last_run_id } else { "" }
        last_queued_item_id = if ($seedQueueReason) { [string]$Meta.last_item_id } else { "" }
    }
}

function Save-RuntimeState {
    param([hashtable]$State)
    $State | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $RuntimeStatePath -Encoding UTF8
}

function Invoke-SupervisorTick {
    $meta = Get-DecisionsMeta -Path $DecisionsJson
    $listenerState = Get-JsonObject -Path $ListenerStatePath
    $seedState = Get-JsonObject -Path $SupervisorStatePath
    $runtime = Get-JsonObject -Path $RuntimeStatePath
    if (-not $runtime) {
        $runtime = New-RuntimeState -Meta $meta -SeedState $seedState
    } else {
        $runtime = ConvertTo-HashtableSafe -InputObject $runtime
    }

    $now = Get-Date
    $lastProgressAt = $now.AddSeconds(-$QuietSeconds)
    if ($runtime.last_progress_at) {
        try { $lastProgressAt = [datetime]$runtime.last_progress_at } catch {}
    }

    $progressChanged = (
        [int]$runtime.last_observed_count -ne [int]$meta.count -or
        [string]$runtime.last_completed_run_id -ne [string]$meta.last_run_id -or
        [string]$runtime.last_completed_item_id -ne [string]$meta.last_item_id
    )

    if ($progressChanged) {
        $lastProgressAt = $now
        $runtime.no_progress_queue_count = 0
        $runtime.last_observed_count = [int]$meta.count
        $runtime.last_completed_run_id = [string]$meta.last_run_id
        $runtime.last_completed_item_id = [string]$meta.last_item_id
        $runtime.last_progress_at = $lastProgressAt.ToString("o")
    }

    $inboxCount = Get-InboxCount
    $quietFor = ($now - $lastProgressAt).TotalSeconds
    $queueBlocker = ""
    $lastError = ""
    $action = "waiting"

    if ($meta.count -ge $TargetCount) {
        $action = "complete"
        Save-RuntimeState -State $runtime
        Write-SupervisorState -Action $action -Meta $meta -InboxCount $inboxCount -QuietFor 0 -ListenerState $listenerState -RuntimeState $runtime -QueueBlocker "" -LastError "" -LockInfo $script:LockInfo
        Write-Host ("Complete: {0}/{1}" -f $meta.count, $TargetCount)
        return
    }

    if ($StatusOnly) {
        Save-RuntimeState -State $runtime
        Write-SupervisorState -Action "status_only" -Meta $meta -InboxCount $inboxCount -QuietFor $quietFor -ListenerState $listenerState -RuntimeState $runtime -QueueBlocker "" -LastError "" -LockInfo $script:LockInfo
        $lastMessageId = if ($listenerState) { [string]$listenerState.last_message_id } else { "" }
        Write-Host ("StatusOnly: count={0}/{1} listener={2} inbox={3} quiet={4:n1}s last_reason={5} last_message={6}" -f $meta.count, $TargetCount, $listenerState.status, $inboxCount, $quietFor, $runtime.last_queue_reason, $lastMessageId)
        return
    }

    if (-not $listenerState) {
        $action = "blocked_listener"
        $queueBlocker = "missing_listener_state"
    } elseif ([string]$listenerState.status -ne "listening") {
        $action = "blocked_listener"
        $queueBlocker = "listener_not_listening"
    } elseif ($inboxCount -gt 0) {
        $action = "waiting"
        $queueBlocker = "inbox_not_empty"
    } elseif ($quietFor -lt $QuietSeconds) {
        $action = "waiting"
        $queueBlocker = "quiet_period"
    } else {
        $currentCheckpoint = "{0}|{1}|{2}" -f $meta.count, $meta.last_run_id, $meta.last_item_id
        $queuedCheckpoint = "{0}|{1}|{2}" -f $runtime.last_queued_count, $runtime.last_queued_run_id, $runtime.last_queued_item_id
        $shouldQueue = $false
        $queueReason = ""

        if ($currentCheckpoint -ne $queuedCheckpoint) {
            $shouldQueue = $true
            $queueReason = "initial_quiet_queue"
        } else {
            $lastQueueAt = [datetime]::MinValue
            if ($runtime.last_queue_at) {
                try { $lastQueueAt = [datetime]$runtime.last_queue_at } catch {}
            }
            $sinceLastQueue = if ($lastQueueAt -eq [datetime]::MinValue) { [double]::PositiveInfinity } else { ($now - $lastQueueAt).TotalSeconds }
            if ($RetryWithoutProgressSeconds -gt 0 -and [int]$runtime.no_progress_queue_count -lt $MaxNoProgressQueues -and $sinceLastQueue -ge $RetryWithoutProgressSeconds) {
                $shouldQueue = $true
                $queueReason = "retry_without_progress"
            } else {
                $action = "waiting"
                $queueBlocker = "awaiting_progress_or_retry_window"
            }
        }

        if ($shouldQueue) {
            try {
                $queueResult = & powershell -NoProfile -ExecutionPolicy Bypass -File $QueueWriter
                $runtime.last_queue_at = $now.ToString("o")
                $runtime.last_queue_reason = $queueReason
                $runtime.last_queue_result = [string]$queueResult
                $runtime.last_queued_count = [int]$meta.count
                $runtime.last_queued_run_id = [string]$meta.last_run_id
                $runtime.last_queued_item_id = [string]$meta.last_item_id
                if ($queueReason -eq "retry_without_progress") {
                    $runtime.no_progress_queue_count = [int]$runtime.no_progress_queue_count + 1
                }
                $action = "queued"
                Save-RuntimeState -State $runtime
                Write-SupervisorState -Action $action -Meta $meta -InboxCount (Get-InboxCount) -QuietFor $quietFor -ListenerState (Get-JsonObject -Path $ListenerStatePath) -RuntimeState $runtime -QueueBlocker "" -LastError "" -LockInfo $script:LockInfo
                Write-Host ("Queued resume prompt at count {0} (reason={1}, attempt={2}) -> {3}" -f $meta.count, $queueReason, $runtime.no_progress_queue_count, $queueResult)
                return
            } catch {
                $action = "queue_failed"
                $queueBlocker = "queue_write_failed"
                $lastError = $_.Exception.Message
            }
        }
    }

    Save-RuntimeState -State $runtime
    Write-SupervisorState -Action $action -Meta $meta -InboxCount $inboxCount -QuietFor $quietFor -ListenerState $listenerState -RuntimeState $runtime -QueueBlocker $queueBlocker -LastError $lastError -LockInfo $script:LockInfo
    $lastMessageId = if ($listenerState) { [string]$listenerState.last_message_id } else { "" }
    Write-Host ("{0}: count={1}/{2} listener={3} inbox={4} quiet={5:n1}s blocker={6} last_reason={7} last_message={8}" -f $action, $meta.count, $TargetCount, $(if ($listenerState) { $listenerState.status } else { "" }), $inboxCount, $quietFor, $queueBlocker, $runtime.last_queue_reason, $lastMessageId)
}

if (-not (Test-Path -LiteralPath $InputJson)) {
    throw "Missing review input: $InputJson"
}

if (-not (Test-Path -LiteralPath $DecisionsJson)) {
    throw "Missing review decisions: $DecisionsJson"
}

if (-not (Test-Path -LiteralPath $QueueWriter)) {
    throw "Missing queue writer: $QueueWriter"
}

$inputCount = Get-JsonCount -Path $InputJson
if ($TargetCount -le 0) {
    $TargetCount = $inputCount
}

$script:LockInfo = Acquire-SupervisorLock -SinglePassMode:$SinglePass
if (-not $script:LockInfo.acquired) {
    $meta = Get-DecisionsMeta -Path $DecisionsJson
    $runtime = Get-JsonObject -Path $RuntimeStatePath
    $listenerState = Get-JsonObject -Path $ListenerStatePath
    Write-SupervisorState -Action "skipped_locked" -Meta $meta -InboxCount (Get-InboxCount) -QuietFor 0 -ListenerState $listenerState -RuntimeState $runtime -QueueBlocker "lock_busy" -LastError "" -LockInfo $script:LockInfo
    Write-Host ("Skipped: supervisor lock is held by pid {0} ({1})" -f $script:LockInfo.owner_pid, $script:LockInfo.owner_mode)
    exit 0
}

try {
    if ($SinglePass -or $StatusOnly) {
        Invoke-SupervisorTick
    } else {
        for ($cycle = 1; $cycle -le $MaxCycles; $cycle++) {
            Invoke-SupervisorTick
            Start-Sleep -Seconds $PollSeconds
        }
    }
} finally {
    Release-SupervisorLock
}
