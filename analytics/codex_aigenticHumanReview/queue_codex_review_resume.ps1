param(
    [string]$PromptPath = ""
)

$ErrorActionPreference = "Stop"

if (-not $PromptPath) {
    $PromptPath = Join-Path (Split-Path -Parent $PSCommandPath) "codex_review_resume_prompt.md"
}

$QueueRoot = "C:\Users\kadek\source\.cogark\control_plane\agent_sync\queues\codex"
$Inbox = Join-Path $QueueRoot "inbox"

New-Item -ItemType Directory -Force -Path $Inbox | Out-Null

if (-not (Test-Path -LiteralPath $PromptPath)) {
    throw "Missing prompt file: $PromptPath"
}

$promptRaw = Get-Content -LiteralPath $PromptPath -Raw -Encoding UTF8
if ($promptRaw -is [array]) {
    $prompt = ($promptRaw -join [Environment]::NewLine)
} else {
    $prompt = [string]$promptRaw
}
if ([string]::IsNullOrWhiteSpace($prompt)) {
    throw "Prompt file was empty: $PromptPath"
}
$id = (Get-Date).ToString("yyyyMMdd-HHmmss-ffffff")
$payload = [ordered]@{
    id = $id
    agent = "codex"
    window_title = "Codex"
    workflow = "domainrag_codex_review"
    workflow_id = (Get-Date).ToString("yyyyMMdd-HHmmss")
    phase = "resume_manual_review"
    source = "domainrag_review_supervisor"
    created_at = (Get-Date).ToString("o")
    prompt = $prompt
    auto_submit = $true
    status = "queued"
}

$outPath = Join-Path $Inbox ($id + ".json")
$payload | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $outPath -Encoding UTF8
Write-Host ("queued={0} chars={1}" -f $outPath, $prompt.Length)

