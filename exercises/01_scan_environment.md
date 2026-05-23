# Alıştırma 01 — Çevredeki Sinyalleri Tara ve Tanı

**Hedef:** Bulunduğun ortamdaki RF spektrumunu tarayıp hangi sinyallerin
yayında olduğunu bulmak ve banda göre tanımlamak. Gerçek donanım kullanılır.

---

## 1) Hızlı doğrulama — FM bandı
FM bandında her zaman güçlü yerel istasyonlar vardır; pipeline'ın çalıştığını
hemen gösterir:
```bash
scripts/scan.sh 88M:108M:50k
```
Çıktıda en güçlü FM istasyonlarını frekanslarıyla görmelisin.

## 2) Geniş tarama — "ortamda ne var?"
```bash
scripts/scan.sh
```
Varsayılan 88–960 MHz'i tek geçişte süpürür (birkaç dakika). Sonunda güçten
sıralı bir sinyal listesi + olası band etiketleri verir:
- FM radyo, havacılık, VHF/UHF telsiz
- GSM900 / LTE800 baz istasyonu kanalları
- DVB-T TV vericileri, DAB

## 3) İlginç bir aralığa odaklan
Listede gördüğün bir bölgeyi daha ince bin ile tekrar tara:
```bash
scripts/scan.sh 430M:440M:10k 3      # 70cm amatör + ISM 433 yakını
scripts/scan.sh 118M:137M:25k 2      # havacılık
scripts/scan.sh 925M:960M:50k        # GSM900 indirme kanalları
```

## 4) Bulduğun sinyali incele / dinle
Bir frekans bulunca:
- **URH / GQRX** ile o frekansa gidip dalga biçimine ve modülasyona bak.
- Hızlı dinleme (FM telsiz/anonslar):
  ```bash
  rtl_fm -f 100.6M -M fm -s 200k - | aplay -r 32000 -f S16_LE
  ```
- 433 MHz cihaz decode:
  ```bash
  rtl_433 -f 433.92M
  ```

## 5) Spektrumu görselleştir (opsiyonel ısı haritası)
`captures/scan_*.csv` dosyasını bir ısı haritasına çevirmek için
[`heatmap.py`](https://github.com/keenerd/rtl-sdr-misc) gibi araçlar kullanılabilir.

---

## 💡 Gözlem soruları
- Gürültü tabanı kaç dB? Anteni değiştirince/yerini değiştirince ne oluyor?
- En güçlü 5 sinyal hangi bantta? Beklediğin gibi mi (FM, GSM)?
- Gün içinde/akşam tarama sonuçları değişiyor mu?
- `-g` kazancını düşürüp artırınca hangi zayıf sinyaller kayboluyor/çıkıyor?

> Not: Yalnızca **alıcı** (RX). Bulduğun sinyalleri dinlemek/analiz etmek
> öğrenim amaçlıdır; şifreli/özel haberleşmeyi çözme, kaydını yayma.
