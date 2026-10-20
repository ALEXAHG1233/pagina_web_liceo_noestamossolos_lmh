// La cara del Tigre LMH (la misma de su página propia): boina, ojos que
// parpadean y siguen al mouse o al dedo, y que muestran lo que está haciendo.
// Escucha el evento "voz-estado" que mandan voz.js y asistente.js:
//   escuchando → los ojos brillan     pensando → mira de lado a lado
//   hablando   → los ojos se mecen    crisis   → borde cálido y mirada suave
const CaraTigre = (() => {
  const FRASES = {
    listo: "Estoy aquí contigo.",
    escuchando: "Te estoy escuchando...",
    pensando: "Estoy pensando...",
    hablando: "Te estoy respondiendo.",
    crisis: "No estás solo. Busquemos ayuda juntos.",
  };
  const reducir = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let estadoActual = "listo";

  const caras = () => document.querySelectorAll(".cara-tigre");

  function ponerEstado(estado) {
    if (!FRASES[estado]) estado = "listo";
    if (estadoActual === "crisis" && estado !== "escuchando") return;  // tras una crisis no vuelve a "listo" sola
    estadoActual = estado;
    caras().forEach((cara) => {
      cara.dataset.estado = estado;
      const frase = cara.querySelector(".cara-tigre-frase");
      if (frase) frase.textContent = FRASES[estado];
    });
  }

  // Los ojos siguen al mouse o al dedo; si nadie se mueve un rato, mira alrededor.
  let ultimo = null, quieto = null;
  function mirar(x, y) {
    caras().forEach((cara) => cara.querySelectorAll(".cara-tigre-pupila").forEach((p) => {
      const ojo = p.parentElement.getBoundingClientRect();
      if (!ojo.width) return;
      const dx = x - (ojo.left + ojo.width / 2);
      const dy = y - (ojo.top + ojo.height / 2);
      const angulo = Math.atan2(dy, dx);
      const cerca = Math.min(1, Math.hypot(dx, dy) / 320);
      p.style.setProperty("--px", `${(Math.cos(angulo) * cerca * ojo.width * 0.22).toFixed(1)}px`);
      p.style.setProperty("--py", `${(Math.sin(angulo) * cerca * ojo.height * 0.2).toFixed(1)}px`);
    }));
  }
  function mirarAlrededor() {
    const caja = document.querySelector(".cara-tigre:not([hidden])")?.getBoundingClientRect();
    if (!caja || document.hidden) return;
    const x = caja.left + caja.width * (0.15 + Math.random() * 0.7);
    const y = caja.top + caja.height * (Math.random() * 1.4 - 0.2);
    mirar(x, y);
  }

  function iniciar() {
    if (!caras().length) return;
    ponerEstado("listo");
    window.addEventListener("voz-estado", (e) => ponerEstado(e.detail));
    if (reducir) return;
    window.addEventListener("pointermove", (e) => {
      ultimo = e;
      requestAnimationFrame(() => { if (ultimo) { mirar(ultimo.clientX, ultimo.clientY); ultimo = null; } });
      clearInterval(quieto);
      quieto = setInterval(mirarAlrededor, 2600);
    }, { passive: true });
    quieto = setInterval(mirarAlrededor, 2600);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar);
  else iniciar();
  return { ponerEstado };
})();
