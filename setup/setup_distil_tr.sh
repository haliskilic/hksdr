#!/usr/bin/env bash
#
# Türkçe STT için distil-whisper-large-v3-tr'yi kurar (HİBRİT: TR bu model,
# EN whisper.cpp small'da kalır). Model Türkçe-only, faster-whisper (CTranslate2)
# ile çalışır. İzole bir venv kullanır (sistem python'a dokunmaz).
#
#   setup/setup_distil_tr.sh
#
# Çıktı:  ~/.cache/whisper-ct2/venv  (faster-whisper)  +  ~/.cache/whisper-ct2/distil-tr (int8 model)
# Geçersiz kılma:  FW_VENV, FW_MODEL
set -euo pipefail

VENV="${FW_VENV:-$HOME/.cache/whisper-ct2/venv}"
OUT="${FW_MODEL:-$HOME/.cache/whisper-ct2/distil-tr}"
SRC="Sercan/distil-whisper-large-v3-tr"

echo "==> venv: $VENV"
mkdir -p "$(dirname "$VENV")"
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"

echo "==> bağımlılıklar (faster-whisper + CPU-only torch — dönüştürme için)"
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q faster-whisper ctranslate2 transformers
"$VENV/bin/pip" install -q torch --index-url https://download.pytorch.org/whl/cpu

echo "==> dönüştür: $SRC → CTranslate2 int8 (~3GB indirir, ~800MB yazar)"
if [ ! -f "$OUT/model.bin" ]; then
    "$VENV/bin/ct2-transformers-converter" --model "$SRC" \
        --output_dir "$OUT" --quantization int8 \
        --copy_files tokenizer.json preprocessor_config.json
fi
echo "    ✓ $OUT"
ls -lh "$OUT" | sed 's/^/    /'

echo
echo "Kuruldu. (HF indirme önbelleğini ~/.cache/huggingface ile boşaltarak ~3GB geri alabilirsin.)"
echo "  FW_VENV  = $VENV"
echo "  FW_MODEL = $OUT"
