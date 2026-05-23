"""SQLite veri katmanı — detections / messages / bookmarks tabloları,
yuvarlanan pencere pruning + bellek-cached sayaç + WAL/indeksler.
(app.py'den ayrıldı — Faz D.)"""
import time
import sqlite3
import threading


class DB:
    KEEP = 8000          # detections tablosunda tutulan azami satır (yuvarlanan pencere)

    def __init__(self, path):
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")     # M6: eşzamanlı okuma/yazma
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS detections(
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, freq_hz REAL,
            power_db REAL, bw_khz REAL, category TEXT, band_name TEXT,
            audio INTEGER, demod TEXT)""")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, source TEXT,
            label TEXT, detail TEXT)""")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS bookmarks(
            id INTEGER PRIMARY KEY AUTOINCREMENT, freq_mhz REAL, label TEXT,
            demod TEXT, category TEXT)""")
        # H4: indeksler (analytics/messages filtreleri full-scan yapmasın)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_det_ts ON detections(ts)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_det_cat ON detections(category)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_msg ON messages(source, id)")
        self.conn.commit()
        # M6: status her pollda COUNT(*) full-scan yapmasın → bellek sayacı
        self._det_count = self.conn.execute("SELECT COUNT(*) FROM detections").fetchone()[0]

    def add_bookmarks(self, items):
        with self.lock:
            self.conn.executemany(
                "INSERT INTO bookmarks(freq_mhz,label,demod,category) VALUES(?,?,?,?)",
                [(b["freq_mhz"], b["label"], b.get("demod", "wbfm"), b.get("category", "")) for b in items])
            self.conn.commit()

    def bookmarks(self):
        with self.lock:
            rows = self.conn.execute(
                "SELECT id,freq_mhz,label,demod,category FROM bookmarks ORDER BY freq_mhz").fetchall()
        return [dict(id=r[0], freq_mhz=r[1], label=r[2], demod=r[3], category=r[4]) for r in rows]

    def del_bookmark(self, bid):
        with self.lock:
            self.conn.execute("DELETE FROM bookmarks WHERE id=?", (bid,))
            self.conn.commit()

    def insert_message(self, source, label, detail):
        with self.lock:
            self.conn.execute(
                "INSERT INTO messages(ts,source,label,detail) VALUES(?,?,?,?)",
                (time.time(), source, label, detail))
            self.conn.execute(
                "DELETE FROM messages WHERE id < "
                "(SELECT COALESCE(MAX(id),0)-5000 FROM messages)")
            self.conn.commit()

    def recent_messages(self, source=None, limit=200):
        with self.lock:
            q = "SELECT ts,source,label,detail FROM messages"
            args = []
            if source:
                q += " WHERE source=?"
                args.append(source)
            q += " ORDER BY id DESC LIMIT ?"
            args.append(limit)
            rows = self.conn.execute(q, args).fetchall()
        return [dict(ts=r[0], source=r[1], label=r[2], detail=r[3]) for r in rows]

    def insert(self, band, sigs):
        with self.lock:
            ts = time.time()
            self.conn.executemany(
                "INSERT INTO detections(ts,freq_hz,power_db,bw_khz,category,"
                "band_name,audio,demod) VALUES(?,?,?,?,?,?,?,?)",
                [(ts, fc, pk, bw, band.category, band.name,
                  1 if band.audio else 0, band.demod or "") for (fc, pk, bw) in sigs])
            self.conn.execute(
                "DELETE FROM detections WHERE id < "
                "(SELECT COALESCE(MAX(id),0)-? FROM detections)", (self.KEEP,))
            self.conn.commit()
            self._det_count = min(self._det_count + len(sigs), self.KEEP)   # cached count

    def recent(self, limit=300, categories=None):
        with self.lock:
            q = ("SELECT ts,freq_hz,power_db,bw_khz,category,band_name,audio,demod "
                 "FROM detections")
            args = []
            if categories:
                q += " WHERE category IN (%s)" % ",".join("?" * len(categories))
                args += categories
            q += " ORDER BY id DESC LIMIT ?"
            args.append(limit)
            rows = self.conn.execute(q, args).fetchall()
        return [dict(ts=r[0], freq_mhz=round(r[1] / 1e6, 4), power=round(r[2], 1),
                     bw_khz=round(r[3]), category=r[4], band=r[5],
                     audio=bool(r[6]), demod=r[7]) for r in rows]

    def recent_grouped(self, limit=400, categories=None):
        """1B: aynı frekansı (1 kHz'e yuvarlı) tek satırda topla — sayım + son görülme +
        maks/ort güç. Sıra: en son görülen üstte."""
        with self.lock:
            q = ("SELECT ROUND(freq_hz/1e6,3) f, MAX(ts) last, COUNT(*) n, "
                 "ROUND(MAX(power_db),1) maxp, ROUND(AVG(power_db),1) avgp, "
                 "ROUND(AVG(bw_khz)) bw, MAX(audio) audio, "
                 "MAX(category) category, MAX(band_name) band, MAX(demod) demod "
                 "FROM detections")
            args = []
            if categories:
                q += " WHERE category IN (%s)" % ",".join("?" * len(categories))
                args += categories
            q += " GROUP BY f ORDER BY last DESC LIMIT ?"
            args.append(limit)
            rows = self.conn.execute(q, args).fetchall()
        return [dict(ts=r[1], freq_mhz=r[0], count=r[2], power=r[3], avg_power=r[4],
                     bw_khz=r[5], audio=bool(r[6]), category=r[7], band=r[8], demod=r[9])
                for r in rows]

    def count(self):
        return self._det_count          # M6: cached (her status pollunda full-scan yok)

    def analytics(self, hours=24):
        now = time.time()
        since = now - hours * 3600
        with self.lock:
            top = self.conn.execute(
                "SELECT ROUND(freq_hz/1e6,3) f, category, COUNT(*) n, ROUND(AVG(power_db),1) p, "
                "MAX(ts) last FROM detections WHERE ts>? GROUP BY f,category "
                "ORDER BY n DESC LIMIT 25", (since,)).fetchall()
            cats = self.conn.execute(
                "SELECT category, COUNT(*) n FROM detections WHERE ts>? "
                "GROUP BY category ORDER BY n DESC", (since,)).fetchall()
            hourly = self.conn.execute(
                "SELECT CAST((?-ts)/3600 AS INT) h, COUNT(*) n FROM detections "
                "WHERE ts>? GROUP BY h ORDER BY h", (now, since)).fetchall()
        return dict(
            hours=hours,
            top=[dict(freq=r[0], category=r[1], count=r[2], avg_power=r[3], last=r[4]) for r in top],
            categories=[dict(category=r[0], count=r[1]) for r in cats],
            hourly=[dict(hour_ago=r[0], count=r[1]) for r in hourly])

    def search(self, q, limit=300):
        like = f"%{q}%"
        with self.lock:
            rows = self.conn.execute(
                "SELECT ts,freq_hz,power_db,bw_khz,category,band_name,audio,demod FROM detections "
                "WHERE band_name LIKE ? OR category LIKE ? OR CAST(ROUND(freq_hz/1e6,3) AS TEXT) LIKE ? "
                "ORDER BY id DESC LIMIT ?", (like, like, like, min(limit, 500))).fetchall()
        return [dict(ts=r[0], freq_mhz=round(r[1] / 1e6, 4), power=round(r[2], 1),
                     bw_khz=round(r[3]), category=r[4], band=r[5],
                     audio=bool(r[6]), demod=r[7]) for r in rows]

    def export(self, table):
        with self.lock:
            if table == "messages":
                cols = ["ts", "source", "label", "detail"]
                rows = self.conn.execute(
                    "SELECT ts,source,label,detail FROM messages ORDER BY id DESC LIMIT 5000").fetchall()
            else:
                cols = ["ts", "freq_hz", "power_db", "bw_khz", "category", "band_name", "audio", "demod"]
                rows = self.conn.execute(
                    "SELECT ts,freq_hz,power_db,bw_khz,category,band_name,audio,demod "
                    "FROM detections ORDER BY id DESC LIMIT 10000").fetchall()
        return cols, rows
