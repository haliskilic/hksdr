"""
Pager (POCSAG / FLEX) decode: rtl_fm | multimon-ng. PipeDecoder deseni (Faz D).

GİZLİLİK: Çağrı (pager) mesajları kişisel/özel veri içerebilir. Bu yüzden mesaj
İÇERİĞİ saklanmaz/gösterilmez; yalnızca tür + capcode + uzunluk loglanır.
"""
import re
import shutil

from decoder_base import PipeDecoder

# "POCSAG1200: Address: 1234567  Function: 0  Alpha:   ..."  /  "FLEX|...|...|...|"
_POCSAG = re.compile(r"(POCSAG\d+):\s*Address:\s*(\d+).*?(Alpha|Numeric|Skyper):\s*(.*)$")
_FLEX = re.compile(r"FLEX[:|].*?(\d{7,10})")


class PagerDecoder(PipeDecoder):
    MODE = "pager"

    def __init__(self, device, db=None, freq="466.025M"):
        super().__init__(device, db, freq)

    def tools_ok(self):
        return bool(shutil.which("multimon-ng"))

    def downstream_cmd(self):
        return [shutil.which("multimon-ng"), "-a", "POCSAG512", "-a", "POCSAG1200",
                "-a", "POCSAG2400", "-a", "FLEX", "-e", "-u", "-t", "raw", "-"]

    def parse(self, line):
        m = _POCSAG.search(line)
        if m:
            proto, capcode, kind, content = m.group(1), m.group(2), m.group(3), m.group(4)
            n = len(content.strip())
            # GİZLİLİK: içerik saklanmaz, yalnızca tür/uzunluk
            detail = f"{kind} · {n} karakter (içerik gizli)"
            if self.db:
                self.db.insert_message("pager", f"{proto} #{capcode}", detail)
            return
        f = _FLEX.search(line)
        if f and self.db:
            self.db.insert_message("pager", f"FLEX #{f.group(1)}", "mesaj (içerik gizli)")
