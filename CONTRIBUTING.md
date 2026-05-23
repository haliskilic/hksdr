# Contributing to HK.SDR

[English](#english) · [Türkçe](#türkçe)

---

## English

Contributions are welcome — bug reports, fixes, new decoders, translations and docs.

### Development setup
- Linux + Python 3.11+, an RTL-SDR dongle, and the tools in [README](README.md#-software-requirements).
- The **web backend uses only the Python standard library** — please keep it dependency-free.
  Optional features (STT, classification) may use `numpy` / external CLI tools, invoked as subprocesses.
- Run locally: `scripts/run_webapp.sh` → http://localhost:8000

### Guidelines
- Match the surrounding style; keep changes focused. Verify Python with `python3 -m py_compile`
  and JS with `node -c webapp/static/app.js`.
- **One RTL-SDR, one task at a time:** any new device user must respect `DEVICE.lock` /
  `TRANSITION_LOCK` and the mutually-exclusive mode model (see `webapp/decoder_base.py`).
- **i18n:** every user-facing string must exist in **both** `I18N.en` and `I18N.tr` in
  `webapp/static/app.js` (or be marked with `data-i18n` in `index.html`). Keep keys in parity.
- **Stay receive-only and lawful.** No transmit features; no decoding of encrypted/public-safety
  voice; keep privacy protections (e.g. pager content masking).

### Reporting bugs
Open an issue with: what you did, what you expected, what happened, your OS, dongle model and
relevant logs (`/tmp` webapp log). For security issues see [SECURITY.md](SECURITY.md).

### Licensing of contributions (important)
HK.SDR is dual-licensed (AGPL-3.0 + commercial — see [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)).
By submitting a contribution you agree that:
1. your contribution is licensed under the **AGPL-3.0**, and
2. you grant the project maintainer (**Halis KILIÇ**) the right to also distribute your
   contribution under the **commercial license** (so the project can remain dual-licensed).

If you cannot agree to this, please note it in your pull request so it can be handled separately.

---

## Türkçe

Katkılar memnuniyetle karşılanır — hata bildirimi, düzeltme, yeni decoder, çeviri ve dokümantasyon.

### Geliştirme ortamı
- Linux + Python 3.11+, bir RTL-SDR çubuğu ve [README](README.tr.md#-yazılım-gereksinimleri)'deki araçlar.
- **Web backend yalnızca Python standart kütüphanesini kullanır** — lütfen bağımlılıksız tut.
  Opsiyonel özellikler (STT, sınıflama) `numpy` / harici CLI araçlarını alt-süreç olarak çağırabilir.
- Yerel çalıştır: `scripts/run_webapp.sh` → http://localhost:8000

### Kurallar
- Çevredeki stile uy; değişiklikleri odaklı tut. Python'ı `python3 -m py_compile`, JS'i
  `node -c webapp/static/app.js` ile doğrula.
- **Tek RTL-SDR, tek anda tek iş:** yeni bir cihaz kullanıcısı `DEVICE.lock` / `TRANSITION_LOCK`
  ve karşılıklı-dışlamalı mod modeline uymalı (bkz. `webapp/decoder_base.py`).
- **i18n:** kullanıcıya görünen her metin `webapp/static/app.js` içinde **hem** `I18N.en` **hem**
  `I18N.tr`'de olmalı (ya da `index.html`'de `data-i18n` ile işaretlenmeli). Anahtarları eşit tut.
- **Yalnızca alıcı ve yasal kal.** Verici özellik yok; şifreli/kamu güvenliği sesi çözme yok;
  gizlilik korumalarını (örn. pager içerik maskesi) koru.

### Hata bildirimi
Bir issue aç: ne yaptın, ne bekledin, ne oldu, işletim sistemin, dongle modelin ve ilgili loglar
(`/tmp` webapp logu). Güvenlik sorunları için bkz. [SECURITY.md](SECURITY.md).

### Katkıların lisansı (önemli)
HK.SDR çift lisanslıdır (AGPL-3.0 + ticari — bkz. [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)).
Bir katkı göndererek şunları kabul edersin:
1. katkın **AGPL-3.0** ile lisanslıdır, ve
2. proje sahibine (**Halis KILIÇ**) katkını **ticari lisans** altında da dağıtma hakkını verirsin
   (böylece proje çift-lisanslı kalabilir).

Bunu kabul edemiyorsan, ayrı değerlendirilebilmesi için pull request'inde belirt.
