#!/bin/bash
set -euo pipefail

PROJECT_DIR="/home/matthew/environmental_data_logger/esp32-environmental-data-logger"
SERVICE_NAME="receive_data.service"
SERVICE_SOURCE="${PROJECT_DIR}/${SERVICE_NAME}"
SERVICE_TARGET="/etc/systemd/system/${SERVICE_NAME}"

sudo cp "$SERVICE_SOURCE" "$SERVICE_TARGET"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "Installed and started ${SERVICE_NAME}"
sudo systemctl status "$SERVICE_NAME" --no-pager
