// Fondo de cuadrícula con ondas (como "WaveGridBackground") para el panel de
// la psicóloga. Dibuja en un <canvas> detrás de todo una cuadrícula cuyas
// líneas suben y bajan como olas; donde la ola está alta, la línea toma el
// color fuerte. El mouse hace una onda suave a su alrededor.
// Se queda quieto si la persona pidió menos movimiento, y se pausa cuando la
// pestaña no se está viendo.
(function () {
  const COLOR_BASE = "#ffffff";
  const COLOR_ALTO = "#0055ff";
  const PASO = 34;          // distancia entre líneas de la cuadrícula (px)
  const ALTURA = 7;         // cuánto suben y bajan las líneas (px)
  const quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const canvas = document.createElement("canvas");
  canvas.className = "fondo-ondas";
  canvas.setAttribute("aria-hidden", "true");
  document.body.prepend(canvas);
  const ctx = canvas.getContext("2d");

  const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  const base = rgb(COLOR_BASE);
  const alto = rgb(COLOR_ALTO);
  function color(t, opacidad) {
    const c = base.map((b, i) => Math.round(b + (alto[i] - b) * t));
    return `rgba(${c[0]},${c[1]},${c[2]},${opacidad})`;
  }

  let ancho = 0, altoPantalla = 0, columnas = 0, filas = 0;
  const raton = { x: -9999, y: -9999 };

  function medir() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    ancho = window.innerWidth;
    altoPantalla = window.innerHeight;
    canvas.width = ancho * dpr;
    canvas.height = altoPantalla * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    columnas = Math.ceil(ancho / PASO) + 2;
    filas = Math.ceil(altoPantalla / PASO) + 2;
  }

  // Altura de la ola (de -1 a 1) en un punto y momento
  function ola(x, y, t) {
    let v = Math.sin(x * 0.012 + t * 0.9) * Math.cos(y * 0.014 - t * 0.7);
    v += 0.5 * Math.sin((x + y) * 0.008 - t * 1.3);
    const d = Math.hypot(x - raton.x, y - raton.y);
    if (d < 260) v += Math.cos(d * 0.05 - t * 4) * (1 - d / 260) * 0.9;
    return Math.max(-1, Math.min(1, v / 1.5));
  }

  function dibujar(t) {
    ctx.clearRect(0, 0, ancho, altoPantalla);
    ctx.lineWidth = 1;
    // Puntos de la cuadrícula ya movidos por la ola
    const puntos = [];
    for (let f = 0; f < filas; f++) {
      const fila = [];
      for (let c = 0; c < columnas; c++) {
        const x = (c - 1) * PASO, y = (f - 1) * PASO;
        const v = ola(x, y, t);
        fila.push({ x, y: y + v * ALTURA, v });
      }
      puntos.push(fila);
    }
    // Cada tramo de línea toma el color según qué tan alta está la ola
    function tramo(a, b) {
      const v = (a.v + b.v) / 2;           // -1 abajo … 1 arriba
      const fuerza = Math.max(0, v);        // solo lo alto se pinta fuerte
      ctx.strokeStyle = color(fuerza, 0.10 + fuerza * 0.45);
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
    }
    for (let f = 0; f < filas; f++) {
      for (let c = 0; c < columnas; c++) {
        const p = puntos[f][c];
        if (c + 1 < columnas) tramo(p, puntos[f][c + 1]);
        if (f + 1 < filas) tramo(p, puntos[f + 1][c]);
      }
    }
  }

  let ultimo = 0;
  function cuadro(ms) {
    if (!document.hidden && ms - ultimo > 33) {  // unos 30 cuadros por segundo
      ultimo = ms;
      dibujar(ms / 1000);
    }
    requestAnimationFrame(cuadro);
  }

  medir();
  window.addEventListener("resize", () => { medir(); if (quieto) dibujar(0); });
  window.addEventListener("pointermove", (e) => { raton.x = e.clientX; raton.y = e.clientY; }, { passive: true });
  document.addEventListener("pointerleave", () => { raton.x = raton.y = -9999; });

  if (quieto) dibujar(0);
  else requestAnimationFrame(cuadro);
})();
