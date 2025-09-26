# TalkBridge Desktop - Conda Environment Activation Script (PowerShell)
# ====================================================================

Write-Host ""
Write-Host "🚀 Activating TalkBridge Desktop Environment..." -ForegroundColor Green
Write-Host ""

# Check if conda is available
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Conda not found in PATH" -ForegroundColor Red
    Write-Host "Please install Miniconda or Anaconda and restart PowerShell" -ForegroundColor Yellow
    Write-Host "Download: https://docs.conda.io/en/latest/miniconda.html" -ForegroundColor Yellow
    exit 1
}

# Initialize conda for PowerShell (if not already done)
$condaPath = (Get-Command conda).Source
$condaBase = Split-Path (Split-Path $condaPath -Parent) -Parent

# Import conda PowerShell module if available
$condaHook = "$condaBase\shell\condabin\conda-hook.ps1"
if (Test-Path $condaHook) {
    . $condaHook
}

# Activate environment
Write-Host "Activating conda environment: talkbridge-desktop-env..." -ForegroundColor Cyan

try {
    conda activate talkbridge-desktop-env

    # Check if activation was successful
    $env:CONDA_DEFAULT_ENV = "talkbridge-desktop-env"

    Write-Host "✓ Environment activated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Yellow
    Write-Host "  python src/desktop/main.py    - Start desktop application" -ForegroundColor White
    Write-Host "  pytest src/desktop/           - Run tests" -ForegroundColor White
    Write-Host ""
    Write-Host "To deactivate: conda deactivate" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Environment is now active in this PowerShell session." -ForegroundColor Green
}
catch {
    Write-Host "❌ Desktop environment not found" -ForegroundColor Red
    Write-Host "Please run: conda env create -f environment-desktop.yaml" -ForegroundColor Yellow
    exit 1
}