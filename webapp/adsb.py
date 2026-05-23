"""
ADS-B (1090 MHz) takibi: dump1090'ı --net modunda çalıştırır, SBS (BaseStation)
port 30003'ten çözülmüş uçak verisini okur, uçak durumunu bellekte tutar.

dump1090 cihazı tek başına kullanır; bu yüzden ADS-B modu açıkken tarama durur
(tek USB cihaz). Mod kapanınca tarama devam eder.
"""
import os
import time
import shutil
import socket
import threading
import subprocess


def _f(s):
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _dump1090_path():
    return shutil.which("dump1090") or os.path.expanduser("~/.local/bin/dump1090")


class AdsbTracker:
    def __init__(self, device, db=None, sbs_port=30003, stale=60):
        self.device = device
        self.db = db                # historik log için (opsiyonel)
        self.sbs_port = sbs_port
        self.stale = stale
        self.aircraft = {}          # icao -> dict
        self.lock = threading.Lock()
        self.running = False
        self._reader = None

    def available(self):
        path = _dump1090_path()
        return bool(path and os.path.exists(path))

    # ---- yaşam döngüsü ----
    def start(self):
        if not self.available():
            return False
        with self.device.lock:
            self.device.mode = "adsb"
            self.device._kill_locked()
            try:
                proc = subprocess.Popen(
                    [_dump1090_path(), "--net", "--net-sbs-port", str(self.sbs_port),
                     "--ppm", os.environ.get("PPM", "0")],   # M4: kalibrasyonu uygula
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                self.device.mode = "scan"
                return False
            self.device.proc = proc
            self._proc = proc
        with self.lock:
            self.aircraft.clear()
        self.running = True
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()
        return True

    def stop(self):
        self.running = False
        with self.device.lock:
            if self.device.proc is getattr(self, "_proc", None):   # yalnız kendi sürecimizse
                self.device._kill_locked()
            if self.device.mode == "adsb":                         # yalnız hâlâ bizim modumuzsa
                self.device.mode = "scan"
        with self.lock:
            self.aircraft.clear()

    # ---- SBS okuma ----
    def _read_loop(self):
        # dump1090'ın net sunucusu açılana kadar birkaç deneme
        while self.running:
            try:
                sock = socket.create_connection(("127.0.0.1", self.sbs_port), timeout=4)
            except OSError:
                time.sleep(1)
                continue
            try:
                f = sock.makefile("r")
                for line in f:
                    if not self.running:
                        break
                    self._parse(line)
            except OSError:
                pass
            finally:
                try:
                    sock.close()
                except OSError:
                    pass
            time.sleep(0.5)

    def _parse(self, line):
        p = line.strip().split(",")
        if len(p) < 17 or p[0] != "MSG":
            return
        icao = p[4].strip()
        if not icao:
            return
        now = time.time()
        log_label = None
        with self.lock:
            a = self.aircraft.setdefault(icao, dict(icao=icao, first=now, trail=[]))
            a["last"] = now
            cs = p[10].strip()
            if cs:
                a["callsign"] = cs
            for key, idx in (("alt", 11), ("speed", 12), ("track", 13), ("vrate", 16)):
                v = _f(p[idx])
                if v is not None:
                    a[key] = v
            lat, lon = _f(p[14]), _f(p[15])
            if lat is not None and lon is not None:
                a["lat"], a["lon"] = lat, lon
                tr = a["trail"]
                if not tr or abs(tr[-1][0] - lat) + abs(tr[-1][1] - lon) > 0.0004:
                    tr.append([round(lat, 5), round(lon, 5)])
                    if len(tr) > 60:
                        del tr[0]
            sq = p[17].strip() if len(p) > 17 else ""
            if sq:
                a["squawk"] = sq
            # historik log: çağrı kodu ilk öğrenildiğinde bir kez kaydet
            if not a.get("logged") and a.get("callsign"):
                a["logged"] = True
                log_label = a["callsign"]
        if log_label and self.db:
            alt = a.get("alt")
            self.db.insert_message("adsb", log_label,
                                   f"{icao}" + (f" · {int(alt)} ft" if alt else ""))

    def snapshot(self):
        now = time.time()
        with self.lock:
            # bayatları at
            for icao in [k for k, v in self.aircraft.items() if now - v["last"] > self.stale]:
                del self.aircraft[icao]
            out = []
            for a in self.aircraft.values():
                out.append(dict(
                    icao=a["icao"],
                    callsign=a.get("callsign", "").strip(),
                    alt=a.get("alt"), speed=a.get("speed"), track=a.get("track"),
                    lat=a.get("lat"), lon=a.get("lon"), squawk=a.get("squawk", ""),
                    seen=round(now - a["last"], 1),
                    trail=a.get("trail", []),
                    pos=("lat" in a and "lon" in a)))
        out.sort(key=lambda x: (x["pos"] is False, x["seen"]))
        return dict(count=len(out),
                    with_pos=sum(1 for x in out if x["pos"]),
                    aircraft=out)
