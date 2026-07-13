#!/bin/bash
# ============================================
# J.A.R.V.I.S. - Complete Installer for Linux Mint
# ============================================
# Run: sudo bash install_jarvis.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

JARVIS_HOME="/opt/jarvis"
REPO_URL="https://github.com/karendayanaangaritaescobar12-cmyk/jarvis.inc.git"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     J.A.R.V.I.S. - Linux Mint Installer         ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================
# 1. INSTALAR DEPENDENCIAS
# ============================================
echo -e "${YELLOW}[1/6] Installing system dependencies...${NC}"

apt update
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    openssl \
    net-tools \
    lsof

echo -e "${GREEN}[OK] System dependencies installed${NC}"

# ============================================
# 2. CLONAR REPOSITORIO
# ============================================
echo -e "${YELLOW}[2/6] Cloning JARVIS repository...${NC}"

if [ -d "$JARVIS_HOME/.git" ]; then
    echo "[INFO] JARVIS already installed. Updating..."
    cd "$JARVIS_HOME"
    git pull origin main
else
    git clone $REPO_URL $JARVIS_HOME
    cd "$JARVIS_HOME"
fi

echo -e "${GREEN}[OK] JARVIS files ready${NC}"

# ============================================
# 3. CREAR ENTORNO VIRTUAL
# ============================================
echo -e "${YELLOW}[3/6] Creating virtual environment...${NC}"

cd "$JARVIS_HOME/backend"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 2>/dev/null

echo -e "${GREEN}[OK] Virtual environment created${NC}"

# ============================================
# 4. GENERAR CERTIFICADOS SSL
# ============================================
echo -e "${YELLOW}[4/6] Generating SSL certificates...${NC}"

if [ ! -f cert.pem ] || [ ! -f key.pem ]; then
    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes \
        -subj "/C=US/ST=Local/L=Local/O=JARVIS/CN=localhost" 2>/dev/null
    echo -e "${GREEN}[OK] SSL certificates generated${NC}"
else
    echo -e "${GREEN}[OK] SSL certificates already exist${NC}"
fi

# ============================================
# 5. CREAR WORKSPACE
# ============================================
echo -e "${YELLOW}[5/6] Creating workspace...${NC}"

mkdir -p "$JARVIS_HOME/backend/workspace"
chmod 755 "$JARVIS_HOME/backend/workspace"

echo -e "${GREEN}[OK] Workspace created${NC}"

# ============================================
# 6. INSTALAR SERVICIO SYSTEMD
# ============================================
echo -e "${YELLOW}[6/6] Installing systemd service...${NC}"

cat > /etc/systemd/system/jarvis.service << EOF
[Unit]
Description=JARVIS AI Assistant Server
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=$JARVIS_HOME/backend
ExecStart=$JARVIS_HOME/backend/venv/bin/python main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

Environment=PORT=8000
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable jarvis.service
systemctl start jarvis.service

echo -e "${GREEN}[OK] Service installed and started${NC}"

# ============================================
# INSTALAR COMANDO 'jarvis'
# ============================================
cat > /usr/local/bin/jarvis << 'EOF'
#!/bin/bash
case "$1" in
    start)   sudo systemctl start jarvis ;;
    stop)    sudo systemctl stop jarvis ;;
    restart) sudo systemctl restart jarvis ;;
    status)  sudo systemctl status jarvis ;;
    logs)    sudo journalctl -u jarvis -f ;;
    update)  sudo bash /opt/jarvis/server/linux/update.sh ;;
    *)
        echo "JARVIS Commands:"
        echo "  jarvis start    - Start server"
        echo "  jarvis stop     - Stop server"
        echo "  jarvis restart  - Restart server"
        echo "  jarvis status   - Check status"
        echo "  jarvis logs     - View logs"
        echo "  jarvis update   - Update JARVIS"
        ;;
esac
EOF
chmod +x /usr/local/bin/jarvis

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          J.A.R.V.I.S. INSTALLED!                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}[URL] PC: https://localhost:8000${NC}"
echo -e "${CYAN}[URL] Red: https://$(hostname -I | awk '{print $1}'):8000${NC}"
echo ""
echo -e "${YELLOW}Commands:${NC}"
echo "  jarvis start    - Iniciar servidor"
echo "  jarvis stop     - Detener servidor"
echo "  jarvis restart  - Reiniciar servidor"
echo "  jarvis status   - Ver estado"
echo "  jarvis logs     - Ver logs en tiempo real"
echo "  jarvis update   - Actualizar JARVIS"
echo ""
