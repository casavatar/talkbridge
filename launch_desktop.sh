#!/usr/bin/env bash
set -euo pipefail

# TalkBridge Desktop Launcher (Conda Environment)
# ===============================================
# Launches the desktop UI using conda environment with unified logging.

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Resolve project root - this ensures the script works regardless of where it's called from
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$ROOT_DIR"

echo -e "${GREEN}🚀 Launching TalkBridge Desktop with Conda...${NC}"
echo -e "${BLUE}📁 Project root: $ROOT_DIR${NC}"

# Conda environment configuration
CONDA_ENV="talkbridge-desktop-env"
CONDA_BASE="/home/ingek/miniconda3"

echo -e "${BLUE}🐍 Conda environment: $CONDA_ENV${NC}"
echo -e "${BLUE}📂 Conda base: $CONDA_BASE${NC}"

# Check if conda environment exists
if [ ! -d "$CONDA_BASE/envs/$CONDA_ENV" ]; then
    echo -e "${RED}❌ Conda environment $CONDA_ENV not found at $CONDA_BASE/envs/$CONDA_ENV${NC}"
    echo -e "${YELLOW}👉 Create it with: conda create -n $CONDA_ENV python=3.11${NC}"
    echo -e "${YELLOW}👉 Then install dependencies: conda activate $CONDA_ENV && pip install -r requirements.txt${NC}"
    exit 1
fi

# Initialize conda in this shell
if [ -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
    echo -e "${GREEN}🔧 Initializing conda...${NC}"
    source "$CONDA_BASE/etc/profile.d/conda.sh"
else
    echo -e "${RED}❌ conda.sh not found at $CONDA_BASE/etc/profile.d/conda.sh${NC}"
    echo -e "${YELLOW}👉 Cannot initialize conda. Please check your conda installation.${NC}"
    exit 1
fi

# Activate conda environment
echo -e "${GREEN}🔄 Activating conda environment: $CONDA_ENV${NC}"
conda activate "$CONDA_ENV"

# Verify we're in the correct environment
CURRENT_ENV=$(conda info --envs | grep '\*' | awk '{print $1}')
if [ "$CURRENT_ENV" != "$CONDA_ENV" ]; then
    echo -e "${RED}❌ Failed to activate $CONDA_ENV. Current environment: $CURRENT_ENV${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Conda environment activated: $CONDA_ENV${NC}"
echo -e "${BLUE}🐍 Python path: $(which python)${NC}"

# Ensure logs directory exists
LOG_DIR="$ROOT_DIR/data/logs"
mkdir -p "$LOG_DIR"
echo -e "${GREEN}📄 Logs directory: $LOG_DIR${NC}"

# Check if the desktop module can be imported (without importing main.py directly)
echo -e "${BLUE}🔍 Checking TalkBridge desktop module...${NC}"
if ! python -c "import sys; sys.path.insert(0, 'src'); import desktop" 2>/dev/null; then
    echo -e "${RED}❌ Cannot import desktop module from src/${NC}"
    echo -e "${YELLOW}👉 Make sure you've installed the package with:${NC}"
    echo -e "${YELLOW}   conda activate $CONDA_ENV${NC}"
    echo -e "${YELLOW}   pip install -e .${NC}"
    exit 1
fi

# Run desktop app with logging
echo -e "${GREEN}🎯 Starting TalkBridge Desktop Application...${NC}"
echo -e "${BLUE}📊 Logs will be written to: $LOG_DIR/desktop.log${NC}"
echo ""

export PYTHONPATH="src:$PYTHONPATH"
exec python -m desktop.main "$@" \
    2>&1 | tee "$LOG_DIR/desktop.log"
