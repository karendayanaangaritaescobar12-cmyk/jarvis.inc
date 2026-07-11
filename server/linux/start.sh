#!/bin/bash
# JARVIS Server - Start

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  J.A.R.V.I.S. Server - Starting...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../../backend"
PORT=8000

# Check if already running
if lsof -i :$PORT -t > /dev/null 2>&1; then
    echo -e "${YELLOW}[WARNING] Server already running on port $PORT${NC}"
    echo -e "${YELLOW}[INFO] Access at: https://localhost:$PORT${NC}"
    exit 0
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python3 not found!${NC}"
    echo "Install with: sudo apt install python3 python3-pip"
    exit 1
fi

echo "[INFO] Starting JARVIS server..."
echo "[INFO] PC: https://localhost:$PORT"
echo "[INFO] Server: https://$(hostname -I | awk '{print $1}'):$PORT"
echo "[INFO] Press Ctrl+C to stop"
echo ""

cd "$BACKEND_DIR"
python3 main.py
