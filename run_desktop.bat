@echo off
REM TalkBridge Desktop Launcher - Windows
REM =====================================

cd /d "%~dp0"

echo ========================================
echo    TalkBridge Desktop Application
echo ========================================
echo.

echo [1/3] Checking Python...

REM Check that Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found in PATH
    echo    Please install Python 3.8 or higher from:
    echo    https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Python available
)

echo [2/3] Checking PyQt6...

REM Check PyQt6
python -c "from PyQt6.QtWidgets import QApplication" >nul 2>&1
if errorlevel 1 (
    echo ❌ PyQt6 not found
    echo    Installing PyQt6...
    python -m pip install PyQt6 PyYAML
    if errorlevel 1 (
        echo ❌ Error installing dependencies
        pause
        exit /b 1
    )
    echo ✅ PyQt6 installed successfully
) else (
    echo ✅ PyQt6 available
)

echo [3/3] Starting TalkBridge Desktop...
echo.

REM Run application
python src/desktop/main.py

REM Check result
if errorlevel 1 (
    echo.
    echo ❌ Error running the application
    echo    Check the logs in data/logs/desktop.log
    echo.
    pause
) else (
    echo.
    echo ✅ Application ran successfully
)