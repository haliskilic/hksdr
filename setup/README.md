# Kurulum (Setup)

Bu klasör **yalnızca ortam kurulumunu** içerir — öğrenim projesinden ayrıdır.

## Ne yapar?
`setup.sh`:
1. SDR araçlarını kurar: `rtl-sdr`, `librtlsdr-dev`, `inspectrum`,
   `rtl-433`, `multimon-ng`, `sox`, `python3-numpy`
2. **URH** (Universal Radio Hacker) kurar
3. RTL-SDR ile çakışan DVB-T çekirdek sürücüsünü
   (`dvb_usb_rtl28xxu` vb.) `/etc/modprobe.d/blacklist-rtlsdr.conf` ile bloklar
4. `rtl_test -t` ile donanımı test eder

## Çalıştırma
sudo gerektirir:
```bash
sudo bash setup/setup.sh
```

## Sorun giderme
| Belirti | Çözüm |
|---------|-------|
| `usb_claim_interface error -6` | DVB-T sürücüsü hâlâ takılı → çubuğu çıkar/tak veya yeniden başlat |
| `dpkg kesintiye uğradı` | `sudo dpkg --configure -a` çalıştır, sonra tekrar dene |
| `urh` bulunamadı | `pipx install urh` veya `pip install --user urh` |
| Cihaz görünmüyor | `lsusb \| grep 0bda:2838` ile takılı mı kontrol et |
