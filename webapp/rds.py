"""
RDS / RBDS (FM yan-verisi) decode: rtl_fm | redsea. Bir FM istasyonuna kilitlenir;
istasyon adı (PS), radiotext (RT — şarkı/duyuru) ve program türünü (PTY) çözer.
Yayın yan-verisidir → herkese açık. PipeDecoder deseni (Faz D).
"""
import os
import json
import time
import shutil
import threading

from decoder_base import PipeDecoder


def _redsea():
    return shutil.which("redsea") or os.path.expanduser("~/.local/bin/redsea")


class RdsDecoder(PipeDecoder):
    MODE = "rds"

    def __init__(self, device, db=None, freq="100.0M"):
        super().__init__(device, db, freq)
        self.lock = threading.Lock()
        self.cur = {}                      # anlık PS/RT/PTY/PI
        self._last_ps = None
        self._last_rt = None

    def tools_ok(self):
        p = _redsea()
        return bool(p and os.path.exists(p))

    def rtl_fm_args(self):                 # redsea pipeline: geniş FM MPX @171k
        return ["-M", "fm", "-l", "0", "-A", "std", "-s", "171k", "-F", "9"]

    def downstream_cmd(self):
        return [_redsea(), "-r", "171000"]

    def reset(self):
        with self.lock:
            self.cur = {}
            self._last_ps = self._last_rt = None

    def parse(self, line):
        try:
            o = json.loads(line)
        except ValueError:
            return
        ps = (o.get("ps") or "").strip()
        rt = (o.get("radiotext") or "").strip()
        pty = (o.get("prog_type") or "").strip()
        pi = o.get("pi") or ""
        with self.lock:
            if ps:
                self.cur["ps"] = ps
            if rt:
                self.cur["rt"] = rt
            if pty:
                self.cur["pty"] = pty
            if pi:
                self.cur["pi"] = pi
            self.cur["ts"] = time.time()
            ps_now = self.cur.get("ps", "RDS")
        # DB'ye yalnız DEĞİŞİNCE logla (spam yok)
        if self.db:
            if ps and ps != self._last_ps:
                self._last_ps = ps
                self.db.insert_message("rds", f"📻 {ps}",
                                       (f"{pty} · " if pty else "") + (f"PI {pi}" if pi else "").strip())
            if rt and rt != self._last_rt:
                self._last_rt = rt
                self.db.insert_message("rds", f"📻 {ps_now}", f"RT: {rt}")

    def snapshot(self):
        with self.lock:
            return dict(self.cur)
