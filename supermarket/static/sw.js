const CACHE = 'elshadai-v1';

const PRECACHE = [
    '/',
    '/pos/',
    '/products/',
    '/sales/',
];

self.addEventListener('install', e => {
    e.waitUntil(
        caches.open(CACHE).then(c => c.addAll(PRECACHE)).catch(() => {})
    );
    self.skipWaiting();
});

self.addEventListener('activate', e => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', e => {
    if (e.request.method !== 'GET') return;
    if (e.request.url.includes('/barcode/lookup/')) return;
    if (e.request.url.includes('/mpesa/')) return;
    if (e.request.url.includes('/admin/')) return;

    e.respondWith(
        fetch(e.request)
        .then(res => {
            const clone = res.clone();
            caches.open(CACHE).then(c => c.put(e.request, clone));
            return res;
        })
        .catch(() => caches.match(e.request))
    );
});
