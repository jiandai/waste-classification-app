// Service Worker for Waste Bin Classifier PWA
const CACHE_NAME = 'waste-classifier-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png'
];

// Install event - cache resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .catch(err => {
        console.log('Cache install error:', err);
        // Don't fail installation if caching fails
        return Promise.resolve();
      })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Clone the response
        const responseToCache = response.clone();
        
        // Cache successful responses for static assets
        // Include navigation requests (HTML pages), root URL, and files with specific extensions
        const url = new URL(event.request.url);
        const isNavigation = event.request.mode === 'navigate';
        const isRoot = url.pathname === '/' || url.pathname === '';
        const hasExtension = event.request.url.includes('.html') || 
                             event.request.url.includes('.json') || 
                             event.request.url.includes('.png') ||
                             event.request.url.includes('.svg');
        
        if (response.status === 200 && (isNavigation || isRoot || hasExtension)) {
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache).catch(err => {
              console.log('Cache put error:', err);
            });
          }).catch(err => {
            console.log('Cache open error:', err);
          });
        }
        
        return response;
      })
      .catch(error => {
        // Network failed, try cache
        return caches.match(event.request).then(response => {
          if (response) {
            return response;
          }
          // If not in cache and it's a navigation request, try index.html
          if (event.request.mode === 'navigate') {
            return caches.match('/index.html').then(indexResponse => {
              if (indexResponse) {
                return indexResponse;
              }
              // If index.html is also not cached, return a fallback HTML page
              return new Response(
                '<!DOCTYPE html><html><head><title>Offline</title></head><body><h1>You are offline</h1><p>This page is not available offline. Please check your connection and try again.</p></body></html>',
                {
                  status: 503,
                  statusText: 'Service Unavailable',
                  headers: { 'Content-Type': 'text/html' }
                }
              );
            });
          }
          // For API calls and other non-navigation requests that aren't cached,
          // return a network error response instead of undefined
          return new Response(
            JSON.stringify({ 
              error: { 
                message: 'Network request failed and resource is not cached',
                code: 503,
                type: 'network_error'
              }
            }),
            {
              status: 503,
              statusText: 'Service Unavailable',
              headers: { 'Content-Type': 'application/json' }
            }
          );
        });
      })
  );
});
