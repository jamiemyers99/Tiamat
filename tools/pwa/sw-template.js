// Tiamat offline cache (generated at build time by vite.config.js — edit tools/pwa/sw-template.js).
// Caches the game on first visit so the installed app works with no connection.
//
// Updating safely matters as much as caching: every file is fetched straight from the server when a new version
// installs (never from the browser's own short-term cache, which could hand back files from the previous
// version), the page itself is always asked for from the network first, and only this version's cache is ever
// read — so a new version can never end up half-mixed with the old one.
const CACHE = 'tiamat-__VERSION__';
const FILES = __FILES__;

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(FILES.map((f) => new Request(f, { cache: 'reload' }))))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith('tiamat-') && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

// fetch from the server, bypassing the browser cache's stale copies, and keep the answer for offline play
function fromNetwork(req) {
  return fetch(req, { cache: 'no-cache' }).then((res) => {
    if (res.ok && res.type === 'basic') {
      const copy = res.clone();
      caches.open(CACHE).then((c) => c.put(req, copy));
    }
    return res;
  });
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) { return; }
  // the page: network first (so a new version shows up straight away), the cached copy when offline
  // (after 4 seconds without an answer — a weak signal — the cached copy is used instead)
  if (req.mode === 'navigate') {
    event.respondWith(new Promise((resolve) => {
      let done = false;
      const finish = (res) => { if (!done && res) { done = true; resolve(res); } };
      const cached = () => caches.open(CACHE).then((c) => c.match('./'));
      const slow = setTimeout(() => cached().then(finish), 4000);
      fromNetwork(req).then((res) => { clearTimeout(slow); finish(res); })
        .catch(() => cached().then((hit) => finish(hit || Response.error())));
    }));
    return;
  }
  // everything else: this version's cache first, then the network
  event.respondWith(
    caches.open(CACHE).then((c) => c.match(req).then((hit) => hit || fromNetwork(req)))
      .catch(() => Response.error()),
  );
});
