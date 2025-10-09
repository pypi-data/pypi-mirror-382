#!/bin/bash

# Script to run the SSE Remote Server for KOSPI-KOSDAQ MCP

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting KOSPI-KOSDAQ SSE Remote Server...${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install/upgrade dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements_sse.txt

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}Port 8000 is already in use!${NC}"
    echo "Do you want to kill the existing process? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        kill $(lsof -Pi :8000 -sTCP:LISTEN -t)
        echo -e "${GREEN}Existing process killed.${NC}"
        sleep 2
    else
        echo -e "${RED}Exiting...${NC}"
        exit 1
    fi
fi

# Run the SSE server
echo -e "${GREEN}Starting SSE server on http://localhost:8000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Run with uvicorn
python -m uvicorn sse_remote_server:app --host 0.0.0.0 --port 8000 --reload --log-level info