#!/usr/bin/env python3
"""
Genel amaçlı IQ analiz aracı (içerik çözmez — yalnızca fiziksel katman/RF analizi).

rtl_sdr ile alınmış uint8 IQ (.bin) dosyasını okur ve:
  - ortalama güç spektrumunu (PSD) ASCII grafik olarak çizer
  - işgal edilen bant genişliğini tahmin eder
  - zarf (genlik) istatistikleriyle sinyalin sabit-zarflı (dijital FSK/PSK gibi)
    olup olmadığını gösterir

Kullanım:
    python3 scripts/analyze_iq.py <dosya.bin> <ornekleme_Hz> [merkez_MHz]
"""
import sys
import numpy as np


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    fs = float(sys.argv[2])
    center = float(sys.argv[3]) * 1e6 if len(sys.argv) > 3 else 0.0

    raw = np.fromfile(path, dtype=np.uint8)
    raw = raw[: (len(raw) // 2) * 2]
    iq = (raw[0::2].astype(np.float32) - 127.5) + 1j * (raw[1::2].astype(np.float32) - 127.5)
    iq /= 127.5
    if len(iq) < 4096:
        print("Yetersiz örnek.")
        sys.exit(1)

    # --- Welch tipi ortalama PSD ---
    nfft = 4096
    win = np.hanning(nfft)
    nseg = len(iq) // nfft
    acc = np.zeros(nfft)
    for k in range(nseg):
        seg = iq[k * nfft:(k + 1) * nfft] * win
        acc += np.abs(np.fft.fftshift(np.fft.fft(seg))) ** 2
    psd = 10 * np.log10(acc / nseg + 1e-12)
    psd -= psd.max()  # tepe = 0 dB
    freqs = np.fft.fftshift(np.fft.fftfreq(nfft, 1 / fs))

    # --- İşgal edilen bant genişliği (tepe -X dB üstü) ---
    noise = np.median(psd)
    thr = noise + 6
    occ = freqs[psd > thr]
    bw = (occ.max() - occ.min()) if occ.size else 0.0
    peak_off = freqs[int(np.argmax(psd))]

    # --- Zarf istatistikleri (sabit zarf mı?) ---
    env = np.abs(iq)
    env_cv = float(np.std(env) / (np.mean(env) + 1e-12))  # değişkenlik katsayısı

    # --- ASCII spektrum (PSD'yi ~60 sütuna indir) ---
    cols = 60
    block = nfft // cols
    bars = psd[: cols * block].reshape(cols, block).mean(axis=1)
    fb = freqs[: cols * block].reshape(cols, block).mean(axis=1)
    lo, hi = bars.min(), 0.0
    width = 50

    print(f"\nDosya: {path}")
    print(f"Örnekleme: {fs/1e6:.3f} MHz | süre: {len(iq)/fs:.2f} s | merkez: {center/1e6:.4f} MHz")
    print(f"Tepe ofseti: {peak_off/1e3:+.1f} kHz  -> ~{(center+peak_off)/1e6:.4f} MHz")
    print(f"İşgal edilen bant genişliği (-6 dB): ~{bw/1e3:.1f} kHz")
    print(f"Zarf değişkenliği (std/mean): {env_cv:.3f}  "
          f"-> {'SABİT zarf (dijital PSK/FSK işareti)' if env_cv < 0.35 else 'değişken zarf (AM/OOK olabilir)'}")
    print(f"\nGüç spektrumu (merkez = {center/1e6:.3f} MHz, tepe 0 dB):")
    print("-" * (width + 18))
    for f, b in zip(fb, bars):
        n = int((b - lo) / (hi - lo + 1e-9) * width)
        print(f"{f/1e3:+8.1f} kHz |{'#' * n}")
    print("-" * (width + 18))
    print("İpucu: görsel burst/TDMA yapısı için:  inspectrum " + path)


if __name__ == "__main__":
    main()
