#!/bin/bash
# JARVIS Server - Uninstall System Service

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${RED}========================================${NC}"
echo -e "${RED}  J.A.R.V.I.S. - Uninstall Service${NC}"
echo -e "${RED}========================================${NC}"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR] Need root! Run: sudo bash uninstall.sh${NC}"
    exit 1
fi

echo "[INFO] Stopping service..."
systemctl stop jarvis.service 2>/dev/null

echo "[INFO] Disabling service..."
systemctl disable jarvis.service 2>/dev/null

echo "[INFO] Removing service file..."
rm -f /etc/systemd/system/jarvis.service
systemctl daemon-reload

echo "[INFO] Removing installed files..."
rm -rf /opt/jarvis

echo ""
echo -e "${GREEN}[OK] JARVIS uninstalled${NC}"
echo ""
