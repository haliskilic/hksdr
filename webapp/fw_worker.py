#!/usr/bin/env python3
"""
faster-whisper kalıcı worker'ı — distil-whisper-large-v3-tr (Türkçe) için.
İZOLE VENV içinde çalışır (~/.cache/whisper-ct2/venv); ana backend bunu bir alt-süreç
olarak başlatır ve borularla konuşur.

Protokol: modeli BİR KEZ yükler → stdout'a {"ready":true} yazar; sonra stdin'den
her satırda bir WAV yolu okur, Türkçe transkripti tek satır JSON olarak yazar:
    {"text": "..."}            (hata → {"text":"", "err":"..."})
Model her çağrıda yeniden yüklenmez (hız için kritik — model ~800MB).
"""
import os
import sys
import json


def main():
    model_dir = os.environ.get("FW_MODEL",
                               os.path.expanduser("~/.cache/whisper-ct2/distil-tr"))
    threads = int(os.environ.get("FW_THREADS", "8"))
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(model_dir, device="cpu",
                             compute_type="int8", cpu_threads=threads)
    except Exception as e:
        sys.stdout.write(json.dumps({"ready": False, "err": str(e)}) + "\n")
        sys.stdout.flush()
        return

    sys.stdout.write(json.dumps({"ready": True}) + "\n")
    sys.stdout.flush()

    for line in sys.stdin:
        path = line.strip()
        if not path:
            continue
        try:
            segments, _info = model.transcribe(
                path, language="tr", beam_size=1,
                vad_filter=True,                 # Silero VAD → sessizlik/gürültü halüsinasyonunu azalt
                condition_on_previous_text=False)
            text = "".join(s.text for s in segments).strip()
            out = {"text": text}
        except Exception as e:
            out = {"text": "", "err": str(e)}
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
