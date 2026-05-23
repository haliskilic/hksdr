#!/usr/bin/env python3
"""
Demodüle edilmiş ses akışında gerçekten ses (konuşma/müzik) olup olmadığını
ölçümle doğrular. rtl_fm çıktısı (ham mono s16le) bekler — kulağa ihtiyaç yok.

Ölçtükleri:
  - zaman içindeki RMS zarfı (aktivite var mı, sessizlik/sabit gürültü mü)
  - ses bandı (300–3400 Hz konuşma) enerji oranı
  - spektral eğim (ses alçak frekanslara yığılır; beyaz gürültü düzdür)

Kullanım:
    python3 scripts/check_audio.py <ses.raw> <ornekleme_Hz>
"""
import sys
import numpy as np


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    path, fs = sys.argv[1], float(sys.argv[2])

    x = np.fromfile(path, dtype=np.int16).astype(np.float32) / 32768.0
    if len(x) < fs * 0.3:
        print("Yetersiz ses verisi.")
        sys.exit(1)
    dur = len(x) / fs

    # --- RMS zarfı (100 ms pencereler) ---
    w = max(1, int(fs * 0.1))
    n = len(x) // w
    wr = np.array([np.sqrt(np.mean(x[i * w:(i + 1) * w] ** 2)) for i in range(n)])
    wr_db = 20 * np.log10(wr + 1e-9)
    med = float(np.median(wr_db))
    peak = float(np.max(wr_db))
    dyn = peak - med                       # ses -> yüksek dinamik; gürültü -> düşük

    # --- Spektrum ---
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1 / fs)
    tot = X[f > 20].sum() + 1e-9
    voice = X[(f >= 300) & (f < 3400)].sum() / tot
    low = X[(f >= 20) & (f < 300)].sum() / tot
    high = X[(f >= 3400)].sum() / tot

    # --- Verdikt ---
    tonal  = (voice + low) > 0.45   # enerji ses bandında mı (gürültü yüksek frekansa yayılır)
    strong = peak > -45             # yeterince yüksek seviye (sürekli ses: kompresyonlu yayın düz olabilir)
    bursty = dyn > 6                # zaman içinde keying/konuşma dalgalanması
    audible = tonal and (strong or bursty)
    verdict = ("SES VAR — sürekli (müzik/yayın)"      if audible and not bursty else
               "SES VAR — aralıklı konuşma (keying)"  if audible and bursty     else
               "ZAYIF/KARARSIZ — belirgin ses yok"    if peak > -55             else
               "SES YOK — sessizlik / sadece gürültü")

    print(f"\nDosya: {path}  ({dur:.1f} s @ {fs/1e3:.0f} kHz)")
    print(f"RMS  medyan: {med:6.1f} dBFS | tepe: {peak:6.1f} dBFS | dinamik: {dyn:5.1f} dB")
    print(f"Enerji oranı — alçak(<300): {low:4.0%}  ses(300-3400): {voice:4.0%}  yüksek(>3400): {high:4.0%}")

    # ASCII RMS zarfı (zaman ekseni)
    cols = min(n, 70)
    step = n / cols
    print(f"\nRMS zarfı (zaman →, {dur:.1f} s):")
    for i in range(cols):
        v = wr_db[int(i * step)]
        bar = int(max(0, (v + 60)) / 60 * 50)
        print(f"{v:6.1f} |{'#' * bar}")

    print(f"\n>>> SONUÇ: {verdict}")


if __name__ == "__main__":
    main()
