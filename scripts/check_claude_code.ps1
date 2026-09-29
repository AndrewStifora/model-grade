# Compares the installed Claude Code CLI with the version this model-grade release is built for
# (CLAUDE_CODE_VERSION at the skill root) and recommends `claude update` when the CLI is older.
#   pwsh -File check_claude_code.ps1                 (checks the skill folder this script sits in)
#   pwsh -File check_claude_code.ps1 -Skill <dir>
# Never fails: a missing CLI or an unreadable version only skips the check. update.ps1 runs it last.
param([string]$Skill = (Split-Path $PSScriptRoot -Parent))
try {
    $file = Join-Path $Skill "CLAUDE_CODE_VERSION"
    if (-not (Test-Path $file)) { return }
    $want = (Get-Content $file -Raw).Trim()
    $cmd = Get-Command claude -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $cmd) {
        Write-Host "Claude Code check skipped: the claude CLI is not on PATH (model-grade is built for $want or later)."
        return
    }
    $raw = (& $cmd.Source --version 2>$null | Out-String)
    if ($raw -notmatch '(\d+\.\d+\.\d+)') {
        Write-Host "Claude Code check skipped: 'claude --version' did not report a version (model-grade is built for $want or later)."
        return
    }
    $have = $Matches[1]
    if ([version]$have -lt [version]$want) {
        Write-Host "Claude Code $have is older than $want, the version this model-grade release is built for. Run 'claude update'."
        Write-Host "Older versions can resolve the model aliases (sonnet, opus) to earlier models than the ones the rubric routes to, so --run may not get the model its verdict names."
    } else {
        Write-Host "Claude Code $have (model-grade is built for $want or later): ok"
    }
} catch {
    Write-Host "Claude Code check skipped: $($_.Exception.Message)"
}
