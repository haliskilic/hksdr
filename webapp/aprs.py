"""
APRS (144.800 MHz): rtl_fm | multimon-ng (AFSK1200) ile AX.25/APRS çözer,
paketlerden konum (sıkıştırılmamış format) çıkarır. PipeDecoder deseni (Faz D).
"""
import re
import time
import shutil
import threading

from decoder_base import PipeDecoder

# sıkıştırılmamış APRS konumu: DDMM.mmN/DDDMM.mmE  (!,=,@,/ tiplerinde)
POS = re.compile(r"(\d{2})([0-5]\d\.\d+)([NS])[/\\](\d{3})([0-5]\d\.\d+)([EW])")


class AprsTracker(PipeDecoder):
    MODE = "aprs"

    def __init__(self, device, db=None, freq="144.800M", stale=1800):
        super().__init__(device, db, freq)
        self.stale = stale
        self.stations = {}
        self.lock = threading.Lock()

    def tools_ok(self):
        return bool(shutil.which("multimon-ng"))

    def downstream_cmd(self):
        return [shutil.which("multimon-ng"), "-a", "AFSK1200", "-A", "-t", "raw", "-"]

    def reset(self):
        with self.lock:
            self.stations.clear()

    def parse(self, line):
        if "APRS:" not in line:
            return
        try:
            body = line.split("APRS:", 1)[1].strip()
        except IndexError:
            return
        src = body.split(">", 1)[0].strip()[:9]
        if not src:
            return
        now = time.time()
        m = POS.search(body)
        with self.lock:
            st = self.stations.setdefault(src, dict(call=src, trail=[]))
            st["last"] = now
            if m:
                lat = (int(m.group(1)) + float(m.group(2)) / 60.0) * (1 if m.group(3) == "N" else -1)
                lon = (int(m.group(4)) + float(m.group(5)) / 60.0) * (1 if m.group(6) == "E" else -1)
                st["lat"], st["lon"] = round(lat, 5), round(lon, 5)
                tr = st["trail"]
                if not tr or abs(tr[-1][0] - lat) + abs(tr[-1][1] - lon) > 0.0005:
                    tr.append([round(lat, 5), round(lon, 5)])
                    if len(tr) > 40:
                        del tr[0]
        if self.db:
            self.db.insert_message("aprs", src, body[:160])

    def snapshot(self):
        now = time.time()
        with self.lock:
            for k in [k for k, v in self.stations.items() if now - v.get("last", 0) > self.stale]:
                del self.stations[k]
            out = [dict(call=s["call"], lat=s.get("lat"), lon=s.get("lon"),
                        seen=round(now - s.get("last", now), 1), trail=s.get("trail", []),
                        pos=("lat" in s and "lon" in s)) for s in self.stations.values()]
        out.sort(key=lambda x: (x["pos"] is False, x["seen"]))
        return dict(count=len(out), with_pos=sum(1 for x in out if x["pos"]), stations=out)
