// Service worker: hace que la página funcione como aplicación instalable.
// - Guarda los estilos, scripts, íconos e imágenes ya vistos, para que abra rápido.
// - Las páginas se piden siempre a internet primero (así se ven los cambios
//   de la psicóloga); si no hay conexión, se muestra la última copia o la
//   página "Sin conexión", que recuerda las líneas 150 y 911.
// - Nunca guarda el chat, el panel de la psicóloga ni las cuentas.
const VERSION = "v1";
const CACHE = `no-estamos-solos-${VERSION}`;
const PRECARGA = [
  "/sin-conexion",
  "/static/css/style.css",
  "/static/css/landing.css",
  "/static/css/diario.css",
  "/static/css/pop.css",
  "/static/js/common.js",
  "/static/iconos/icono-192.png",
  "/static/images/logo_liceo.png",
];
const NUNCA = [/^\/socket\.io/, /^\/psicologa/, /^\/api\//, /^\/cuenta/, /^\/chatbot/, /^\/estudiante/, /^\/diario/];

self.addEventListener("install", (evento) => {
  evento.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECARGA)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (evento) => {
  evento.waitUntil(
    caches.keys()
      .then((claves) => Promise.all(claves.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (evento) => {
  const pedido = evento.request;
  if (pedido.method !== "GET") return;
  const url = new URL(pedido.url);
  if (url.origin !== location.origin) return;
  if (NUNCA.some((r) => r.test(url.pathname))) {
    // Páginas privadas o en vivo: solo internet; sin conexión, la página de aviso.
    if (pedido.mode === "navigate") {
      evento.respondWith(fetch(pedido).catch(() => caches.match("/sin-conexion")));
    }
    return;
  }

  if (pedido.mode === "navigate") {
    // Páginas: internet primero, copia guardada si no hay conexión.
    evento.respondWith(
      fetch(pedido)
        .then((resp) => {
          const copia = resp.clone();
          if (resp.ok) caches.open(CACHE).then((c) => c.put(pedido, copia));
          return resp;
        })
        .catch(() => caches.match(pedido).then((r) => r || caches.match("/sin-conexion")))
    );
    return;
  }

  if (url.pathname.startsWith("/static/")) {
    // Archivos fijos: se usan los guardados y se actualizan en segundo plano.
    evento.respondWith(
      caches.match(pedido).then((guardado) => {
        const deRed = fetch(pedido)
          .then((resp) => {
            if (resp.ok) { const copia = resp.clone(); caches.open(CACHE).then((c) => c.put(pedido, copia)); }
            return resp;
          })
          .catch(() => guardado);
        return guardado || deRed;
      })
    );
  }
});
