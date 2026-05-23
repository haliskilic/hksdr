<div align="center">

# 📡 HK.SDR

### Tarayıcıda çalışan, çok-modlu RTL-SDR tarayıcı, decoder ve sinyal-analiz laboratuvarı

[English](README.md) · **Türkçe**

[![Lisans: AGPL-3.0](https://img.shields.io/badge/Lisans-AGPL--3.0-blue.svg)](LICENSE)
[![Ticari lisans](https://img.shields.io/badge/Ticari-lisans%20mevcut-green.svg)](COMMERCIAL_LICENSE.md)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![Backend: sadece stdlib](https://img.shields.io/badge/backend-saf%20stdlib-success.svg)]()
[![Yalnızca RX](https://img.shields.io/badge/RX--only-yaln%C4%B1zca%20al%C4%B1c%C4%B1-orange.svg)]()
![Platform](https://img.shields.io/badge/platform-Linux-333.svg)

![HK.SDR tarama görünümü](docs/images/screenshot-scan.png)

</div>

## 🎯 Amaç

**HK.SDR**, ucuz bir RTL-SDR 820T2 çubuğunu, tamamen tarayıcıdan yönettiğin, sürekli tarama
yapan çok-modlu bir **sinyal-analiz laboratuvarına** dönüştürür. Eğitim amaçlı, **yalnızca alıcı
(RX-only)** bir proje olarak; çevrendeki radyo sinyallerini — havacılık, denizcilik, çağrı,
sensör, yayın ve dijital bantlarda — *bulmak, loglamak, sınıflamak, çözmek ve metne dökmek*
için yapıldı. Hiçbir bulut servisi yok; her şey kendi makinende yerel çalışır.

Web backend'in tamamı **saf Python standart kütüphanesidir** (`http.server` + `sqlite3`, pip
bağımlılığı yok); yalnızca opsiyonel özellikler (konuşma→metin, modülasyon sınıflama) ek araç kullanır.

## ✨ Özellikler

- **Sürekli kategorik tarama** — `rtl_power` ile bant planlarını gezer, her sinyali (frekans, güç,
  bant genişliği, kategori, bant) SQLite'a loglar; en güncel üstte canlı tarihçe.
- **Canlı ses** — ses-uygun kanala tıkla, canlı WB-FM / AM / NFM akışını dinle; opsiyonel WebAudio
  **gürültü filtresi**; her dinleme otomatik WAV olarak arşivlenir.
- **Decoder'lar** (tek paylaşımlı dongle, karşılıklı dışlamalı modlar):
  - ✈️ **ADS-B** uçak takibi — canlı harita (dump1090)
  - 🚢 **AIS** gemi takibi (rtl_ais)
  - 📡 **APRS** istasyonları (multimon-ng)
  - 🛩️ **ACARS** & 🛰️ **VDL2** uçak veri-linki mesajları (acarsdec / dumpvdl2)
  - 📟 **Pager** POCSAG/FLEX — **gizlilik için içerik maskeli** (yalnızca tür + capcode + uzunluk)
  - 📻 **RDS** FM istasyon adı / radiotext (redsea)
  - 🌡️ **ISM 433 MHz** sensörleri — gruplu canlı cihaz tablosu (rtl_433): TPMS, termometre, kumanda…
- **Waterfall / spektrum** — canlı canvas ısı haritası; **tıkla→dinle**, **Shift+tıkla→sınıflandır**,
  tekerlek→zoom.
- **Konuşma→metin (STT)** — **whisper.cpp** ile çevrimdışı, cihaz-üstü transkripsiyon (çok-dilli,
  otomatik TR/EN tespiti); opsiyonel Türkçe-özel `distil-whisper-large-v3-tr`. Aktivite-kapılı;
  tarama tablosunda frekans başına bir cümle, dinlerken de canlı akan metin gösterir.
- **Modülasyon sınıflama** — özellik-tabanlı (bant genişliği / zarf CV / spektral düzlük / SNR)
  kural sınıflandırıcı (FM-geniş, sabit-zarf dijital, AM/NFM, OOK, gürültü) + olası-servis tahmini.
- **Analitik & arama** — en aktif frekanslar, kategori & saatlik dağılım, tam-metin arama, CSV/JSON dışa aktarma.
- **Frekans gruplama** — aynı frekansın tekrarlarını tek satırda toplar (sayım + son görülme).
- **Tarama profilleri & zamanlama**, **kazanç / PPM kalibrasyonu**, **CSV yer-imi içe aktarma**,
  **alarmlar** (kelime/kategori/frekans eşleşince tarayıcı bildirimi + bip + toast).
- **PWA** — telefona kurulabilir; **iki dilli arayüz (İngilizce / Türkçe)** tek tık bayrak düğmesiyle;
  opsiyonel Basic-auth ve LAN bağlama.

## 🖼️ Ekran görüntüleri

| Masaüstü — tarama | Mobil (PWA) |
|---|---|
| ![tarama](docs/images/screenshot-scan.png) | ![mobil](docs/images/screenshot-mobile.png) |

## 🔌 Donanım

![sinyal zinciri](docs/images/hardware.svg)

| Öğe | Gereksinim |
|------|-------------|
| **SDR** | RTL-SDR çubuğu (RTL2832U + R820T2 / "820T2", USB id `0bda:2838`). Kararlılık için RTL-SDR Blog **V4** önerilir (TCXO, daha iyi filtreleme). |
| **Anten** | Banda uygun anten. ADS-B (1090 MHz) kısa antenle çalışır; **VHF/UHF (airband, AIS, APRS, ACARS/VDL2, ISM 433)** için düzgün ~½λ dipol veya ~46 cm ¼λ gerekir. Zayıf bantlarda asıl kısıt kod değil **reception** (alım). |
| **Güç/USB** | **Beslemeli USB hub** şiddetle önerilir — 820T2 yük altında (ısı / yetersiz güç) USB'den düşebilir. |
| **Bilgisayar** | Herhangi bir Linux PC / SBC (Raspberry Pi sınıfı ve üzeri). |

> 📷 *İpucu: kendi kurulumunun fotoğrafını `docs/images/hardware.jpg` olarak ekleyip burada gösterebilirsin.*

## 🧰 Yazılım gereksinimleri

| Bileşen | Ne için |
|-----------|-----------|
| **Linux** (Debian 12 test edildi) + **Python 3.11+** | çekirdek (web backend yalnız stdlib) |
| **rtl-sdr** araçları (`rtl_power`, `rtl_fm`, `rtl_sdr`, `rtl_test`) | tarama & canlı ses (**zorunlu**) |
| `numpy` | modülasyon sınıflama |
| `rtl_433` | ISM 433 MHz sensörleri |
| `multimon-ng` | Pager (POCSAG/FLEX) & APRS |
| `dump1090` | ADS-B |
| `rtl_ais` | AIS |
| `acarsdec` / `dumpvdl2` | ACARS / VDL2 |
| `redsea` | RDS |
| **whisper.cpp** (+ model) · opsiyonel `faster-whisper` | konuşma→metin |

## 📥 Kurulum

```bash
git clone https://github.com/haliskilic/hksdr.git
cd hksdr

# 1) Çekirdek: RTL-SDR sürücüleri + yaygın decoder araçları (apt; sudo gerek)
sudo bash setup/setup.sh

# 2) Opsiyonel decoder'lar (kaynaktan ~/.local içine derle)
bash setup/build_dump1090.sh      # ADS-B
bash setup/build_rtl_ais.sh       # AIS
bash setup/build_acarsdec.sh      # ACARS
bash setup/build_dumpvdl2.sh      # VDL2
bash setup/build_redsea.sh        # RDS

# 3) Opsiyonel konuşma→metin (whisper.cpp small, çok-dilli)
bash setup/setup_whisper.sh
# Opsiyonel Türkçe-özel model (daha ağır, USE_DISTIL_TR=1 ile devreye girer):
bash setup/setup_distil_tr.sh
```

Web uygulamasının **Python bağımlılığı yoktur** — yalnızca opsiyonel STT/sınıflama
`numpy` / `faster-whisper` kullanır.

## 🚀 Kullanım

```bash
scripts/run_webapp.sh                 # → http://localhost:8000
# seçenekler:
PORT=9000 GAIN=45 scripts/run_webapp.sh
HOST=0.0.0.0 scripts/run_webapp.sh    # LAN'da sun (güvenlik için AUTH kullan)
AUTH=kullanici:parola HOST=0.0.0.0 scripts/run_webapp.sh
USE_DISTIL_TR=1 scripts/run_webapp.sh # Türkçe distil-whisper motorunu aç
```

Sayfayı aç, **tarama otomatik başlar**. Sol menüden (☰) bir decoder'ı, haritayı, waterfall'ı,
kayıtları, analitiği veya ayarları aç. Bir frekansın **▶ Dinle**'sine bas, sesi duy. Dili
istediğin an sağ üstteki **🇬🇧/🇹🇷** düğmesiyle değiştir.

## 🏗️ Mimari (kısa)

Tek bir `Device` yöneticisi, tek RTL-SDR'yi karşılıklı-dışlamalı modlar arasında sıralı kullanır
(`scan / listen / adsb / ais / aprs / ism / pager / acars / rds / vdl2 / wf`). Tarayıcı arka plan
thread'inde çalışır; decoder'lar araç çıktısını SQLite / bellek durumuna ayrıştıran alt-süreç
sarmalayıcılarıdır. Frontend, JSON endpoint'lerini yoklayan bağımlılıksız vanilla-JS SPA'dır.
Tam tasarım, durum ve yol haritası için: [`docs/ROADMAP.md`](docs/ROADMAP.md).

## ⚖️ Yasal & etik

HK.SDR **yalnızca alıcıdır (RX-only)** ve **eğitim ile açık sinyallerin yasal izlenmesi** içindir.
Ülkenin radyo/gizlilik yasalarına uymak senin sorumluluğundadır.

- Pager içeriği **maskelenir** (yalnız tür/capcode/uzunluk saklanır) — tasarımdan gizlilik.
- **Şifreli / kamu güvenliği** sesini (örn. TETRA/P25/DMR) çözmek **kapsam dışıdır**.
- STT yalnızca **yasal, açık analog ve şifresiz-dijital** sinyaller içindir.

## 📄 Lisans

HK.SDR, **GNU Affero General Public License v3.0 (AGPL-3.0)** ile lisanslıdır —
bkz. [`LICENSE`](LICENSE). Özetle: özgürce kullanabilir, inceleyebilir, değiştirebilir ve
kendin barındırabilirsin; ancak değiştirilmiş bir sürümü ağ servisi olarak çalıştırırsan
kaynağını aynı lisansla kullanıcılarına açmalısın.

AGPL-3.0 ile uyumsuz kullanım için (örn. kapalı kaynak / ticari ürünler) ayrı bir
**ticari lisans** mevcuttur — bkz. [`COMMERCIAL_LICENSE.md`](COMMERCIAL_LICENSE.md).

**Telif © 2026 Halis KILIÇ.** Tüm hakları saklıdır.

---

<div align="center">
RTL-SDR topluluğu için yapıldı · katkılar memnuniyetle (bkz. <a href="CONTRIBUTING.md">CONTRIBUTING</a>)
</div>
