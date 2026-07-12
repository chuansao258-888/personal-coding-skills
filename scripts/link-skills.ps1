[CmdletBinding()]
param(
    [string]$DiscoveryRoot = (Join-Path $HOME '.codex\skills'),
    [ValidateSet('Junction', 'SymbolicLink', 'Copy')]
    [string]$Mode = 'Junction',
    [switch]$ReplaceExisting
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$manifest = Get-Content -Raw -Encoding utf8 -LiteralPath (Join-Path $repoRoot 'skills-manifest.json') |
    ConvertFrom-Json
$resolvedDiscoveryRoot = [System.IO.Path]::GetFullPath($DiscoveryRoot)
$backupRoot = Join-Path $HOME ("codex-skill-backups\" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$backupCreated = $false

& (Join-Path $PSScriptRoot 'validate-skills.ps1')

New-Item -ItemType Directory -Force -Path $resolvedDiscoveryRoot | Out-Null

foreach ($entry in $manifest.skills) {
    $source = (Resolve-Path (Join-Path $repoRoot $entry.path)).Path
    $destination = Join-Path $resolvedDiscoveryRoot $entry.name
    $movedBackup = $null

    if (Test-Path -LiteralPath $destination) {
        $existing = Get-Item -Force -LiteralPath $destination
        $existingTargets = @($existing.Target) | ForEach-Object {
            if ($_ -and [System.IO.Path]::IsPathRooted($_)) {
                [System.IO.Path]::GetFullPath($_)
            }
        }
        if ($existing.LinkType -and $existingTargets -contains $source) {
            Write-Host "Already linked: $($entry.name)"
            continue
        }
        if (-not $ReplaceExisting) {
            throw "Destination already exists: $destination. Re-run with -ReplaceExisting after reviewing it."
        }

        if (-not $backupCreated) {
            New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
            $backupCreated = $true
        }
        $movedBackup = Join-Path $backupRoot $entry.name
        Move-Item -LiteralPath $destination -Destination $movedBackup
        Write-Host "Backed up: $destination -> $movedBackup"
    }

    try {
        if ($Mode -eq 'Copy') {
            Copy-Item -Recurse -LiteralPath $source -Destination $destination
        }
        else {
            New-Item -ItemType $Mode -Path $destination -Target $source | Out-Null
        }
        Write-Host "$Mode created: $destination -> $source"
    }
    catch {
        if ($movedBackup -and -not (Test-Path -LiteralPath $destination)) {
            Move-Item -LiteralPath $movedBackup -Destination $destination
            Write-Warning "Link creation failed; restored original directory: $destination"
        }
        throw
    }
}

if ($Mode -eq 'Copy') {
    Write-Warning 'Copy mode does not provide live synchronization. Prefer Junction or SymbolicLink.'
}
if ($backupCreated) {
    Write-Host "Backups retained at: $backupRoot"
}
