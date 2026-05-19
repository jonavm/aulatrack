$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path $projectRoot ".venv"
$pythonExe = Join-Path $venvPath "Scripts\\python.exe"
$pipExe = Join-Path $venvPath "Scripts\\pip.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "Creando entorno virtual en .venv..." -ForegroundColor Cyan
    $systemPython = Get-Command python -ErrorAction SilentlyContinue
    if (-not $systemPython) {
        $systemPython = Get-Command py -ErrorAction SilentlyContinue
    }

    if (-not $systemPython) {
        throw "No se encontro Python en el sistema. Instala Python 3.11+ y vuelve a intentarlo."
    }

    if ($systemPython.Name -eq "py.exe" -or $systemPython.Name -eq "py") {
        & $systemPython.Source -m venv $venvPath
    } else {
        & $systemPython.Source -m venv $venvPath
    }
}

Write-Host "Instalando dependencias..." -ForegroundColor Cyan
& $pipExe install -r (Join-Path $projectRoot "requirements.txt")

Write-Host "Iniciando AulaTrack..." -ForegroundColor Green
& $pythonExe (Join-Path $projectRoot "main.py")

