// Service Worker for Marathon 4:35 PWA
var CACHE_NAME = 'marathon-v1';
var urlsToCache = [
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/manifest.json'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(urlsToCache);
        })
    );
});

self.addEventListener('fetch', function(event) {
    // Network first, fallback to cache
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request).then(function(response) {
            if (response && response.status === 200) {
                var responseClone = response.clone();
                caches.open(CACHE_NAME).then(function(cache) {
                    cache.put(event.request, responseClone);
                });
            }
            return response;
        }).catch(function() {
            return caches.match(event.request);
        })
    );
});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(name) {
                    return name !== CACHE_NAME;
                }).map(function(name) {
                    return caches.delete(name);
                })
            );
        })
    );
});
