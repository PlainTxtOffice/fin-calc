[CmdletBinding()]
param([string]$DistPath = 'build/standalone/main.dist')
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
Import-Module (Join-Path $PSScriptRoot 'BuildSupport.psm1') -Force
$distPath = Resolve-ProjectPath $projectRoot $DistPath
$pythonPath = Join-Path $projectRoot '.venv/Scripts/python.exe'
try {
    $problems = & $pythonPath (Join-Path $PSScriptRoot 'validate_dist.py') $distPath $projectRoot
    if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect distribution.' }
    $problems = @($problems | ConvertFrom-Json)
    if ($problems.Count) {
        foreach ($problem in $problems) { Write-Host $problem }
        exit 1
    }
    Write-Host "Clean distribution: $distPath"
    exit 0
} catch {
    Write-Host $_.Exception.Message
    exit 1
}
