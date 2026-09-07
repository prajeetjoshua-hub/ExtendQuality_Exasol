param([switch]$Full)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$failures = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()
$passes = [System.Collections.Generic.List[string]]::new()

function Pass([string]$Message) {
    $passes.Add($Message)
    Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Fail([string]$Message) {
    $failures.Add($Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Warn([string]$Message) {
    $warnings.Add($Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Require-File([string]$RelativePath, [int64]$MinimumBytes = 1) {
    $path = Join-Path $repo $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Fail "Missing required file: $RelativePath"
        return
    }
    $item = Get-Item -LiteralPath $path
    if ($item.Length -lt $MinimumBytes) {
        Fail "Required file is unexpectedly small: $RelativePath ($($item.Length) bytes)"
        return
    }
    Pass "$RelativePath ($($item.Length) bytes)"
}

function Test-Command([string]$Name) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) { Pass "$Name is available" } else { Fail "$Name is not available on PATH" }
}

function Test-Port([int]$Port, [string]$ExpectedUrl, [string]$ExpectedText) {
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $listener) {
        Pass "Port $Port is free"
        return
    }
    try {
        $response = Invoke-WebRequest -UseBasicParsing $ExpectedUrl -TimeoutSec 3
        if ($response.StatusCode -eq 200 -and $response.Content -match [regex]::Escape($ExpectedText)) {
            Warn "Port $Port already hosts EXtendQuality (PID $($listener.OwningProcess)); stop or reuse it deliberately"
        } else {
            Fail "Port $Port is occupied by an unexpected service (PID $($listener.OwningProcess))"
        }
    } catch {
        Fail "Port $Port is occupied but did not answer as EXtendQuality (PID $($listener.OwningProcess))"
    }
}

Write-Host 'EXtendQuality - SSN event readiness' -ForegroundColor Cyan
Write-Host "Repository: $repo"
Write-Host "Mode: $(if ($Full) { 'FULL' } else { 'FAST' })"
Write-Host ''

Test-Command 'npm.cmd'
Require-File '.venv\Scripts\python.exe' 10000
Require-File 'models\weights\bearing_real_3class.pt' 1000000
Require-File 'docs\EXtendQuality_SSN_Vision_to_Venture.pptx' 100000
Require-File 'docs\ssn_timed_pitch_script.md' 1000
Require-File 'docs\ssn_judge_qa.md' 1000

$preparedCases = @(
    'storage\raw\d1c83ab19c7b467082bf513c8516d378.jpg',
    'storage\raw\974fdfd1b1564360a8a5c16bd648fd3c.jpg',
    'storage\raw\7f8e3e9a4924486a8ef38419bd878cd3.jpg',
    'storage\raw\6df2224d3a4c45409d6b2526b47e28c4.jpg'
)
foreach ($case in $preparedCases) { Require-File $case 10000 }

$provider = if ($env:EXTENDQUALITY_VLM_PROVIDER) { $env:EXTENDQUALITY_VLM_PROVIDER.ToLowerInvariant() } else { 'demo' }
if ($provider -eq 'gemini') {
    if ($env:EXTENDQUALITY_VLM_API_KEY) {
        Pass 'Gemini mode selected and API key is present (value hidden)'
    } else {
        Fail 'Gemini mode is selected but EXTENDQUALITY_VLM_API_KEY is missing'
    }
} elseif ($provider -eq 'demo') {
    Warn 'Offline demo VLM fallback is selected; never describe its output as Gemini'
} else {
    Warn "VLM provider '$provider' is not the rehearsed event configuration"
}

Test-Port 8000 'http://127.0.0.1:8000/api/health' 'EXtendQuality API'
Test-Port 3000 'http://127.0.0.1:3000/' 'EXtendQuality'

if ($Full -and $failures.Count -eq 0) {
    Push-Location $repo
    try {
        Write-Host ''
        Write-Host '[FULL] Running backend tests...'
        & '.\.venv\Scripts\python.exe' -m pytest backend\tests -q
        if ($LASTEXITCODE -eq 0) { Pass 'Backend test suite passed' } else { Fail 'Backend test suite failed' }

        Write-Host '[FULL] Running frontend build and rendered-HTML tests...'
        & npm.cmd test
        if ($LASTEXITCODE -eq 0) { Pass 'Frontend build and test suite passed' } else { Fail 'Frontend build or test suite failed' }

        Write-Host '[FULL] Running isolated four-case rehearsal...'
        & '.\.venv\Scripts\python.exe' scripts\rehearse_demo.py
        if ($LASTEXITCODE -eq 0) { Pass 'Four-case rehearsal passed' } else { Fail 'Four-case rehearsal failed' }
    } finally {
        Pop-Location
    }
} elseif ($Full) {
    Warn 'Full executable checks were skipped because static preflight already failed'
}

Write-Host ''
Write-Host "Summary: $($passes.Count) passed, $($warnings.Count) warning(s), $($failures.Count) failure(s)."
if ($warnings.Count -gt 0) {
    Write-Host 'Warnings:' -ForegroundColor Yellow
    foreach ($warning in $warnings) { Write-Host "  - $warning" }
}
if ($failures.Count -gt 0) {
    Write-Host 'NO-GO - resolve every failure before presenting.' -ForegroundColor Red
    exit 1
}

Write-Host 'GO - readiness gate passed.' -ForegroundColor Green
if (-not $Full) { Write-Host 'Run again with -Full after code, model, dependency, or laptop changes.' }
exit 0
