#!/bin/bash
# TalkBridge Desktop Launcher with Correct Environment
# ===================================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting TalkBridge Desktop...${NC}"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Conda not found. Please install Miniconda/Anaconda first.${NC}"
    exit 1
fi

# Check if the environment exists
if ! conda env list | grep -q "talkbridge-desktop-env"; then
    echo -e "${RED}❌ Environment 'talkbridge-desktop-env' not found.${NC}"
    echo -e "${YELLOW}💡 Please create it first with:${NC}"
    echo "   conda env create -f config/environment-desktop.yml"
    exit 1
fi

# Navigate to the project directory
cd "$(dirname "$0")"

echo -e "${GREEN}🔧 Activating conda environment...${NC}"

# Activate environment and run application
conda run -n talkbridge-desktop-env python -m src.desktop.main

echo -e "${GREEN}✨ TalkBridge Desktop session ended.${NC}"
