// Fondo de "onda de plasma" (como PlasmaWave): dos ondas de luz que se
// curvan y se mueven, con un núcleo brillante, resplandor y un poco de
// grano. El mouse las dobla un poco hacia donde apunta. Es un shader de
// WebGL, sin librerías. Colores del liceo: verde y dorado.
(function () {
  const lienzo = document.querySelector("[data-plasma]");
  if (!lienzo) return;
  const gl = lienzo.getContext("webgl", { antialias: false });
  if (!gl) { lienzo.remove(); return; }

  const AJUSTES = {
    colores: ["#2fae5f", "#ffc83d"],  // verde → dorado
    fondo: "#0b2213",                 // verde muy oscuro
    velocidad: 1,
    curva1: 1,
    curva2: 0.5,
    grosor: 0.3,
    resplandor: 1,
    nucleo: 0.6,
    velocidad1: 0.05,
    velocidad2: 0.05,
    direccion2: 1,
    brillo: 1,
    grano: 0.03,
  };
  const sinMovimiento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);

  const vertice = `
    attribute vec2 p;
    void main() { gl_Position = vec4(p, 0.0, 1.0); }
  `;
  const fragmento = `
    precision mediump float;
    uniform vec2 uRes, uMouse;
    uniform float uTiempo, uCurva1, uCurva2, uGrosor, uResplandor, uNucleo;
    uniform float uVel1, uVel2, uDir2, uBrillo, uGrano, uEntrada, uFuerzaMouse;
    uniform vec3 uColorA, uColorB, uFondo;

    float azar(vec2 c) { return fract(sin(dot(c, vec2(12.9898, 78.233))) * 43758.5453); }

    // Luz de una onda: muy fuerte cerca de la línea y se apaga suave.
    vec3 onda(vec2 q, float fase, float curva, float desplazar, vec3 color) {
      float y = sin(q.x * 2.2 * curva + fase) * 0.22 * curva
              + sin(q.x * 5.1 + fase * 1.7) * 0.04
              + desplazar;
      float d = abs(q.y - y);
      float luz = (uGrosor * 0.02) / max(d, 0.002);
      float halo = exp(-d * 9.0) * 0.35 * uResplandor;
      float centro = smoothstep(0.012 * uGrosor * 3.0, 0.0, d) * uNucleo;
      return color * (luz + halo) + vec3(1.0) * centro;
    }

    void main() {
      vec2 uv = gl_FragCoord.xy / uRes;
      float aspecto = uRes.x / uRes.y;
      vec2 q = vec2((uv.x - 0.5) * aspecto, uv.y - 0.5);

      // El mouse dobla las ondas cerca de donde está.
      vec2 m = vec2((uMouse.x - 0.5) * aspecto, uMouse.y - 0.5);
      float cerca = exp(-pow(q.x - m.x, 2.0) * 6.0) * uFuerzaMouse;
      float tirar = (m.y - 0.0) * 0.35 * cerca;

      float t = uTiempo;
      vec3 color = uFondo;
      color += onda(q, t * uVel1 * 20.0, uCurva1, tirar, uColorA);
      color += onda(q, -t * uVel2 * 20.0 * uDir2 + 1.7, uCurva2 * 1.6, tirar * 0.7 - 0.05, uColorB) * 0.85;

      color *= uBrillo;
      color += (azar(gl_FragCoord.xy + t) - 0.5) * uGrano;
      color = 1.0 - exp(-color * 1.4);         // que no se queme el blanco
      color = mix(uFondo, color, uEntrada);    // entrada suave (intro)
      gl_FragColor = vec4(color, 1.0);
    }
  `;

  function compilar(tipo, codigo) {
    const sh = gl.createShader(tipo);
    gl.shaderSource(sh, codigo);
    gl.compileShader(sh);
    return sh;
  }
  const programa = gl.createProgram();
  gl.attachShader(programa, compilar(gl.VERTEX_SHADER, vertice));
  gl.attachShader(programa, compilar(gl.FRAGMENT_SHADER, fragmento));
  gl.linkProgram(programa);
  if (!gl.getProgramParameter(programa, gl.LINK_STATUS)) { lienzo.remove(); return; }
  gl.useProgram(programa);

  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  const ubic = gl.getAttribLocation(programa, "p");
  gl.enableVertexAttribArray(ubic);
  gl.vertexAttribPointer(ubic, 2, gl.FLOAT, false, 0, 0);

  const U = {};
  ["uRes", "uMouse", "uTiempo", "uCurva1", "uCurva2", "uGrosor", "uResplandor", "uNucleo", "uVel1", "uVel2",
    "uDir2", "uBrillo", "uGrano", "uEntrada", "uFuerzaMouse", "uColorA", "uColorB", "uFondo"]
    .forEach((n) => { U[n] = gl.getUniformLocation(programa, n); });

  gl.uniform1f(U.uCurva1, AJUSTES.curva1);
  gl.uniform1f(U.uCurva2, AJUSTES.curva2);
  gl.uniform1f(U.uGrosor, AJUSTES.grosor);
  gl.uniform1f(U.uResplandor, AJUSTES.resplandor);
  gl.uniform1f(U.uNucleo, AJUSTES.nucleo);
  gl.uniform1f(U.uVel1, AJUSTES.velocidad1);
  gl.uniform1f(U.uVel2, AJUSTES.velocidad2);
  gl.uniform1f(U.uDir2, AJUSTES.direccion2);
  gl.uniform1f(U.uBrillo, AJUSTES.brillo);
  gl.uniform1f(U.uGrano, AJUSTES.grano);
  gl.uniform3fv(U.uColorA, rgb(AJUSTES.colores[0]));
  gl.uniform3fv(U.uColorB, rgb(AJUSTES.colores[1]));
  gl.uniform3fv(U.uFondo, rgb(AJUSTES.fondo));

  function medir() {
    const escala = 0.75;  // un poco menos de resolución: se ve igual y gasta menos
    lienzo.width = Math.round(window.innerWidth * escala);
    lienzo.height = Math.round(window.innerHeight * escala);
    gl.viewport(0, 0, lienzo.width, lienzo.height);
    gl.uniform2f(U.uRes, lienzo.width, lienzo.height);
  }

  // El mouse dobla las ondas; si se deja de mover, vuelven solas.
  const objetivo = { x: 0.5, y: 0.5, f: 0 }, actual = { x: 0.5, y: 0.5, f: 0 };
  let ultimoMouse = -1e9;
  window.addEventListener("pointermove", (e) => {
    objetivo.x = e.clientX / window.innerWidth;
    objetivo.y = 1 - e.clientY / window.innerHeight;
    ultimoMouse = performance.now();
  }, { passive: true });

  const arranque = performance.now();
  let anterior = 0;
  function cuadro(ahora) {
    requestAnimationFrame(cuadro);
    if (document.hidden || ahora - anterior < 33) return;   // ~30 cuadros por segundo
    anterior = ahora;
    const t = ((ahora - arranque) / 1000) * AJUSTES.velocidad;
    objetivo.f = ahora - ultimoMouse < 2500 ? 1 : 0;
    actual.x += (objetivo.x - actual.x) * 0.12;
    actual.y += (objetivo.y - actual.y) * 0.12;
    actual.f += (objetivo.f - actual.f) * 0.05;
    gl.uniform1f(U.uTiempo, t);
    gl.uniform2f(U.uMouse, actual.x, actual.y);
    gl.uniform1f(U.uFuerzaMouse, actual.f);
    gl.uniform1f(U.uEntrada, Math.min(t / 1.5, 1));
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }

  medir();
  window.addEventListener("resize", medir);
  if (sinMovimiento) {
    gl.uniform1f(U.uTiempo, 0);
    gl.uniform2f(U.uMouse, 0.5, 0.5);
    gl.uniform1f(U.uFuerzaMouse, 0);
    gl.uniform1f(U.uEntrada, 1);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  } else {
    requestAnimationFrame(cuadro);
  }
})();
