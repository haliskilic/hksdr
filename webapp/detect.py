"""rtl_power CSV çıktısından sinyal tespiti: gürültü medyanı üstü tepeleri
kümeler, her küme için (merkez_hz, tepe_dB, genişlik_kHz) döndürür. (Faz D.)"""
import statistics


def detect_signals(csv_path, band):
    freqs, powers = [], []
    try:
        with open(csv_path) as fh:
            for line in fh:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 7:
                    continue
                try:
                    lo = float(parts[2]); step = float(parts[4])
                except ValueError:
                    continue
                for i, val in enumerate(parts[6:]):
                    try:
                        db = float(val)
                    except ValueError:
                        continue
                    if db != db or db in (float("inf"), float("-inf")):
                        continue
                    freqs.append(lo + (i + 0.5) * step)
                    powers.append(db)
    except FileNotFoundError:
        return []
    if len(freqs) < 4:
        return []

    pairs = sorted(zip(freqs, powers))
    fs = [p[0] for p in pairs]
    ps = [p[1] for p in pairs]
    noise = statistics.median(ps)
    thr = noise + band.thr
    step = statistics.median([fs[i + 1] - fs[i] for i in range(len(fs) - 1)]) or 1e5
    gap = max(step * 3, 150e3)

    sigs = []
    i, n = 0, len(fs)
    while i < n:
        if ps[i] <= thr:
            i += 1
            continue
        j = i
        while j + 1 < n and ps[j + 1] > thr and (fs[j + 1] - fs[j]) <= gap:
            j += 1
        seg = list(zip(fs[i:j + 1], ps[i:j + 1]))
        fc, pk = max(seg, key=lambda x: x[1])
        sigs.append((fc, pk, (fs[j] - fs[i]) / 1e3))
        i = j + 1
    return sigs
