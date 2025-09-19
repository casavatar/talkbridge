#!/usr/bin/env bash
set -euo pipefail

# TalkBridge Desktop Launcher
# ==========================
# Launches the desktop UI with clean paths, virtual environment support, and unified logging.

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Resolve project root - this ensures the script works regardless of where it's called from
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$ROOT_DIR"

echo -e "${GREEN}🚀 Launching TalkBridge Desktop...${NC}"
echo -e "${BLUE}📁 Project root: $ROOT_DIR${NC}"

# Check for virtual environment
VENV_DIR="$ROOT_DIR/.venv"
if [ -d "$VENV_DIR" ]; then
    echo -e "${GREEN}🔧 Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✅ Virtual environment activated: $VENV_DIR${NC}"
else
    echo -e "${RED}❌ Virtual environment not found at $VENV_DIR${NC}"
    echo -e "${YELLOW}� Run the following commands to set up:${NC}"
    echo -e "${YELLOW}   python3 -m venv .venv${NC}"
    echo -e "${YELLOW}   source .venv/bin/activate${NC}"
    echo -e "${YELLOW}   pip install -r requirements.txt${NC}"
    exit 1
fi

# Ensure logs directory exists
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"
echo -e "${GREEN}� Logs directory: $LOG_DIR${NC}"

# Check if the desktop module can be imported
if ! python -c "import talkbridge.desktop.main" 2>/dev/null; then
    echo -e "${RED}❌ Cannot import talkbridge.desktop.main${NC}"
    echo -e "${YELLOW}👉 Make sure you've installed the package with:${NC}"
    echo -e "${YELLOW}   pip install -e .${NC}"
    exit 1
fi

# Run desktop app with logging
echo -e "${GREEN}🎯 Starting TalkBridge Desktop Application...${NC}"
echo -e "${BLUE}📊 Logs will be written to: $LOG_DIR/desktop.log${NC}"
echo ""

exec python -m talkbridge.desktop.main "$@" \
    2>&1 | tee "$LOG_DIR/desktop.log"
