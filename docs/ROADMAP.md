# 📡 HK.SDR — İnceleme, Özellik Analizi & Yol Haritası

RTL-SDR 820T2 (RTL2832U + R820T2, `0bda:2838`), Debian 12. Backend: saf Python stdlib
(`http.server` + `sqlite3`); STT için whisper.cpp (small) + opsiyonel distil-tr (faster-whisper);
sınıflama için numpy. Son güncelleme: 2026-05 (kapsamlı review sonrası).

İçindekiler: 1) Mimari · 2) Tamamlananlar · 3) Bilinen hatalar/teknik borç (review) ·
4) Özellik boşluk analizi (ekosistem) · 5) Yol haritası · 6) Donanım · 7) Kaynaklar.

---

## 1. Mimari

```
  tarayıcı (HTML/JS SPA)  ⇄  HTTP (ThreadingHTTPServer)  ⇄  DeviceManager (Lock + mode + proc)
        │  polling: status/detections/map/ism/msg/wf/listen-stt        │
       SQLite (detections + messages + bookmarks)        alt-süreçler: rtl_power/rtl_fm/dump1090/
                                                          rtl_433/rtl_ais/acarsdec/multimon-ng/whisper
```

- **Tek cihaz, tek anda tek iş.** `DEVICE.lock` + `DEVICE.mode` ile karşılıklı dışlama.
  Modlar: `scan · listen · adsb · ais · aprs · ism · pager · acars · wf` (+ tarama-gömülü STT).
- **Görünüm panelleri** (cihaz kullanmaz): Kayıtlar · Analitik · Ayarlar.
- **Decoder modülleri** (`webapp/{adsb,ais,aprs,ism,pager,acars,waterfall}.py`) ortak desen:
  `available/start/stop/_read_loop`.
- **STT** (`whisper_stt.py`): whisper.cpp small (TR+EN, çok-dilli); `USE_DISTIL_TR=1` ile
  Türkçe için distil-large-v3-tr (faster-whisper, varsayılan KAPALI — CPU'da yavaş).
- **Sınıflama** (`classify.py`): IQ özellik-tabanlı kural modülasyon tahmini.

**Mimari değerlendirme:** Tek-dongle donanımı için doğru model. Zayıf yönler: (a) `app.py`
~1050 satır, çok iş yapıyor (routing + DB + scanner + STT + kayıt) — dispatch tablosu + DB
katmanı ayrılmalı; (b) decoder start/stop boilerplate 7 modülde kopyalanmış (base class adayı);
(c) **mod geçişleri kilit üstünde serialize değil** (TOCTOU); (d) **test yok**, yapılandırılmış
log yok, DB indeksi/migration yok.

---

## 2. ✅ Tamamlananlar

| Faz | Özellikler |
|-----|-----------|
| 0 Çekirdek | Sürekli kategorik tarama (rtl_power→SQLite), canlı dinleme (rtl_fm WAV akışı) |
| 1 Decoder | ADS-B (dump1090), ISM 433 (rtl_433), Pager (multimon, **içerik maskeli**), APRS, AIS (rtl_ais), ACARS (acarsdec) |
| 2 Görsel/kayıt | Waterfall (canvas), paylaşımlı harita (Leaflet), etkileşimli wf (tıkla-dinle/Shift-sınıflandır/zoom), ses oto-kayıt + arşiv, 🔔 alarm, 🔇 gürültü filtresi |
| 3 Akıl/analitik | Modülasyon sınıflama + sinyal-kimlik, analitik (en aktif/kategori/saatlik), arama, CSV/JSON export |
| 4 Platform (kısmi) | Tarama profilleri + zamanlama, gain/PPM kalibrasyon, CSV içe aktarma + yer imleri, PWA + LAN + Basic auth |
| STT | whisper.cpp small (TR+EN otomatik dil) tarama tablosunda + canlı dinlemede akan metin; distil-tr opsiyonel |
| UI | Sol gezinme menüsü (gruplu, aktif vurgu, geniş ekranda sabit) |
| Sertleştirme | XSS kaçışı (esc), input validation (_qint), schedule doğrulama, hmac auth, kilit/timeout düzeltmeleri, SW cache-temizleme |

---

## 3. 🐞 Bilinen hatalar / teknik borç (2026-05 review)

Önceki tur düzeltilenlerin **ötesinde**, ikinci-görüş incelemede bulunan ve **doğrulanan** sorunlar:

### Yüksek
- **H1 — Mod geçişi TOCTOU.** `stop_other_modes()` kilit DIŞINDA çalışıp sonra ayrı kilitle
  mode set ediliyor → iki eşzamanlı POST (hızlı tık / sendBeacon yarışı) iki `rtl_*` sürecini
  cihaza çıkarabilir. **Çözüm:** modül düzeyinde `TRANSITION_LOCK` ile "durdur→mode set→spawn"
  dizisini bütün serialize et.
- **H3 — Dongle düşmesi sessizce yutuluyor.** Cihaz USB'den düşünce (sık!) `run_sweep` rc≠0
  döner, döngü 0.3 sn'de bir boşa `rtl_power` doğurur; decoder'lar süreç spawn olunca `ok=True`
  der ama veri gelmez → UI sonsuza "aktif" gösterir, **kullanıcıya hata yansımaz.** **Çözüm:**
  `/api/status`'a `device_present/device_error`, scanner'da backoff, "dongle yok/usb_claim" uyarısı.
- **H4 — DB'de indeks yok.** (Doğrulandı: 8001 satır, 0 indeks.) `analytics`/`search` full-scan;
  pruning her insert'te correlated subquery; hiç `VACUUM` yok. **Çözüm:** `detections(ts)`,
  `detections(category)`, `messages(ts,source)` indeksleri; periyodik prune; cached count.

### Orta
- **M1 — gain/PPM doğrulanmıyor.** `POST /api/config?gain=<x>` ham os.environ'a yazılıp argv'ye
  gidiyor; bozuk değer sonraki tüm yakalamaları kırar (sessizce). **Çözüm:** sayısal/"auto" doğrula.
- **M4 — PPM decoder'lara geçmiyor.** Yalnız `run_sweep` + `start_listen` `-p` kullanıyor;
  ADS-B/AIS/APRS/pager/ACARS/ISM/wf/STT/classify kalibrasyonsuz çalışıyor (820T2 ~40-80 ppm).
  **Çözüm:** ortak komut-kurucu yardımcısı.
- **M6 — Tek SQLite bağlantısı + tek kilit; `/api/status` her pollda `COUNT(*)` full-scan.**
  Çok istemcide kilit çekişmesi. **Çözüm:** WAL + cached count (MAX(id) veya bellek sayacı).
- **M2 — LAN modunda CSRF/Origin koruması yok.** `HOST=0.0.0.0` + AUTH yokken her sayfa
  `fetch` ile cihazı ele geçirebilir. **Çözüm:** loopback-dışı bağlamada Origin kontrolü; AUTH öner.
- **M5 — Kayıt arşivi yalnız adetle (50) sınırlı, toplam boyutla değil** (~50×115MB ≈ 5.7GB olası).

### Düşük
- **L1** SIGTERM'de graceful shutdown yok (systemd stop → atexit atlanır, süreç sızar).
- **L2** Yapılandırılmış log yok; hatalar `except: pass` ile yutuluyor.
- **L3** `classify` import-anındaki GAIN'i kullanıyor (canlı `_gain()` değil).
- **L8** DB migration/versiyonlama yok (`PRAGMA user_version`).
- Mimari: `app.py` çok büyük; decoder boilerplate kopyalanmış; test yok.

---

## 4. 🔍 Özellik boşluk analizi (ekosisteme göre)

OpenWebRX+ / SDR ekosisteminde olup **bu projede olmayan**, **stok 820T2 ile (24–1700 MHz, HF yok)
yapılabilir** olanlar:

| Özellik | Değer | Efor | Not |
|---------|-------|------|-----|
| ⭐ **RDS** (FM istasyon adı/şarkı/RT) | ★★★★ | S | `redsea`; FM yerelde **güçlü** → kesin çalışır. En yüksek getiri/maliyet. |
| ⭐ **VDL2** (VHF uçak verisi, ~136 MHz) | ★★★ | M | `dumpvdl2`; ACARS deseniyle aynı; ADS-B/ACARS'ı tamamlar |
| **SSTV** (ISS 145.8 geçişleri + analog) | ★★★ | M | görüntü çıktısı; `qsstv`/kütüphane; eğlenceli |
| **Radiosonde RS41/M10** (400–406, balon 2x/gün) | ★★★ | M-L | hafif decoder entegre edilebilir; gerçek decode |
| **Gerçek "scanner" modu** (squelch → aktif kanalda dur-dinle) | ★★★ | M | polis-tarayıcı tarzı; mevcut tarama + dinleme birleşimi |
| **Kayıt zamanlayıcı** (frekansı çizelgeyle kaydet) | ★★ | S | mevcut kayıt + schedule altyapısı üstüne |
| **WebSocket** (polling yerine push) | ★★ | M | gecikme/CPU iyileştirir |

**Stok 820T2 ile YAPILAMAYAN (HF/upconverter gerek):** CW/RTTY/SITOR/FT8/WSPR/HFDL (HF),
DAB+ ses. **Ağır harici yığın (standalone önerilir):** Meteor-M2 LRPT (SatDump; ⚠️ NOAA APT
Ağustos 2025'te kapandı), LoRa/Meshtastic (GNU Radio ~1GB), radiosonde_auto_rx (kendi web yığını).
**Kapsam dışı (yasal/şifreli):** DMR/P25/TETRA **ses** decode, trunking takip.

---

## 5. 🗺️ Yol Haritası (öncelikli)

> Efor: **S** saat · **M** 1–2 gün · **L** hafta. Sıra = önerilen.

### Faz A — Sağlamlık & doğruluk · ✅ TAMAMLANDI (commit db42eae)
**H1** TRANSITION_LOCK + start_mode() ile mod geçişi serialize · **H3** dongle-yok tespiti
(device_ok/fail_streak) + UI '🔴 Cihaz yok' + scanner backoff · **H4** DB indeksleri (ts/category/
source) + WAL · **M1** gain/PPM doğrulama · **M4** PPM tüm decoder'lara (dump1090/rtl_433/rtl_ais/
acarsdec/rtl_fm/rtl_power/rtl_sdr/whisper) · **M6** WAL + bellek-cached count (status COUNT(*) yok).
Kalan düşükler: M2 (LAN CSRF), M5 (kayıt toplam-boyut), L1 (SIGTERM), L2 (log), L8 (DB migration).

### Faz B — Operasyonel olgunluk · S–M
**4.2** systemd kullanıcı servisi (`Restart=on-failure`, journald log) + graceful SIGTERM (L1) ·
yapılandırılmış log (L2) · `/api/health` endpoint · DB migration (`user_version`, L8) ·
ilk testler (`tests/` — parser'lar: AIVDM/SBS/POCSAG/ACARS + classify + DB).

### Faz C — Yeni decoder'lar · ✅ C1+C2 TAMAMLANDI (commit 5c82e3f)
**C1 ⭐ RDS** (rds.py, redsea — FM istasyon adı/RT/PTY; setup/build_redsea.sh) ✅ ·
**C2 ⭐ VDL2** (vdl2.py, dumpvdl2 — 136 MHz; setup/build_dumpvdl2.sh) ✅ · sidebar 📻/🛰️.
Pipeline doğru, start/stop/scan-dönüş test edildi; **canlı decode reception-sınırlı**
(stok anten — iyi VHF/FM anteniyle çözer). **C2-ertelendi: SSTV** (headless decode ağır,
ISS-geçişi bağımlı) · **Radiosonde RS41** (balon-saati bağımlı, sürekli tarayıcıya düşük getiri).

### Faz D — Mimari & bakım · ✅ TAMAMLANDI (commit'ler 5c82e3f, 61198178)
**PipeDecoder** ortak temel (decoder_base.py); aprs/pager/rds ona taşındı (boilerplate
tekilleştirildi, ortak PPM/GAIN/handoff). **app.py 1139→910 satır:** DB → `webapp/db.py`,
sinyal tespiti → `webapp/detect.py`, 9×2 tekrar eden mod rotası → `MODE_DEC` tablosu +
tek jenerik dispatch. (adsb/ais/acars/ism/wf farklı süreç desenleri — kendi modüllerinde kaldı.)

### Faz E — Donanım & ölçeklenme · L
**4.1** çoklu-dongle (`DevicePool`; biri tararken biri decode) · WebSocket push ·
"scanner" squelch-dur-dinle modu · kayıt zamanlayıcı.

### Ertelenen (Faz F — ağır/standalone)
Meteor-M2 LRPT (SatDump) · LoRa/Meshtastic (GNU Radio) · radiosonde_auto_rx — birer
başlatıcı betikle "yan araç" olarak. Digital voice = **kapsam dışı**.

---

## 6. Donanım gerçeği

Stok anten **VHF (AIS 162 / APRS 144.8 / airband 118–137 / ACARS-VDL2 131–136) ve ISM 433**
için zayıf → bu bantlarda canlı yakalama sınırlı (decode kodları test edildi, eksik olan reception).
**ADS-B (1090) ve FM/TETRA güçlü.** Öncelik: (1) banda uygun anten (~46cm ¼λ VHF / dipol);
(2) **beslemeli USB hub + soğutma** — çubuk yük altında USB'den **sık düşüyor** (donanımsal,
bu oturumda 4 kez); (3) ileride RTL-SDR Blog V4 (TCXO, R828D, daha iyi termal/filtre).

---

## 7. Kaynaklar
- RTL-SDR 2026 proje rehberi — https://www.sdrstore.eu/7-rtl-sdr-projects-guide-2026/
- OpenWebRX+ (FAX/SSTV/RDS/HFDL/VDL2/scanner decoder listesi) — https://fms.komkon.org/OWRX/
- SDR yazılım karşılaştırma 2026 — https://policeradioencryption.com/learn/sdr-software-comparison
- Meshtastic/LoRa SDR — https://www.rtl-sdr.com/decoding-meshtastic-in-realtime-with-an-rtl-sdr-and-gnu-radio/
- SatDump (Meteor LRPT; NOAA APT kapandı) — https://www.rtl-sdr.com/automating-noaa-apt-and-meteor-m2-lrpt-reception-with-satdump-1-1-2/
- redsea (RDS) · dumpvdl2 (VDL2) · dump1090 / rtl-ais / acarsdec / multimon-ng / rtl_433 — GitHub
