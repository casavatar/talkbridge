# TalkBridge Desktop Launcher (Conda Environment) - PowerShell
# ============================================================
# Launches the desktop UI using conda environment with unified logging.

# Error handling
$ErrorActionPreference = "Stop"

# Colors for output (PowerShell equivalent)
function Write-ColoredText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

# Resolve project root - this ensures the script works regardless of where it's called from
$scriptPath = $MyInvocation.MyCommand.Path
$rootDir = Split-Path $scriptPath -Parent
Set-Location $rootDir

Write-ColoredText "🚀 Launching TalkBridge Desktop with Conda..." "Green"
Write-ColoredText "📁 Project root: $rootDir" "Cyan"

# Conda environment configuration
$condaEnv = "talkbridge-desktop-env"

# Try to detect conda base directory
$condaBase = $null
$condaCommand = Get-Command conda -ErrorAction SilentlyContinue

if ($condaCommand) {
    $condaPath = $condaCommand.Source
    if (![string]::IsNullOrWhiteSpace($condaPath)) {
        try {
            $condaBase = Split-Path (Split-Path $condaPath -Parent) -Parent
        } catch {
            Write-ColoredText "❌ Failed to parse Conda path: $condaPath" "Red"
        }
    } else {
        Write-ColoredText "⚠️  Conda command found, but path is empty or invalid." "Yellow"
    }
} else {
    Write-ColoredText "❌ Conda is not available in your PATH. Please activate Conda first or add it to PATH." "Red"
}

# Alternative: Check common conda installation paths on Windows
if (-not $condaBase -or -not (Test-Path $condaBase)) {
    $possiblePaths = @(
        "$env:USERPROFILE\miniconda3",
        "$env:USERPROFILE\anaconda3",
        "$env:ProgramData\miniconda3",
        "$env:ProgramData\anaconda3",
        "C:\miniconda3",
        "C:\anaconda3"
    )

    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $condaBase = $path
            break
        }
    }
}

if (-not $condaBase) {
    Write-ColoredText "❌ Could not find conda installation" "Red"
    Write-ColoredText "👉 Please install Miniconda or Anaconda" "Yellow"
    Write-ColoredText "👉 Download: https://docs.conda.io/en/latest/miniconda.html" "Yellow"
    exit 1
}

Write-ColoredText "🐍 Conda environment: $condaEnv" "Cyan"
Write-ColoredText "📂 Conda base: $condaBase" "Cyan"

# Check if conda environment exists
$envPath = "$condaBase\envs\$condaEnv"
if (-not (Test-Path $envPath)) {
    Write-ColoredText "❌ Conda environment $condaEnv not found at $envPath" "Red"
    Write-ColoredText "👉 Create it with: conda create -n $condaEnv python=3.11" "Yellow"
    Write-ColoredText "👉 Then install dependencies: conda activate $condaEnv && pip install -r requirements.txt" "Yellow"
    exit 1
}

# Initialize conda in PowerShell
$condaHook = "$condaBase\shell\condabin\conda-hook.ps1"
if (Test-Path $condaHook) {
    Write-ColoredText "🔧 Initializing conda..." "Green"
    . $condaHook
} else {
    Write-ColoredText "❌ conda-hook.ps1 not found at $condaHook" "Red"
    Write-ColoredText "👉 Cannot initialize conda. Please check your conda installation." "Yellow"
    exit 1
}

# Activate conda environment
Write-ColoredText "🔄 Activating conda environment: $condaEnv" "Green"

try {
    conda activate $condaEnv

    # Verify we're in the correct environment
    $currentEnv = conda info --envs | Select-String '\*' | ForEach-Object { ($_ -split '\s+')[0] }

    if ($currentEnv -ne $condaEnv) {
        Write-ColoredText "❌ Failed to activate $condaEnv. Current environment: $currentEnv" "Red"
        exit 1
    }

    Write-ColoredText "✅ Conda environment activated: $condaEnv" "Green"

    # Get Python path
    $pythonPath = (Get-Command python).Source
    Write-ColoredText "🐍 Python path: $pythonPath" "Cyan"

    # Ensure logs directory exists
    $logDir = "$rootDir\data\logs"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    Write-ColoredText "📄 Logs directory: $logDir" "Green"

    # Check if the desktop module can be imported
    Write-ColoredText "🔍 Checking TalkBridge desktop module..." "Cyan"

    $importTest = python -c "import sys; sys.path.insert(0, 'src'); import desktop" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-ColoredText "❌ Cannot import desktop module from src/" "Red"
        Write-ColoredText "👉 Make sure you've installed the package with:" "Yellow"
        Write-ColoredText "   conda activate $condaEnv" "Yellow"
        Write-ColoredText "   pip install -e ." "Yellow"
        exit 1
    }

    # Run desktop app with logging
    Write-ColoredText "🎯 Starting TalkBridge Desktop Application..." "Green"
    Write-ColoredText "📊 Logs will be written to: $logDir\desktop.log" "Cyan"
    Write-Host ""

    # Start the application with logging (PowerShell equivalent of tee)
    $logFile = "$logDir\desktop.log"
    $env:PYTHONPATH = "src;$env:PYTHONPATH"
    python -m desktop.main $args 2>&1 | Tee-Object -FilePath $logFile

} catch {
    Write-ColoredText "❌ Error: $($_.Exception.Message)" "Red"
    exit 1
}