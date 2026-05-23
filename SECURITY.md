# Security Policy

[English](#english) · [Türkçe](#türkçe)

## English

### Reporting a vulnerability
Please report security issues **privately** by email to **Halis KILIÇ**
<haliskilic90@gmail.com> rather than opening a public issue. Include reproduction steps and
affected version/commit. You will receive an acknowledgement and a fix timeline.

### Scope & hardening notes
- HK.SDR is **receive-only**; it controls one local RTL-SDR and a local web server.
- By default the server binds to **`127.0.0.1`** (localhost only).
- If you expose it on a LAN with `HOST=0.0.0.0`, **always set `AUTH=user:pass`** (HTTP Basic auth)
  and prefer a trusted network or a reverse proxy with TLS. The built-in server is plain HTTP.
- The app runs external SDR tools as subprocesses with fixed argument lists (no shell);
  user-supplied values (gain/PPM, CSV, search) are validated/escaped, and file-serving endpoints
  are restricted to their directories.
- Treat captured/transcribed RF data according to your local laws; pager content is masked by design.

## Türkçe

### Güvenlik açığı bildirimi
Lütfen güvenlik sorunlarını herkese açık issue açmak yerine **gizli olarak** e-posta ile bildir:
**Halis KILIÇ** <haliskilic90@gmail.com>. Yeniden üretme adımlarını ve etkilenen sürüm/commit'i
ekle. Bir onay ve düzeltme zaman çizelgesi alırsın.

### Kapsam & sertleştirme notları
- HK.SDR **yalnızca alıcıdır**; tek bir yerel RTL-SDR'yi ve yerel bir web sunucusunu kontrol eder.
- Sunucu varsayılan olarak **`127.0.0.1`**'e (yalnız localhost) bağlanır.
- `HOST=0.0.0.0` ile LAN'a açarsan **mutlaka `AUTH=kullanici:parola` ayarla** (HTTP Basic auth);
  güvenilir ağ ya da TLS'li ters vekil tercih et. Yerleşik sunucu düz HTTP'dir.
- Uygulama harici SDR araçlarını sabit argüman listeleriyle (shell'siz) alt-süreç olarak çalıştırır;
  kullanıcı değerleri (kazanç/PPM, CSV, arama) doğrulanır/kaçışlanır, dosya-sunan endpoint'ler
  kendi dizinleriyle sınırlıdır.
- Yakalanan/çözülen RF verisini yerel yasalarına göre değerlendir; pager içeriği tasarımdan maskelidir.
