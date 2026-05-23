#!/usr/bin/env bash
#
# Havacılık (airband) AM dinleyici / tarayıcı.
#   - Tek frekans verilirse o kanalı sürekli dinler.
#   - Birden çok frekans verilirse squelch ile aralarında gezer (tarayıcı).
#
# Kullanım:
#   scripts/airband.sh 120.100M                  # tek kanalı dinle
#   scripts/airband.sh 118.1M 121.5M 124.0M      # tarayıcı modu
#   scripts/airband.sh                           # yaygın kanallarda tara
#   GAIN=49 SQUELCH=80 scripts/airband.sh ...    # kazanç/squelch ayarı
#
# Sesi DUYABİLMEN için bunu kendi terminalinde çalıştır (Ctrl-C ile çık).
#
set -euo pipefail

GAIN="${GAIN:-49}"
SQUELCH="${SQUELCH:-0}"     # 0 = squelch kapalı (sürekli ses). Tarayıcıda 50-120 dene.

if [ "$#" -eq 0 ]; then
    # Varsayılan yaygın airband kanalları (gerçek aktif kanalı taramayla bulduysan onları ver)
    set -- 118.100M 119.100M 120.100M 121.500M 121.900M 122.800M \
           123.000M 124.000M 125.000M 126.000M 127.000M 130.000M 131.000M
    [ "$SQUELCH" = "0" ] && SQUELCH=60      # tarayıcı modunda squelch şart
fi

FREQ_ARGS=()
for f in "$@"; do FREQ_ARGS+=(-f "$f"); done

echo "Kanal(lar) : $*"
echo "Kazanç     : $GAIN   Squelch: $SQUELCH"
echo "(Ctrl-C ile çık)"
echo

# Oynatıcı seç: aplay > sox play
if command -v aplay >/dev/null 2>&1; then
    PLAYER=(aplay -r 12000 -f S16_LE -t raw -c 1 -q)
else
    PLAYER=(play -q -r 12000 -t raw -e signed -b 16 -c 1 -)
fi

# AM demodülasyon, 12 kHz ses çıkışı
rtl_fm -M am -g "$GAIN" -l "$SQUELCH" -s 12k "${FREQ_ARGS[@]}" - | "${PLAYER[@]}"
