#!/bin/bash
# JARVIS Server Manager

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PORT=8000

show_status() {
    if systemctl is-active --quiet jarvis.service 2>/dev/null; then
        PID=$(systemctl show jarvis.service --property=MainPID --value 2>/dev/null)
        echo -e "${GREEN}[STATUS] Server RUNNING (PID: $PID)${NC}"
        echo -e "${CYAN}[URL] https://localhost:$PORT${NC}"
        echo -e "${CYAN}[URL] https://$(hostname -I | awk '{print $1}'):$PORT${NC}"
    else
        echo -e "${RED}[STATUS] Server STOPPED${NC}"
    fi
}

show_menu() {
    clear
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     J.A.R.V.I.S. Server Manager         ║${NC}"
    echo -e "${CYAN}║     Just A Rather Very Intelligent      ║${NC}"
    echo -e "${CYAN}║              System                      ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
    echo ""
    show_status
    echo ""
    echo -e "${CYAN}┌────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│  [1] Start Server                      │${NC}"
    echo -e "${CYAN}│  [2] Stop Server                       │${NC}"
    echo -e "${CYAN}│  [3] Restart Server                    │${NC}"
    echo -e "${CYAN}│  [4] View Logs                         │${NC}"
    echo -e "${CYAN}│  [5] Install Service (sudo)            │${NC}"
    echo -e "${CYAN}│  [6] Uninstall Service (sudo)          │${NC}"
    echo -e "${CYAN}│  [0] Exit                              │${NC}"
    echo -e "${CYAN}└────────────────────────────────────────┘${NC}"
    echo ""
}

start_server() {
    if systemctl is-active --quiet jarvis.service 2>/dev/null; then
        echo -e "${YELLOW}[WARNING] Server already running${NC}"
        return
    fi
    
    if [ -f /etc/systemd/system/jarvis.service ]; then
        sudo systemctl start jarvis.service
        echo -e "${GREEN}[OK] Server started via systemd${NC}"
    else
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        bash "$SCRIPT_DIR/start.sh" &
        echo -e "${GREEN}[OK] Server started${NC}"
    fi
}

stop_server() {
    if [ -f /etc/systemd/system/jarvis.service ]; then
        sudo systemctl stop jarvis.service
        echo -e "${GREEN}[OK] Server stopped${NC}"
    else
        bash "$(dirname "${BASH_SOURCE[0]}")/stop.sh"
    fi
}

restart_server() {
    stop_server
    sleep 1
    start_server
}

view_logs() {
    if [ -f /etc/systemd/system/jarvis.service ]; then
        sudo journalctl -u jarvis.service -f
    else
        echo -e "${YELLOW}[INFO] Logs only available with systemd service${NC}"
    fi
}

install_service() {
    bash "$(dirname "${BASH_SOURCE[0]}")/install.sh"
}

uninstall_service() {
    bash "$(dirname "${BASH_SOURCE[0]}")/uninstall.sh"
}

# Make scripts executable
chmod +x "$(dirname "${BASH_SOURCE[0]}")/"*.sh 2>/dev/null

while true; do
    show_menu
    read -p "    Select option: " choice
    
    case $choice in
        1) start_server ;;
        2) stop_server ;;
        3) restart_server ;;
        4) view_logs ;;
        5) install_service ;;
        6) uninstall_service ;;
        0) echo -e "\n  Goodbye!\n"; exit 0 ;;
        *) echo -e "\n  ${RED}[ERROR] Invalid option${NC}" ;;
    esac
    
    read -p "  Press Enter to continue..."
done
