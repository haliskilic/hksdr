#!/usr/bin/env python3
"""
rtl_power CSV çıktısını analiz eder: gürültü tabanının üzerindeki sinyalleri
bulur, bitişik bin'leri tek sinyale kümeler ve olası band kullanımını etiketler.

Kullanım:
    python3 scripts/find_signals.py <rtl_power.csv> [eşik_dB]
    (eşik_dB = gürültü medyanının kaç dB üstü sayılsın, varsayılan 6)
"""
import sys
import numpy as np

# (alt_Hz, üst_Hz, etiket) — Türkiye/genel band kullanımları
BANDS = [
    (0.135e6, 0.285e6,  "LF / uzun dalga"),
    (0.526e6, 1.606e6,  "AM/MW radyo yayını"),
    (3.5e6,   4.0e6,    "80m amatör"),
    (5.9e6,   6.2e6,    "49m kısa dalga yayın"),
    (7.0e6,   7.3e6,    "40m amatör"),
    (26.96e6, 27.41e6,  "CB telsiz (27 MHz)"),
    (49.0e6,  50.0e6,   "kablosuz / oyuncak"),
    (87.5e6,  108.0e6,  "FM radyo yayını"),
    (108.0e6, 137.0e6,  "Havacılık (airband, AM)"),
    (137.0e6, 138.0e6,  "Hava durumu uydusu (NOAA/Meteor)"),
    (144.0e6, 146.0e6,  "2m amatör telsiz"),
    (146.0e6, 156.0e6,  "VHF iş/kamu telsizi"),
    (156.0e6, 162.05e6, "Deniz VHF / AIS"),
    (162.05e6,174.0e6,  "VHF telsiz"),
    (174.0e6, 230.0e6,  "DAB dijital radyo / Band III"),
    (315.0e6, 316.0e6,  "ISM 315 (uzaktan kumanda)"),
    (380.0e6, 400.0e6,  "TETRA (kamu/güvenlik)"),
    (400.0e6, 406.0e6,  "Uydu / çağrı"),
    (406.0e6, 430.0e6,  "UHF telsiz"),
    (430.0e6, 440.0e6,  "70cm amatör telsiz"),
    (433.05e6,434.79e6, "ISM 433 (sensör/kumanda)"),
    (446.0e6, 446.2e6,  "PMR446 el telsizi"),
    (450.0e6, 470.0e6,  "UHF iş telsizi / LTE450"),
    (470.0e6, 694.0e6,  "UHF TV (DVB-T)"),
    (694.0e6, 790.0e6,  "700 MHz mobil (LTE/5G)"),
    (791.0e6, 821.0e6,  "LTE800 (indirme)"),
    (832.0e6, 862.0e6,  "LTE800 (yükleme)"),
    (868.0e6, 870.0e6,  "ISM 868 (sensör/IoT)"),
    (880.0e6, 915.0e6,  "GSM900 (yükleme)"),
    (925.0e6, 960.0e6,  "GSM900 (indirme)"),
    (1090e6,  1091e6,   "ADS-B uçak"),
    (1227e6,  1228e6,   "GPS L2"),
    (1575e6,  1576e6,   "GPS L1"),
    (1710e6,  1785e6,   "LTE1800 (yükleme)"),
    (1805e6,  1880e6,   "LTE1800 (indirme)"),
]


def band_of(freq_hz: float) -> str:
    for lo, hi, name in BANDS:
        if lo <= freq_hz <= hi:
            return name
    return "—"


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    thr_offset = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0

    freqs, powers = [], []
    with open(path) as fh:
        for line in fh:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 7:
                continue
            try:
                low = float(parts[2])
                step = float(parts[4])
            except ValueError:
                continue
            for i, val in enumerate(parts[6:]):
                try:
                    db = float(val)
                except ValueError:
                    continue
                if not np.isfinite(db):
                    continue
                freqs.append(low + (i + 0.5) * step)
                powers.append(db)

    if not freqs:
        print("CSV'de geçerli veri bulunamadı.")
        sys.exit(1)

    freqs = np.array(freqs)
    powers = np.array(powers)
    order = np.argsort(freqs)
    freqs, powers = freqs[order], powers[order]

    noise = float(np.median(powers))
    thr = noise + thr_offset
    step = float(np.median(np.diff(freqs))) if len(freqs) > 1 else 1e5
    gap = max(step * 3, 150e3)   # bu kadar yakın bin'ler aynı sinyale ait sayılır

    mask = powers > thr
    signals = []
    i, n = 0, len(freqs)
    while i < n:
        if not mask[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and mask[j + 1] and (freqs[j + 1] - freqs[j]) <= gap:
            j += 1
        seg_f, seg_p = freqs[i:j + 1], powers[i:j + 1]
        k = int(np.argmax(seg_p))
        signals.append((seg_f[k], float(seg_p[k]), seg_f[0], seg_f[-1]))
        i = j + 1

    signals.sort(key=lambda s: s[1], reverse=True)

    print(f"\nGürültü tabanı (medyan): {noise:.1f} dB | eşik: {thr:.1f} dB (+{thr_offset:.0f} dB)")
    print(f"Taranan aralık: {freqs[0]/1e6:.3f} – {freqs[-1]/1e6:.3f} MHz | {n} bin")
    print(f"Bulunan sinyal sayısı: {len(signals)}\n")
    print(f"{'#':>3} {'Frekans (MHz)':>14} {'Güç(dB)':>8} {'Genişlik':>9}  Olası kullanım")
    print("-" * 80)
    for idx, (fc, pk, f0, f1) in enumerate(signals[:40], 1):
        bw = (f1 - f0) / 1e3
        print(f"{idx:>3} {fc/1e6:>14.4f} {pk:>8.1f} {bw:>7.0f}kHz  {band_of(fc)}")
    print()
    print("İpucu: bir sinyali yakından dinlemek için GQRX/URH ile o frekansa git,")
    print("veya:  rtl_fm -f <MHz>M -M fm -s 200k - | aplay -r 32k -f S16_LE")


if __name__ == "__main__":
    main()
