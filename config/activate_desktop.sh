#!/bin/bash
# TalkBridge Desktop - Conda Environment Activation Script
# =========================================================

echo ""
echo "🚀 Activating TalkBridge Desktop Environment..."
echo ""

# Initialize conda for shell
eval "$(conda shell.bash hook)"

# Activate environment
conda activate talkbridge-desktop-env

if [ $? -eq 0 ]; then
    echo "✓ Environment activated successfully!"
    echo ""
    echo "Available commands:"
    echo "  python src/desktop/main.py    - Start desktop application"
    echo "  pytest src/desktop/           - Run tests"
    echo ""
    echo "To deactivate: conda deactivate"
    echo ""
    
    # Start a new shell with the environment activated
    exec bash
else
    echo "❌ Desktop environment not found"
    echo "Please run: conda env create -f environment-desktop.yaml"
    exit 1
fi
