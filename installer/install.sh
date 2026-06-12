#!/bin/bash
# AegisGAN Native Installer for Linux
# This script installs Zeek, Python, Node.js, and sets up AegisGAN as a system service.

set -e

echo "========================================"
echo "    AEGISGAN NATIVE INSTALLER (LINUX)   "
echo "========================================"

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./install.sh)"
  exit 1
fi

INSTALL_DIR="/opt/aegisgan"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"

echo "[1/5] Installing System Dependencies..."
# Detect package manager
if command -v apt-get &> /dev/null; then
    # Add Zeek repository for Ubuntu/Debian
    echo "Detected apt package manager."
    apt-get update
    apt-get install -y curl wget software-properties-common python3 python3-pip python3-venv git
    
    # Node.js
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    
    # Install Zeek (if not already installed)
    if ! command -v zeek &> /dev/null; then
        echo "Installing Zeek..."
        echo 'deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_22.04/ /' | tee /etc/apt/sources.list.d/security:zeek.list
        curl -fsSL https://download.opensuse.org/repositories/security:zeek/xUbuntu_22.04/Release.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/security_zeek.gpg > /dev/null
        apt-get update
        apt-get install -y zeek
    fi
elif command -v yum &> /dev/null; then
    echo "Detected yum package manager."
    yum install -y curl wget python3 python3-pip python3-virtualenv git nodejs
    # Zeek for CentOS/RHEL would go here
else
    echo "Unsupported package manager. Please install Python 3, Node.js, and Zeek manually."
fi

echo "[2/5] Copying AegisGAN to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r "$SOURCE_DIR/"* "$INSTALL_DIR/"
chown -R root:root "$INSTALL_DIR"

echo "[3/5] Setting up Python Environment & Backend..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r db_microservice/requirements.txt
deactivate

echo "[4/5] Building React Frontend..."
cd "$INSTALL_DIR/frontend"
npm install
npm run build

echo "[5/5] Configuring Systemd Services..."
cd "$INSTALL_DIR/installer"
cp aegisgan-backend.service /etc/systemd/system/
cp aegisgan-frontend.service /etc/systemd/system/
cp aegisgan-bridge.service /etc/systemd/system/
cp aegisgan-db.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable aegisgan-backend.service
systemctl enable aegisgan-frontend.service
systemctl enable aegisgan-bridge.service
systemctl enable aegisgan-db.service

systemctl restart aegisgan-backend.service
systemctl restart aegisgan-frontend.service
systemctl restart aegisgan-bridge.service
systemctl restart aegisgan-db.service

echo "========================================"
echo " AegisGAN Installation Complete! "
echo "========================================"
echo "The system is now running in the background."
echo "Access the dashboard at: http://<your_server_ip>:5173"
echo "Check backend status: sudo systemctl status aegisgan-backend"
echo "Check frontend status: sudo systemctl status aegisgan-frontend"
echo "Check bridge status: sudo systemctl status aegisgan-bridge"
echo "Check db status: sudo systemctl status aegisgan-db"
echo "========================================"

