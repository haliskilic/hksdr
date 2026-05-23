#!/usr/bin/env bash
#
# ACARS decoder'ı (acarsdec) + libacars'ı kaynaktan derler, ~/.local'a kurar.
# Gereksinim: git, cmake, gcc, librtlsdr-dev. sudo GEREKMEZ.
# Çalışma anında libacars için LD_LIBRARY_PATH=$HOME/.local/lib gerekir (webapp ayarlar).
#
set -euo pipefail
PREFIX="$HOME/.local"
SRC="$HOME/src"
mkdir -p "$SRC" "$PREFIX/bin"

# --- libacars ---
if [ ! -d "$SRC/libacars/.git" ]; then
    echo "[*] libacars klonlanıyor..."
    git clone --depth 1 https://github.com/szpajder/libacars "$SRC/libacars"
fi
echo "[*] libacars derleniyor..."
cmake -S "$SRC/libacars" -B "$SRC/libacars/build" -DCMAKE_INSTALL_PREFIX="$PREFIX" >/dev/null
make -C "$SRC/libacars/build" -j2 >/dev/null
make -C "$SRC/libacars/build" install >/dev/null

# --- acarsdec ---
if [ ! -d "$SRC/acarsdec/.git" ]; then
    echo "[*] acarsdec klonlanıyor..."
    git clone --depth 1 https://github.com/TLeconte/acarsdec "$SRC/acarsdec"
fi
echo "[*] acarsdec derleniyor (RTL desteği + libacars linki)..."
cmake -S "$SRC/acarsdec" -B "$SRC/acarsdec/build" -Drtl=ON \
    -DCMAKE_PREFIX_PATH="$PREFIX" -DCMAKE_INSTALL_PREFIX="$PREFIX" \
    -DCMAKE_EXE_LINKER_FLAGS="-L$PREFIX/lib -Wl,-rpath,$PREFIX/lib" >/dev/null
make -C "$SRC/acarsdec/build" -j2 >/dev/null
BIN=$(find "$SRC/acarsdec/build" -maxdepth 2 -name acarsdec -type f | head -1)
cp "$BIN" "$PREFIX/bin/acarsdec"
echo "[+] Kuruldu: $PREFIX/bin/acarsdec"
LD_LIBRARY_PATH="$PREFIX/lib" "$PREFIX/bin/acarsdec" --help 2>&1 | head -6 || true
