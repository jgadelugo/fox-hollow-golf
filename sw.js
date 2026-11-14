/* Offline support for the shot map and the group scorecard.

   Signal on a golf course is patchy, so once the pages have been opened with a
   connection they must open again without one:
   - the site's own files: fresh from the network when it answers quickly, else the saved copy
   - the map library (a fixed version on a CDN): saved copy first
   - satellite tiles: saved as you look at them, so holes you have viewed still show offline
   Group scores (ntfy.sh) are never touched here; the group page has its own outbox. */
const SHELL = "fh-shell-v1", LIBS = "fh-libs-v1", TILES = "fh-tiles-v1";
const MAX_TILES = 800;          // roughly the whole course at the zoom levels the map uses
const SLOW_MS = 2500;           // how long to wait for the network before showing the saved copy
const APP_FILES = ["./", "course-data.js", "green-data.js", "group/", "manifest.webmanifest", "icons/icon-192.png"];
const LIB_FILES = [
  "https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/4.7.1/maplibre-gl.css",
  "https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/4.7.1/maplibre-gl.js",
];

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const shell = await caches.open(SHELL), libs = await caches.open(LIBS);
    // Best effort: a file that is missing or unreachable must not block the rest.
    await Promise.allSettled([
      ...APP_FILES.map(u => shell.add(new Request(u, { cache: "reload" }))),
      ...LIB_FILES.map(u => libs.add(u)),
    ]);
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keep = [SHELL, LIBS, TILES];
    for (const k of await caches.keys()) if (k.startsWith("fh-") && !keep.includes(k)) await caches.delete(k);
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  if (url.origin === location.origin) e.respondWith(networkFirst(e, url));
  else if (url.hostname === "cdnjs.cloudflare.com") e.respondWith(cacheFirst(e, LIBS));
  else if (url.hostname === "server.arcgisonline.com") e.respondWith(cacheFirst(e, TILES, MAX_TILES));
});

async function networkFirst(e, url) {
  const cache = await caches.open(SHELL);
  const key = url.origin + url.pathname;          // "?r=CODE" on the group page is the same file
  const hit = await cache.match(key);
  const net = fetch(e.request).then(res => {
    if (res.ok && !res.redirected) e.waitUntil(cache.put(key, res.clone()));
    return res.ok || !hit ? res : hit;
  });
  if (!hit) return net;
  e.waitUntil(net.catch(() => {}));               // let a slow download finish and refresh the saved copy
  return Promise.race([net.catch(() => hit), new Promise(done => setTimeout(() => done(hit), SLOW_MS))]);
}

let puts = 0;
async function cacheFirst(e, name, max) {
  const cache = await caches.open(name), key = e.request.url;
  const hit = await cache.match(key, { ignoreVary: true });
  if (hit) return hit;
  // Ask for a readable (CORS) copy so it can be saved; fall back to the page's own request.
  const res = await fetch(key).catch(() => fetch(e.request));
  if (res.ok) {
    e.waitUntil(cache.put(key, res.clone()).then(() => {
      if (max && ++puts % 40 === 0) return trim(cache, max);
    }));
  }
  return res;
}
async function trim(cache, max) {
  const keys = await cache.keys();                // oldest first
  for (const k of keys.slice(0, Math.max(0, keys.length - max))) await cache.delete(k);
}
