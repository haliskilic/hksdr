"""
ISM (433.92 MHz) sensör decode: rtl_433'ü JSON modunda çalıştırır, çözülen
sensör mesajlarını (sıcaklık/nem/TPMS vb.) okuyup DB'ye "mesaj" olarak loglar.

rtl_433 cihazı tek başına kullanır; ISM modu açıkken tarama durur (tek USB cihaz).
"""
import os
import json
import time
import shutil
import threading
import subprocess


def _rtl433():
    return shutil.which("rtl_433") or "/usr/bin/rtl_433"


# gösterimde öne çıkaracağımız alanlar (varsa)
INTERESTING = [
    ("temperature_C", "°C"), ("temperature_F", "°F"), ("humidity", "% nem"),
    ("pressure_hPa", "hPa"), ("wind_avg_km_h", "km/s rüzgar"), ("rain_mm", "mm yağmur"),
    ("battery_ok", "batt"), ("pressure_kPa", "kPa tlastik"), ("moisture", "% nem"),
]


class IsmDecoder:
    def __init__(self, device, db, freq="433.92M"):
        self.device = device
        self.db = db
        self.freq = freq
        self.running = False
        self._reader = None
        self.seen_models = set()
        self.devices = {}            # 2B: label → {son ölçüm, sayım, görülme} (canlı cihaz tablosu)
        self.lock = threading.Lock()

    def available(self):
        return bool(shutil.which("rtl_433"))

    def start(self):
        if not self.available():
            return False
        with self.device.lock:
            self.device.mode = "ism"
            self.device._kill_locked()
            try:
                proc = subprocess.Popen(
                    [_rtl433(), "-F", "json", "-f", self.freq,
                     "-p", os.environ.get("PPM", "0")],     # M4: kalibrasyonu uygula
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=1, text=True)
            except FileNotFoundError:
                self.device.mode = "scan"
                return False
            self.device.proc = proc
            self._proc = proc
        with self.lock:
            self.devices = {}        # her başlangıçta canlı tabloyu sıfırla
        self.running = True
        self._reader = threading.Thread(target=self._read_loop, args=(proc,), daemon=True)
        self._reader.start()
        return True

    def stop(self):
        self.running = False
        with self.device.lock:
            if self.device.proc is getattr(self, "_proc", None):
                self.device._kill_locked()
            if self.device.mode == "ism":
                self.device.mode = "scan"

    def _read_loop(self, proc):
        try:
            for line in proc.stdout:
                if not self.running:
                    break
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                self._store(obj)
        except (OSError, ValueError):
            pass

    def _store(self, obj):
        model = str(obj.get("model", "?"))
        ident = obj.get("id", obj.get("channel", ""))
        label = f"{model}" + (f" #{ident}" if ident != "" else "")
        # öne çıkan ölçümleri kısa özet olarak
        parts = []
        for key, unit in INTERESTING:
            if key in obj:
                v = obj[key]
                parts.append(f"{v}{('' if unit.startswith('%') or unit.endswith('batt') else ' ')}{unit}"
                             if not isinstance(v, bool) else f"{unit}:{'ok' if v else 'düşük'}")
        summary = " · ".join(parts) if parts else json.dumps(
            {k: v for k, v in obj.items() if k not in ("time", "model", "id", "mic")},
            ensure_ascii=False)[:120]
        self.seen_models.add(model)
        now = time.time()
        with self.lock:               # 2B: aynı cihazı grupla (son ölçüm + sayım + görülme)
            d = self.devices.get(label)
            if d:
                d["summary"] = summary
                d["last"] = now
                d["count"] += 1
            else:
                self.devices[label] = {"label": label, "model": model, "summary": summary,
                                       "count": 1, "first": now, "last": now}
        if self.db:
            self.db.insert_message("ism", label, summary)

    def snapshot(self):
        """2B: gruplu canlı cihaz listesi (en son görülen üstte)."""
        now = time.time()
        with self.lock:
            devs = sorted(self.devices.values(), key=lambda d: -d["last"])
            out = [dict(label=d["label"], summary=d["summary"], count=d["count"],
                        seen=round(now - d["last"], 1)) for d in devs]
        return dict(count=len(out), devices=out)
