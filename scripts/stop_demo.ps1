$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$runtime = Join-Path $repo '.demo-runtime'

function Stop-ProcessTree([int]$RootId) {
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $RootId" -ErrorAction SilentlyContinue
    foreach ($child in $children) { Stop-ProcessTree -RootId $child.ProcessId }
    if (Get-Process -Id $RootId -ErrorAction SilentlyContinue) { Stop-Process -Id $RootId -Force }
}

foreach ($entry in @(@('api','api.pid'), @('frontend listener','frontend-listener.pid'), @('frontend wrapper','frontend.pid'))) {
    $name = $entry[0]
    $pidFile = Join-Path $runtime $entry[1]
    if (-not (Test-Path -LiteralPath $pidFile -PathType Leaf)) { continue }
    $processId = [int](Get-Content -LiteralPath $pidFile -Raw)
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($process) { Stop-ProcessTree -RootId $processId; Write-Host "Stopped $name process tree $processId." }
}
