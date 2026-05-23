#!/usr/bin/env bash
#
# whisper.cpp (Whisper "small", çok-dilli — Türkçe + İngilizce + 97 dil) kurar.
# Vosk'un yerine STT motoru olarak kullanılır (tarama + canlı dinleme).
#
#   setup/setup_whisper.sh
#
# Çıktı:  ~/whisper.cpp/build/bin/whisper-cli   ve   ~/.cache/whisper/ggml-small.bin
# Geçersiz kılma:  WHISPER_DIR / WHISPER_MODEL_DIR / WHISPER_MODEL
set -euo pipefail

WDIR="${WHISPER_DIR:-$HOME/whisper.cpp}"
MODEL_DIR="${WHISPER_MODEL_DIR:-$HOME/.cache/whisper}"
MODEL="${WHISPER_MODEL:-ggml-small.bin}"        # çok-dilli small (~466MB). .en KULLANMA (TR gerek).

echo "==> whisper.cpp kaynağı"
if [ ! -d "$WDIR/.git" ]; then
    git clone --depth 1 https://github.com/ggml-org/whisper.cpp "$WDIR"
else
    echo "    mevcut: $WDIR"
fi

echo "==> derleniyor (whisper-cli)"
cd "$WDIR"
cmake -B build -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake --build build -j"$(nproc)" --target whisper-cli >/dev/null
BIN="$WDIR/build/bin/whisper-cli"
[ -x "$BIN" ] || { echo "HATA: whisper-cli derlenemedi"; exit 1; }
echo "    ✓ $BIN"

echo "==> model: $MODEL (~466MB, çok-dilli)"
mkdir -p "$MODEL_DIR"
if [ ! -f "$MODEL_DIR/$MODEL" ]; then
    curl -L --fail -o "$MODEL_DIR/$MODEL.part" \
        "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/$MODEL"
    mv "$MODEL_DIR/$MODEL.part" "$MODEL_DIR/$MODEL"
fi
ls -lh "$MODEL_DIR/$MODEL" | awk '{print "    ✓ "$NF" ("$5")"}'

echo
echo "Kuruldu. webapp/app.py bunları otomatik bulur:"
echo "  WHISPER_BIN   = $BIN"
echo "  WHISPER_MODEL = $MODEL_DIR/$MODEL"
