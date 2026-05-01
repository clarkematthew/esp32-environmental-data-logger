#!/bin/bash
set -euo pipefail

PROJECT_DIR="/home/matthew/environmental_data_logger/esp32-environmental-data-logger"
CRON_LINE="*/5 * * * * cd ${PROJECT_DIR} && /usr/bin/python3 display_data.py >> ${PROJECT_DIR}/display_data.log 2>&1"

TMP_CRON="$(mktemp)"
trap 'rm -f "$TMP_CRON"' EXIT

crontab -l 2>/dev/null | grep -Fv "display_data.py" > "$TMP_CRON" || true
printf '%s\n' "$CRON_LINE" >> "$TMP_CRON"
crontab "$TMP_CRON"

echo "Installed cron job:"
echo "$CRON_LINE"
