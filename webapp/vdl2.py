"""
VDL Mode 2 (VHF Digital Link, ~136 MHz) — dumpvdl2 ile uçak veri linki mesajları.
ACARS'ın halefi; ADS-B/ACARS'ı tamamlar. Cihazı doğrudan kullanır (rtl_fm pipe değil),
JSON çıktısını stdout'tan okur. Mesajları DB'ye loglar.
"""
import os
import json
import shutil
import threading
import subprocess

# Yaygın VDL2 frekansları (MHz→Hz). Hepsi tek RTL bandında (~136.7–136.98).
VDL2_FREQS = ["136725000", "136975000", "136775000", "136875000"]


def _dumpvdl2():
    return shutil.which("dumpvdl2") or os.path.expanduser("~/.local/bin/dumpvdl2")


class Vdl2Decoder:
    def __init__(self, device, db=None):
        self.device = device
        self.db = db
        self.running = False
        self._proc = None
        self._reader = None

    def available(self):
        p = _dumpvdl2()
        return bool(p and os.path.exists(p))

    def start(self):
        if not self.available():
            return False
        env = dict(os.environ)
        env["LD_LIBRARY_PATH"] = os.path.expanduser("~/.local/lib") + ":" + env.get("LD_LIBRARY_PATH", "")
        cmd = [_dumpvdl2(), "--rtlsdr", "0",
               "--gain", os.environ.get("GAIN", "40"),
               "--correction", os.environ.get("PPM", "0"),
               "--output", "decoded:json:file:path=-"] + VDL2_FREQS
        with self.device.lock:
            self.device.mode = "vdl2"
            self.device._kill_locked()
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, env=env, text=True, bufsize=1)
            except FileNotFoundError:
                self.device.mode = "scan"
                return False
            self.device.proc = proc
            self._proc = proc
        self.running = True
        self._reader = threading.Thread(target=self._read_loop, args=(proc,), daemon=True)
        self._reader.start()
        return True

    def stop(self):
        self.running = False
        p = self._proc
        with self.device.lock:
            if self.device.proc is p:
                self.device._kill_locked()
            if self.device.mode == "vdl2":
                self.device.mode = "scan"
        self._proc = None

    def _read_loop(self, proc):
        try:
            for line in proc.stdout:
                if not self.running:
                    break
                line = line.strip()
                if line.startswith("{"):
                    self._handle(line)
        except (OSError, ValueError):
            pass

    def _handle(self, line):
        try:
            o = json.loads(line)
        except ValueError:
            return
        v = o.get("vdl2") or {}
        avlc = v.get("avlc") or {}
        src = (avlc.get("src") or {}).get("addr", "")          # uçak adresi (ICAO benzeri)
        acars = avlc.get("acars") or {}
        reg = (acars.get("reg") or "").strip()
        flight = (acars.get("flight") or "").strip()
        label = (acars.get("label") or "").strip()
        text = (acars.get("msg_text") or "").replace("\r", " ").replace("\n", " ").strip()
        who = flight or reg or src or "VDL2"
        if acars:
            detail = (f"{reg} · " if reg and flight else "") + (f"[{label}] " if label else "") + \
                     (text[:130] if text else "(ACARS/VDL2)")
        else:                                                  # ACARS olmayan VDL2 çerçevesi
            detail = f"VDL2 çerçeve (src {src})" if src else "VDL2 çerçeve"
        if self.db:
            self.db.insert_message("vdl2", who, detail)

    def snapshot(self):
        return {}
