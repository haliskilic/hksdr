#!/usr/bin/env bash
#
# RTL-SDR sinyal analizi & decode ortami kurulumu (Debian 12 / Bookworm)
# Calistir:   sudo bash scripts/setup.sh
#
set -euo pipefail

echo "==> 1/4  Paket listesi guncelleniyor..."
apt-get update

echo "==> 2/4  Cekirdek araclar kuruluyor..."
# rtl-sdr        : rtl_test / rtl_sdr / rtl_fm / rtl_power
# librtlsdr-dev  : URH'nin RTL-SDR backend'i icin
# inspectrum     : IQ dosyasini spektrogramda gorsel inceleme
# rtl-433        : 433 MHz ISM cihaz decode
# multimon-ng    : POCSAG / APRS / AX.25 decode
# sox            : ses/IQ donusum
# python3-numpy  : sentetik sinyal ureteci icin
apt-get install -y \
    rtl-sdr librtlsdr-dev \
    inspectrum rtl-433 multimon-ng \
    sox python3-numpy

echo "==> 3/4  Universal Radio Hacker (URH) kuruluyor..."
# NOT: Debian 12 deposunda 'urh' apt paketi YOK (sadece snap). pipx ile izole kurulur.
apt-get install -y pipx python3-dev
# URH'yi root'a degil, betigi cagiran kullaniciya kur:
RUN_USER="${SUDO_USER:-$USER}"
if ! sudo -u "$RUN_USER" -H bash -lc 'pipx install urh && pipx ensurepath'; then
    echo "    URH otomatik kurulamadi. Elle:  pipx install urh"
fi

echo "==> 4/4  DVB-T cekirdek surucusu bloklaniyor (cihazi SDR olarak kullanabilmek icin)..."
cat > /etc/modprobe.d/blacklist-rtlsdr.conf <<'EOF'
# RTL-SDR ile cakisan DVB-T/DAB suruculeri devre disi
blacklist dvb_usb_rtl28xxu
blacklist rtl2832_sdr
blacklist rtl2832
blacklist rtl2830
blacklist dvb_usb_v2
EOF

# Suruculeri simdi kaldir (yeniden baslatmadan)
modprobe -r rtl2832_sdr      2>/dev/null || true
modprobe -r dvb_usb_rtl28xxu 2>/dev/null || true
modprobe -r rtl2832          2>/dev/null || true

echo
echo "==> Donanim testi (rtl_test -t):"
rtl_test -t || true

echo
echo "============================================================"
echo " Kurulum bitti."
echo " 'usb_claim_interface error -6' gorursen: cubugu cikar/tak"
echo " ya da bir kez yeniden baslat (blacklist kalici olsun diye)."
echo "============================================================"
