#!/usr/bin/env bash
#
# Çevredeki sinyalleri tara: rtl_power ile tek geçişte spektrumu süpürür,
# sonucu find_signals.py ile analiz edip güçlü sinyalleri listeler.
#
# Kullanım:
#   scripts/scan.sh [aralık] [integrasyon_sn] [eşik_dB]
#
# Örnekler:
#   scripts/scan.sh                      # geniş tarama 88–960 MHz
#   scripts/scan.sh 88M:108M:50k         # sadece FM bandı (hızlı)
#   scripts/scan.sh 400M:470M:25k 2      # UHF telsiz bandı, 2 sn integrasyon
#
set -euo pipefail

RANGE="${1:-88M:960M:200k}"     # alt:üst:bin_boyu
INTEG="${2:-1}"                 # saniye / hop
THR="${3:-6}"                   # gürültü üstü eşik (dB)

mkdir -p captures
OUT="captures/scan_$(date +%Y%m%d_%H%M%S).csv"

echo "[*] Tarama aralığı : $RANGE"
echo "[*] İntegrasyon    : ${INTEG}s/hop  (tek geçiş -1)"
echo "[*] Çıktı CSV       : $OUT"
echo "[*] rtl_power çalışıyor... (geniş tarama birkaç dakika sürebilir)"

# -1 tek geçiş; timeout -s KILL güvenlik ağı (cihazı asla takılı bırakma)
timeout -s KILL 1800 rtl_power -f "$RANGE" -i "$INTEG" -g 40 -1 "$OUT"

echo "[*] Analiz:"
python3 scripts/find_signals.py "$OUT" "$THR"
