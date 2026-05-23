#!/usr/bin/env bash
#
# HK.SDR web uygulamasını başlatır.
#   scripts/run_webapp.sh
#   PORT=9000 GAIN=45 scripts/run_webapp.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

# Cihazı kapan DVB-T sürücüsü yüklüyse uyar
if lsmod | grep -q dvb_usb_rtl28xxu; then
    echo "UYARI: dvb_usb_rtl28xxu yüklü, cihazı kapabilir. setup/setup.sh çalıştırdın mı?"
fi

PORT="${PORT:-8000}"
echo "Tarayıcıda aç:  http://localhost:${PORT}"
exec python3 webapp/app.py
