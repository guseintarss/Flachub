/* Service worker ФлакХаба: офлайн-оболочка и кэш статики. */
const CACHE = 'flachub-shell-v1'
const SHELL = ['/', '/manifest.webmanifest', '/favicon.svg', '/icons/icon-192.png']

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting()),
  )
})

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
      .then(() => self.clients.claim()),
  )
})

self.addEventListener('fetch', event => {
  const request = event.request
  if (request.method !== 'GET') return
  const url = new URL(request.url)
  if (url.origin !== self.location.origin) return
  if (/^\/(api|admin|ws|media|ckeditor5|upload|ajax)\//.test(url.pathname)) return

  // Навигация: сначала сеть, офлайн — сохранённая оболочка.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then(response => {
          const copy = response.clone()
          caches.open(CACHE).then(cache => cache.put(request, copy)).catch(() => {})
          return response
        })
        .catch(() => caches.match(request).then(cached => cached || caches.match('/'))),
    )
    return
  }

  // Статика: сначала кэш, затем сеть с сохранением.
  event.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached
      return fetch(request).then(response => {
        if (response.ok && (url.pathname.startsWith('/assets/') || /\.(css|js|png|svg|webp|woff2?)$/.test(url.pathname))) {
          const copy = response.clone()
          caches.open(CACHE).then(cache => cache.put(request, copy)).catch(() => {})
        }
        return response
      })
    }),
  )
})
