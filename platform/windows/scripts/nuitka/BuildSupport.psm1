Set-StrictMode -Version Latest

function Resolve-ProjectPath {
    param([string]$ProjectRoot, [string]$Path)
    if ([IO.Path]::IsPathRooted($Path)) { return [IO.Path]::GetFullPath($Path) }
    return [IO.Path]::GetFullPath((Join-Path $ProjectRoot $Path))
}

function Get-BuildConfiguration {
    param([string]$ProjectRoot, [string]$PythonExecutable, [string]$OutputDirectory,
          [string]$OutputFilename, [string]$Variant)
    $pythonPath = Resolve-ProjectPath $ProjectRoot $PythonExecutable
    if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
        throw "Build interpreter does not exist: $pythonPath"
    }
    $metadata = & $pythonPath -X utf8 -c 'import json,sys,tomllib; print(json.dumps(tomllib.load(open(sys.argv[1], "rb"))))' (Join-Path $ProjectRoot 'pyproject.toml')
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read project metadata.' }
    $metadata = $metadata | ConvertFrom-Json
    $product = $metadata.tool.fin_calc
    if (-not $OutputFilename) { $OutputFilename = "$($product.'product-name').exe" }
    if ([IO.Path]::GetFileName($OutputFilename) -ne $OutputFilename -or
        [IO.Path]::GetExtension($OutputFilename) -ne '.exe') {
        throw 'OutputFilename must be a filename ending in .exe, without directories.'
    }
    if (-not $OutputDirectory) { $OutputDirectory = "build/$Variant" }
    $outputPath = Resolve-ProjectPath $ProjectRoot $OutputDirectory
    $repositoryRoot = [IO.Path]::GetFullPath((Join-Path $ProjectRoot '../..'))
    $icon = Join-Path $ProjectRoot 'assets/icon.ico'
    if (-not (Test-Path -LiteralPath $icon -PathType Leaf)) { throw "Missing icon: $icon" }
    [PSCustomObject]@{
        Python = $pythonPath; Output = $outputPath; Filename = $OutputFilename
        Title = $product.'product-name'; Version = $metadata.project.version
        Description = $metadata.project.description; Company = $product.'company-name'
        Copyright = $product.copyright; AppDataName = $product.'app-data-dir'
        Icon = $icon; RepositoryRoot = $repositoryRoot
    }
}

function Get-NuitkaArguments {
    param($Configuration, [string]$ConsoleMode, [switch]$Commercial)
    @('-m', 'nuitka', '--enable-plugin=pyside6', "--windows-console-mode=$ConsoleMode",
      '--msvc=latest', '--assume-yes-for-downloads',
      "--output-filename=$($Configuration.Filename)", "--output-dir=$($Configuration.Output)",
      "--windows-icon-from-ico=$($Configuration.Icon)",
      "--include-data-files=$($Configuration.Icon)=assets/icon.ico",
      "--product-name=$($Configuration.Title)", "--file-version=$($Configuration.Version)",
      "--product-version=$($Configuration.Version)", "--file-description=$($Configuration.Description)",
      "--company-name=$($Configuration.Company)", "--copyright=$($Configuration.Copyright)")
    if ($Commercial) { '--enable-plugin=data-hiding' }
}

function Show-PersistedData {
    param($Configuration, [switch]$Portable, [switch]$ResetRuntimeDefaults)
    $localRoot = $env:LOCALAPPDATA
    if (-not $localRoot) { $localRoot = Join-Path ([Environment]::GetFolderPath('UserProfile')) 'AppData/Local' }
    $paths = @(Join-Path $localRoot $Configuration.AppDataName)
    if ($Portable) { $paths += Join-Path $Configuration.Output "$($Configuration.AppDataName)-data" }
    if ($Configuration.AppDataName -ne 'fin-calc') {
        throw 'Unexpected application data folder; review reset targets before building.'
    }
    foreach ($path in $paths) {
        $absolutePath = [IO.Path]::GetFullPath($path)
        if (Test-Path -LiteralPath $absolutePath) {
            if (-not $ResetRuntimeDefaults) {
                Write-Warning "Persisted data at $absolutePath may affect smoke tests. Existing data is preserved."
                continue
            }
            $target = Get-Item -LiteralPath $absolutePath -Force
            $resolved = [IO.Path]::GetFullPath($target.FullName)
            $allowed = @('fin-calc', 'fin-calc-data')
            if ($resolved -ne $absolutePath -or $target.Name -notin $allowed -or -not $target.PSIsContainer) {
                throw "Refusing unexpected reset target: $resolved"
            }
            $entries = @($target) + @(Get-ChildItem -LiteralPath $resolved -Recurse -Force)
            if ($entries | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) {
                throw "Refusing to reset linked application data: $resolved"
            }
            try { Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction Stop }
            catch { throw "Cannot reset $resolved. Close running instances of Fin Calc and retry. $_" }
        }
    }
}

function Invoke-PrivacyScan {
    param($Configuration, [string]$ProjectRoot, [string]$DistPath, [switch]$Commercial)
    $hits = & $Configuration.Python (Join-Path $PSScriptRoot 'privacy_scan.py') $DistPath $ProjectRoot $Configuration.RepositoryRoot
    if ($LASTEXITCODE -ne 0) { throw 'Privacy scan could not inspect the build output.' }
    foreach ($hit in ($hits | ConvertFrom-Json)) {
        Write-Warning "Privacy scan found '$($hit.term)' in $($hit.file)"
    }
    if (-not $Commercial) { Write-Warning 'Program constants are not encrypted without -Commercial.' }
}

Export-ModuleMember -Function Resolve-ProjectPath, Get-BuildConfiguration, Get-NuitkaArguments, Show-PersistedData, Invoke-PrivacyScan
