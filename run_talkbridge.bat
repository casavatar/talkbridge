@echo off
REM TalkBridge Launcher with Conda Environment
REM This script activates the conda environment and runs TalkBridge

echo Starting TalkBridge with conda environment...
echo.

REM Activate conda environment
call C:\Users\ingek\miniconda3\Scripts\activate.bat talkbridge

REM Run the application
python app.py

pause 