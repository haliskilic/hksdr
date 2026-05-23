"""
Özellik-tabanlı modülasyon sınıflama + sinyal-kimlik (Faz 3.1/3.2).
Verilen frekansta kısa IQ yakalar (rtl_sdr), şu özellikleri çıkarır: işgal edilen
bant genişliği, zarf değişkenliği (sabit zarf = dijital PSK/FSK göstergesi),
spektral düzlük (gürültü ~1), SNR. Kural-tabanlı modülasyon tahmini yapar
(eğitim verisi gerektirmez). Cihaz scan modundayken çağrılır.
"""
import os
import time
import shutil
import tempfile
import subprocess
import numpy as np

# (alt_MHz, üst_MHz, olası servis)
SERVICES = [
    (87.5, 108, "FM yayın"), (118, 137, "Havacılık (AM)"), (137, 138, "Hava uydusu"),
    (144, 146, "2m amatör"), (156, 162.05, "Deniz VHF / AIS"), (174, 230, "DAB / Band III"),
    (380, 400, "TETRA"), (430, 440, "70cm amatör"), (446, 446.2, "PMR446"),
    (450, 470, "UHF telsiz"), (470, 694, "DVB-T TV"), (791, 862, "LTE800"),
    (880, 960, "GSM900"), (1090, 1091, "ADS-B"),
]


def _service(fmhz):
    for lo, hi, name in SERVICES:
        if lo <= fmhz <= hi:
            return name
    return "—"


def classify(device, freq_hz, sample_rate=1_000_000, seconds=2, gain="40"):
    if not shutil.which("rtl_sdr"):
        return {"error": "rtl_sdr yok"}
    tmp = os.path.join(tempfile.gettempdir(), f"cls_{int(time.time())}.bin")
    nsamp = int(sample_rate * seconds)
    with device.lock:
        if device.mode != "scan":
            return {"error": "cihaz meşgul (yalnızca tarama modunda sınıflandırılır)"}
        device._kill_locked()          # tarayıcının rtl_power'ını temiz durdur (cihazı boşalt)
        try:
            proc = subprocess.Popen(
                ["rtl_sdr", "-f", str(int(freq_hz)), "-s", str(int(sample_rate)),
                 "-g", gain, "-p", os.environ.get("PPM", "0"), "-n", str(nsamp), tmp],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            return {"error": "rtl_sdr yok"}
        device.proc = proc
    # KİLİT DIŞINDA bekle (timeout'lu) — rtl_sdr takılırsa cihaz alt sistemi kilitlenmesin
    try:
        rc = proc.wait(timeout=seconds + 10)
    except subprocess.TimeoutExpired:
        rc = -1
    with device.lock:
        if device.proc is proc:
            device.proc = None
    if proc.poll() is None:                     # takıldıysa/sahip değiştiyse öldür
        try:
            proc.terminate(); proc.wait(timeout=2)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    if rc != 0 or not os.path.exists(tmp):
        return {"error": "yakalama başarısız"}
    try:
        raw = np.fromfile(tmp, dtype=np.uint8)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    raw = raw[: (len(raw) // 2) * 2]
    if len(raw) < 8192:
        return {"error": "yetersiz örnek"}
    iq = (raw[0::2].astype(np.float32) - 127.5) + 1j * (raw[1::2].astype(np.float32) - 127.5)
    iq /= 127.5

    # --- PSD ---
    nfft = 4096
    win = np.hanning(nfft)
    nseg = len(iq) // nfft
    acc = np.zeros(nfft)
    for k in range(nseg):
        seg = iq[k * nfft:(k + 1) * nfft] * win
        acc += np.abs(np.fft.fftshift(np.fft.fft(seg))) ** 2
    psd = acc / max(nseg, 1)
    psd_db = 10 * np.log10(psd + 1e-12)
    psd_db -= psd_db.max()                      # tepe = 0 dB
    freqs = np.fft.fftshift(np.fft.fftfreq(nfft, 1 / sample_rate))
    noise = float(np.median(psd_db))
    snr = -noise                                # tepe 0 dB'e göre gürültü tabanı derinliği
    occ = freqs[psd_db > (noise + 6)]
    bw_khz = (occ.max() - occ.min()) / 1e3 if occ.size else 0.0

    # --- zarf + düzlük ---
    env = np.abs(iq)
    env_cv = float(np.std(env) / (np.mean(env) + 1e-12))
    flat = float(np.exp(np.mean(np.log(psd + 1e-12))) / (np.mean(psd) + 1e-12))
    off_frac = float(np.mean(env < 0.3 * np.max(env))) if env.size else 0.0

    # --- kural-tabanlı sınıflama (sıra önemli) ---
    if snr < 8:
        mod = "gürültü / belirgin sinyal yok"
    elif env_cv < 0.32:
        mod = "dijital, sabit zarf (PSK/FSK — TETRA/DMR vb.)"
    elif off_frac > 0.3 and env_cv > 0.7:
        mod = "OOK/ASK (açık-kapalı; kumanda/sensör)"
    elif bw_khz > 100:
        mod = "FM (geniş bant — yayın)"
    elif 4 < bw_khz < 35:
        mod = "dar bant sesli (AM / NFM)"
    elif flat > 0.5:
        mod = "gürültü / belirsiz"
    else:
        mod = "belirsiz (dijital/karışık)"

    return dict(freq_mhz=round(freq_hz / 1e6, 4), bandwidth_khz=round(bw_khz, 1),
                snr_db=round(snr, 1), env_cv=round(env_cv, 3), flatness=round(flat, 3),
                modulation=mod, likely=_service(freq_hz / 1e6))
