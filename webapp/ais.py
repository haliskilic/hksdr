"""
AIS (gemi takibi, 161.975 / 162.025 MHz): rtl_ais çalıştırır; AIVDM (NMEA)
mesajlarını UDP 10110'dan alır ve çözer.
Desteklenen tipler: 1/2/3 (konum), 5 (gemi adı). Cihazı tek başına kullanır.
"""
import os
import time
import shutil
import socket
import threading
import subprocess

AIS_CHARS = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_ !\"#$%&'()*+,-./0123456789:;<=>?"


def _rtl_ais():
    return shutil.which("rtl_ais") or os.path.expanduser("~/.local/bin/rtl_ais")


def _sixbit(payload):
    out = []
    for c in payload:
        v = ord(c) - 48
        if v > 40:
            v -= 8
        if v < 0 or v > 63:
            return None
        out.append(format(v, "06b"))
    return "".join(out)


def _u(b, a, e):
    return int(b[a:e], 2) if 0 <= a < e <= len(b) else 0


def _i(b, a, e):
    if not (0 <= a < e <= len(b)):
        return 0
    v = int(b[a:e], 2)
    n = e - a
    return v - (1 << n) if v & (1 << (n - 1)) else v


def _text(b, a, e):
    s = ""
    for i in range(a, min(e, len(b)), 6):
        if i + 6 > len(b):
            break
        s += AIS_CHARS[int(b[i:i + 6], 2)]
    return s.replace("@", " ").strip()


class AisTracker:
    def __init__(self, device, db=None, port=10110, stale=900):
        self.device = device
        self.db = db
        self.port = port
        self.stale = stale
        self.ships = {}
        self.lock = threading.Lock()
        self.running = False
        self._reader = None
        self._sock = None
        self._frag = {}
        self._frag_ts = {}

    def available(self):
        p = _rtl_ais()
        return bool(p and os.path.exists(p))

    def start(self):
        if not self.available():
            return False
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("127.0.0.1", self.port))
            s.settimeout(1.0)
        except OSError:
            return False
        with self.device.lock:
            self.device.mode = "ais"
            self.device._kill_locked()
            try:
                proc = subprocess.Popen([_rtl_ais(), "-P", str(self.port),
                                         "-p", os.environ.get("PPM", "0")],   # M4: kalibrasyon
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                self.device.mode = "scan"
                s.close()
                return False
            self.device.proc = proc
            self._proc = proc
        self._sock = s
        with self.lock:
            self.ships.clear()
            self._frag = {}
            self._frag_ts = {}
        self.running = True
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()
        return True

    def stop(self):
        self.running = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        with self.device.lock:
            if self.device.proc is getattr(self, "_proc", None):
                self.device._kill_locked()
            if self.device.mode == "ais":
                self.device.mode = "scan"

    def _read_loop(self):
        while self.running and self._sock:
            try:
                data, _ = self._sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            for line in data.decode("ascii", "ignore").splitlines():
                if line.startswith("!AIVD"):
                    self._handle(line)

    def _handle(self, line):
        try:
            f = line.split(",")
            cnt, num, seq, payload = int(f[1]), int(f[2]), f[3], f[5]
        except (IndexError, ValueError):
            return
        if cnt == 1:
            bits = _sixbit(payload)
        else:
            now = time.time()
            for k in [k for k, ts in self._frag_ts.items() if now - ts > 60]:
                self._frag.pop(k, None)          # kayıp fragment biriktirmesin (sızıntı/çakışma)
                self._frag_ts.pop(k, None)
            key = seq or "_"
            buf = self._frag.setdefault(key, {})
            buf[num] = payload
            self._frag_ts[key] = now
            if len(buf) < cnt:
                return
            bits = _sixbit("".join(buf[i] for i in sorted(buf)))
            self._frag.pop(key, None)
            self._frag_ts.pop(key, None)
        if not bits or len(bits) < 38:
            return
        self._decode(bits)

    def _decode(self, b):
        t = _u(b, 0, 6)
        mmsi = _u(b, 8, 38)
        if mmsi == 0:
            return
        now = time.time()
        if t in (1, 2, 3):
            lon = _i(b, 61, 89) / 600000.0
            lat = _i(b, 89, 116) / 600000.0
            if abs(lat) > 90 or abs(lon) > 180:
                return
            with self.lock:
                sh = self.ships.setdefault(mmsi, dict(mmsi=mmsi, trail=[]))
                sh["last"] = now
                sh["lat"], sh["lon"] = lat, lon
                sh["sog"] = round(_u(b, 50, 60) / 10.0, 1)
                sh["cog"] = round(_u(b, 116, 128) / 10.0, 1)
                tr = sh["trail"]
                if not tr or abs(tr[-1][0] - lat) + abs(tr[-1][1] - lon) > 0.0005:
                    tr.append([round(lat, 5), round(lon, 5)])
                    if len(tr) > 40:
                        del tr[0]
        elif t == 5 and len(b) >= 232:
            name = _text(b, 112, 232)
            with self.lock:
                sh = self.ships.setdefault(mmsi, dict(mmsi=mmsi, trail=[]))
                sh["last"] = now
                if name:
                    sh["name"] = name
            if self.db and name:
                self.db.insert_message("ais", name, f"MMSI {mmsi}")

    def snapshot(self):
        now = time.time()
        with self.lock:
            for m in [k for k, v in self.ships.items() if now - v.get("last", 0) > self.stale]:
                del self.ships[m]
            out = []
            for s in self.ships.values():
                out.append(dict(mmsi=s["mmsi"], name=s.get("name", "").strip(),
                                lat=s.get("lat"), lon=s.get("lon"),
                                sog=s.get("sog"), cog=s.get("cog"),
                                seen=round(now - s.get("last", now), 1),
                                trail=s.get("trail", []),
                                pos=("lat" in s and "lon" in s)))
        out.sort(key=lambda x: (x["pos"] is False, x["seen"]))
        return dict(count=len(out), with_pos=sum(1 for x in out if x["pos"]), ships=out)
