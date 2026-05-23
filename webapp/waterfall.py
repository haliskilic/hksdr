"""
Waterfall / spektrum: rtl_power'ı SÜREKLI (tek geçiş değil) çalıştırır; her
tarama bir satır olur. Aralık < ~2.4 MHz tutulur -> tek hop -> ~saniyede 1 satır.
Cihazı tek başına kullanır; waterfall modu açıkken tarama durur.
"""
import os
import time
import tempfile
import threading
import subprocess
from collections import deque

MAXCOLS = 256
MAXROWS = 140


class Waterfall:
    def __init__(self, device):
        self.device = device
        self.running = False
        self.lock = threading.Lock()
        self.freqs = []
        self.rows = deque(maxlen=MAXROWS)
        self.center = 100.0e6
        self.span = 2.0e6
        self.csv = None
        self._reader = None

    def start(self, center, span):
        try:
            center = float(center)
            span = max(0.2e6, min(float(span), 2.4e6))
        except (TypeError, ValueError):
            return False
        binhz = max(int(span / MAXCOLS), 500)
        rng = f"{int(center - span / 2)}:{int(center + span / 2)}:{binhz}"
        csv = os.path.join(tempfile.gettempdir(), f"wf_{int(time.time())}.csv")
        with self.device.lock:
            self.device.mode = "wf"
            self.device._kill_locked()
            try:
                proc = subprocess.Popen(
                    ["rtl_power", "-f", rng, "-i", "1",
                     "-g", os.environ.get("GAIN", "40"),
                     "-p", os.environ.get("PPM", "0"), csv],   # M4: kalibrasyonu uygula
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                self.device.mode = "scan"
                return False
            self.device.proc = proc
            self._proc = proc
        self.center, self.span, self.csv = center, span, csv
        with self.lock:
            self.freqs = []
            self.rows.clear()
        self.running = True
        self._reader = threading.Thread(target=self._read_loop, args=(csv, proc), daemon=True)
        self._reader.start()
        return True

    def stop(self):
        self.running = False
        with self.device.lock:
            if self.device.proc is getattr(self, "_proc", None):
                self.device._kill_locked()
            if self.device.mode == "wf":
                self.device.mode = "scan"
        if self.csv and os.path.exists(self.csv):
            try:
                os.remove(self.csv)
            except OSError:
                pass

    def _read_loop(self, path, proc):
        while self.running and not os.path.exists(path):
            time.sleep(0.2)
        try:
            with open(path) as fh:
                while self.running:
                    line = fh.readline()
                    if not line:
                        if proc.poll() is not None:
                            break
                        time.sleep(0.2)
                        continue
                    self._parse(line)
        except OSError:
            pass

    def _parse(self, line):
        p = [x.strip() for x in line.split(",")]
        if len(p) < 7:
            return
        try:
            low = float(p[2])
            step = float(p[4])
        except ValueError:
            return
        dbs = []
        for v in p[6:]:
            try:
                d = float(v)
            except ValueError:
                continue
            dbs.append(-120.0 if d != d else d)   # nan -> taban
        if not dbs:
            return
        n = len(dbs)
        if n > MAXCOLS:                            # tepe-tutarak indir
            f = n / MAXCOLS
            ds = [max(dbs[int(i * f):max(int(i * f) + 1, int((i + 1) * f))]) for i in range(MAXCOLS)]
        else:
            ds = dbs
        with self.lock:
            if not self.freqs:
                m = len(ds)
                self.freqs = [round((low + (i + 0.5) * step * (n / m)) / 1e6, 4) for i in range(m)]
            self.rows.append([round(x) for x in ds])

    def snapshot(self):
        with self.lock:
            return dict(center=round(self.center / 1e6, 4), span=round(self.span / 1e6, 4),
                        freqs=self.freqs, rows=list(self.rows))
