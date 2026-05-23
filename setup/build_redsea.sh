#!/usr/bin/env bash
#
# redsea (RDS/RBDS decoder) kurar — FM istasyon adı (PS), radiotext (RT), PTY.
# rtl_fm | redsea pipeline'ı ile çalışır.  Kaynak: github.com/windytan/redsea
#   setup/build_redsea.sh
# Çıktı:  ~/redsea/build/redsea   (PATH'e de eklenir: ~/.local/bin/redsea sembolik)
set -euo pipefail

echo "==> bağımlılıklar (apt — sudo parolası sorulabilir)"
sudo apt-get install -y --no-install-recommends \
    build-essential git meson ninja-build libsndfile1-dev libliquid-dev || \
    echo "    (apt atlandı/zaten kurulu olabilir)"

DIR="${REDSEA_DIR:-$HOME/redsea}"
echo "==> kaynak: $DIR"
[ -d "$DIR/.git" ] || git clone --depth 1 https://github.com/windytan/redsea "$DIR"
cd "$DIR"

echo "==> derle (meson/ninja)"
[ -d build ] || meson setup build
ninja -C build
BIN="$DIR/build/redsea"
[ -x "$BIN" ] || { echo "HATA: redsea derlenemedi"; exit 1; }

mkdir -p "$HOME/.local/bin"
ln -sf "$BIN" "$HOME/.local/bin/redsea"
echo "    ✓ $BIN  (→ ~/.local/bin/redsea)"
"$BIN" --version 2>/dev/null | head -1 || true
