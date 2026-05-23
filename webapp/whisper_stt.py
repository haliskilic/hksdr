"""
Speech-to-Text motoru: whisper.cpp (Whisper "small", çok-dilli — TR + EN + 97 dil).
Vosk'un yerine geçer; app.py'nin beklediği Transcriber arayüzünü korur
(available / langs_available / probe). Ek olarak canlı dinleme için transcribe_pcm().

Yaklaşım: kısa ses klibi yakala (rtl_fm @16k) → geçici WAV → whisper-cli ile çöz.
Kurulum:  setup/setup_whisper.sh   (whisper-cli + ~/.cache/whisper/ggml-small.bin)
Geçersiz kılma:  WHISPER_BIN, WHISPER_MODEL
"""
import os
import json
import time
import wave
import array
import atexit
import shutil
import tempfile
import threading
import subprocess

FW_WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fw_worker.py")

# rtl_fm'i doğrudan 16 kHz mono üretmeye zorla (whisper 16k ister; resample gerekmez)
DEMOD16 = {
    "wbfm": ["-M", "wbfm", "-r", "16000"],
    "am":   ["-M", "am", "-s", "16k"],
    "nfm":  ["-M", "fm", "-s", "16k"],
}
LANGS = ("tr", "en")          # arayüzde aç/kapa edilebilen diller


def _find_bin():
    for p in (os.environ.get("WHISPER_BIN"),
              os.path.expanduser("~/whisper.cpp/build/bin/whisper-cli"),
              shutil.which("whisper-cli")):
        if p and os.path.exists(p):
            return p
    return None


def _find_model():
    for p in (os.environ.get("WHISPER_MODEL"),
              os.path.expanduser("~/.cache/whisper/ggml-small.bin")):
        if p and os.path.exists(p):
            return p
    return None


def _find_fw():
    """HİBRİT Türkçe motoru: izole venv + distil-tr (CTranslate2).
    VARSAYILAN KAPALI — distil-large-v3-tr bu sınıf CPU'da ~2.3x yavaş (encoder tam
    large-v3). Açmak için: USE_DISTIL_TR=1. Kapalıyken her şey whisper.cpp small (hızlı)."""
    if os.environ.get("USE_DISTIL_TR", "").lower() not in ("1", "true", "yes", "on", "evet"):
        return None, None
    venv = os.environ.get("FW_VENV", os.path.expanduser("~/.cache/whisper-ct2/venv"))
    model = os.environ.get("FW_MODEL", os.path.expanduser("~/.cache/whisper-ct2/distil-tr"))
    py = os.path.join(venv, "bin", "python")
    if os.path.exists(py) and os.path.exists(os.path.join(model, "model.bin")):
        return py, model
    return None, None


def _write_wav16(path, pcm_bytes):
    w = wave.open(path, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(16000)
    w.writeframes(pcm_bytes)
    w.close()


class Transcriber:
    def __init__(self, device):
        self.device = device
        self.bin = _find_bin()              # whisper.cpp (çok-dilli small) → EN + dil tespiti
        self.model = _find_model()
        self.threads = str(min(8, os.cpu_count() or 4))
        self.fw_py, self.fw_model = _find_fw()   # distil-tr (faster-whisper) → TR
        self.fw_proc = None
        self.fw_alive = False
        self.fw_lock = threading.Lock()
        atexit.register(self.close)              # çıkışta worker'ı sızdırma

    def available(self):
        return bool((self.bin and self.model) or self.fw_model)

    def langs_available(self):
        if self.bin and self.model:
            return list(LANGS)              # whisper.cpp small: TR + EN
        if self.fw_model:
            return ["tr"]                   # yalnız distil-tr varsa: TR
        return []

    # ---- HİBRİT TR motoru: kalıcı faster-whisper worker (modeli bir kez yükler) ----
    def _fw_kill_locked(self):
        if self.fw_proc:
            try:
                self.fw_proc.terminate(); self.fw_proc.wait(timeout=2)
            except Exception:
                try:
                    self.fw_proc.kill()
                except Exception:
                    pass
            self.fw_proc = None
        self.fw_alive = False

    @staticmethod
    def _readline_timeout(stream, timeout):
        """stream.readline()'ı süreli yap (worker model yüklerken takılırsa thread'i bloklamasın)."""
        box = {}

        def _rd():
            try:
                box["line"] = stream.readline()
            except Exception:
                box["line"] = ""
        th = threading.Thread(target=_rd, daemon=True)
        th.start()
        th.join(timeout)
        return box.get("line", "")

    def _fw_ready(self):
        if not self.fw_model:
            return False
        with self.fw_lock:
            if self.fw_proc and self.fw_proc.poll() is None and self.fw_alive:
                return True
            self._fw_kill_locked()                         # ölü/yok → temizle, yeniden başlat
            try:
                env = dict(os.environ)
                env["FW_MODEL"] = self.fw_model
                env["FW_THREADS"] = self.threads
                self.fw_proc = subprocess.Popen(
                    [self.fw_py, FW_WORKER], stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                    env=env, text=True, bufsize=1)
                line = self._readline_timeout(self.fw_proc.stdout, 90)  # model yükleme payı
                self.fw_alive = bool(line) and json.loads(line).get("ready") is True
            except Exception:
                self.fw_alive = False
            if not self.fw_alive:
                self._fw_kill_locked()                     # başlamadıysa süreci bırakma
            return self.fw_alive

    def close(self):
        with self.fw_lock:
            self._fw_kill_locked()

    def _fw_tr(self, wav_path):
        if not self._fw_ready():
            return ""
        with self.fw_lock:
            try:
                self.fw_proc.stdin.write(wav_path + "\n")
                self.fw_proc.stdin.flush()
                line = self.fw_proc.stdout.readline()
                if not line:
                    self.fw_alive = False
                    return ""
                return (json.loads(line).get("text") or "").strip()
            except Exception:
                self.fw_alive = False
                return ""

    # ---- whisper.cpp çağrısı (16k mono WAV → metin + tespit edilen dil) ----
    def _cli(self, wav_path, lang):
        if not (self.bin and self.model):
            return ("", "")
        out = wav_path + ".w"
        cmd = [self.bin, "-m", self.model, "-f", wav_path, "-t", self.threads,
               "-nt", "-oj", "-of", out, "-nth", "0.6"]
        cmd += ["-l", lang if lang in LANGS else "auto"]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=120)
            with open(out + ".json", encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            return ("", "")
        finally:
            try:
                os.remove(out + ".json")
            except OSError:
                pass
        text = "".join(s.get("text", "") for s in d.get("transcription", [])).strip()
        dl = (d.get("result") or {}).get("language", "") or (lang if lang in LANGS else "")
        if text in (".", "[", "]", "(", ")", "-", "—"):   # kısa/sessiz girdide tek im → ele
            text = ""
        return (text, dl)

    # ---- HİBRİT yönlendirme: TR→distil-tr, EN→whisper.cpp, ikisi→tespit et+yönlendir ----
    def _transcribe_file(self, wav_path, langs):
        langs = [l for l in langs if l in LANGS]
        if not langs:
            return ("", "")
        cli_ok = bool(self.bin and self.model)
        want_tr, want_en = "tr" in langs, "en" in langs
        # yalnız TR ve distil-tr mevcut → en doğru Türkçe
        if want_tr and not want_en and self._fw_ready():
            return (self._fw_tr(wav_path), "tr")
        # yalnız EN → whisper.cpp İngilizce
        if want_en and not want_tr and cli_ok:
            return self._cli(wav_path, "en")
        # ikisi de açık: whisper.cpp ile dili tespit (+ EN metni); TR ise distil-tr ile yenile
        if cli_ok:
            text, lang = self._cli(wav_path, "auto" if want_tr and want_en else langs[0])
            if lang == "tr" and want_tr and self._fw_ready():
                tr = self._fw_tr(wav_path)
                if tr:
                    return (tr, "tr")
            return (text, lang)
        # whisper.cpp yok, sadece distil-tr var
        if self._fw_ready():
            return (self._fw_tr(wav_path), "tr")
        return ("", "")

    # ---- tarama-gömülü: kısa klip yakala + çöz (Vosk probe ile aynı imza) ----
    def probe(self, freq_hz, demod, langs=LANGS, check_s=2.0, max_s=8.0, rms_thresh=0.03):
        if not self.available():
            return ("", "", 0.0)
        langs = [l for l in langs if l in LANGS]
        if not langs:
            return ("", "", 0.0)

        args = DEMOD16.get(demod, DEMOD16["wbfm"])
        cmd = [shutil.which("rtl_fm") or "rtl_fm", "-f", str(int(freq_hz)),
               "-g", os.environ.get("GAIN", "40"),
               "-p", os.environ.get("PPM", "0")] + args + ["-"]
        dev = self.device
        with dev.lock:
            if dev.mode != "scan":
                return ("", "", 0.0)
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                return ("", "", 0.0)
            dev.proc = proc

        buf = bytearray()
        sq = 0.0
        cnt = 0
        active = None
        t0 = time.time()
        try:
            while time.time() - t0 < max_s and dev.mode == "scan":
                data = proc.stdout.read(4000)
                if not data:
                    break
                buf += data
                a = array.array("h")
                a.frombytes(data[: len(data) // 2 * 2])
                sq += sum(v * v for v in a)
                cnt += len(a)
                if active is None and time.time() - t0 >= check_s:
                    active = (sq / max(cnt, 1)) ** 0.5 / 32768.0 >= rms_thresh
                    if not active:
                        break
        except Exception:
            pass
        with dev.lock:
            if dev.proc is proc:
                if proc.poll() is None:
                    try:
                        proc.terminate(); proc.wait(timeout=2)
                    except Exception:
                        try:
                            proc.kill()
                        except Exception:
                            pass
                dev.proc = None

        rms = (sq / max(cnt, 1)) ** 0.5 / 32768.0
        if active is None:
            active = rms >= rms_thresh
        if not active or len(buf) < 16000:        # sessiz veya <0.5 sn → boş
            return ("", "", rms)

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir="/tmp")
        tmp.close()
        try:
            _write_wav16(tmp.name, bytes(buf))
            text, dl = self._transcribe_file(tmp.name, langs)
        finally:
            try:
                os.remove(tmp.name)
            except OSError:
                pass
        return (text, dl, rms)

    # ---- canlı dinleme: ham PCM bloğunu 16k'ya indir + çöz (parça-parça) ----
    def transcribe_pcm(self, pcm_bytes, src_rate, langs=LANGS):
        if not self.available() or not pcm_bytes:
            return ("", "")
        langs = [l for l in langs if l in LANGS]
        if not langs:
            return ("", "")
        pcm = pcm_bytes[: len(pcm_bytes) // 2 * 2]
        if src_rate != 16000:
            try:
                import numpy as np
                x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
                if len(x) > 1:
                    n = max(1, int(len(x) * 16000 / src_rate))
                    x = np.interp(np.linspace(0, len(x) - 1, n),
                                  np.arange(len(x)), x)
                pcm = x.astype(np.int16).tobytes()
            except Exception:
                pass                                  # numpy yoksa ham (yaklaşık) dene
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir="/tmp")
        tmp.close()
        try:
            _write_wav16(tmp.name, pcm)
            return self._transcribe_file(tmp.name, langs)
        finally:
            try:
                os.remove(tmp.name)
            except OSError:
                pass
