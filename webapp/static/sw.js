// HK.SDR — service worker (ağ-öncelikli, çevrimdışı yedek)
const CACHE = "sdr-v2";
self.addEventListener("install", (e) => self.skipWaiting());
self.addEventListener("activate", (e) => {
  // eski sürüm cache'lerini temizle (bayat app shell'i önle)
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || req.url.includes("/api/")) return;   // canlı API'yi cache'leme
  e.respondWith(
    fetch(req).then((r) => {
      // yalnız sağlam, aynı-köken (basic) 200 yanıtları cache'le — hata/opaque/auth-HTML değil
      if (r.ok && r.status === 200 && r.type === "basic") {
        const cp = r.clone();
        caches.open(CACHE).then((c) => c.put(req, cp)).catch(() => {});
      }
      return r;
    }).catch(() => caches.match(req))
  );
});
