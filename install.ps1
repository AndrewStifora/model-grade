# Installs model-grade from this folder (a git checkout or an unzipped release) at the user level:
#   ~/.claude/skills/model-grade  (this folder, minus .git)
#   ~/.claude/skills/mg           (the /mg alias, from assets/mg)
#   ~/.claude/agents/mg-run-*.md  (the --run executors, from assets/agents)
# Usage: pwsh -File install.ps1        (or: powershell -ExecutionPolicy Bypass -File install.ps1)
#        pwsh -File install.ps1 -Target C:\some\other\.claude   (only for testing)
param(
    [string]$Target = (Join-Path $HOME ".claude")
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillsDir = Join-Path $Target "skills"
$agentsDir = Join-Path $Target "agents"
$skill = Join-Path $skillsDir "model-grade"
New-Item -ItemType Directory -Force -Path $skillsDir, $agentsDir | Out-Null

if (Test-Path $skill) {
    $bak = "$skill.bak-" + (Get-Date -Format "yyyyMMdd-HHmmss")
    Move-Item -Path $skill -Destination $bak
    Write-Host "Existing model-grade moved to $bak"
}
New-Item -ItemType Directory -Force -Path $skill | Out-Null
Get-ChildItem -Path $root -Force | Where-Object { $_.Name -notin @(".git", "__pycache__", "dist") } | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $skill $_.Name) -Recurse -Force
}
Get-ChildItem -Path $skill -Recurse -Directory | Where-Object { $_.Name -in @("__pycache__", "docs-cache") } | Remove-Item -Recurse -Force

New-Item -ItemType Directory -Force -Path (Join-Path $skillsDir "mg") | Out-Null
Copy-Item -Path (Join-Path $root "assets\mg\SKILL.md") -Destination (Join-Path $skillsDir "mg\SKILL.md") -Force
Copy-Item -Path (Join-Path $root "assets\agents\*.md") -Destination $agentsDir -Force

$version = (Get-Content (Join-Path $skill "VERSION") -Raw).Trim()
Write-Host ""
Write-Host "Installed model-grade $version in $skill"
Write-Host "Installed /mg alias in $skillsDir\mg and executors mg-run-* in $agentsDir"
Write-Host ""
Write-Host "Open Claude Code and type:  /mg <a request>"
Write-Host "(the executors used by --run may take a couple of minutes or a new session to appear)"
