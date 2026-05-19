$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path $projectRoot ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"
$distDir = Join-Path $projectRoot "dist"
$buildDir = Join-Path $projectRoot "build"
$specPath = Join-Path $projectRoot "AulaTrack.spec"
$iconSvg = Join-Path $projectRoot "assets\app_icon.svg"
$iconIco = Join-Path $projectRoot "assets\app_icon.ico"

if (-not (Test-Path $pythonExe)) {
    Write-Host "No existe .venv. Ejecuta primero .\run.ps1 o crea el entorno virtual." -ForegroundColor Yellow
    exit 1
}

Write-Host "Instalando dependencias base..." -ForegroundColor Cyan
& $pipExe install -r (Join-Path $projectRoot "requirements.txt")

Write-Host "Instalando PyInstaller..." -ForegroundColor Cyan
& $pipExe install pyinstaller

if (Test-Path $iconSvg) {
    Write-Host "Generando icono .ico..." -ForegroundColor Cyan
    & $pythonExe (Join-Path $projectRoot "scripts\generate_icon.py")
}

if (Test-Path $distDir) {
    Remove-Item -Recurse -Force $distDir
}
if (Test-Path $buildDir) {
    Remove-Item -Recurse -Force $buildDir
}
if (Test-Path $specPath) {
    Remove-Item -Force $specPath
}

Write-Host "Generando build de Windows..." -ForegroundColor Green
& $pythonExe -m PyInstaller `
    --noconfirm `
    --windowed `
    --name AulaTrack `
    --icon $iconIco `
    --add-data "assets;assets" `
    --add-data "database\schema.sql;database" `
    main.py

$outputAppDir = Join-Path $distDir "AulaTrack"
$outputDataDir = Join-Path $outputAppDir "data"
if (-not (Test-Path $outputDataDir)) {
    New-Item -ItemType Directory -Path $outputDataDir | Out-Null
}

Write-Host "Build listo en: $outputAppDir" -ForegroundColor Green
