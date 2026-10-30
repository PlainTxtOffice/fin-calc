[CmdletBinding()]
param(
    [string]$PythonExecutable = '.venv/Scripts/python.exe',
    [string]$OutputDirectory,
    [string]$OutputFilename,
    [switch]$Commercial,
    [switch]$UseCurrentDefaultPaths,
    [switch]$ResetRuntimeDefaults,
    [switch]$Console
)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
Import-Module (Join-Path $PSScriptRoot 'BuildSupport.psm1') -Force
$variant = if ($Console) { 'standalone-console' } else { 'standalone' }
$config = Get-BuildConfiguration $projectRoot $PythonExecutable $OutputDirectory $OutputFilename $variant
$pythonPath = $config.Python
Write-Host "Building $($config.Title): $variant"
if ($UseCurrentDefaultPaths) {
    throw 'Fin Calc has no configurable default-path file. UseCurrentDefaultPaths is unsupported; live settings are never bundled.'
}
Show-PersistedData $config -ResetRuntimeDefaults:$ResetRuntimeDefaults
$consoleMode = if ($Console) { 'force' } else { 'disable' }
$nuitkaArguments = @(Get-NuitkaArguments $config $consoleMode -Commercial:$Commercial)
$nuitkaArguments += @('--standalone', 'main.py')
$null = New-Item -ItemType Directory -Path $config.Output -Force
Push-Location $projectRoot
try {
    Write-Host "Output directory: $($config.Output)"
    & $pythonPath @nuitkaArguments
    if ($LASTEXITCODE -ne 0) { throw "Nuitka failed with exit code $LASTEXITCODE" }
    $distPath = Join-Path $config.Output 'main.dist'
    Invoke-PrivacyScan $config $projectRoot $distPath -Commercial:$Commercial
    $validateScript = Join-Path $PSScriptRoot 'validate_release.ps1'
    & $validateScript -DistPath $distPath
    if ($LASTEXITCODE -ne 0) { throw 'Release validation failed.' }
} finally { Pop-Location }
