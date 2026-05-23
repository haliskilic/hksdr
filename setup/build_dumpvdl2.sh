#!/usr/bin/env bash
#
# dumpvdl2 (VDL Mode 2 — VHF uçak veri linki, ~136 MHz) kurar. ACARS'ın halefi;
# ADS-B/ACARS'ı tamamlar.  Kaynak: github.com/szpajder/dumpvdl2
#   setup/build_dumpvdl2.sh
# Çıktı:  ~/.local/bin/dumpvdl2
set -euo pipefail

echo "==> bağımlılıklar (apt — sudo parolası sorulabilir)"
sudo apt-get install -y --no-install-recommends \
    build-essential cmake git pkg-config librtlsdr-dev libglib2.0-dev || \
    echo "    (apt atlandı/zaten kurulu olabilir)"

DIR="${VDL2_DIR:-$HOME/dumpvdl2}"
PREFIX="$HOME/.local"
LIBACARS="$HOME/.local"     # acarsdec kurulumundan gelen libacars (varsa)

echo "==> kaynak: $DIR"
[ -d "$DIR/.git" ] || git clone --depth 1 https://github.com/szpajder/dumpvdl2 "$DIR"
cd "$DIR"
rm -rf build && mkdir build && cd build

# libacars-2.pc ~/.local/lib/pkgconfig altında (acarsdec kurulumundan) → pkg-config'e tanıt
export PKG_CONFIG_PATH="$LIBACARS/lib/pkgconfig:${PKG_CONFIG_PATH:-}"

echo "==> derle (cmake)"
cmake .. -DCMAKE_INSTALL_PREFIX="$PREFIX" \
    -DCMAKE_PREFIX_PATH="$LIBACARS" \
    -DCMAKE_EXE_LINKER_FLAGS="-L$LIBACARS/lib -Wl,-rpath,$LIBACARS/lib" >/dev/null
make -j"$(nproc)"
make install
BIN="$PREFIX/bin/dumpvdl2"
[ -x "$BIN" ] || { echo "HATA: dumpvdl2 derlenemedi"; exit 1; }
echo "    ✓ $BIN"
