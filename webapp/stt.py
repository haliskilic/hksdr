"""
Speech-to-Text (Vosk, offline, çok dilli: TR + EN) — TARAMAYA gömülü.
Tarayıcı her tur ses frekanslarını kısa dinler; AÇIK dillerde (TR/EN) aynı sesi
çözer ve güvenilirliği (ortalama kelime conf) en yüksek olanı seçer (otomatik
dil tespiti). Sonuç 'Metin (STT)' sütununda dil etiketiyle gösterilir.

Modeller: TR ~ ~/.cache/vosk/model(-tr), EN ~ ~/.cache/vosk/model-en
(VOSK_MODEL_TR / VOSK_MODEL_EN ile geçersiz kılınabilir). Ses: 16 kHz mono.
"""
import os
import json
import time
import shutil
import subprocess

DEMOD16 = {
    "wbfm": ["-M", "wbfm", "-r", "16000"],
    "am":   ["-M", "am", "-s", "16k"],
    "nfm":  ["-M", "fm", "-s", "16k"],
}

_CACHE = os.path.expanduser("~/.cache/vosk")
MODEL_CANDIDATES = {
    "tr": [os.environ.get("VOSK_MODEL_TR"), os.environ.get("VOSK_MODEL"),
           os.path.join(_CACHE, "model-tr"), os.path.join(_CACHE, "model")],
    "en": [os.environ.get("VOSK_MODEL_EN"), os.path.join(_CACHE, "model-en")],
}
LANGS = ("tr", "en")


def _model_path(lang):
    for p in MODEL_CANDIDATES.get(lang, []):
        if p and os.path.exists(p):
            return p
    return None


def _vosk_ok():
    try:
        import vosk  # noqa: F401
        return True
    except Exception:
        return False


class Transcriber:
    def __init__(self, device):
        self.device = device
        self.models = {}        # lang -> vosk.Model

    def langs_available(self):
        if not _vosk_ok():
            return []
        return [l for l in LANGS if _model_path(l)]

    def available(self):
        return bool(self.langs_available())

    def _ensure(self, lang):
        if lang in self.models:
            return self.models[lang]
        p = _model_path(lang)
        if not p:
            return None
        import vosk
        vosk.SetLogLevel(-1)
        self.models[lang] = vosk.Model(p)
        return self.models[lang]

    def probe(self, freq_hz, demod, langs=LANGS, check_s=2.0, max_s=8.0, rms_thresh=0.03):
        """Hareketlilik-kapılı, çok dilli transkript. Döner: (cümle, dil, rms)."""
        langs = [l for l in langs if _model_path(l)]
        if not langs or not _vosk_ok():
            return ("", "", 0.0)
        try:
            from vosk import KaldiRecognizer
            recs = {}
            for l in langs:
                m = self._ensure(l)
                if m is not None:
                    r = KaldiRecognizer(m, 16000)
                    r.SetWords(True)
                    recs[l] = r
        except Exception:
            return ("", "", 0.0)
        if not recs:
            return ("", "", 0.0)

        args = DEMOD16.get(demod, DEMOD16["wbfm"])
        cmd = [shutil.which("rtl_fm") or "rtl_fm", "-f", str(int(freq_hz)),
               "-g", os.environ.get("GAIN", "40")] + args + ["-"]
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

        import array
        texts = {l: [] for l in recs}
        confs = {l: [] for l in recs}

        def _collect(lang, res):
            if res.get("text"):
                texts[lang].append(res["text"])
                confs[lang].extend(w.get("conf", 0.0) for w in res.get("result", []))

        sq = 0.0
        cnt = 0
        active = None
        t0 = time.time()
        try:
            while time.time() - t0 < max_s and dev.mode == "scan":
                data = proc.stdout.read(4000)
                if not data:
                    break
                a = array.array("h")
                a.frombytes(data[: len(data) // 2 * 2])
                sq += sum(v * v for v in a)
                cnt += len(a)
                for lang, rec in recs.items():
                    if rec.AcceptWaveform(data):
                        _collect(lang, json.loads(rec.Result()))
                if active is None and time.time() - t0 >= check_s:
                    active = (sq / max(cnt, 1)) ** 0.5 / 32768.0 >= rms_thresh
                    if not active:
                        break
        except Exception:
            pass
        if active:
            for lang, rec in recs.items():
                try:
                    _collect(lang, json.loads(rec.FinalResult()))
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
        if not active:
            return ("", "", rms)

        # En güvenilir dili seç (ortalama kelime conf; eşitlikte daha çok kelime)
        best_text, best_lang, best_score = "", "", -1.0
        for lang in recs:
            t = " ".join(x.strip() for x in texts[lang] if x.strip()).strip()
            if not t:
                continue
            avg = sum(confs[lang]) / len(confs[lang]) if confs[lang] else 0.0
            score = avg + 0.01 * len(confs[lang])
            if score > best_score:
                best_text, best_lang, best_score = t, lang, score
        if best_text:
            best_text = best_text[0].upper() + best_text[1:]
            if best_text[-1] not in ".!?":
                best_text += "."
        return (best_text, best_lang, rms)
