# Changelog

All notable changes to HK.SDR are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-05-23

First public release.

### Features
- Continuous categorized scanning (`rtl_power` → SQLite, live newest-on-top history, category filters).
- Live audio streaming (WB-FM / AM / NFM) with WebAudio noise filter and automatic WAV recording archive.
- Decoders: ADS-B (map), AIS, APRS, ACARS, VDL2, Pager (POCSAG/FLEX, content masked), RDS, ISM 433 MHz
  (grouped live device table).
- Interactive waterfall/spectrum (click-to-listen, Shift-click classify, wheel zoom).
- Offline speech-to-text via whisper.cpp (multilingual TR/EN auto-detect); optional Turkish
  `distil-whisper-large-v3-tr` (opt-in).
- Feature-based modulation classification + likely-service identification.
- Analytics & search, CSV/JSON export, frequency grouping.
- Scan profiles & scheduling, gain/PPM calibration, CSV bookmark import, keyword alarms.
- PWA, optional LAN binding + HTTP Basic auth.
- Bilingual UI (English / Türkçe) with a flag toggle; English by default.

### Engineering
- Single-device concurrency model (`DEVICE.lock` + `TRANSITION_LOCK`) with serialized mode transitions
  and graceful USB-handoff; device-drop detection surfaced in the UI.
- Pure-stdlib backend; modular `db.py` / `detect.py` / `decoder_base.py` (`PipeDecoder`); dispatch-table routing.
- SQLite WAL + indexes + cached counters; input validation; XSS escaping; hardened service worker.

### License
- Dual-licensed: AGPL-3.0 (`LICENSE`) + commercial (`COMMERCIAL_LICENSE.md`). Copyright © 2026 Halis KILIÇ.
