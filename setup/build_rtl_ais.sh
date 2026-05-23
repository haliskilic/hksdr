#!/usr/bin/env bash
#
# AIS (gemi takibi) decoder'ı rtl_ais'i kaynaktan derler, ~/.local/bin'e kurar.
# Gereksinim: gcc, make, git, librtlsdr-dev, libusb-1.0-0-dev (setup.sh ile kurulu).
# sudo GEREKMEZ.
#
set -euo pipefail
SRC="${HOME}/src/rtl-ais"
BIN="${HOME}/.local/bin"
mkdir -p "$(dirname "$SRC")" "$BIN"

if [ ! -d "$SRC/.git" ]; then
    echo "[*] rtl-ais klonlanıyor..."
    git clone --depth 1 https://github.com/dgiardini/rtl-ais "$SRC"
fi
echo "[*] Derleniyor..."
make -C "$SRC"
cp "$SRC/rtl_ais" "$BIN/rtl_ais"
echo "[+] Kuruldu: $BIN/rtl_ais"
command -v rtl_ais || echo "NOT: PATH'e ekle:  export PATH=\$HOME/.local/bin:\$PATH"
