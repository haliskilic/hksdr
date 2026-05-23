"""
PipeDecoder — `rtl_fm | <araç>` desenindeki decoder'lar için ortak temel sınıf
(Faz D: aprs/pager/rds boilerplate'ini tekilleştirir).

Alt sınıf yalnızca FARKLI olanı tanımlar:
  MODE              : cihaz mod adı ("aprs" | "pager" | "rds" …)
  tools_ok()        : ek aracın (multimon-ng/redsea) varlığı
  rtl_fm_args()     : rtl_fm'in -f/-g/-p dışındaki argümanları
  downstream_cmd()  : rtl_fm çıktısını işleyen araç komutu (liste)
  parse(line)       : aracın her satırını işle (DB/durum güncelle)
  reset()           : start'ta durum temizliği (opsiyonel)

Ortak: cihaz kilidi + temiz handoff (_kill_locked), PPM/GAIN, sahiplik-kontrollü
stop (canlı sweep'i yetim bırakmaz), okuyucu thread.
"""
import os
import time
import shutil
import threading
import subprocess


class PipeDecoder:
    MODE = "?"

    def __init__(self, device, db=None, freq="144.800M"):
        self.device = device
        self.db = db
        self.freq = freq
        self.running = False
        self._fm = None
        self._dn = None
        self._reader = None

    # ---- alt sınıf geçersiz kılar ----
    def tools_ok(self):
        return True

    def rtl_fm_args(self):
        return ["-M", "fm", "-s", "22050"]

    def downstream_cmd(self):
        raise NotImplementedError

    def parse(self, line):
        pass

    def reset(self):
        pass

    def snapshot(self):
        return {}

    # ---- ortak ----
    def available(self):
        return bool(shutil.which("rtl_fm")) and self.tools_ok()

    def start(self, freq=None):
        if not self.available():
            return False
        if freq:
            self.freq = freq
        gain = os.environ.get("GAIN", "40")
        ppm = os.environ.get("PPM", "0")
        with self.device.lock:
            self.device.mode = self.MODE
            self.device._kill_locked()
            fm = None
            try:
                fm = subprocess.Popen(
                    [shutil.which("rtl_fm"), "-f", self.freq, *self.rtl_fm_args(),
                     "-g", gain, "-p", ppm, "-"],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                dn = subprocess.Popen(
                    self.downstream_cmd(), stdin=fm.stdout, stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL, text=True, bufsize=1)
            except OSError:                   # downstream başlamadıysa fm'i sızdırma
                if fm and fm.poll() is None:
                    try:
                        fm.kill()
                    except Exception:
                        pass
                self.device.mode = "scan"
                return False
            fm.stdout.close()                 # downstream ölünce fm SIGPIPE alsın
            self.device.proc = fm
            self._fm, self._dn = fm, dn
        self.reset()
        self.running = True
        self._reader = threading.Thread(target=self._read_loop, args=(dn,), daemon=True)
        self._reader.start()
        return True

    def stop(self):
        self.running = False
        fm, dn = self._fm, self._dn
        for p in (dn, fm):
            if p and p.poll() is None:
                try:
                    p.terminate(); p.wait(timeout=2)
                except Exception:
                    try:
                        p.kill()
                    except Exception:
                        pass
        self._fm = self._dn = None
        with self.device.lock:
            if self.device.proc in (fm, dn):     # yalnız kendi sürecimizse temizle
                self.device.proc = None
            if self.device.mode == self.MODE:    # yalnız hâlâ bizim modumuzsa scan'e dön
                self.device.mode = "scan"
        time.sleep(0.2)

    def _read_loop(self, dn):
        try:
            for line in dn.stdout:
                if not self.running:
                    break
                self.parse(line.strip())
        except (OSError, ValueError):
            pass
