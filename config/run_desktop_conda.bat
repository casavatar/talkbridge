@echo off
REM TalkBridge Desktop - Quick Start Script (Conda)
REM ==============================================

echo.
echo 🚀 TalkBridge Desktop - Conda Environment
echo ===========================================
echo.

REM Change to project root directory (parent of config)
cd /d "%~dp0\.."

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Conda not found in PATH
    echo Please install Miniconda or Anaconda and restart your terminal
    echo Download: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

REM Check if environment exists
conda env list | findstr "talkbridge-desktop" >nul
if %ERRORLEVEL% NEQ 0 (
    echo 🔧 Environment not found. Creating TalkBridge Desktop environment...
    echo This may take several minutes...
    echo.
    cd config
    python setup_conda_desktop.py
    cd ..
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Environment created successfully
    ) else (
        echo ❌ Failed to create environment
        pause
        exit /b 1
    )
)

echo ✅ Activating TalkBridge Desktop environment...
call conda activate talkbridge-desktop

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 🎉 Environment activated successfully!
    echo.
    echo Available commands:
    echo   python src/desktop/main.py     - Start desktop application
    echo   pytest src/desktop/            - Run tests
    echo   conda deactivate               - Exit environment
    echo.
    
    REM Keep the window open with activated environment
    cmd /k
) else (
    echo ❌ Failed to activate environment
    pause
)
