#!/usr/bin/env bash
#
# ADS-B (1090 MHz) decoder'ı dump1090'ı kaynaktan derler ve ~/.local/bin'e kurar.
# Gereksinimler: gcc, make, git, librtlsdr-dev (setup.sh ile zaten kurulu).
# sudo GEREKMEZ.
#
set -euo pipefail

SRC="${HOME}/src/dump1090"
BIN="${HOME}/.local/bin"

mkdir -p "$(dirname "$SRC")" "$BIN"

if [ ! -d "$SRC/.git" ]; then
    echo "[*] dump1090 klonlanıyor..."
    git clone --depth 1 https://github.com/antirez/dump1090 "$SRC"
fi

echo "[*] Derleniyor..."
make -C "$SRC"

cp "$SRC/dump1090" "$BIN/dump1090"
echo "[+] Kuruldu: $BIN/dump1090"
command -v dump1090 || echo "NOT: $BIN PATH'te değilse:  export PATH=\$HOME/.local/bin:\$PATH"
