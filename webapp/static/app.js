"use strict";

// ==================== i18n (EN varsayılan + TR) ====================
const I18N = {
  en: {
    "title": "📡 HK.SDR", "status.connecting": "connecting…",
    "nav.scan": "🏠 Scan", "grp.decoders": "Decoders", "grp.visual": "Visual",
    "grp.recana": "Record & Analyze", "grp.system": "System",
    "btn.adsb": "✈️ ADS-B", "btn.ais": "🚢 AIS ships", "btn.aprs": "📡 APRS",
    "btn.acars": "🛩️ ACARS", "btn.vdl2": "🛰️ VDL2", "btn.pager": "📟 Pager",
    "btn.rds": "📻 RDS (FM)", "btn.ism": "🌡️ ISM (433)", "btn.wf": "📊 Waterfall",
    "btn.rec": "🎙️ Recordings", "btn.ana": "📈 Analytics", "btn.cfg": "⚙️ Settings",
    "listen.label": "Listening", "listen.nr": "🔇 Noise filter",
    "listen.stop": "⏹ Stop & resume scan", "adsb.label": "✈️ ADS-B mode — listening on 1090 MHz",
    "common.waiting": "waiting…", "common.apply": "Apply", "common.refresh": "Refresh", "common.close": "⏹ Close", "common.error": "error",
    "ism.label": "📟 ISM 433 MHz — sensor messages", "ism.th.device": "Device",
    "ism.th.last": "Last reading / data", "ism.th.count": "Count", "ism.th.seen": "Seen",
    "ism.empty": "Waiting for sensor message… (wireless thermometer, TPMS, remote, etc. — intermittent)",
    "msg.label": "Messages", "msg.freq": "Freq", "msg.th.time": "Time", "msg.th.source": "Source",
    "msg.th.detail": "Detail", "msg.empty": "Waiting for message…",
    "wf.title": "📊 Spectrum / Waterfall", "wf.cursor": "cursor: —", "wf.center": "Center", "wf.span": "Span",
    "wf.hint": "Top row = newest · color = power · <b>click → listen</b> · <b>Shift+click → classify 🔬</b> · wheel → zoom",
    "ana.title": "📈 Analytics & Search", "ana.h1": "last 1h", "ana.h6": "last 6h", "ana.h24": "last 24h", "ana.h7d": "last 7d",
    "ana.exp.det": "⬇ Detections CSV", "ana.exp.msg": "⬇ Messages CSV", "ana.topfreq": "Most active frequencies",
    "ana.th.count": "Count", "ana.th.avgpow": "Avg power", "ana.catdist": "Category distribution",
    "ana.hourly": "Hourly activity (going back)", "ana.search.ph": "🔍 search: category / band / frequency (e.g. TETRA, 385, FM)",
    "ana.nomatch": "no match", "ana.nodata": "no data",
    "th.time": "Time", "th.freq": "Frequency", "th.category": "Category", "th.band": "Band",
    "th.power": "Power", "th.width": "Width", "th.audio": "Audio", "th.stt": "Text (STT)",
    "cfg.title": "⚙️ Settings", "cfg.sched.h": "⏱️ Schedule (hour → profile)", "cfg.sched.save": "Save schedule",
    "cfg.sched.hint": "Empty = off. You can also pick a profile from the dropdown above.",
    "cfg.gain.h": "📶 Gain & PPM calibration", "cfg.gain": "Gain", "cfg.measure": "Measure PPM (~35 s)",
    "cfg.bm.h": "⭐ Bookmarks — import CSV (freq_mhz,label,demod,category)", "cfg.import": "Import",
    "bm.th.label": "Label", "bm.th.mod": "Mode", "bm.th.action": "Action",
    "bm.empty": "No bookmarks — import a CSV or add manually.", "cfg.access.h": "📲 Access & PWA",
    "cfg.access.body": "From your phone: start with <code>HOST=0.0.0.0 scripts/run_webapp.sh</code>, then on the same network open <code>http://&lt;computer-IP&gt;:8000</code>. For security use <code>AUTH=user:pass</code>. In the browser use <b>\"Add to Home Screen\"</b> to install it like an app (PWA).",
    "rec.title": "🎙️ Audio Recordings — frequencies you listen to are archived automatically",
    "rec.th.time": "Time", "rec.th.mod": "Mode", "rec.th.size": "Size", "rec.th.play": "Play / Delete",
    "rec.empty": "No recordings yet — listening to a frequency (▶ Listen or click the waterfall) archives it automatically.",
    "flt.profile": "Profile:", "flt.categories": "Categories:", "flt.lang": "| Lang:", "flt.view": "| 🔀 View:",
    "flt.alarm": "| 🔔 Alarm:", "flt.alarm.ph": "word/category/frequency, comma-separated",
    "group.off": "Group: off", "group.on": "Group: on 🔀", "alert.off": "off", "alert.on": "on 🔔",
    "scan.empty": "No data yet — scan starting…", "scan.none": "No records yet…",
    "row.listen": "▶ Listen", "row.digital": "digital", "wf.waiting": "waiting for spectrum…",
    "flt.profile.set": "Profile: {name}",
    "footer": "Newest on top · ▶ live-listen audio-capable channels · ✈️ track aircraft on the map with ADS-B · scanning pauses during listen/ADS-B",
    "status.noserver": "cannot reach server",
    "st.adsb": "✈️ <b>ADS-B</b> · aircraft: <b>{n}</b>", "st.ais": "🚢 <b>AIS</b> · ships on map",
    "st.aprs": "📡 <b>APRS</b> · stations on map", "st.ism": "🌡️ <b>ISM 433</b> · sensor messages",
    "st.pager": "📟 <b>Pager</b> · content hidden", "st.acars": "🛩️ <b>ACARS</b> · aircraft data messages",
    "st.wf": "📊 <b>Waterfall</b> · spectrum streaming", "st.listen": "🔴 <b>Listening</b> · recordings: <b>{n}</b>",
    "st.nodev": "🔴 <b>No device / USB error</b> — is the dongle connected? (scan paused)",
    "st.scan": "🟢 <b>Scanning</b>{band} · last {age}s · records: <b>{n}</b> · gain {gain}{stt}",
    "st.band": " · now: <b>{band}</b>", "st.stton": " · 🗣️ STT on",
    "wf.cursor.live": "cursor: {f} MHz ({demod}) — click→listen",
    "cls.run": "🔬 classifying {f} MHz…", "cls.res": "🔬 {f} MHz · {mod} · ~{bw} kHz · SNR {snr} dB · likely: {likely}",
    "cls.err": "🔬 classify error",
    "map.adsb.label": "✈️ ADS-B aircraft", "map.adsb.head": "ICAO|Callsign|Alt|Speed|Track|Squawk|Pos|Seen",
    "map.adsb.empty": "Waiting for aircraft… (depends on antenna/location)",
    "map.ais.label": "🚢 AIS ships", "map.ais.head": "MMSI|Name|Speed|Course|Pos|Seen",
    "map.ais.empty": "Waiting for ship… (need coast / near the Bosphorus)",
    "map.aprs.label": "📡 APRS stations", "map.aprs.head": "Callsign|Pos|Seen",
    "map.aprs.empty": "Waiting for APRS packet… (144.800 MHz, intermittent)",
    "msgcfg.pager.label": "📟 Pager (POCSAG/FLEX) — content HIDDEN", "msgcfg.pager.empty": "Waiting for pager message… (frequency/region dependent)",
    "msgcfg.acars.label": "🛩️ ACARS — aircraft data messages (131 MHz)", "msgcfg.acars.empty": "Waiting for ACARS message… (fast when air traffic is busy)",
    "msgcfg.rds.label": "📻 RDS — FM station name / radiotext", "msgcfg.rds.empty": "Waiting for RDS… (tune to a strong FM station — e.g. 100.0)",
    "msgcfg.vdl2.label": "🛰️ VDL2 — aircraft data link (136 MHz)", "msgcfg.vdl2.empty": "Waiting for VDL2 message… (VHF antenna required)",
    "listen.now": "Listening: {f} MHz ({demod})", "stt.listening": "listening…", "stt.off": "STT off (no language selected)",
    "alert.toast.on": "Alarm on: {words}", "alert.toast.empty": "Alarm on but no word entered",
    "cfg.applied": "Gain {g} · PPM {p} applied", "cfg.measuring": "measuring… (~35 s, scan will pause)",
    "cfg.ppmset": "PPM = {ppm} (applied)", "cfg.ppmfail": "could not measure", "cfg.invalidjson": "Invalid JSON",
    "cfg.pickfile": "pick a file", "cfg.imported": "{n} bookmarks imported", "cfg.schedsaved": "Schedule saved",
    "err.start": "{mode} failed to start (decoder / device?)", "err.ism": "ISM failed to start (rtl_433 / device?)",
    "err.wf": "Waterfall failed to start (device?)", "err.leaflet": "Map library (Leaflet) failed to load — internet connection required.",
    "seen.s": "{n}s ago", "seen.min": "{n}m ago", "alarm.title": "📡 SDR Alarm",
  },
  tr: {
    "title": "📡 HK.SDR", "status.connecting": "bağlanıyor…",
    "nav.scan": "🏠 Tarama", "grp.decoders": "Decoder'lar", "grp.visual": "Görsel",
    "grp.recana": "Kayıt & Analiz", "grp.system": "Sistem",
    "btn.adsb": "✈️ ADS-B", "btn.ais": "🚢 AIS gemiler", "btn.aprs": "📡 APRS",
    "btn.acars": "🛩️ ACARS", "btn.vdl2": "🛰️ VDL2", "btn.pager": "📟 Pager",
    "btn.rds": "📻 RDS (FM)", "btn.ism": "🌡️ ISM (433)", "btn.wf": "📊 Waterfall",
    "btn.rec": "🎙️ Kayıtlar", "btn.ana": "📈 Analitik", "btn.cfg": "⚙️ Ayarlar",
    "listen.label": "Dinleniyor", "listen.nr": "🔇 Gürültü filtresi",
    "listen.stop": "⏹ Durdur ve taramaya dön", "adsb.label": "✈️ ADS-B modu — 1090 MHz dinleniyor",
    "common.waiting": "bekleniyor…", "common.apply": "Uygula", "common.refresh": "Yenile", "common.close": "⏹ Kapat", "common.error": "hata",
    "ism.label": "📟 ISM 433 MHz — sensör mesajları", "ism.th.device": "Cihaz",
    "ism.th.last": "Son ölçüm / veri", "ism.th.count": "Tekrar", "ism.th.seen": "Görülme",
    "ism.empty": "Sensör mesajı bekleniyor… (kablosuz termometre, TPMS, kumanda vb. — aralıklı yayın)",
    "msg.label": "Mesajlar", "msg.freq": "Frekans", "msg.th.time": "Saat", "msg.th.source": "Kaynak",
    "msg.th.detail": "Detay", "msg.empty": "Mesaj bekleniyor…",
    "wf.title": "📊 Spektrum / Waterfall", "wf.cursor": "imleç: —", "wf.center": "Merkez", "wf.span": "Genişlik",
    "wf.hint": "Üst satır = en güncel · renk = güç · <b>tıkla → dinle</b> · <b>Shift+tıkla → sınıflandır 🔬</b> · tekerlek → zoom",
    "ana.title": "📈 Analitik & Arama", "ana.h1": "son 1s", "ana.h6": "son 6s", "ana.h24": "son 24s", "ana.h7d": "son 7g",
    "ana.exp.det": "⬇ Tespitler CSV", "ana.exp.msg": "⬇ Mesajlar CSV", "ana.topfreq": "En aktif frekanslar",
    "ana.th.count": "Sayı", "ana.th.avgpow": "Ort.güç", "ana.catdist": "Kategori dağılımı",
    "ana.hourly": "Saatlik aktivite (geriye doğru)", "ana.search.ph": "🔍 ara: kategori / bant / frekans (örn. TETRA, 385, FM)",
    "ana.nomatch": "eşleşme yok", "ana.nodata": "veri yok",
    "th.time": "Saat", "th.freq": "Frekans", "th.category": "Kategori", "th.band": "Bant",
    "th.power": "Güç", "th.width": "Genişlik", "th.audio": "Ses", "th.stt": "Metin (STT)",
    "cfg.title": "⚙️ Ayarlar", "cfg.sched.h": "⏱️ Zamanlama (saat → profil)", "cfg.sched.save": "Zamanlamayı kaydet",
    "cfg.sched.hint": "Boş = kapalı. Profili üstteki açılır menüden de seçebilirsin.",
    "cfg.gain.h": "📶 Kazanç & PPM kalibrasyon", "cfg.gain": "Kazanç", "cfg.measure": "PPM ölç (~35 sn)",
    "cfg.bm.h": "⭐ Yer imleri — CSV içe aktar (freq_mhz,etiket,demod,kategori)", "cfg.import": "İçe aktar",
    "bm.th.label": "Etiket", "bm.th.mod": "Mod", "bm.th.action": "İşlem",
    "bm.empty": "Yer imi yok — CSV içe aktar veya elle ekle.", "cfg.access.h": "📲 Erişim & PWA",
    "cfg.access.body": "Telefondan: <code>HOST=0.0.0.0 scripts/run_webapp.sh</code> ile başlat, aynı ağdan <code>http://&lt;bilgisayar-IP&gt;:8000</code>. Güvenlik için <code>AUTH=kullanıcı:parola</code>. Tarayıcıda <b>\"Ana ekrana ekle\"</b> ile uygulama gibi kurulur (PWA).",
    "rec.title": "🎙️ Ses Kayıtları — dinlediğin frekanslar otomatik arşivlenir",
    "rec.th.time": "Zaman", "rec.th.mod": "Mod", "rec.th.size": "Boyut", "rec.th.play": "Oynat / Sil",
    "rec.empty": "Henüz kayıt yok — bir frekansı dinlediğinde (▶ Dinle veya waterfall'a tıkla) otomatik arşivlenir.",
    "flt.profile": "Profil:", "flt.categories": "Kategoriler:", "flt.lang": "| Dil:", "flt.view": "| 🔀 Görünüm:",
    "flt.alarm": "| 🔔 Alarm:", "flt.alarm.ph": "kelime/kategori/frekans, virgülle",
    "group.off": "Grupla: kapalı", "group.on": "Grupla: açık 🔀", "alert.off": "kapalı", "alert.on": "açık 🔔",
    "scan.empty": "Henüz veri yok — tarama başlıyor…", "scan.none": "Kayıt yok…",
    "row.listen": "▶ Dinle", "row.digital": "dijital", "wf.waiting": "spektrum bekleniyor…",
    "flt.profile.set": "Profil: {name}",
    "footer": "En güncel üstte · ses-uygun kanallarda ▶ canlı dinle · ✈️ ADS-B ile uçakları haritada izle · dinleme/ADS-B sırasında tarama durur",
    "status.noserver": "sunucuya bağlanılamıyor",
    "st.adsb": "✈️ <b>ADS-B</b> · uçak: <b>{n}</b>", "st.ais": "🚢 <b>AIS</b> · gemiler haritada",
    "st.aprs": "📡 <b>APRS</b> · istasyonlar haritada", "st.ism": "🌡️ <b>ISM 433</b> · sensör mesajları",
    "st.pager": "📟 <b>Pager</b> · içerik gizli", "st.acars": "🛩️ <b>ACARS</b> · uçak veri mesajları",
    "st.wf": "📊 <b>Waterfall</b> · spektrum akıyor", "st.listen": "🔴 <b>Dinleniyor</b> · kayıt: <b>{n}</b>",
    "st.nodev": "🔴 <b>Cihaz yok / USB hatası</b> — dongle bağlı mı? (tarama duraklı)",
    "st.scan": "🟢 <b>Taranıyor</b>{band} · son {age}s · kayıt: <b>{n}</b> · kazanç {gain}{stt}",
    "st.band": " · şu an: <b>{band}</b>", "st.stton": " · 🗣️ STT açık",
    "wf.cursor.live": "imleç: {f} MHz ({demod}) — tıkla→dinle",
    "cls.run": "🔬 {f} MHz sınıflandırılıyor…", "cls.res": "🔬 {f} MHz · {mod} · ~{bw} kHz · SNR {snr} dB · olası: {likely}",
    "cls.err": "🔬 sınıflama hatası",
    "map.adsb.label": "✈️ ADS-B uçakları", "map.adsb.head": "ICAO|Çağrı|İrtifa|Hız|Yön|Squawk|Konum|Görülme",
    "map.adsb.empty": "Uçak bekleniyor… (anten ve konuma bağlı)",
    "map.ais.label": "🚢 AIS gemiler", "map.ais.head": "MMSI|Ad|Hız|Yön|Konum|Görülme",
    "map.ais.empty": "Gemi bekleniyor… (kıyı / Boğaz yakını gerekir)",
    "map.aprs.label": "📡 APRS istasyonlar", "map.aprs.head": "Çağrı|Konum|Görülme",
    "map.aprs.empty": "APRS paketi bekleniyor… (144.800 MHz, aralıklı)",
    "msgcfg.pager.label": "📟 Pager (POCSAG/FLEX) — içerik GİZLİ", "msgcfg.pager.empty": "Pager mesajı bekleniyor… (frekans/bölge bağımlı)",
    "msgcfg.acars.label": "🛩️ ACARS — uçak veri mesajları (131 MHz)", "msgcfg.acars.empty": "ACARS mesajı bekleniyor… (hava trafiği yoğunsa hızlı gelir)",
    "msgcfg.rds.label": "📻 RDS — FM istasyon adı / radiotext", "msgcfg.rds.empty": "RDS bekleniyor… (güçlü bir FM istasyonuna ayarla — örn. 100.0)",
    "msgcfg.vdl2.label": "🛰️ VDL2 — uçak veri linki (136 MHz)", "msgcfg.vdl2.empty": "VDL2 mesajı bekleniyor… (VHF anten gerekir)",
    "listen.now": "Dinleniyor: {f} MHz ({demod})", "stt.listening": "dinleniyor…", "stt.off": "STT kapalı (dil seçili değil)",
    "alert.toast.on": "Alarm açık: {words}", "alert.toast.empty": "Alarm açık ama kelime girilmedi",
    "cfg.applied": "Kazanç {g} · PPM {p} uygulandı", "cfg.measuring": "ölçülüyor… (~35 sn, tarama duracak)",
    "cfg.ppmset": "PPM = {ppm} (uygulandı)", "cfg.ppmfail": "ölçülemedi", "cfg.invalidjson": "Geçersiz JSON",
    "cfg.pickfile": "dosya seç", "cfg.imported": "{n} yer imi içe aktarıldı", "cfg.schedsaved": "Zamanlama kaydedildi",
    "err.start": "{mode} başlatılamadı (decoder / cihaz?)", "err.ism": "ISM başlatılamadı (rtl_433 / cihaz?)",
    "err.wf": "Waterfall başlatılamadı (cihaz?)", "err.leaflet": "Harita kütüphanesi (Leaflet) yüklenemedi — internet bağlantısı gerekiyor.",
    "seen.s": "{n}s önce", "seen.min": "{n}dk önce", "alarm.title": "📡 SDR Alarm",
  },
};
let lang = localStorage.getItem("sdrLang") || "en";
const DLOC = lang === "tr" ? "tr-TR" : "en-GB";   // tarih/saat yeresi (dile göre)
function t(k, v) {
  let s = (I18N[lang] && k in I18N[lang]) ? I18N[lang][k] : (k in I18N.en ? I18N.en[k] : k);
  if (v) s = s.replace(/\{(\w+)\}/g, (_, n) => (v[n] != null ? v[n] : ""));
  return s;
}
function applyI18n() {
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((e) => { e.textContent = t(e.dataset.i18n); });
  document.querySelectorAll("[data-i18n-html]").forEach((e) => { e.innerHTML = t(e.dataset.i18nHtml); });
  document.querySelectorAll("[data-i18n-ph]").forEach((e) => { e.placeholder = t(e.dataset.i18nPh); });
  $("langBtn").textContent = lang === "en" ? "🇬🇧 EN" : "🇹🇷 TR";
}
function setLang(l) { lang = l; localStorage.setItem("sdrLang", l); location.reload(); }
function toggleLang() { setLang(lang === "en" ? "tr" : "en"); }

const POLL_MS = 2500;
const AC_MS = 1500;
const ISM_MS = 2000;
const WF_MS = 1500;
let COLORS = {};
let active = new Set();
let allCats = [];
let lastTopTs = 0;
let listening = false;
let ismOn = false;
let wfOn = false;
let mapMode = null;          // "adsb" | "ais" | "aprs"
let msgMode = null;          // "pager" | "acars"
let sttCatsBuilt = false;
let recOpen = false;         // ses kayıt arşivi paneli açık mı
let anaOpen = false;         // analitik paneli açık mı
let cfgOpen = false;         // ayarlar paneli açık mı
let profBuilt = false;       // profil seçici dolduruldu mu
let grouped = false;         // 1B: tarama tablosu frekansa göre gruplu mu
let _wfMeta = null;          // {center, span} — etkileşimli waterfall için
let alertOn = false, alertWords = [], lastAlertTs = 0, alertTimes = {};
let actx = null, srcNode = null, nrHP = null, nrLP = null, audioGraph = false;
let _wfZoomTimer = null;

// harita
let map = null, markersLayer = null, trailsLayer = null;
let acMarkers = {}, acTrails = {}, fitted = false;

const $ = (id) => document.getElementById(id);
// HTML kaçışı: sunucudan/OTA'dan/CSV'den gelen metinleri innerHTML'e basmadan önce (XSS koruması)
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// ---------------- sol hamburger menü ----------------
function openSidebar() { $("sidebar").classList.add("open"); $("backdrop").classList.add("open"); }
function closeSidebar() { $("sidebar").classList.remove("open"); $("backdrop").classList.remove("open"); }
function toggleSidebar() { $("sidebar").classList.toggle("open"); $("backdrop").classList.toggle("open"); }
async function goHome() {      // 🏠 Tarama: açık paneli/modu kapat → tarama görünümü
  if (mapMode || ismOn || wfOn || msgMode || listening) await stopActiveTakeover();
  if (recOpen) closeRec();
  if (anaOpen) closeAna();
  if (cfgOpen) closeCfg();
  updateActiveNav();           // durum gerçekten temizlendikten SONRA vurguyu güncelle
}
function updateActiveNav() {   // menüde aktif sayfayı vurgula
  const m = {
    adsbBtn: mapMode === "adsb", aisBtn: mapMode === "ais", aprsBtn: mapMode === "aprs",
    pagerBtn: msgMode === "pager", acarsBtn: msgMode === "acars", ismBtn: ismOn,
    rdsBtn: msgMode === "rds", vdl2Btn: msgMode === "vdl2",
    wfBtn: wfOn, recBtn: recOpen, anaBtn: anaOpen, cfgBtn: cfgOpen,
  };
  let any = false;
  for (const id in m) { $(id).classList.toggle("active", !!m[id]); if (m[id]) any = true; }
  $("navScan").classList.toggle("active", !any && !listening);
}

async function init() {
  applyI18n();                                          // statik metinleri seçili dile çevir
  $("langBtn").addEventListener("click", toggleLang);   // 🇬🇧/🇹🇷 dil değiştir (sayfa yenilenir)
  try { COLORS = (await (await fetch("/api/bands")).json()).colors || {}; } catch (e) {}
  $("hamburger").addEventListener("click", toggleSidebar);
  $("backdrop").addEventListener("click", closeSidebar);
  $("navScan").addEventListener("click", goHome);
  $("sidebar").addEventListener("click", (e) => {
    if (e.target.tagName === "BUTTON") { closeSidebar(); setTimeout(updateActiveNav, 200); }
  });
  $("stopBtn").addEventListener("click", stopListening);
  $("adsbBtn").addEventListener("click", () => (mapMode === "adsb" ? stopMap() : startMap("adsb")));
  $("aisBtn").addEventListener("click", () => (mapMode === "ais" ? stopMap() : startMap("ais")));
  $("aprsBtn").addEventListener("click", () => (mapMode === "aprs" ? stopMap() : startMap("aprs")));
  $("ismBtn").addEventListener("click", () => (ismOn ? stopIsm() : startIsm()));
  $("pagerBtn").addEventListener("click", () => (msgMode === "pager" ? stopMsg() : startMsg("pager")));
  $("acarsBtn").addEventListener("click", () => (msgMode === "acars" ? stopMsg() : startMsg("acars")));
  $("rdsBtn").addEventListener("click", () => (msgMode === "rds" ? stopMsg() : startMsg("rds")));
  $("vdl2Btn").addEventListener("click", () => (msgMode === "vdl2" ? stopMsg() : startMsg("vdl2")));
  $("msgApply").addEventListener("click", () => { if (msgMode) startMsg(msgMode); });
  $("wfBtn").addEventListener("click", () => (wfOn ? stopWf() : startWf()));
  $("recBtn").addEventListener("click", () => (recOpen ? closeRec() : openRec()));
  $("recClose").addEventListener("click", closeRec);
  $("recRefresh").addEventListener("click", loadRec);
  $("anaBtn").addEventListener("click", () => (anaOpen ? closeAna() : openAna()));
  $("anaClose").addEventListener("click", closeAna);
  $("anaRefresh").addEventListener("click", loadAna);
  $("anaHours").addEventListener("change", loadAna);
  $("anaSearch").addEventListener("input", searchAna);
  $("cfgBtn").addEventListener("click", () => (cfgOpen ? closeCfg() : openCfg()));
  $("cfgClose").addEventListener("click", closeCfg);
  $("cfgApply").addEventListener("click", applyCfg);
  $("cfgMeasure").addEventListener("click", measurePpm);
  $("cfgSchedSave").addEventListener("click", saveSchedule);
  $("cfgImport").addEventListener("click", importCsv);
  $("profSel").addEventListener("change", () => {
    fetch(`/api/profile?set=${encodeURIComponent($("profSel").value)}`, { method: "POST" });
    toast(t("flt.profile.set", { name: $("profSel").value }));
  });
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
  $("alertBtn").addEventListener("click", toggleAlerts);
  $("groupBtn").addEventListener("click", toggleGroup);
  $("alertWords").addEventListener("change", () => {
    alertWords = $("alertWords").value.toLowerCase().split(",").map((s) => s.trim()).filter(Boolean);
  });
  $("nrChk").addEventListener("change", () => setNR($("nrChk").checked));
  $("wfCanvas").addEventListener("wheel", (ev) => {
    if (!wfOn || !_wfMeta) return;
    ev.preventDefault();
    const f = wfFreqAt(ev) || _wfMeta.center;
    let span = _wfMeta.span * (ev.deltaY > 0 ? 1.25 : 0.8);
    span = Math.min(2.4, Math.max(0.2, span));
    $("wfCenter").value = f.toFixed(3);
    $("wfSpan").value = span.toFixed(2);
    clearTimeout(_wfZoomTimer);
    _wfZoomTimer = setTimeout(() => { if (wfOn) startWf(); }, 350);
  }, { passive: false });
  $("wfApply").addEventListener("click", () => { if (wfOn) startWf(); });
  $("wfCanvas").addEventListener("mousemove", (ev) => {
    const f = wfFreqAt(ev);
    if (f != null) $("wfCursor").textContent = t("wf.cursor.live", { f: f.toFixed(3), demod: wfDemod(f).toUpperCase() });
  });
  $("wfCanvas").addEventListener("click", async (ev) => {
    const f = wfFreqAt(ev);
    if (f == null) return;
    if (ev.shiftKey) {                    // SHIFT+tıkla → sınıflandır
      await stopWf();
      toast(t("cls.run", { f: f.toFixed(3) }));
      try {
        const r = await (await fetch(`/api/classify?freq=${f.toFixed(4)}`)).json();
        toast(r.error
          ? `🔬 ${f.toFixed(3)} MHz: ${r.error}`
          : t("cls.res", { f: r.freq_mhz, mod: r.modulation, bw: r.bandwidth_khz, snr: r.snr_db, likely: r.likely }));
      } catch (e) { toast(t("cls.err")); }
      return;
    }
    const d = wfDemod(f);                  // normal tık → dinle
    await stopWf();
    window.listen(f, d);
  });
  $("player").addEventListener("error", () => { if (listening) stopListening(); });
  window.addEventListener("beforeunload", () => {
    if (listening) navigator.sendBeacon("/api/listen/stop");
    if (mapMode) navigator.sendBeacon(`/api/${mapMode}/stop`);
    if (ismOn) navigator.sendBeacon("/api/ism/stop");
    if (wfOn) navigator.sendBeacon("/api/wf/stop");
    if (msgMode) navigator.sendBeacon(`/api/${msgMode}/stop`);
  });
  tick();
  setInterval(tick, POLL_MS);
  setInterval(pollMap, AC_MS);
  setInterval(pollIsm, ISM_MS);
  setInterval(pollWaterfall, WF_MS);
  setInterval(pollMsg, ISM_MS);
  setInterval(pollListenStt, 700);
}

// ---------------- durum + tarama ----------------
async function tick() {
  let st;
  try { st = await (await fetch("/api/status")).json(); }
  catch (e) { $("status").textContent = t("status.noserver"); return; }

  $("adsbBtn").classList.toggle("hidden", !st.adsb_available);
  $("aisBtn").classList.toggle("hidden", !st.ais_available);
  $("aprsBtn").classList.toggle("hidden", !st.aprs_available);
  $("ismBtn").classList.toggle("hidden", !st.ism_available);
  $("pagerBtn").classList.toggle("hidden", !st.pager_available);
  $("acarsBtn").classList.toggle("hidden", !st.acars_available);
  $("rdsBtn").classList.toggle("hidden", !st.rds_available);
  $("vdl2Btn").classList.toggle("hidden", !st.vdl2_available);
  if (st.stt_available && st.stt_cats && !sttCatsBuilt) {
    buildSttCats(st.stt_cats); buildSttLangs(st.stt_langs); sttCatsBuilt = true;
  }
  if (!profBuilt) { profBuilt = true; buildProfiles(); }
  renderStatus(st);
  updateActiveNav();

  if (st.mode !== "scan" || mapMode || ismOn || wfOn || msgMode || recOpen || anaOpen || cfgOpen) return;
  try {
    const rows = await (await fetch(`/api/detections?limit=400&group=${grouped ? 1 : 0}`)).json();
    window._rows = rows;
    [...new Set(rows.map((r) => r.category))].forEach((c) => { if (!allCats.includes(c)) allCats.push(c); });
    buildChips();
    render(rows);
    checkAlerts(rows);
  } catch (e) {}
}

function renderStatus(st) {
  const S = $("status");
  if (st.mode === "adsb") S.innerHTML = t("st.adsb", { n: st.adsb_count });
  else if (st.mode === "ais") S.innerHTML = t("st.ais");
  else if (st.mode === "aprs") S.innerHTML = t("st.aprs");
  else if (st.mode === "ism") S.innerHTML = t("st.ism");
  else if (st.mode === "pager") S.innerHTML = t("st.pager");
  else if (st.mode === "acars") S.innerHTML = t("st.acars");
  else if (st.mode === "wf") S.innerHTML = t("st.wf");
  else if (st.mode === "listen") S.innerHTML = t("st.listen", { n: st.total });
  else if (st.device_ok === false) S.innerHTML = t("st.nodev");   // H3: cihaz yok uyarısı
  else {
    const age = st.last_scan_ts ? Math.round(Date.now() / 1000 - st.last_scan_ts) : "—";
    const band = st.cur_band ? t("st.band", { band: esc(st.cur_band) }) : "";
    const stt = st.stt_available ? t("st.stton") : "";
    S.innerHTML = t("st.scan", { band, age, n: st.total, gain: esc(st.gain), stt });
  }
}

function buildChips() {
  const box = $("chips");
  box.innerHTML = "";
  allCats.forEach((c) => {
    const on = active.size === 0 || active.has(c);
    const el = document.createElement("span");
    el.className = "chip" + (on ? " on" : "");
    el.textContent = c;
    el.style.borderColor = COLORS[c] || "#334155";
    el.style.background = on ? (COLORS[c] || "#334155") : "transparent";
    el.style.color = on ? "#0b1020" : "#9ca3af";
    el.onclick = () => { active.has(c) ? active.delete(c) : active.add(c); buildChips(); render(window._rows || []); };
    box.appendChild(el);
  });
}

// STT kategori aç/kapa tikleri
function buildSttCats(cats) {
  if (!cats || !cats.all || !cats.all.length) { $("sttCatTitle").classList.add("hidden"); return; }
  $("sttCatTitle").classList.remove("hidden");
  const onSet = new Set(cats.on || []);
  $("sttCats").innerHTML = cats.all.map((c) =>
    `<label class="stt-tick"><input type="checkbox" data-cat="${c}" ${onSet.has(c) ? "checked" : ""}>${c}</label>`
  ).join("");
  $("sttCats").querySelectorAll("input").forEach((inp) => inp.addEventListener("change", saveSttCats));
}
async function saveSttCats() {
  const on = [...$("sttCats").querySelectorAll("input:checked")].map((i) => i.dataset.cat);
  try { await fetch(`/api/stt/cats?on=${on.join(",")}`, { method: "POST" }); } catch (e) {}
}
// STT dil aç/kapa tikleri (TR / EN)
function buildSttLangs(langs) {
  if (!langs || !langs.all || langs.all.length < 1) { $("sttLangTitle").classList.add("hidden"); return; }
  $("sttLangTitle").classList.remove("hidden");
  const onSet = new Set(langs.on || []);
  $("sttLangs").innerHTML = langs.all.map((l) =>
    `<label class="stt-tick"><input type="checkbox" data-lang="${l}" ${onSet.has(l) ? "checked" : ""}>${l.toUpperCase()}</label>`
  ).join("");
  $("sttLangs").querySelectorAll("input").forEach((inp) => inp.addEventListener("change", saveSttLangs));
}
async function saveSttLangs() {
  const on = [...$("sttLangs").querySelectorAll("input:checked")].map((i) => i.dataset.lang);
  try { await fetch(`/api/stt/langs?on=${on.join(",")}`, { method: "POST" }); } catch (e) {}
}

function render(rows) {
  const tb = $("rows");
  const sel = active.size ? rows.filter((r) => active.has(r.category)) : rows;
  if (!sel.length) { tb.innerHTML = `<tr><td colspan="8" class="empty">${t("scan.none")}</td></tr>`; return; }
  tb.innerHTML = sel.map(rowHtml).join("");
  if (sel[0].ts !== lastTopTs) {
    [...tb.querySelectorAll("tr")].slice(0, 8).forEach((tr) => {
      if (parseFloat(tr.dataset.ts) === sel[0].ts) tr.classList.add("fresh");
    });
    lastTopTs = sel[0].ts;
  }
}

function rowHtml(r) {
  const t = new Date(r.ts * 1000).toLocaleTimeString(DLOC);
  const color = COLORS[r.category] || "#64748b";
  const dm = (r.demod || "").replace(/[^a-z]/gi, "").toLowerCase();   // onclick JS-string güvenliği
  const listen = r.audio
    ? `<button class="listen-btn" onclick="listen(${Number(r.freq_mhz)},'${dm}')">${t("row.listen")}</button>`
    : `<span class="muted">${t("row.digital")}</span>`;
  // STT sütunu: yalnızca dinlenebilir (ses) frekanslar için cümle (+ dil etiketi)
  const langTag = r.stt_lang ? `<span class="stt-lang">${esc(r.stt_lang.toUpperCase())}</span> ` : "";
  const stt = r.audio
    ? (r.stt ? `${langTag}<span class="stt-text">${esc(r.stt)}</span>` : `<span class="muted">…</span>`)
    : `<span class="muted">—</span>`;
  const cnt = r.count ? ` <span class="cnt">×${r.count}</span>` : "";   // 1B: gruplu tekrar sayısı
  return `<tr data-ts="${r.ts}"><td>${t}</td>
    <td class="freq">${r.freq_mhz.toFixed(r.count ? 3 : 4)} MHz${cnt}</td>
    <td><span class="badge" style="background:${color}">${esc(r.category)}</span></td>
    <td>${esc(r.band)}</td><td>${r.power} dB</td><td>${r.bw_khz} kHz</td>
    <td>${listen}</td><td class="stt-cell">${stt}</td></tr>`;
}

// ---------------- canlı dinleme ----------------
window.listen = function (freqMhz, demod) {
  const p = $("player");
  p.src = `/api/audio.wav?freq=${Math.round(freqMhz * 1e6)}&demod=${demod}`;
  p.play().catch(() => {});
  ensureAudioGraph();
  if (actx && actx.state === "suspended") actx.resume();
  listening = true;
  $("listenLabel").textContent = t("listen.now", { f: freqMhz.toFixed(4), demod: demod.toUpperCase() });
  $("listenSttText").innerHTML = `<span class="stt-dim">${t("stt.listening")}</span>`;
  $("listenBar").classList.remove("hidden");
};
async function stopListening() {
  const p = $("player");
  p.pause(); p.removeAttribute("src"); p.load();
  try { await fetch("/api/listen/stop", { method: "POST" }); } catch (e) {}
  resumeUI();
}
function resumeUI() { listening = false; $("listenBar").classList.add("hidden"); $("listenSttText").innerHTML = ""; lastTopTs = 0; }

// dinlerken canlı STT'yi çek ve akan yazı olarak göster (en yeni metin görünür kalır)
async function pollListenStt() {
  if (!listening) return;
  let d;
  try { d = await (await fetch("/api/listen/stt")).json(); } catch (e) { return; }
  const el = $("listenSttText");
  if (!el) return;
  if (!d.avail) { el.innerHTML = `<span class="stt-dim">${t("stt.off")}</span>`; return; }
  const txt = (d.text || "").trim();
  const part = (d.partial || "").trim();
  if (!txt && !part) { el.innerHTML = `<span class="stt-dim">${t("stt.listening")}</span>`; return; }
  const tag = d.lang ? `<span class="stt-lang">${esc(d.lang)}</span> ` : "";
  el.innerHTML = `${tag}${esc(txt)}${part ? ` <span class="stt-partial">${esc(part)}</span>` : ""}`;
  el.scrollLeft = el.scrollWidth;   // akış: en yeni kelimeler hep görünür
}

// ---------------- takeover modları ----------------
const MAP_MODES = ["adsb", "ais", "aprs"];
function enterTakeover(which) {
  mapMode = MAP_MODES.includes(which) ? which : null;
  ismOn = which === "ism"; wfOn = which === "wf";
  if (which !== "msg") msgMode = null;
  $("filters").classList.add("hidden");
  $("scanMain").classList.add("hidden");
  $("listenBar").classList.add("hidden");
  $("adsbPanel").classList.toggle("hidden", mapMode === null);
  $("ismPanel").classList.toggle("hidden", which !== "ism");
  $("wfPanel").classList.toggle("hidden", which !== "wf");
  $("msgPanel").classList.toggle("hidden", which !== "msg");
  if (mapMode === null) clearMapLayers();
  setButtonLabels();
}
function exitTakeover() {
  mapMode = null; ismOn = false; wfOn = false; msgMode = null;
  clearMapLayers();
  $("adsbPanel").classList.add("hidden");
  $("ismPanel").classList.add("hidden");
  $("wfPanel").classList.add("hidden");
  $("msgPanel").classList.add("hidden");
  $("filters").classList.remove("hidden");
  $("scanMain").classList.remove("hidden");
  setButtonLabels();
}
// Etiketler sabit; aktif/seçili durumu sidebar'daki .active vurgusu gösterir (updateActiveNav).
function setButtonLabels() { updateActiveNav(); }

// ---------------- harita modları (ADS-B / AIS / APRS — paylaşılan harita) ----------------
const MAP_CFG = {
  adsb: {
    ep: "/api/aircraft", key: "aircraft", label: t("map.adsb.label"),
    head: t("map.adsb.head").split("|"), trail: "#38bdf8",
    id: (o) => o.icao,
    icon: (o) => planeIcon(o.track, (o.callsign || o.icao) + (o.alt != null ? ` ${Math.round(o.alt)}ft` : "")),
    row: (o) => `<td class="freq">${esc(o.icao)}</td><td><b>${esc(o.callsign) || "—"}</b></td>
      <td>${o.alt != null ? Math.round(o.alt) + " ft" : "—"}</td>
      <td>${o.speed != null ? Math.round(o.speed) + " kt" : "—"}</td>
      <td>${o.track != null ? Math.round(o.track) + "°" : "—"}</td>
      <td>${esc(o.squawk) || "—"}</td><td>${o.pos ? "📍" : "—"}</td><td>${o.seen}s</td>`,
    empty: t("map.adsb.empty"),
  },
  ais: {
    ep: "/api/ships", key: "ships", label: t("map.ais.label"),
    head: t("map.ais.head").split("|"), trail: "#34d399",
    id: (o) => o.mmsi,
    icon: (o) => shipIcon(o.cog, o.name || String(o.mmsi)),
    row: (o) => `<td class="freq">${o.mmsi}</td><td><b>${esc(o.name) || "—"}</b></td>
      <td>${o.sog != null ? o.sog + " kn" : "—"}</td>
      <td>${o.cog != null ? Math.round(o.cog) + "°" : "—"}</td>
      <td>${o.pos ? "📍" : "—"}</td><td>${o.seen}s</td>`,
    empty: t("map.ais.empty"),
  },
  aprs: {
    ep: "/api/aprs", key: "stations", label: t("map.aprs.label"),
    head: t("map.aprs.head").split("|"), trail: "#fbbf24",
    id: (o) => o.call,
    icon: (o) => aprsIcon(o.call),
    row: (o) => `<td class="freq">${esc(o.call)}</td><td>${o.pos ? "📍" : "—"}</td><td>${o.seen}s</td>`,
    empty: t("map.aprs.empty"),
  },
};

async function startMap(mode) {
  let r;
  try { r = await (await fetch(`/api/${mode}/start`, { method: "POST" })).json(); } catch (e) { return; }
  if (!r.ok) { alert(t("err.start", { mode: mode.toUpperCase() })); return; }
  enterTakeover(mode);
  const cfg = MAP_CFG[mode];
  $("adsbLabel").textContent = cfg.label;
  $("acHead").innerHTML = cfg.head.map((h) => `<th>${h}</th>`).join("");
  initMap();
  clearMapLayers();
  setTimeout(() => map && map.invalidateSize(), 200);
  pollMap();
}
async function stopMap() {
  const mode = mapMode;
  if (mode) { try { await fetch(`/api/${mode}/stop`, { method: "POST" }); } catch (e) {} }
  exitTakeover();
}

function initMap() {
  if (map) return true;
  if (typeof L === "undefined") {            // Leaflet CDN yüklenmediyse (çevrimdışı) → çökme yerine uyarı
    toast(t("err.leaflet"));
    return false;
  }
  map = L.map("map").setView([39.0, 35.0], 5);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    { maxZoom: 14, attribution: "© OpenStreetMap" }).addTo(map);
  trailsLayer = L.layerGroup().addTo(map);
  markersLayer = L.layerGroup().addTo(map);
}
function clearMapLayers() {
  if (markersLayer) markersLayer.clearLayers();
  if (trailsLayer) trailsLayer.clearLayers();
  acMarkers = {}; acTrails = {}; fitted = false;
}

async function pollMap() {
  if (!mapMode || !map) return;
  const cfg = MAP_CFG[mapMode];
  let d;
  try { d = await (await fetch(cfg.ep)).json(); } catch (e) { return; }
  const objs = d[cfg.key] || [];
  const tb = $("acRows");
  tb.innerHTML = objs.length
    ? objs.map((o) => `<tr>${cfg.row(o)}</tr>`).join("")
    : `<tr><td colspan="${cfg.head.length}" class="empty">${cfg.empty}</td></tr>`;

  const seen = new Set();
  objs.filter((o) => o.pos).forEach((o) => {
    const key = String(cfg.id(o));
    seen.add(key);
    const ll = [o.lat, o.lon];
    if (o.trail && o.trail.length > 1) {
      if (acTrails[key]) acTrails[key].setLatLngs(o.trail);
      else acTrails[key] = L.polyline(o.trail, { color: cfg.trail, weight: 2, opacity: 0.6 }).addTo(trailsLayer);
    }
    if (acMarkers[key]) acMarkers[key].setLatLng(ll).setIcon(cfg.icon(o));
    else acMarkers[key] = L.marker(ll, { icon: cfg.icon(o) }).addTo(markersLayer);
  });
  Object.keys(acMarkers).forEach((k) => {
    if (!seen.has(k)) {
      markersLayer.removeLayer(acMarkers[k]); delete acMarkers[k];
      if (acTrails[k]) { trailsLayer.removeLayer(acTrails[k]); delete acTrails[k]; }
    }
  });
  if (!fitted && seen.size) {
    map.fitBounds(L.featureGroup(Object.values(acMarkers)).getBounds().pad(0.3));
    fitted = true;
  }
}

function planeIcon(track, label) {
  return L.divIcon({ className: "plane-icon",
    html: `<div class="plane-wrap" style="transform:rotate(${track || 0}deg)">
        <svg viewBox="0 0 24 24" width="32" height="32"><path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg></div>
      <div class="plane-label">${esc(label)}</div>`,
    iconSize: [32, 32], iconAnchor: [16, 16] });
}
function shipIcon(cog, label) {
  return L.divIcon({ className: "ship-icon",
    html: `<div class="ship-wrap" style="transform:rotate(${cog || 0}deg)">▲</div><div class="ship-label">${esc(label)}</div>`,
    iconSize: [22, 22], iconAnchor: [11, 11] });
}
function aprsIcon(label) {
  return L.divIcon({ className: "aprs-icon",
    html: `<div class="aprs-dot"></div><div class="aprs-label">${esc(label)}</div>`,
    iconSize: [14, 14], iconAnchor: [7, 7] });
}

// ---------------- ISM (433) ----------------
async function startIsm() {
  let r;
  try { r = await (await fetch("/api/ism/start", { method: "POST" })).json(); } catch (e) { return; }
  if (!r.ok) { alert(t("err.ism")); return; }
  enterTakeover("ism");
  pollIsm();
}
async function stopIsm() {
  try { await fetch("/api/ism/stop", { method: "POST" }); } catch (e) {}
  exitTakeover();
}
async function pollIsm() {
  if (!ismOn) return;
  let d;
  try { d = await (await fetch("/api/ism/devices")).json(); } catch (e) { return; }   // 2B: gruplu cihazlar
  const tb = $("ismRows");
  const devs = (d && d.devices) || [];
  if (!devs.length) {
    tb.innerHTML = `<tr><td colspan="4" class="empty">${t("ism.empty")}</td></tr>`;
    return;
  }
  tb.innerHTML = devs.map((x) => `<tr>
    <td><b>${esc(x.label)}</b></td><td>${esc(x.summary)}</td>
    <td><span class="cnt">×${x.count}</span></td>
    <td>${x.seen < 90 ? t("seen.s", { n: Math.round(x.seen) }) : t("seen.min", { n: Math.round(x.seen / 60) })}</td></tr>`).join("");
}

// ---------------- Pager / ACARS (mesaj listesi, paylaşılan panel) ----------------
const MSG_CFG = {
  pager: { label: t("msgcfg.pager.label"), freq: true, defFreq: 466.025, empty: t("msgcfg.pager.empty") },
  acars: { label: t("msgcfg.acars.label"), freq: false, empty: t("msgcfg.acars.empty") },
  rds: { label: t("msgcfg.rds.label"), freq: true, defFreq: 100.0, empty: t("msgcfg.rds.empty") },
  vdl2: { label: t("msgcfg.vdl2.label"), freq: false, empty: t("msgcfg.vdl2.empty") },
};
async function startMsg(mode) {
  const cfg = MSG_CFG[mode];
  if (cfg.freq && cfg.defFreq && msgMode !== mode) $("msgFreq").value = cfg.defFreq;  // doğru banda ön-ayarla
  let url = `/api/${mode}/start`;
  if (cfg.freq) url += `?freq=${parseFloat($("msgFreq").value) || cfg.defFreq}M`;
  let r;
  try { r = await (await fetch(url, { method: "POST" })).json(); } catch (e) { return; }
  if (!r.ok) { alert(t("err.start", { mode: mode.toUpperCase() })); return; }
  msgMode = mode;
  enterTakeover("msg");
  $("msgLabel").textContent = cfg.label;
  $("msgFreqWrap").classList.toggle("hidden", !cfg.freq);
  $("msgApply").classList.toggle("hidden", !cfg.freq);
  pollMsg();
}
async function stopMsg() {
  const mode = msgMode;
  if (mode) { try { await fetch(`/api/${mode}/stop`, { method: "POST" }); } catch (e) {} }
  exitTakeover();
}
async function pollMsg() {
  if (!msgMode) return;
  let m;
  try { m = await (await fetch(`/api/messages?source=${msgMode}&limit=200`)).json(); } catch (e) { return; }
  const tb = $("msgRows");
  if (!m.length) { tb.innerHTML = `<tr><td colspan="3" class="empty">${MSG_CFG[msgMode].empty}</td></tr>`; return; }
  tb.innerHTML = m.map((x) => `<tr>
    <td>${new Date(x.ts * 1000).toLocaleTimeString(DLOC)}</td>
    <td><b>${esc(x.label)}</b></td><td>${esc(x.detail)}</td></tr>`).join("");
}

// ---------------- Waterfall ----------------
async function startWf() {
  const center = parseFloat($("wfCenter").value) || 100;
  const span = parseFloat($("wfSpan").value) || 2;
  let r;
  try { r = await (await fetch(`/api/wf/start?center=${center}&span=${span}`, { method: "POST" })).json(); }
  catch (e) { return; }
  if (!r.ok) { alert(t("err.wf")); return; }
  enterTakeover("wf");
}
async function stopWf() {
  try { await fetch("/api/wf/stop", { method: "POST" }); } catch (e) {}
  exitTakeover();
}
async function pollWaterfall() {
  if (!wfOn) return;
  let d;
  try { d = await (await fetch("/api/waterfall")).json(); } catch (e) { return; }
  const cv = $("wfCanvas");
  const cols = (d.freqs && d.freqs.length) || 256;
  if (cv.width !== cols) cv.width = cols;
  const ctx = cv.getContext("2d");
  const h = cv.height;
  const rows = d.rows || [];
  if (!rows.length) { ctx.clearRect(0, 0, cv.width, h); $("wfAxis").textContent = t("wf.waiting"); return; }
  let mn = Infinity, mx = -Infinity;
  for (const r of rows) for (const v of r) { if (v < mn) mn = v; if (v > mx) mx = v; }
  const rng = Math.max(1, mx - mn);
  const img = ctx.createImageData(cols, h);
  const N = rows.length;
  for (let y = 0; y < h; y++) {
    const ri = N - 1 - y;                       // en güncel üstte
    for (let x = 0; x < cols; x++) {
      let rgb = [11, 16, 32];
      if (ri >= 0 && x < rows[ri].length) rgb = wfColor((rows[ri][x] - mn) / rng);
      const o = (y * cols + x) * 4;
      img.data[o] = rgb[0]; img.data[o + 1] = rgb[1]; img.data[o + 2] = rgb[2]; img.data[o + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  _wfMeta = { center: d.center, span: d.span };
  const lo = d.center - d.span / 2, hi = d.center + d.span / 2;
  $("wfAxis").textContent = `${lo.toFixed(3)}   ◀   ${d.center.toFixed(3)} MHz   ▶   ${hi.toFixed(3)}`;
}
// imleç altındaki frekansı hesapla
function wfFreqAt(ev) {
  if (!_wfMeta) return null;
  const r = ev.target.getBoundingClientRect();
  const frac = Math.min(1, Math.max(0, (ev.clientX - r.left) / r.width));
  return _wfMeta.center - _wfMeta.span / 2 + frac * _wfMeta.span;   // MHz
}
function wfDemod(f) {
  if (f >= 87.5 && f <= 108) return "wbfm";
  if (f >= 118 && f <= 137) return "am";
  return "nfm";
}
function wfColor(v) {
  v = Math.max(0, Math.min(1, v));
  return hslToRgb((1 - v) * 240 / 360, 1, 0.10 + v * 0.45);   // mavi(düşük)→kırmızı(yüksek)
}
function hslToRgb(h, s, l) {
  let r, g, b;
  if (s === 0) { r = g = b = l; }
  else {
    const hue2rgb = (p, q, t) => {
      if (t < 0) t += 1; if (t > 1) t -= 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    };
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r = hue2rgb(p, q, h + 1 / 3); g = hue2rgb(p, q, h); b = hue2rgb(p, q, h - 1 / 3);
  }
  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

// ---------------- Ses kayıt arşivi ----------------
async function stopActiveTakeover() {
  // ayrı if'ler: tutarsız durumda (birden çok bayrak açık) hepsini durdur, ilkinde durma
  if (mapMode) await stopMap();
  if (ismOn) await stopIsm();
  if (wfOn) await stopWf();
  if (msgMode) await stopMsg();
  if (listening) await stopListening();
}
async function openRec() {
  await stopActiveTakeover();           // aktif modu temiz kapat, sonra arşivi göster
  recOpen = true;
  $("filters").classList.add("hidden");
  $("scanMain").classList.add("hidden");
  $("recPanel").classList.remove("hidden");
  loadRec();
}
function closeRec() {
  recOpen = false;
  $("recPanel").classList.add("hidden");
  $("filters").classList.remove("hidden");
  $("scanMain").classList.remove("hidden");
}
async function loadRec() {
  let recs;
  try { recs = await (await fetch("/api/recordings")).json(); } catch (e) { return; }
  const tb = $("recRows");
  if (!recs.length) {
    tb.innerHTML = `<tr><td colspan="5" class="empty">${t("rec.empty")}</td></tr>`;
    return;
  }
  tb.innerHTML = recs.map((r) => `<tr>
    <td>${new Date(r.ts * 1000).toLocaleString(DLOC)}</td>
    <td class="freq">${r.freq} MHz</td>
    <td>${(r.demod || "").toUpperCase()}</td>
    <td>${(r.size / 1024).toFixed(0)} KB</td>
    <td class="rec-actions">
      <audio controls preload="none" src="/api/rec?file=${encodeURIComponent(r.file)}"></audio>
      <button class="listen-btn" onclick="delRec('${r.file}')">🗑️</button></td></tr>`).join("");
}
window.delRec = async function (f) {
  try { await fetch(`/api/rec/delete?file=${encodeURIComponent(f)}`, { method: "POST" }); } catch (e) {}
  loadRec();
};

// ---------------- Gürültü filtresi (WebAudio ses bandı) ----------------
function ensureAudioGraph() {
  if (audioGraph) return;
  try {
    actx = new (window.AudioContext || window.webkitAudioContext)();
    srcNode = actx.createMediaElementSource($("player"));
    nrHP = actx.createBiquadFilter(); nrHP.type = "highpass"; nrHP.frequency.value = 250;
    nrLP = actx.createBiquadFilter(); nrLP.type = "lowpass"; nrLP.frequency.value = 3200;
    audioGraph = true;
    applyNR();
  } catch (e) { audioGraph = false; }
}
function applyNR() {
  if (!audioGraph) return;
  try { srcNode.disconnect(); nrHP.disconnect(); nrLP.disconnect(); } catch (e) {}
  if ($("nrChk").checked) { srcNode.connect(nrHP); nrHP.connect(nrLP); nrLP.connect(actx.destination); }
  else { srcNode.connect(actx.destination); }
}
function setNR() {
  ensureAudioGraph();
  if (actx && actx.state === "suspended") actx.resume();
  applyNR();
}

// ---------------- Alarm / bildirim ----------------
function toggleGroup() {        // 1B: tarama tablosu gruplu ↔ kronolojik
  grouped = !grouped;
  $("groupBtn").textContent = grouped ? t("group.on") : t("group.off");
  $("groupBtn").classList.toggle("on", grouped);
  lastTopTs = 0;
  tick();
}
function toggleAlerts() {
  alertOn = !alertOn;
  $("alertBtn").textContent = alertOn ? t("alert.on") : t("alert.off");
  $("alertBtn").classList.toggle("on", alertOn);
  alertWords = $("alertWords").value.toLowerCase().split(",").map((s) => s.trim()).filter(Boolean);
  if (alertOn && "Notification" in window && Notification.permission === "default") Notification.requestPermission();
  lastAlertTs = Date.now() / 1000;     // sadece bundan sonrasını uyar
  if (alertOn) toast(alertWords.length ? t("alert.toast.on", { words: alertWords.join(", ") }) : t("alert.toast.empty"));
}
function checkAlerts(rows) {
  if (!alertOn || !alertWords.length || !rows.length) return;
  let maxTs = lastAlertTs;
  for (const r of rows) {
    if (r.ts <= lastAlertTs) continue;
    if (r.ts > maxTs) maxTs = r.ts;
    const hay = `${r.category} ${r.band} ${r.freq_mhz} ${r.stt || ""}`.toLowerCase();
    for (const w of alertWords) {
      if (hay.includes(w)) {
        const now = Date.now() / 1000;
        if (now - (alertTimes[w] || 0) > 20) {     // kelime başına 20 sn sınır (spam önle)
          alertTimes[w] = now;
          fireAlert(`🔔 "${w}" → ${r.band} ${r.freq_mhz.toFixed(3)} MHz${r.stt ? " · " + r.stt : ""}`);
        }
      }
    }
  }
  lastAlertTs = maxTs;
}
function fireAlert(msg) {
  toast(msg);
  beep();
  if ("Notification" in window && Notification.permission === "granted") {
    try { new Notification(t("alarm.title"), { body: msg }); } catch (e) {}
  }
}
function beep() {
  try {
    const c = actx || new (window.AudioContext || window.webkitAudioContext)();
    const o = c.createOscillator(), g = c.createGain();
    o.frequency.value = 880; o.connect(g); g.connect(c.destination);
    g.gain.setValueAtTime(0.15, c.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.25);
    o.start(); o.stop(c.currentTime + 0.25);
  } catch (e) {}
}
function toast(msg) {
  const el = document.createElement("div");
  el.className = "toast";
  el.textContent = msg;
  $("toasts").appendChild(el);
  setTimeout(() => el.remove(), 6000);
}

// ---------------- Analitik & arama ----------------
async function openAna() {
  await stopActiveTakeover();
  anaOpen = true;
  $("filters").classList.add("hidden");
  $("scanMain").classList.add("hidden");
  $("anaPanel").classList.remove("hidden");
  $("anaResRows").innerHTML = "";
  loadAna();
}
function closeAna() {
  anaOpen = false;
  $("anaPanel").classList.add("hidden");
  $("filters").classList.remove("hidden");
  $("scanMain").classList.remove("hidden");
}
function anaBar(label, val, max, color) {
  const w = Math.round((val / max) * 100);
  return `<div class="bar-row"><span class="bar-lbl">${label}</span>
    <span class="bar" style="width:${w}%;background:${color || "#64748b"}"></span>
    <span class="bar-val">${val}</span></div>`;
}
async function loadAna() {
  let d;
  try { d = await (await fetch(`/api/analytics?hours=${$("anaHours").value}`)).json(); } catch (e) { return; }
  $("anaTopRows").innerHTML = d.top.length
    ? d.top.map((t) => `<tr><td class="freq">${t.freq.toFixed(3)} MHz</td>
        <td><span class="badge" style="background:${COLORS[t.category] || "#64748b"}">${esc(t.category)}</span></td>
        <td>${t.count}</td><td>${t.avg_power} dB</td></tr>`).join("")
    : `<tr><td colspan="4" class="empty">${t("ana.nodata")}</td></tr>`;
  const cmax = Math.max(1, ...d.categories.map((c) => c.count));
  $("anaCats").innerHTML = d.categories.map((c) => anaBar(c.category, c.count, cmax, COLORS[c.category])).join("") || "—";
  const hmax = Math.max(1, ...d.hourly.map((h) => h.count));
  $("anaHourly").innerHTML = d.hourly.map((h) => anaBar(`${h.hour_ago}s`, h.count, hmax, "#38bdf8")).join("") || "—";
}
async function searchAna() {
  const q = $("anaSearch").value.trim();
  if (!q) { $("anaResRows").innerHTML = ""; return; }
  let rows;
  try { rows = await (await fetch(`/api/search?q=${encodeURIComponent(q)}`)).json(); } catch (e) { return; }
  $("anaResRows").innerHTML = rows.length
    ? rows.map((r) => `<tr><td>${new Date(r.ts * 1000).toLocaleTimeString(DLOC)}</td>
        <td class="freq">${r.freq_mhz.toFixed(4)}</td><td>${esc(r.category)}</td><td>${esc(r.band)}</td><td>${r.power} dB</td></tr>`).join("")
    : `<tr><td colspan="5" class="empty">${t("ana.nomatch")}</td></tr>`;
}

// ---------------- Ayarlar: profil / kalibrasyon / yer imleri ----------------
async function buildProfiles() {
  let p;
  try { p = await (await fetch("/api/profile")).json(); } catch (e) { return; }
  $("profSel").innerHTML = p.all.map((n) => `<option ${n === p.active ? "selected" : ""}>${n}</option>`).join("");
  $("cfgSchedule").value = JSON.stringify(p.schedule || []);
}
async function openCfg() {
  await stopActiveTakeover();
  cfgOpen = true;
  $("filters").classList.add("hidden"); $("scanMain").classList.add("hidden");
  $("cfgPanel").classList.remove("hidden");
  loadCfg();
}
function closeCfg() {
  cfgOpen = false; $("cfgPanel").classList.add("hidden");
  $("filters").classList.remove("hidden"); $("scanMain").classList.remove("hidden");
}
async function loadCfg() {
  try { const c = await (await fetch("/api/config")).json(); $("cfgGain").value = c.gain; $("cfgPpm").value = c.ppm; } catch (e) {}
  loadBookmarks();
}
async function applyCfg() {
  const g = $("cfgGain").value, p = $("cfgPpm").value;
  try { await fetch(`/api/config?gain=${g}&ppm=${p}`, { method: "POST" }); toast(t("cfg.applied", { g, p })); } catch (e) {}
}
async function measurePpm() {
  $("cfgPpmStat").textContent = t("cfg.measuring");
  try {
    const r = await (await fetch("/api/ppm/measure", { method: "POST" })).json();
    if (r.ok) { $("cfgPpm").value = r.ppm; $("cfgPpmStat").textContent = t("cfg.ppmset", { ppm: r.ppm }); }
    else $("cfgPpmStat").textContent = r.error || t("cfg.ppmfail");
  } catch (e) { $("cfgPpmStat").textContent = t("common.error"); }
}
async function saveSchedule() {
  try {
    const r = await (await fetch("/api/schedule", { method: "POST", body: $("cfgSchedule").value })).json();
    toast(r.ok ? t("cfg.schedsaved") : t("cfg.invalidjson"));
  } catch (e) {}
}
async function importCsv() {
  const f = $("cfgCsv").files[0];
  if (!f) { $("cfgImpStat").textContent = t("cfg.pickfile"); return; }
  const text = await f.text();
  try {
    const r = await (await fetch("/api/import", { method: "POST", body: text })).json();
    $("cfgImpStat").textContent = t("cfg.imported", { n: r.imported });
    loadBookmarks();
  } catch (e) { $("cfgImpStat").textContent = t("common.error"); }
}
async function loadBookmarks() {
  let bm;
  try { bm = await (await fetch("/api/bookmarks")).json(); } catch (e) { return; }
  $("bmRows").innerHTML = bm.length ? bm.map((b) => {
    const dm = (b.demod || "").replace(/[^a-z]/gi, "").toLowerCase();   // onclick JS-string injection'a karşı whitelist
    return `<tr>
    <td class="freq">${Number(b.freq_mhz).toFixed(4)} MHz</td><td>${esc(b.label)}</td><td>${esc(dm.toUpperCase())}</td>
    <td><button class="listen-btn" onclick="bmListen(${Number(b.freq_mhz)},'${dm}')">${t("row.listen")}</button>
        <button class="listen-btn" onclick="bmDel(${Number(b.id)})">🗑️</button></td></tr>`; }).join("")
    : `<tr><td colspan="4" class="empty">${t("bm.empty")}</td></tr>`;
}
window.bmListen = function (f, d) { closeCfg(); window.listen(f, d || "wbfm"); };
window.bmDel = async function (id) {
  try { await fetch(`/api/bookmarks/delete?id=${id}`, { method: "POST" }); } catch (e) {}
  loadBookmarks();
};

init();
