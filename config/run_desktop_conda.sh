#!/bin/bash
# TalkBridge Desktop - Quick Start Script (Conda)
# ==============================================

echo ""
echo "🚀 TalkBridge Desktop - Conda Environment"
echo "==========================================="
echo ""

# Change to project root directory (parent of config)
cd "$(dirname "$0")/.."

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found in PATH"
    echo "Please install Miniconda or Anaconda and restart your terminal"
    echo "Download: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Initialize conda for this shell
eval "$(conda shell.bash hook)"

# Check if environment exists
if ! conda env list | grep -q "talkbridge-desktop"; then
    echo "🔧 Environment not found. Creating TalkBridge Desktop environment..."
    echo "This may take several minutes..."
    echo ""
    cd config
    python setup_conda_desktop.py
    cd ..
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create environment"
        exit 1
    fi
fi

echo "✅ Activating TalkBridge Desktop environment..."
conda activate talkbridge-desktop

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Environment activated successfully!"
    echo ""
    echo "Available commands:"
    echo "  python src/desktop/main.py     - Start desktop application"
    echo "  pytest src/desktop/            - Run tests"
    echo "  conda deactivate               - Exit environment"
    echo ""
    
    # Start a new shell with the environment activated
    exec bash
else
    echo "❌ Failed to activate environment"
    exit 1
fi
