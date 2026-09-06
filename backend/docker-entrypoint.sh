#!/bin/sh
set -eu

if [ ! -f "${TELCORD_DATA_DIR}/telcord.db" ]; then
    echo "TELCORD database not found; importing bundled XLSX data"
    PYTHONPATH=/app python scripts/seed.py
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'
