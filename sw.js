const CACHE = 'draft-v6';
// The four data files are precached, not just cached-on-use. The draft room has bad wifi and the
// snapshot board (rank, value, adp, bye, sos, $) is what keeps the app usable when the FFA API is
// unreachable — a data file that was never fetched online is a blank board offline.
const ASSETS = ['./', 'index.html', 'icon-512.png', 'manifest.webmanifest',
  'data/ffa-tiers.json', 'data/ffa-ranks-rpb.json', 'data/ffa-ranks-mwv.json', 'data/keepers-rpb.json', 'data/notes.json'];

// GitHub Pages sends `cache-control: max-age=600` on everything, including this file and
// index.html. A plain fetch() here can be answered from the HTTP cache, which would re-cache a
// stale page and strand an installed PWA on an old build; addAll() would bake the same stale copy
// into a fresh cache version. So HTML and data always go to the network, and the precache reloads.
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE)
    .then(c => Promise.all(ASSETS.map(u => c.add(new Request(u, { cache: 'reload' })).catch(() => {}))))
    .then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  // Only cache same-origin GETs; let cross-origin (the FFA API) pass straight through.
  if (new URL(req.url).origin !== self.location.origin) return;
  const mustBeFresh = req.mode === 'navigate' || req.url.indexOf('/data/') !== -1;
  const hit = mustBeFresh ? fetch(req.url, { cache: 'no-store' }) : fetch(req);
  e.respondWith(hit.then(r => {
    if (r.ok) { const cp = r.clone(); caches.open(CACHE).then(c => c.put(req, cp)); }
    return r;
  }).catch(() => caches.match(req).then(m => m || caches.match('index.html'))));
});
