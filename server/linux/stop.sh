#!/bin/bash
# JARVIS Server - Stop

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${RED}========================================${NC}"
echo -e "${RED}  J.A.R.V.I.S. Server - Stopping...${NC}"
echo -e "${RED}========================================${NC}"
echo ""

PORT=8000
PID=$(lsof -i :$PORT -t 2>/dev/null)

if [ -n "$PID" ]; then
    echo "[INFO] Found server (PID: $PID)"
    kill -9 $PID 2>/dev/null
    echo -e "${GREEN}[OK] Server stopped${NC}"
else
    echo -e "${YELLOW}[INFO] No server running on port $PORT${NC}"
fi

echo ""
