# Updates the installed model-grade skill to the newest published version.
#   pwsh -File update.ps1                      (git pull if the skill is a git clone, otherwise download the repo zip)
#   pwsh -File update.ps1 -Ref v1.2.0          (a tag or branch; default main)
# Testing hooks: -Target <fake .claude dir>, -ZipPath <local zip instead of downloading>, MODEL_GRADE_REPO env var.
param(
    [string]$Repo = $env:MODEL_GRADE_REPO,
    [string]$Ref = "main",
    [string]$Target = (Join-Path $HOME ".claude"),
    [string]$ZipPath = ""
)
$ErrorActionPreference = "Stop"
if (-not $Repo) { $Repo = "https://github.com/AndrewStifora/model-grade" }
$skill = Join-Path $Target "skills\model-grade"
$before = if (Test-Path (Join-Path $skill "VERSION")) { (Get-Content (Join-Path $skill "VERSION") -Raw).Trim() } else { "unknown" }

if (Test-Path (Join-Path $skill ".git")) {
    Write-Host "git clone detected, pulling $Ref from origin"
    git -C $skill fetch --quiet origin
    git -C $skill checkout --quiet $Ref
    git -C $skill pull --ff-only --quiet origin $Ref
} else {
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ("model-grade-update-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    if ($ZipPath) {
        $zip = $ZipPath
    } else {
        $zip = Join-Path $tmp "model-grade.zip"
        $url = "$Repo/archive/refs/heads/$Ref.zip"
        if ($Ref -match '^v?\d') { $url = "$Repo/archive/refs/tags/$Ref.zip" }
        Write-Host "downloading $url"
        Invoke-WebRequest -Uri $url -OutFile $zip
    }
    Expand-Archive -Path $zip -DestinationPath $tmp -Force
    $src = Get-ChildItem $tmp -Directory | Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } | Select-Object -First 1
    if (-not $src) { throw "the archive does not contain a SKILL.md at its top level" }
    if (Test-Path $skill) {
        $bak = "$skill.bak-" + (Get-Date -Format "yyyyMMdd-HHmmss")
        Move-Item -Path $skill -Destination $bak
        Write-Host "previous version moved to $bak"
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $skill) | Out-Null
    Copy-Item -Path $src.FullName -Destination $skill -Recurse
    Remove-Item -Path $tmp -Recurse -Force
}

# The alias and the executors live outside the skill folder; refresh them from assets.
$skillsDir = Join-Path $Target "skills"
$agentsDir = Join-Path $Target "agents"
New-Item -ItemType Directory -Force -Path (Join-Path $skillsDir "mg"), $agentsDir | Out-Null
Copy-Item -Path (Join-Path $skill "assets\mg\SKILL.md") -Destination (Join-Path $skillsDir "mg\SKILL.md") -Force
Copy-Item -Path (Join-Path $skill "assets\agents\*.md") -Destination $agentsDir -Force

$after = (Get-Content (Join-Path $skill "VERSION") -Raw).Trim()
Write-Host ""
Write-Host "model-grade $before -> $after   ($skill)"
Write-Host "alias /mg and executors mg-run-* refreshed in $skillsDir\mg and $agentsDir"
if (Test-Path (Join-Path $skill "CHANGELOG.md")) {
    Write-Host ""
    Get-Content (Join-Path $skill "CHANGELOG.md") -TotalCount 25
}
