[CmdletBinding()]
param(
    [string]$PythonExecutable = '.venv/Scripts/python.exe',
    [string]$OutputDirectory,
    [string]$OutputFilename,
    [switch]$Commercial,
    [switch]$UseCurrentDefaultPaths,
    [switch]$ResetRuntimeDefaults
)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
Import-Module (Join-Path $PSScriptRoot 'BuildSupport.psm1') -Force
$config = Get-BuildConfiguration $projectRoot $PythonExecutable $OutputDirectory $OutputFilename 'onefile'
$pythonPath = $config.Python
Write-Host "Building $($config.Title): onefile"
if ($UseCurrentDefaultPaths) {
    throw 'Fin Calc has no configurable default-path file. UseCurrentDefaultPaths is unsupported; live settings are never bundled.'
}
& $pythonPath -c 'import zstandard'
if ($LASTEXITCODE -ne 0) {
    throw "Compressed onefile builds require zstandard. Run: $pythonPath -m pip install 'nuitka[onefile]'"
}
Show-PersistedData $config -ResetRuntimeDefaults:$ResetRuntimeDefaults -Portable
$inputPath = Join-Path $projectRoot 'build/nuitka-inputs'
$null = New-Item -ItemType Directory -Path $inputPath -Force
[IO.File]::WriteAllBytes((Join-Path $inputPath 'portable.marker'), [byte[]]@())
$nuitkaArguments = @(Get-NuitkaArguments $config 'disable' -Commercial:$Commercial)
$nuitkaArguments += @('--onefile', '--include-data-files=build/nuitka-inputs/portable.marker=portable.marker', 'main.py')
$null = New-Item -ItemType Directory -Path $config.Output -Force
Push-Location $projectRoot
try {
    Write-Host "Output directory: $($config.Output)"
    & $pythonPath @nuitkaArguments
    if ($LASTEXITCODE -ne 0) { throw "Nuitka failed with exit code $LASTEXITCODE" }
    Invoke-PrivacyScan $config $projectRoot (Join-Path $config.Output 'main.dist') -Commercial:$Commercial
} finally { Pop-Location }
