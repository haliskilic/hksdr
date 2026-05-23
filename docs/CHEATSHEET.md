# Hızlı Başvuru — Yakalama & Decode Komutları

## Donanım testi
```bash
rtl_test -t                       # cihaz + tuner görünüyor mu, örnek kaybı var mı
```

## Ham IQ yakalama (rtl_sdr)
```bash
# -f frekans(Hz)  -s örnekleme(Hz)  -g kazanç(dB)  -n örnek sayısı
rtl_sdr -f 433920000 -s 1000000 -g 40 -n 10000000 captures/capture.bin
```
- Çıktı: **uint8 interleaved IQ**. URH'de açarken format **"unsigned 8-bit"** seç.
- 433.92 MHz = en yoğun ISM bandı (uzaktan kumanda, sensör). Çevrende bir şeye
  bas (kablosuz zil, araba anahtarı vb.) ve yakala.

## URH ile canlı yakalama (en kolay)
URH içinde: **File → Record signal → Device: RTL-SDR** → frekans/örnekleme gir → Record.
Kaydı doğrudan analiz sekmesine taşıyabilirsin.

## Spektrum tarama (rtl_power) — "ortamda ne var?"
```bash
rtl_power -f 400M:450M:10k -i 5 -g 40 scan.csv
# 400-450 MHz arası, 10 kHz çözünürlük, 5 sn aralık -> ısı haritası CSV
```

## inspectrum ile görsel analiz
```bash
inspectrum captures/capture.bin
```
Spektrogramda sinyali seçip sembolleri, bit süresini *gözle* ölç. URH'ye paralel,
ölçüm için harika.

## Hazır decoder'ları incele (öğretici)
```bash
rtl_433 -f 433920000               # 433 MHz cihazları otomatik decode -> JSON
rtl_433 -A                          # bilinmeyen sinyali analiz modu (puls çözümü)
```
```bash
# POCSAG pager decode (kendi bölgendeki açık yayınlar)
rtl_fm -f 153.350M -s 22050 - | multimon-ng -a POCSAG512 -a POCSAG1200 -t raw -
```

## Format dönüşümleri
- `rtl_sdr` çıktısı (uint8) → URH'de "unsigned 8-bit" seçerek aç.
- URH `.complex` (float32) ↔ GNU Radio uyumlu.
- `sox` ile ses dosyası işleme/çevrim.

## Faydalı frekanslar (RX, dinleme serbest)
| Ne | Frekans |
|----|---------|
| FM radyo | 88–108 MHz |
| Hava bandı (uçak) | 118–137 MHz AM |
| NOAA hava uydusu | 137 MHz |
| ADS-B (uçak) | 1090 MHz |
| AIS (gemi) | 161.975 / 162.025 MHz |
| ISM / uzaktan kumanda | 433.92 MHz, 868 MHz |
