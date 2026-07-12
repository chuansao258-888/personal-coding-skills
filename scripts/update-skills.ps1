[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

Push-Location $repoRoot
try {
    $dirty = git status --porcelain
    if ($LASTEXITCODE -ne 0) {
        throw 'Unable to inspect repository status.'
    }
    if ($dirty) {
        throw 'The repository has local changes. Commit, discard, or resolve them before pulling.'
    }

    git pull --ff-only
    if ($LASTEXITCODE -ne 0) {
        throw 'git pull --ff-only failed.'
    }

    & (Join-Path $PSScriptRoot 'validate-skills.ps1')
}
finally {
    Pop-Location
}
