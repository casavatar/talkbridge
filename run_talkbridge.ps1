# TalkBridge Launcher with Conda Environment
# This script activates the conda environment and runs TalkBridge

Write-Host "Starting TalkBridge with conda environment..." -ForegroundColor Green
Write-Host ""

# Activate conda environment
& C:\Users\ingek\miniconda3\Scripts\activate.bat talkbridge

# Run the application
python app.py

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 