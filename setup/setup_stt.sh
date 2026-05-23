#!/usr/bin/env bash
#
# Speech-to-Text (Vosk, offline) kurulumu: vosk paketi + Türkçe ve İngilizce model.
# sudo GEREKMEZ. Modeller ~/.cache/vosk/model-tr ve model-en altına kurulur.
#
set -euo pipefail

echo "[*] vosk kuruluyor (pip --user)..."
pip install --user --break-system-packages vosk 2>&1 | tail -4

MODEL_DIR="${HOME}/.cache/vosk"
mkdir -p "$MODEL_DIR"
cd "$MODEL_DIR"

# (link adı, indirme URL'si)
get_model() {
    local link="$1" url="$2" name
    name=$(basename "$url" .zip)
    if [ -e "$link" ]; then
        echo "[=] $link zaten var"
        return
    fi
    echo "[*] İndiriliyor: $name"
    curl -fSL "$url" -o m.zip
    python3 -c "import zipfile; zipfile.ZipFile('m.zip').extractall('.')"
    rm -f m.zip
    ln -sfn "$name" "$link"
}

get_model model-tr "https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip"
get_model model-en "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
# Geriye dönük: 'model' -> TR
[ -e model ] || ln -sfn model-tr model

echo "[+] Modeller:"
ls -la "$MODEL_DIR" | grep -E "model-(tr|en)|^l" || true
echo "[*] vosk testi:"
python3 -c "import vosk; print('   vosk OK')" || echo "   vosk import HATASI"
