#!/bin/bash
# JARVIS Server - Update Script
# Run: sudo bash update.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

JARVIS_HOME="/opt/jarvis"

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  J.A.R.V.I.S. - Updating...${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Detener servidor
echo "[INFO] Stopping server..."
sudo systemctl stop jarvis.service 2>/dev/null

# Actualizar código
echo "[INFO] Updating code..."
cd "$JARVIS_HOME"

if [ -d ".git" ]; then
    git pull origin main
    echo -e "${GREEN}[OK] Repository updated${NC}"
else
    echo -e "${YELLOW}[WARNING] Not a git repository. Re-cloning...${NC}"
    cd /opt
    sudo rm -rf jarvis
    sudo git clone https://github.com/karendayanaangaritaescobar12-cmyk/jarvis.inc.git jarvis
    echo -e "${GREEN}[OK] Repository re-cloned${NC}"
fi

# Actualizar dependencias
echo "[INFO] Updating dependencies..."
cd "$JARVIS_HOME/backend"
source venv/bin/activate 2>/dev/null
pip install -r requirements.txt --upgrade --quiet 2>/dev/null

# Regenerar certificados si es necesario
if [ ! -f cert.pem ] || [ ! -f key.pem ]; then
    echo "[INFO] Generating SSL certificates..."
    openssl req -x500 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes \
        -subj "/C=US/ST=Local/L=Local/O=JARVIS/CN=localhost" 2>/dev/null
fi

# Reiniciar servidor
echo "[INFO] Starting server..."
sudo systemctl start jarvis.service

echo ""
echo -e "${GREEN}[OK] JARVIS updated and running!${NC}"
echo ""
