"""
ACARS (uçak veri mesajları, ~131 MHz) — acarsdec çalıştırır, JSON çıktısını
UDP'den okur (acarsdec -j 127.0.0.1:port). Mesajları DB'ye loglar.
ACARS operasyonel uçak verisidir (ADS-B'yi tamamlar). Cihazı tek başına kullanır.
"""
import os
import json
import time
import shutil
import socket
import threading
import subprocess

# Yaygın VHF ACARS frekansları (MHz) — hepsi tek RTL bandında (~131.5–131.85)
ACARS_FREQS = ["131.525", "131.550", "131.725", "131.825", "131.850"]


def _acarsdec():
    return shutil.which("acarsdec") or os.path.expanduser("~/.local/bin/acarsdec")


class AcarsDecoder:
    def __init__(self, device, db=None, port=5557):
        self.device = device
        self.db = db
        self.port = port
        self.running = False
        self._reader = None
        self._sock = None

    def available(self):
        p = _acarsdec()
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
        env = dict(os.environ)
        env["LD_LIBRARY_PATH"] = os.path.expanduser("~/.local/lib") + ":" + env.get("LD_LIBRARY_PATH", "")
        cmd = [_acarsdec(), "-j", f"127.0.0.1:{self.port}",
               "-g", os.environ.get("GAIN", "40"), "-p", os.environ.get("PPM", "0"),
               "-r", "0"] + ACARS_FREQS
        with self.device.lock:
            self.device.mode = "acars"
            self.device._kill_locked()
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL, env=env)
            except FileNotFoundError:
                self.device.mode = "scan"
                s.close()
                return False
            self.device.proc = proc
            self._proc = proc
        self._sock = s
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
            if self.device.mode == "acars":
                self.device.mode = "scan"

    def _read_loop(self):
        while self.running and self._sock:
            try:
                data, _ = self._sock.recvfrom(8192)
            except socket.timeout:
                continue
            except OSError:
                break
            for line in data.decode("utf-8", "ignore").splitlines():
                line = line.strip()
                if line.startswith("{"):
                    self._handle(line)

    def _handle(self, line):
        try:
            o = json.loads(line)
        except ValueError:
            return
        reg = (o.get("tail") or "").strip()
        flight = (o.get("flight") or "").strip()
        label = (o.get("label") or "").strip()
        text = (o.get("text") or "").replace("\r", " ").replace("\n", " ").strip()
        who = flight or reg or "?"
        detail = (f"{reg} · " if reg and flight else "") + (f"[{label}] " if label else "") + (text[:130] if text else "(veri)")
        if self.db:
            self.db.insert_message("acars", who, detail)

    def snapshot(self):
        return {}
