param([switch]$SkipRehearsal, [switch]$SkipBuild)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$python = Join-Path $repo '.venv\Scripts\python.exe'
$weights = Join-Path $repo 'models\weights\bearing_real_3class.pt'
$runtime = Join-Path $repo '.demo-runtime'

foreach ($required in @($python, $weights, (Join-Path $repo 'storage\raw\d1c83ab19c7b467082bf513c8516d378.jpg'))) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Demo preflight failed: missing $required" }
}

Push-Location $repo
try {
    $localEnvironment = Join-Path $repo '.env.local'
    if (Test-Path -LiteralPath $localEnvironment -PathType Leaf) {
        foreach ($line in Get-Content -LiteralPath $localEnvironment) {
            $trimmed = $line.Trim()
            if (-not $trimmed -or $trimmed.StartsWith('#') -or -not $trimmed.Contains('=')) { continue }
            $name, $value = $trimmed.Split('=', 2)
            [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim().Trim('"').Trim("'"), 'Process')
        }
        Write-Host 'Loaded local configuration from .env.local (values hidden).'
    }
    if (-not $SkipRehearsal) {
        Write-Host '[1/5] Running four-case rehearsal gate...'
        & $python 'scripts\rehearse_demo.py'
        if ($LASTEXITCODE -ne 0) { throw 'Prepared-case rehearsal failed.' }
    }
    if (-not $SkipBuild) {
        Write-Host '[2/5] Building presentation frontend...'
        & npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
    }

    New-Item -ItemType Directory -Path $runtime -Force | Out-Null
    $env:YOLO_CONFIG_DIR = Join-Path $runtime 'ultralytics'
    Write-Host '[3/5] Starting local API...'
    $apiHealthy = $false
    try { $existing = Invoke-RestMethod 'http://127.0.0.1:8000/api/health' -TimeoutSec 2; $apiHealthy = $existing.service -eq 'EXtendQuality API' } catch {}
    if (-not $apiHealthy) {
        $api = Start-Process -FilePath $python -ArgumentList @('-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000') -WorkingDirectory $repo -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtime 'api.out.log') -RedirectStandardError (Join-Path $runtime 'api.err.log') -PassThru
        Set-Content -LiteralPath (Join-Path $runtime 'api.pid') -Value $api.Id
    }
    for ($attempt = 0; $attempt -lt 30 -and -not $apiHealthy; $attempt++) {
        Start-Sleep -Milliseconds 500
        try { $health = Invoke-RestMethod 'http://127.0.0.1:8000/api/health' -TimeoutSec 2; $apiHealthy = $health.service -eq 'EXtendQuality API' } catch {}
    }
    if (-not $apiHealthy) { throw 'API did not become healthy. Check .demo-runtime\api.err.log.' }

    Write-Host '[4/5] Warming YOLO in the live API process...'
    try {
        $warmup = Invoke-RestMethod 'http://127.0.0.1:8000/api/warmup' -Method Post -TimeoutSec 30
    } catch {
        throw 'Port 8000 is serving an outdated or unrelated API. Close that process and rerun start_demo.ps1.'
    }
    if (-not $warmup.model_ready) { throw "YOLO warm-up degraded: $($warmup.model_version)" }

    Write-Host '[5/5] Starting presentation frontend...'
    $frontendHealthy = $false
    try { $page = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:3000/' -TimeoutSec 2; $frontendHealthy = $page.StatusCode -eq 200 -and $page.Content -match 'EXtendQuality' } catch {}
    if (-not $frontendHealthy) {
        $npm = (Get-Command npm.cmd).Source
        $frontend = Start-Process -FilePath $npm -ArgumentList @('run','start') -WorkingDirectory $repo -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtime 'frontend.out.log') -RedirectStandardError (Join-Path $runtime 'frontend.err.log') -PassThru
        Set-Content -LiteralPath (Join-Path $runtime 'frontend.pid') -Value $frontend.Id
    }
    for ($attempt = 0; $attempt -lt 90 -and -not $frontendHealthy; $attempt++) {
        Start-Sleep -Milliseconds 500
        try { $page = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:3000/' -TimeoutSec 2; $frontendHealthy = $page.StatusCode -eq 200 -and $page.Content -match 'EXtendQuality' } catch {}
    }
    if (-not $frontendHealthy) { throw 'Frontend did not become healthy. Check .demo-runtime\frontend.err.log.' }
    $listener = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($listener) { Set-Content -LiteralPath (Join-Path $runtime 'frontend-listener.pid') -Value $listener.OwningProcess }
    $visualizer = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:3000/inspection-visualizer' -TimeoutSec 5
    if ($visualizer.StatusCode -ne 200 -or $visualizer.Content -notmatch 'LIVE PROCESS TRACE') { throw 'Inspection visualizer readiness check failed.' }

    Write-Host ''
    Write-Host 'EXtendQuality demo is READY.' -ForegroundColor Green
    Write-Host "YOLO: $($warmup.model_version) warmed in $($warmup.warmup_time_ms) ms"
    Write-Host 'Dashboard:  http://localhost:3000/'
    Write-Host 'Visualizer: http://localhost:3000/inspection-visualizer'
    Write-Host 'API docs:   http://127.0.0.1:8000/docs'
} finally { Pop-Location }
