// Service worker de "5 estrellas, a comer".
// Guarda la web, PyScript, MicroPython y las fuentes para poder jugar sin conexión.
// Si cambias algo importante, sube el número de versión para renovar la caché.
const CACHE = 'cocina-v2';
const PROPIOS = [
  './',
  './index.html',
  './main.py',
  './pedido.py',
  './manifest.webmanifest',
  './iconos/icono-192.png',
  './iconos/icono-512.png',
  './iconos/apple-touch-icon.png',
];

self.addEventListener('install', (evento) => {
  evento.waitUntil(caches.open(CACHE).then((c) => c.addAll(PROPIOS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (evento) => {
  evento.waitUntil(
    caches.keys()
      .then((nombres) => Promise.all(nombres.filter((n) => n !== CACHE).map((n) => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

// La página nos pasa la lista de todo lo que ha cargado (PyScript, wasm, fuentes…).
self.addEventListener('message', (evento) => {
  const datos = evento.data || {};
  if (datos.tipo !== 'guardar' || !Array.isArray(datos.urls)) return;
  evento.waitUntil(
    caches.open(CACHE).then((c) =>
      Promise.all(
        datos.urls
          .filter((u) => u.startsWith('http'))
          .map((u) =>
            c.match(u).then((ya) => ya || fetch(u).then((r) => (r.ok ? c.put(u, r) : null)).catch(() => null))
          )
      )
    )
  );
});

self.addEventListener('fetch', (evento) => {
  const peticion = evento.request;
  if (peticion.method !== 'GET') return;
  const url = new URL(peticion.url);

  if (url.origin === self.location.origin) {
    // Archivos propios: primero la red (para ver siempre la última versión), si no, la caché.
    evento.respondWith(
      fetch(peticion)
        .then((r) => {
          if (r.ok) {
            const copia = r.clone();
            caches.open(CACHE).then((c) => c.put(peticion, copia));
          }
          return r;
        })
        .catch(() => caches.match(peticion, { ignoreSearch: true }).then((r) => r || caches.match('./index.html')))
    );
  } else {
    // Librerías y fuentes externas (tienen versión fija): primero la caché.
    evento.respondWith(
      caches.match(peticion).then(
        (guardada) =>
          guardada ||
          fetch(peticion).then((r) => {
            if (r.ok || r.type === 'opaque') {
              const copia = r.clone();
              caches.open(CACHE).then((c) => c.put(peticion, copia));
            }
            return r;
          })
      )
    );
  }
});
