#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVICE_NAME="receive_data.service"
SERVICE_TARGET="/etc/systemd/system/${SERVICE_NAME}"
SERVICE_USER="${SUDO_USER:-$USER}"
TMP_SERVICE="$(mktemp)"
trap 'rm -f "$TMP_SERVICE"' EXIT

cat > "$TMP_SERVICE" <<EOF
[Unit]
Description=Environmental Data Logger Receiver
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${PROJECT_DIR}
ExecStart=/usr/bin/python3 ${PROJECT_DIR}/receiver/receive_data.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo cp "$TMP_SERVICE" "$SERVICE_TARGET"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "Installed and started ${SERVICE_NAME}"
sudo systemctl status "$SERVICE_NAME" --no-pager
