#!/bin/bash
# JARVIS Server - Install as System Service

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  J.A.R.V.I.S. - Install System Service${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR] Need root! Run: sudo bash install.sh${NC}"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python3 not found!${NC}"
    echo "Install with: sudo apt install python3 python3-pip"
    exit 1
fi

# Install dependencies
echo "[INFO] Installing Python dependencies..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../../backend"
pip3 install -r "$BACKEND_DIR/requirements.txt" --quiet 2>/dev/null

# Copy files to /opt
echo "[INFO] Installing to /opt/jarvis..."
mkdir -p /opt/jarvis
cp -r "$BACKEND_DIR"/* /opt/jarvis/backend/

# Create workspace
mkdir -p /opt/jarvis/backend/workspace

# Generate SSL certificates
echo "[INFO] Generating SSL certificates..."
cd /opt/jarvis/backend
if [ ! -f cert.pem ] || [ ! -f key.pem ]; then
    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes \
        -subj "/C=US/ST=Local/L=Local/O=JARVIS/CN=localhost" 2>/dev/null
fi

# Install service
echo "[INFO] Installing systemd service..."
cp "$SCRIPT_DIR/jarvis.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable jarvis.service
systemctl start jarvis.service

echo ""
echo -e "${GREEN}[OK] JARVIS installed and started!${NC}"
echo ""
echo -e "${YELLOW}[URL] PC: https://localhost:8000${NC}"
echo -e "${YELLOW}[URL] Server: https://$(hostname -I | awk '{print $1}'):8000${NC}"
echo ""
echo "Commands:"
echo "  sudo systemctl status jarvis    # Check status"
echo "  sudo systemctl restart jarvis   # Restart"
echo "  sudo systemctl stop jarvis      # Stop"
echo "  sudo systemctl logs jarvis      # View logs"
echo ""
