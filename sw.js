// Service worker de Organización Maia: la app abre sin conexión con los últimos datos descargados.
const VERSION = "hub-v7";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icons/eco-192.png", "icons/eco-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  // Datos y página: primero la red, si no hay conexión, lo último guardado
  if (url.origin === location.origin && (url.pathname.endsWith("data.enc.json") || e.request.mode === "navigate" || url.pathname.endsWith("index.html"))) {
    const cacheKey = url.pathname.endsWith("data.enc.json") ? "data.enc.json" : "index.html";
    e.respondWith(fetch(e.request).then(r => {
      if (r.ok) { const copy = r.clone(); caches.open(VERSION).then(c => c.put(cacheKey, copy)); }
      return r;
    }).catch(() => caches.match(cacheKey)));
    return;
  }
  // Tipografías e iconos: lo guardado primero
  if (url.origin === location.origin || /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => {
      if (r.ok || r.type === "opaque") { const copy = r.clone(); caches.open(VERSION).then(c => c.put(e.request, copy)); }
      return r;
    })));
  }
});
