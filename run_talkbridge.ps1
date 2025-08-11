# TalkBridge Launcher with Conda Environment
# This script uses the conda environment Python directly

Write-Host "Starting TalkBridge with conda environment..." -ForegroundColor Green
Write-Host ""

# Run the application with conda Python directly
& C:\Users\ingek\miniconda3\envs\talkbridge\python.exe app.py

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 