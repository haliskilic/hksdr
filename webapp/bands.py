"""
Tarama planı: hangi bantlar taransın, kategorisi, demodülasyon tipi ve
ses olarak dinlenebilir mi.

demod:  "wbfm" (geniş FM yayın) | "am" (havacılık) | "nfm" (dar FM telsiz) | None (dijital)
audio:  True  -> arayüzde ▶ ile dinlenebilir (analog ses)
        False -> dijital/şifreli; yalnızca loglanır (TETRA, GSM, LTE...)
"""
from dataclasses import dataclass


@dataclass
class Band:
    name: str
    category: str
    lo: float            # Hz
    hi: float            # Hz
    bin: str             # rtl_power bin boyu (örn "12k")
    demod: str | None
    audio: bool
    thr: float = 6.0     # gürültü medyanı üstü eşik (dB)


# İlgi alanına göre düzenleyebilirsin. Dar aralıklar döngüyü hızlı tutar.
SCAN_PLAN = [
    Band("FM radyo",       "FM",    88.0e6, 108.0e6, "50k",  "wbfm", True,  8),
    Band("Havacılık (AM)", "AIR",   118.0e6, 137.0e6, "12k", "am",   True,  5),
    Band("2m amatör",      "HAM",   144.0e6, 146.0e6, "12k", "nfm",  True,  6),
    Band("Deniz VHF",      "VHF",   156.0e6, 162.0e6, "12k", "nfm",  True,  6),
    Band("PMR/UHF telsiz", "UHF",   446.0e6, 450.0e6, "12k", "nfm",  True,  6),
    Band("TETRA",          "TETRA", 380.0e6, 400.0e6, "25k", None,   False, 8),
    Band("LTE800",         "CELL",  791.0e6, 821.0e6, "200k", None,  False, 8),
    Band("GSM900",         "CELL",  935.0e6, 960.0e6, "200k", None,  False, 8),
]

# Tarama profilleri: ad -> izinli kategoriler (None = tüm bantlar)
PROFILES = {
    "Tümü": None,
    "Havacılık & telsiz": ["AIR", "VHF", "UHF", "HAM"],
    "Yayın (FM)": ["FM"],
    "Dijital (TETRA/Hücresel)": ["TETRA", "CELL"],
    "Ses (analog)": ["FM", "AIR", "VHF", "UHF", "HAM"],
}

# Kategori renkleri (arayüz rozetleri)
CATEGORY_COLORS = {
    "FM":    "#4ade80",
    "AIR":   "#38bdf8",
    "HAM":   "#2dd4bf",
    "VHF":   "#22d3ee",
    "UHF":   "#a78bfa",
    "TETRA": "#f87171",
    "CELL":  "#fb923c",
}

# demod -> (rtl_fm ek argümanları, çıkış örnekleme Hz)
DEMOD = {
    "wbfm": (["-M", "wbfm"],            32000),
    "am":   (["-M", "am",  "-s", "24k"], 24000),
    "nfm":  (["-M", "fm",  "-s", "24k"], 24000),
}
