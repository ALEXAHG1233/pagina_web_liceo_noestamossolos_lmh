// Letras que giran y aparecen ("flip fade") en el panel de la psicóloga.
// - Los títulos (h1, h2) entran letra por letra al abrir la página.
// - Un elemento con data-flip-palabras="uno|dos|tres" va cambiando de palabra.
// - El título del chat vuelve a girar cada vez que se abre otra conversación.
// Quien pidió menos movimiento en su sistema ve el texto quieto.
(function () {
  const quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const PASO = 35;  // milisegundos entre una letra y la siguiente

  // Pone cada letra en su propio <span> (las palabras no se parten al final de línea)
  function partir(el, texto) {
    el.setAttribute("aria-label", texto);
    el.textContent = "";
    let i = 0;
    texto.split(/(\s+)/).forEach((trozo) => {
      if (!trozo) return;
      if (/^\s+$/.test(trozo)) { el.appendChild(document.createTextNode(" ")); return; }
      const palabra = document.createElement("span");
      palabra.className = "flip-palabra";
      palabra.setAttribute("aria-hidden", "true");
      for (const letra of trozo) {
        const s = document.createElement("span");
        s.className = "flip-letra";
        s.textContent = letra;
        s.style.animationDelay = (i++ * PASO) + "ms";
        palabra.appendChild(s);
      }
      el.appendChild(palabra);
    });
    return i;
  }

  function entrar(el, texto) {
    if (quieto) { el.textContent = texto; return 0; }
    el.classList.remove("flip-sale");
    el.classList.add("flip-entra");
    return partir(el, texto);
  }

  window.flipFadeEntrar = (el) => entrar(el, el.textContent.trim());

  // Títulos de la página
  document.querySelectorAll("h1:not(#chat-titulo), h2").forEach((h) => {
    if (!h.children.length) entrar(h, h.textContent.trim());
  });

  // Palabras que se van turnando
  document.querySelectorAll("[data-flip-palabras]").forEach((el) => {
    const palabras = el.dataset.flipPalabras.split("|").map((p) => p.trim()).filter(Boolean);
    if (palabras.length < 2) return;
    let actual = 0;
    entrar(el, palabras[0]);
    if (quieto) return;
    setInterval(() => {
      el.classList.remove("flip-entra");
      el.classList.add("flip-sale");
      el.querySelectorAll(".flip-letra").forEach((s, i) => { s.style.animationDelay = (i * PASO) + "ms"; });
      const salida = el.querySelectorAll(".flip-letra").length * PASO + 350;
      setTimeout(() => {
        actual = (actual + 1) % palabras.length;
        entrar(el, palabras[actual]);
      }, salida);
    }, 2800);
  });

  // Título del chat: gira cuando cambia de conversación
  const titulo = document.getElementById("chat-titulo");
  if (titulo) {
    let ultimo = titulo.textContent.trim();
    new MutationObserver(() => {
      const texto = titulo.getAttribute("aria-label") && titulo.querySelector(".flip-letra")
        ? titulo.getAttribute("aria-label") : titulo.textContent.trim();
      if (texto === ultimo) return;
      ultimo = texto;
      entrar(titulo, texto);
    }).observe(titulo, { childList: true, characterData: true, subtree: true });
  }
})();
