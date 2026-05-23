#!/usr/bin/env python3
"""
HK.SDR — browser-based RTL-SDR scanner web app (tarayıcıda çalışan web uygulaması).

- Arka planda rtl_power ile bantları döngüsel tarar, sinyalleri tespit edip
  kategoriyle SQLite'a loglar (sürekli/historik).
- Web arayüzünde en güncel üstte, geçmiş altta listelenir.
- Ses-uygun (analog) kanallarda ▶ ile CANLI ses akışı (WAV) verir.
- Dinleme başlayınca tarama durur (tek USB cihaz); dinleme bitince devam eder.

Bağımlılık YOK (yalnızca Python stdlib). Çalıştır:  python3 webapp/app.py
Ortam değişkenleri:  PORT (8000), GAIN (40)
"""
import os
import re
import sys
import hmac
import time
import json
import atexit
import base64
import shutil
import signal
import sqlite3
import struct
import queue
import threading
import subprocess
import tempfile
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bands import SCAN_PLAN, CATEGORY_COLORS, DEMOD, PROFILES  # noqa: E402
from adsb import AdsbTracker  # noqa: E402
from ism import IsmDecoder  # noqa: E402
from waterfall import Waterfall  # noqa: E402
from ais import AisTracker  # noqa: E402
from aprs import AprsTracker  # noqa: E402
from whisper_stt import Transcriber  # noqa: E402  (STT motoru: whisper.cpp small)
from pager import PagerDecoder  # noqa: E402
from acars import AcarsDecoder  # noqa: E402
from rds import RdsDecoder  # noqa: E402
from vdl2 import Vdl2Decoder  # noqa: E402
from classify import classify as classify_signal  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "static")
DB_PATH = os.path.join(HERE, "sdrscanner.db")
RECORDINGS = os.path.join(HERE, "recordings")
os.makedirs(RECORDINGS, exist_ok=True)
REC_KEEP = 50              # arşivde tutulacak azami kayıt
GAIN = os.environ.get("GAIN", "40")
PORT = int(os.environ.get("PORT", "8000"))
TMPDIR = tempfile.mkdtemp(prefix="sdrscan_")
atexit.register(lambda: shutil.rmtree(TMPDIR, ignore_errors=True))   # çıkışta geçici dizini temizle


def _qint(qs, key, default):
    """Sorgu parametresini güvenli int'e çevir (bozuk değer → varsayılan, 500 yok)."""
    try:
        return int(qs.get(key, [str(default)])[0])
    except (ValueError, TypeError):
        return default


# --------------------------------------------------------------------------- DB
from db import DB  # noqa: E402  (Faz D: sınıf webapp/db.py'ye taşındı)
# ----------------------------------------------------------------- sinyal tespit
from detect import detect_signals  # noqa: E402  (Faz D: webapp/detect.py)
# ------------------------------------------------------------- cihaz yöneticisi
class Device:
    def __init__(self):
        self.lock = threading.Lock()
        self.proc = None
        self.mode = "scan"          # "scan" | "listen"
        self.listen = None          # {freq_mhz, demod, rate}
        self.cur_band = None
        self.last_scan_ts = 0.0
        self.device_ok = True       # H3: dongle erişilebilir mi (ardışık sweep hatasıyla düşer)
        self.fail_streak = 0        # ardışık başarısız sweep sayısı

    def _kill_locked(self):
        p = self.proc
        self.proc = None
        if p and p.poll() is None:
            # Önce SIGTERM: rtl_power/rtl_fm/dump1090 cihazı temiz serbest bıraksın.
            try:
                p.terminate()
            except Exception:
                pass
            try:
                p.wait(timeout=2)
            except Exception:
                try:
                    p.send_signal(signal.SIGKILL)
                    p.wait(timeout=2)
                except Exception:
                    pass
            time.sleep(0.3)   # USB'nin tam serbest kalması için kısa bekleme


DEVICE = Device()
TRANSITION_LOCK = threading.RLock()   # H1: mod geçişlerini (durdur→mode set→spawn) bütün serialize et
DBASE = DB(DB_PATH)
ADSB = AdsbTracker(DEVICE, DBASE)
ISM = IsmDecoder(DEVICE, DBASE)
WF = Waterfall(DEVICE)
AIS = AisTracker(DEVICE, DBASE)
APRS = AprsTracker(DEVICE, DBASE)
PAGER = PagerDecoder(DEVICE, DBASE)
ACARS = AcarsDecoder(DEVICE, DBASE)
RDS = RdsDecoder(DEVICE, DBASE)
VDL2 = Vdl2Decoder(DEVICE, DBASE)
TRANSCRIBER = Transcriber(DEVICE)        # taramaya gömülü STT

# STT durumu (anahtar = round(MHz, 3))
STT_TEXT = {}              # freq -> {"text", "ts"}   (yalnızca dolu cümleler)
AUDIO_REG = {}             # freq -> {"hz","demod","last_seen","checked","active"}
STT_LOCK = threading.Lock()
STT_BUDGET = 30.0          # her turda STT'ye ayrılan azami süre (sn)
START_TS = time.time()     # uygulama açılış anı
STT_WARMUP = 45.0          # açılış ısınması: bu süre boyunca STT başlamaz (ilk dakikada
                           # menü/geçiş akıcı kalsın — Vosk yükü kullanıcıyı etkilemesin)
RMS_THRESH = 0.03          # hareketlilik (aktif kanal) eşiği
PER_BAND_AUDIO = 5         # band başına kaç ses frekansı kaydedilsin
AUDIO_REG_MAX_AGE = 600    # sn; bu kadar görülmeyen freq kayıttan düşer
ACTIVE_PROFILE = "Tümü"     # 4.3 tarama profili
SCHEDULE = []               # 4.3 zamanlama: [{"from":h,"to":h,"profile":ad}]
AUDIO_CATS = sorted({b.category for b in SCAN_PLAN if b.audio})  # STT'ye uygun kategoriler
STT_CATS = set(AUDIO_CATS)  # STT açık kategoriler (varsayılan: hepsi açık)
STT_LANGS = set(TRANSCRIBER.langs_available())  # STT açık diller (tr/en, varsayılan: hepsi)

# Canlı dinleme STT: dinlerken aynı sesi Vosk'a besleyip akan metin üretir.
LISTEN_STT = {"text": "", "partial": "", "lang": "", "id": 0}
LISTEN_STT_LOCK = threading.Lock()


def run_stt_pass():
    """Tur sonu STT geçişi: ses frekanslarını öncelikle BOŞ olanlar olmak üzere
    gez; her birinde hareketlilik (RMS) varsa transkript et. Zaman bütçeli."""
    now = time.time()
    with STT_LOCK:
        for k in [k for k, e in AUDIO_REG.items()
                  if now - e.get("last_seen", 0) > AUDIO_REG_MAX_AGE]:
            del AUDIO_REG[k]
            STT_TEXT.pop(k, None)          # eskiyen frekansın transkripti de düşsün (sızıntı önle)
        cats = set(STT_CATS)
        langs = sorted(STT_LANGS)
        items = [(k, dict(e)) for k, e in AUDIO_REG.items()
                 if e.get("category") in cats]      # yalnızca STT'si açık kategoriler
        have = set(STT_TEXT.keys())
    if not items or not langs:                       # kategori veya dil seçili değilse STT kapalı
        return
    # öncelik: STT'si olmayanlar (boş) önce, sonra en eski kontrol edilen (sürekli taze)
    items.sort(key=lambda kv: (1 if kv[0] in have else 0, kv[1].get("checked", 0.0)))
    budget_end = time.time() + STT_BUDGET
    for k, e in items:
        if DEVICE.mode != "scan" or time.time() > budget_end:
            break
        text, lang, rms = TRANSCRIBER.probe(e["hz"], e["demod"], langs=langs)
        ts = time.time()
        with STT_LOCK:
            if k in AUDIO_REG:
                AUDIO_REG[k]["checked"] = ts
                AUDIO_REG[k]["active"] = rms >= RMS_THRESH
            if text:
                STT_TEXT[k] = {"text": text, "lang": lang, "ts": ts}


LISTEN_STT_BLOCK = 4.0     # canlı dinlemede her ~kaç sn'lik blok whisper'a verilsin

def _listen_stt_worker(rate, langs, q, sess_id):
    """Dinleme PCM'ini biriktirir, ~her LISTEN_STT_BLOCK sn'de whisper.cpp ile çözer
    (Whisper streaming değil → parça-parça). Ayrı thread; ses akışını bloklamaz."""
    block_bytes = int(rate * 2 * LISTEN_STT_BLOCK)
    buf = bytearray()
    finals = []

    def _flush(pcm):
        if len(pcm) < rate:                       # <0.5 sn → atla
            return
        text, lang = TRANSCRIBER.transcribe_pcm(bytes(pcm), rate, langs)
        with LISTEN_STT_LOCK:
            if LISTEN_STT["id"] != sess_id:       # yeni oturum başladı → bırak
                return False
            if text:
                finals.append(text)
                del finals[:-12]                  # son ~12 bloğu tut
                LISTEN_STT["text"] = " ".join(finals)
                if lang:
                    LISTEN_STT["lang"] = lang
            LISTEN_STT["partial"] = ""            # whisper'da anlık partial yok
        return True

    while True:
        chunk = q.get()
        if chunk is None:
            _flush(buf)                           # kapanışta kalanı çöz
            return
        buf += chunk
        if len(buf) >= block_bytes:
            block, buf = bytes(buf), bytearray()
            if _flush(block) is False:
                return


def stop_other_modes(keep):
    """Tek cihaz: yeni mod başlamadan diğer cihaz-modlarını durdur."""
    if keep != "adsb" and ADSB.running:
        ADSB.stop()
    if keep != "ism" and ISM.running:
        ISM.stop()
    if keep != "wf" and WF.running:
        WF.stop()
    if keep != "ais" and AIS.running:
        AIS.stop()
    if keep != "aprs" and APRS.running:
        APRS.stop()
    if keep != "pager" and PAGER.running:
        PAGER.stop()
    if keep != "acars" and ACARS.running:
        ACARS.stop()
    if keep != "rds" and RDS.running:
        RDS.stop()
    if keep != "vdl2" and VDL2.running:
        VDL2.stop()
    if keep != "listen" and DEVICE.listen:
        stop_listen()


def start_mode(keep, starter):
    """H1: mod geçişini atomik yap — diğer modları durdur + yeni modu başlat aynı
    TRANSITION_LOCK altında (iki eşzamanlı POST iki rtl_* sürecini cihaza çıkaramaz)."""
    with TRANSITION_LOCK:
        stop_other_modes(keep)
        return starter()


# mod adı → decoder örneği (do_POST'taki tekrar eden start/stop bloklarını tek dispatch'e indirir)
MODE_DEC = {"adsb": ADSB, "ais": AIS, "aprs": APRS, "ism": ISM, "pager": PAGER,
            "acars": ACARS, "rds": RDS, "vdl2": VDL2, "wf": WF}


def _start_decoder(mode, qs):
    """Mod-özgü argümanları çözüp start_mode ile başlat (wf: merkez/genişlik; pager/rds: freq)."""
    dec = MODE_DEC[mode]
    if mode == "wf":
        try:
            c = float(qs.get("center", ["100"])[0]) * 1e6
            s = float(qs.get("span", ["2"])[0]) * 1e6
        except (ValueError, TypeError):       # bozuk param → varsayılan (500 atma)
            c, s = 100e6, 2e6
        return start_mode("wf", lambda: dec.start(c, s))
    if mode in ("pager", "rds"):
        return start_mode(mode, lambda: dec.start(qs.get("freq", [""])[0] or None))
    return start_mode(mode, dec.start)


def run_sweep(band):
    """Tek bir bandı tarar; iptal edilirse None döner."""
    csv = os.path.join(TMPDIR, f"{band.category}_{int(band.lo)}.csv")
    cmd = ["rtl_power", "-f", f"{int(band.lo)}:{int(band.hi)}:{band.bin}",
           "-i", "1", "-g", _gain(), "-p", _ppm(), "-1", csv]
    with DEVICE.lock:
        if DEVICE.mode != "scan":
            return None
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print("HATA: rtl_power bulunamadı (rtl-sdr kurulu mu?)", file=sys.stderr)
            return None
        DEVICE.proc = proc
        DEVICE.cur_band = band.name
    rc = proc.wait()
    with DEVICE.lock:
        if DEVICE.proc is proc:
            DEVICE.proc = None
    if DEVICE.mode != "scan":
        return None                      # mod değişti — hata değil
    if rc != 0:                          # rtl_power hata → cihaz/USB düşmüş olabilir
        DEVICE.fail_streak += 1
        if DEVICE.fail_streak >= 3:
            DEVICE.device_ok = False
        return None
    DEVICE.fail_streak = 0
    DEVICE.device_ok = True
    return csv


def _gain():
    return os.environ.get("GAIN", "40")


def _ppm():
    return os.environ.get("PPM", "0")


def apply_schedule():
    """4.3: saat çizelgesine göre aktif profili ayarla. (Her tarama turunda çağrılır;
    bozuk girdi scanner thread'ini ASLA çökertmemeli → tümü try/except içinde.)"""
    global ACTIVE_PROFILE
    if not SCHEDULE:
        return
    try:
        h = time.localtime().tm_hour
        for e in SCHEDULE:
            a, b = int(e.get("from", 0)), int(e.get("to", 0))
            inrange = (a <= h < b) if a <= b else (h >= a or h < b)   # gece sarması
            if inrange and e.get("profile") in PROFILES:
                ACTIVE_PROFILE = e["profile"]
                return
    except (ValueError, TypeError):
        pass


def scanner_loop():
    # Tarama + STT'yi düşük önceliğe al ki HTTP (menü geçişi/poll) akıcı kalsın.
    try:
        os.nice(10)
    except Exception:
        pass
    while True:
        if DEVICE.mode != "scan":
            time.sleep(0.3)
            continue
        if not DEVICE.device_ok:        # H3: dongle hatalı → tek yoklama + geri çekil (boşa spinleme)
            run_sweep(SCAN_PLAN[0])      # başarılı olursa device_ok yeniden True olur
            if not DEVICE.device_ok:
                time.sleep(3.0)
                continue
        apply_schedule()
        prof_cats = PROFILES.get(ACTIVE_PROFILE)   # None = tümü
        for band in SCAN_PLAN:
            if DEVICE.mode != "scan":
                break
            if prof_cats is not None and band.category not in prof_cats:
                continue                       # profil dışı bandı atla
            csv = run_sweep(band)
            if not csv:
                continue
            sigs = detect_signals(csv, band)
            if sigs:
                DBASE.insert(band, sigs)
                if band.audio and band.demod:
                    # ses kanallarını kayda al (band başına en güçlü PER_BAND_AUDIO)
                    now = time.time()
                    with STT_LOCK:
                        for fc, _pk, _bw in sorted(sigs, key=lambda s: -s[1])[:PER_BAND_AUDIO]:
                            k = round(fc / 1e6, 3)
                            e = AUDIO_REG.setdefault(k, {"checked": 0.0, "active": False})
                            e["hz"] = fc
                            e["demod"] = band.demod
                            e["category"] = band.category
                            e["last_seen"] = now
            DEVICE.last_scan_ts = time.time()
        DEVICE.cur_band = None
        # --- STT geçişi: boşları/aktifleri sürekli güncelle (zaman bütçeli) ---
        # Açılış ısınması bitene kadar atla (ilk dakikada arayüz akıcı kalsın).
        if (DEVICE.mode == "scan" and TRANSCRIBER.available()
                and time.time() - START_TS >= STT_WARMUP):
            run_stt_pass()
        time.sleep(0.3)


def start_listen(freq_hz, demod):
    stop_other_modes("listen")
    args, rate = DEMOD.get(demod, DEMOD["nfm"])
    cmd = ["rtl_fm", "-f", str(int(freq_hz)), "-g", _gain(), "-p", _ppm()] + args
    with DEVICE.lock:
        DEVICE.mode = "listen"
        DEVICE._kill_locked()
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL, bufsize=0)
        except FileNotFoundError:
            DEVICE.mode = "scan"
            return None, 0
        DEVICE.proc = proc
        DEVICE.listen = dict(freq_mhz=freq_hz / 1e6, demod=demod, rate=rate)
    return proc, rate


def stop_listen(only_proc=None):
    with DEVICE.lock:
        if only_proc is not None and DEVICE.proc is not only_proc:
            return            # daha yeni bir dinleme başlamış; dokunma
        DEVICE._kill_locked()
        DEVICE.listen = None
        DEVICE.mode = "scan"


def wav_header(rate, bits=16, ch=1, datasize=0x7FFFF000):
    return (b"RIFF" + struct.pack("<I", 36 + datasize) + b"WAVE" +
            b"fmt " + struct.pack("<IHHIIHH", 16, 1, ch, rate,
                                  rate * ch * bits // 8, ch * bits // 8, bits) +
            b"data" + struct.pack("<I", datasize))


def _prune_recordings():
    try:
        files = sorted((os.path.join(RECORDINGS, f) for f in os.listdir(RECORDINGS)
                        if f.endswith(".wav")), key=os.path.getmtime)
        for p in files[:-REC_KEEP]:
            try:
                os.remove(p)
            except OSError:
                pass
    except OSError:
        pass


def _list_recordings():
    out = []
    try:
        names = [f for f in os.listdir(RECORDINGS) if f.endswith(".wav")]
    except OSError:
        return out
    for f in names:
        try:
            size = os.path.getsize(os.path.join(RECORDINGS, f))
            ts = os.path.getmtime(os.path.join(RECORDINGS, f))
        except OSError:
            continue
        parts = f[:-4].split("_")           # {ts}_{freqMHz}_{demod}
        out.append(dict(file=f, ts=ts,
                        freq=parts[1] if len(parts) > 1 else "?",
                        demod=parts[2] if len(parts) > 2 else "",
                        size=size))
    out.sort(key=lambda x: x["ts"], reverse=True)
    return out


# ----------------------------------------------------------------- HTTP handler
def measure_ppm(seconds=45):
    """4.6: rtl_test -p ile dongle saat hatasını (ppm) ölç ve uygula.
    stdbuf ile satır-tamponu (yoksa satırlar gecikir); 'ppm' geçen satırdaki
    son sayı kümülatif PPM olarak alınır (rtl_test ~10s'de bir raporlar)."""
    cmd = (["stdbuf", "-oL"] if shutil.which("stdbuf") else []) + ["rtl_test", "-p"]
    with DEVICE.lock:
        if DEVICE.mode != "scan":
            return {"ok": False, "error": "yalnızca tarama modunda ölçülür"}
        DEVICE._kill_locked()
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True)
        except FileNotFoundError:
            return {"ok": False, "error": "rtl_test yok"}
        DEVICE.proc = proc
    # KİLİT DIŞINDA oku — uzun ölçüm boyunca cihaz alt sistemini/uygulamayı bloklama
    last = None
    t0 = time.time()
    try:
        while time.time() - t0 < seconds and DEVICE.mode == "scan":
            line = proc.stdout.readline()
            if not line:
                break
            if "ppm" in line.lower():
                nums = re.findall(r"-?\d+(?:\.\d+)?", line)
                if nums:
                    last = nums[-1]      # kümülatif ppm satırdaki son sayı
    except Exception:
        pass
    with DEVICE.lock:
        if DEVICE.proc is proc:           # hâlâ bizim sürecimizse temiz öldür
            DEVICE._kill_locked()
    if proc.poll() is None:               # sahip değiştiyse bile bizimkini öldür (yetim bırakma)
        try:
            proc.terminate(); proc.wait(timeout=2)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    if last is not None:
        os.environ["PPM"] = str(int(round(float(last))))
        return {"ok": True, "ppm": os.environ["PPM"]}
    return {"ok": False, "error": "ölçülemedi (~1 dk + güçlü sinyal gerekebilir; PPM'i elle de girebilirsin)"}


def import_csv(text):
    """4.5: CSV (freq_mhz[,etiket[,demod[,kategori]]]) → yer imleri."""
    import csv as _csv
    import io
    items = []
    for row in _csv.reader(io.StringIO(text)):
        if not row:
            continue
        try:
            f = float(str(row[0]).strip())
        except ValueError:
            continue                              # başlık/boş satır
        if not (0.1 < f < 2000):
            continue
        label = row[1].strip() if len(row) > 1 and row[1].strip() else f"{f:.4f} MHz"
        d = row[2].strip().lower() if len(row) > 2 else ""
        if d not in ("wbfm", "am", "nfm"):
            d = "wbfm" if 87 <= f <= 108 else ("am" if 118 <= f <= 137 else "nfm")
        cat = row[3].strip() if len(row) > 3 else ""
        items.append(dict(freq_mhz=round(f, 4), label=label, demod=d, category=cat))
    if items:
        DBASE.add_bookmarks(items)
    return len(items)


CONTENT_TYPES = {".html": "text/html; charset=utf-8",
                 ".js": "application/javascript; charset=utf-8",
                 ".css": "text/css; charset=utf-8",
                 ".json": "application/manifest+json",
                 ".svg": "image/svg+xml"}
HOST = os.environ.get("HOST", "127.0.0.1")     # 0.0.0.0 = LAN erişimi (4.4)
AUTH = os.environ.get("AUTH", "")              # "kullanıcı:parola" → temel kimlik doğrulama


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            return self.rfile.read(n).decode("utf-8", "ignore") if n else ""
        except (ValueError, OSError):
            return ""

    def _auth_ok(self):
        if not AUTH:
            return True
        h = self.headers.get("Authorization", "")
        if h.startswith("Basic "):
            try:
                if hmac.compare_digest(base64.b64decode(h[6:]).decode("utf-8", "replace"), AUTH):
                    return True            # sabit-zamanlı karşılaştırma (timing attack'a kapalı)
            except Exception:
                pass
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="SDR"')
        self.end_headers()
        return False

    def _static(self, name):
        path = os.path.join(STATIC, name)
        if not os.path.isfile(path):
            self.send_error(404)
            return
        with open(path, "rb") as f:
            body = f.read()
        ext = os.path.splitext(name)[1]
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES.get(ext, "text/plain"))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self._auth_ok():
            return
        u = urlparse(self.path)
        path, qs = u.path, parse_qs(u.query)

        if path == "/":
            return self._static("index.html")
        if path in ("/app.js", "/style.css", "/manifest.json", "/sw.js", "/icon.svg"):
            return self._static(path.lstrip("/"))

        if path == "/api/bands":
            return self._json(dict(colors=CATEGORY_COLORS,
                                   bands=[b.name for b in SCAN_PLAN]))

        if path == "/api/status":
            return self._json(dict(
                mode=DEVICE.mode,
                listen=DEVICE.listen,
                cur_band=DEVICE.cur_band,
                last_scan_ts=DEVICE.last_scan_ts,
                device_ok=DEVICE.device_ok,
                total=DBASE.count(),
                gain=_gain(),
                adsb_available=ADSB.available(),
                adsb_count=len(ADSB.aircraft) if DEVICE.mode == "adsb" else 0,
                ism_available=ISM.available(),
                ais_available=AIS.available(),
                aprs_available=APRS.available(),
                pager_available=PAGER.available(),
                acars_available=ACARS.available(),
                rds_available=RDS.available(),
                vdl2_available=VDL2.available(),
                stt_available=TRANSCRIBER.available(),
                stt_cats=dict(all=AUDIO_CATS, on=sorted(STT_CATS)),
                stt_langs=dict(all=TRANSCRIBER.langs_available(), on=sorted(STT_LANGS))))

        if path == "/api/aircraft":
            return self._json(ADSB.snapshot())

        if path == "/api/ism/devices":           # 2B: gruplu canlı ISM cihaz tablosu
            return self._json(ISM.snapshot())

        if path == "/api/messages":
            src = qs.get("source", [None])[0]
            limit = _qint(qs, "limit", 200)
            return self._json(DBASE.recent_messages(source=src, limit=min(max(limit, 1), 1000)))

        if path == "/api/waterfall":
            return self._json(WF.snapshot())

        if path == "/api/analytics":
            hours = _qint(qs, "hours", 24)
            return self._json(DBASE.analytics(hours=min(max(hours, 1), 168)))

        if path == "/api/search":
            return self._json(DBASE.search(qs.get("q", [""])[0]))

        if path == "/api/classify":
            try:
                freq = float(qs["freq"][0]) * 1e6
            except (KeyError, ValueError):
                return self.send_error(400)
            with TRANSITION_LOCK:                       # mod-başlatmayla yarışma
                return self._json(classify_signal(DEVICE, freq, gain=_gain()))

        if path == "/api/export":
            what = qs.get("what", ["detections"])[0]
            fmt = qs.get("fmt", ["csv"])[0]
            cols, rows = DBASE.export(what)
            if fmt == "json":
                body = json.dumps([dict(zip(cols, r)) for r in rows]).encode()
                ctype, ext = "application/json", "json"
            else:
                import io
                import csv as _csv
                buf = io.StringIO()
                w = _csv.writer(buf)
                w.writerow(cols)
                w.writerows(rows)
                body = buf.getvalue().encode()
                ctype, ext = "text/csv", "csv"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Disposition", f'attachment; filename="{what}.{ext}"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/profile":
            return self._json(dict(all=list(PROFILES.keys()), active=ACTIVE_PROFILE, schedule=SCHEDULE))

        if path == "/api/config":
            return self._json(dict(gain=_gain(), ppm=_ppm()))

        if path == "/api/bookmarks":
            return self._json(DBASE.bookmarks())

        if path == "/api/recordings":
            return self._json(_list_recordings())

        if path == "/api/rec":
            name = os.path.basename(qs.get("file", [""])[0])
            fp = os.path.join(RECORDINGS, name)
            if not name.endswith(".wav") or not os.path.isfile(fp):
                return self.send_error(404)
            with open(fp, "rb") as fh:
                body = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/ships":
            return self._json(AIS.snapshot())

        if path == "/api/aprs":
            return self._json(APRS.snapshot())

        if path == "/api/detections":
            limit = _qint(qs, "limit", 300)
            cats = qs.get("categories", [None])[0]
            cats = cats.split(",") if cats else None
            if qs.get("group", ["0"])[0] in ("1", "true"):     # 1B: frekansa göre grupla
                rows = DBASE.recent_grouped(limit=min(max(limit, 1), 2000), categories=cats)
            else:
                rows = DBASE.recent(limit=min(limit, 1000), categories=cats)
            with STT_LOCK:
                items = list(STT_TEXT.items())
            for r in rows:
                r["stt"] = ""
                r["stt_lang"] = ""
                if r.get("audio"):
                    bv, bestd = None, 0.06         # MHz tolerans
                    for f, v in items:
                        d = abs(f - r["freq_mhz"])
                        if d < bestd:
                            bestd, bv = d, v
                    if bv:
                        r["stt"] = bv["text"]
                        r["stt_lang"] = bv.get("lang", "")
            return self._json(rows)

        if path == "/api/listen/stt":
            with LISTEN_STT_LOCK:
                d = dict(LISTEN_STT)
            d["on"] = DEVICE.mode == "listen"
            d["avail"] = TRANSCRIBER.available() and bool(STT_LANGS)
            return self._json(d)

        if path == "/api/audio.wav":
            return self._stream_audio(qs)

        self.send_error(404)

    def do_POST(self):
        if not self._auth_ok():
            return
        u = urlparse(self.path)
        if u.path == "/api/listen/stop":
            with TRANSITION_LOCK:
                stop_listen()
            return self._json(dict(ok=True, mode=DEVICE.mode))
        # mod start/stop tek dispatch (adsb/ais/aprs/ism/pager/acars/rds/vdl2/wf)
        if u.path.startswith("/api/") and u.path.endswith(("/start", "/stop")):
            seg = u.path[5:].split("/")
            if len(seg) == 2 and seg[0] in MODE_DEC:
                if seg[1] == "start":
                    return self._json(dict(ok=_start_decoder(seg[0], parse_qs(u.query)),
                                           mode=DEVICE.mode))
                with TRANSITION_LOCK:
                    MODE_DEC[seg[0]].stop()
                return self._json(dict(ok=True, mode=DEVICE.mode))
        if u.path == "/api/rec/delete":
            name = os.path.basename(parse_qs(u.query).get("file", [""])[0])
            fp = os.path.join(RECORDINGS, name)
            if name.endswith(".wav") and os.path.isfile(fp):
                try:
                    os.remove(fp)
                except OSError:
                    pass
            return self._json(dict(ok=True))
        if u.path == "/api/stt/cats":
            global STT_CATS
            on = parse_qs(u.query).get("on", [""])[0]
            sel = {c for c in on.split(",") if c} & set(AUDIO_CATS)
            with STT_LOCK:
                STT_CATS = sel
            return self._json(dict(ok=True, on=sorted(sel)))
        if u.path == "/api/stt/langs":
            global STT_LANGS
            on = parse_qs(u.query).get("on", [""])[0]
            sel = {c for c in on.split(",") if c} & set(TRANSCRIBER.langs_available())
            with STT_LOCK:
                STT_LANGS = sel
            return self._json(dict(ok=True, on=sorted(sel)))
        if u.path == "/api/profile":
            global ACTIVE_PROFILE
            name = parse_qs(u.query).get("set", [""])[0]
            if name in PROFILES:
                ACTIVE_PROFILE = name
            return self._json(dict(ok=True, active=ACTIVE_PROFILE))
        if u.path == "/api/schedule":
            global SCHEDULE
            try:
                data = json.loads(self._body() or "[]")
                if not isinstance(data, list):
                    raise ValueError("liste bekleniyor")
                # şemayı doğrula (from/to int, profile str) — bozuk girdi scanner'ı çökertmesin
                SCHEDULE = [{"from": int(e.get("from", 0)), "to": int(e.get("to", 0)),
                             "profile": str(e.get("profile", ""))}
                            for e in data if isinstance(e, dict)]
            except (ValueError, TypeError):
                return self._json(dict(ok=False, error="geçersiz zamanlama (örn. [{\"from\":18,\"to\":24,\"profile\":\"...\"}])"))
            return self._json(dict(ok=True, schedule=SCHEDULE))
        if u.path == "/api/config":
            qs = parse_qs(u.query)
            if "gain" in qs:                           # M1: doğrula (bozuk değer tüm yakalamayı kırar)
                g = qs["gain"][0].strip()
                if g.lower() == "auto" or re.fullmatch(r"\d{1,2}(\.\d+)?", g):
                    os.environ["GAIN"] = g
                else:
                    return self._json(dict(ok=False, error="geçersiz kazanç (0–49 veya auto)"))
            if "ppm" in qs:
                try:
                    os.environ["PPM"] = str(int(float(qs["ppm"][0])))
                except ValueError:
                    return self._json(dict(ok=False, error="geçersiz PPM (tam sayı)"))
            return self._json(dict(ok=True, gain=_gain(), ppm=_ppm()))
        if u.path == "/api/ppm/measure":
            with TRANSITION_LOCK:                       # mod-başlatmayla yarışma
                return self._json(measure_ppm())
        if u.path == "/api/import":
            return self._json(dict(ok=True, imported=import_csv(self._body())))
        if u.path == "/api/bookmarks/delete":
            try:
                DBASE.del_bookmark(int(parse_qs(u.query).get("id", ["0"])[0]))
            except ValueError:
                pass
            return self._json(dict(ok=True))
        self.send_error(404)

    def _stream_audio(self, qs):
        try:
            freq = float(qs["freq"][0])
            demod = qs.get("demod", ["nfm"])[0]
        except (KeyError, ValueError):
            return self.send_error(400)

        with TRANSITION_LOCK:                          # H1: dinleme başlatmayı da serialize et
            proc, rate = start_listen(freq, demod)
        if proc is None:
            return self.send_error(500)

        # arşiv kaydı (kayıt dosyası açılır, sonunda başlık boyutları düzeltilir)
        rec_path = os.path.join(RECORDINGS, f"{int(time.time())}_{freq/1e6:.4f}_{demod}.wav")
        rec = None
        written = 0
        try:
            rec = open(rec_path, "wb")
            rec.write(wav_header(rate, datasize=0))
        except OSError:
            rec = None

        # canlı STT: etkin dil(ler) varsa sesi paralel Vosk worker'ına besle
        stt_q = None
        langs = sorted(STT_LANGS) if TRANSCRIBER.available() else []
        if langs:
            with LISTEN_STT_LOCK:
                LISTEN_STT["id"] += 1
                sess_id = LISTEN_STT["id"]
                LISTEN_STT["text"] = LISTEN_STT["partial"] = LISTEN_STT["lang"] = ""
            stt_q = queue.Queue(maxsize=128)
            threading.Thread(target=_listen_stt_worker,
                             args=(rate, langs, stt_q, sess_id), daemon=True).start()

        self.send_response(200)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        cap = rate * 2 * 1800          # azami ~30 dk (takılı akış/kayıt sınırı)
        try:
            self.wfile.write(wav_header(rate))
            while written < cap:
                chunk = proc.stdout.read(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
                written += len(chunk)
                if rec:
                    rec.write(chunk)
                if stt_q is not None:
                    try:
                        stt_q.put_nowait(chunk)   # STT geride kalırsa düşür, sesi bloklama
                    except queue.Full:
                        pass
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            if stt_q is not None:
                try:
                    stt_q.put_nowait(None)
                except queue.Full:
                    pass
            stop_listen(only_proc=proc)
            if rec:
                try:
                    rec.seek(4); rec.write(struct.pack("<I", 36 + written))
                    rec.seek(40); rec.write(struct.pack("<I", written))
                    rec.close()
                except OSError:
                    pass
                if written < 8000:          # çok kısa/boş kaydı sakla­ma
                    try:
                        os.remove(rec_path)
                    except OSError:
                        pass
                else:
                    _prune_recordings()


def main():
    if not os.path.isdir(STATIC):
        sys.exit("static/ klasörü yok")
    threading.Thread(target=scanner_loop, daemon=True).start()
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    srv.daemon_threads = True
    print(f"HK.SDR çalışıyor / running:  http://{'localhost' if HOST=='127.0.0.1' else HOST}:{PORT}"
          + ("  (LAN açık)" if HOST == "0.0.0.0" else "")
          + ("  (kimlik doğrulamalı)" if AUTH else ""))
    print(f"Tarama bantları: {', '.join(b.name for b in SCAN_PLAN)}")
    print("Ctrl-C ile durdur.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        ADSB.stop()
        ISM.stop()
        WF.stop()
        AIS.stop()
        APRS.stop()
        PAGER.stop()
        ACARS.stop()
        stop_listen()
        srv.shutdown()


if __name__ == "__main__":
    main()
