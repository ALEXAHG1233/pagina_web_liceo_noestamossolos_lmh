/**
 * Utilidades compartidas de interfaz: revelado de secciones al hacer scroll,
 * y botón de sonido reutilizable. El fundido de entrada de la página se
 * maneja aparte con una animación CSS pura (no depende de que este script cargue).
 */

// Botón flotante de WhatsApp, visible en todas las páginas que cargan este script.
const WHATSAPP_NUMERO = "50431746810";

function crearBotonWhatsAppFlotante() {
  if (document.getElementById("whatsapp-flotante")) return;
  const boton = document.createElement("a");
  boton.id = "whatsapp-flotante";
  boton.href = `https://wa.me/${WHATSAPP_NUMERO}`;
  boton.target = "_blank";
  boton.rel = "noopener noreferrer";
  boton.className = "whatsapp-flotante";
  boton.setAttribute("aria-label", "Contactar por WhatsApp");
  boton.innerHTML =
    '<svg viewBox="0 0 32 32" width="26" height="26" fill="#fff"><path d="M16 3C9 3 3.2 8.7 3.2 15.8c0 2.6.7 5 2 7.1L3 29l6.3-2.1c2 1.1 4.3 1.7 6.7 1.7 7 0 12.8-5.7 12.8-12.8C28.8 8.7 23 3 16 3zm0 23.3c-2.1 0-4.1-.6-5.8-1.6l-.4-.2-3.8 1.3 1.3-3.7-.3-.4a10.4 10.4 0 0 1-1.7-5.7C5.3 9.9 10.1 5.1 16 5.1S26.7 9.9 26.7 15.8 21.9 26.3 16 26.3zm5.7-7.8c-.3-.2-1.8-.9-2.1-1-.3-.1-.5-.2-.7.2s-.8 1-1 1.2c-.2.2-.4.2-.7.1a8.6 8.6 0 0 1-2.5-1.5 9.3 9.3 0 0 1-1.7-2.1c-.2-.3 0-.5.1-.7l.4-.5c.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-1-2.3c-.2-.6-.5-.5-.7-.5h-.6a1.2 1.2 0 0 0-.8.4 3.5 3.5 0 0 0-1.1 2.6c0 1.6 1.1 3.1 1.3 3.3.2.2 2.2 3.4 5.4 4.7.8.3 1.4.5 1.8.6.8.3 1.5.2 2-.1.6-.4 1.8-1.2 2.1-1.9.3-.7.3-1.3.2-1.4-.1-.2-.3-.3-.6-.4z"/></svg>' +
    '<span class="whatsapp-flotante-texto">Escribir por WhatsApp</span>';
  document.body.appendChild(boton);
}

document.addEventListener("DOMContentLoaded", crearBotonWhatsAppFlotante);

/**
 * Barra de navegación: abre/cierra el menú hamburguesa en celular, lo
 * cierra al elegir un enlace, y le agrega sombra cuando ya se hizo
 * scroll (para que se note que está "flotando" sobre el contenido).
 */
function activarNavPrincipal() {
  const nav = document.getElementById("nav-principal");
  const boton = document.getElementById("nav-hamburguesa");
  const enlaces = document.getElementById("nav-enlaces");
  if (!nav || !boton || !enlaces) return;

  boton.addEventListener("click", () => {
    const abierto = enlaces.classList.toggle("nav-abierto");
    boton.setAttribute("aria-expanded", abierto ? "true" : "false");
  });

  enlaces.querySelectorAll("a").forEach((enlace) => {
    enlace.addEventListener("click", () => {
      enlaces.classList.remove("nav-abierto");
      boton.setAttribute("aria-expanded", "false");
    });
  });

  function actualizarSombra() {
    nav.classList.toggle("nav-con-scroll", window.scrollY > 10);
  }
  window.addEventListener("scroll", actualizarSombra, { passive: true });
  actualizarSombra();
}

document.addEventListener("DOMContentLoaded", activarNavPrincipal);

// Botón ☀️/🌙 del menú: alterna entre el modo oscuro (verde, el de siempre)
// y el modo claro. La preferencia se guarda en este navegador; el <head>
// de la portada la aplica antes de pintar para que no "parpadee".
function activarCambioTema() {
  const boton = document.getElementById("nav-tema");
  if (!boton) return;
  const raiz = document.documentElement;
  const icono = boton.querySelector(".nav-tema-icono");

  function pintarBoton() {
    const claro = raiz.dataset.tema === "claro";
    icono.textContent = claro ? "🌙" : "☀️";
    boton.setAttribute("aria-label", claro ? "Cambiar a modo oscuro" : "Cambiar a modo claro");
    boton.setAttribute("aria-pressed", claro ? "true" : "false");
  }

  boton.addEventListener("click", () => {
    const claro = raiz.dataset.tema !== "claro";
    if (claro) raiz.dataset.tema = "claro";
    else delete raiz.dataset.tema;
    try { localStorage.setItem("tema", claro ? "claro" : "oscuro"); } catch (e) {}
    pintarBoton();
  });
  pintarBoton();
}

document.addEventListener("DOMContentLoaded", activarCambioTema);

const SIN_MOVIMIENTO = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Barra dorada fina arriba que muestra cuánto has bajado en la página.
function crearBarraProgreso() {
  if (!document.querySelector(".landing-body") || document.getElementById("barra-progreso")) return;
  const barra = document.createElement("div");
  barra.id = "barra-progreso";
  barra.className = "barra-progreso";
  barra.setAttribute("aria-hidden", "true");
  document.body.appendChild(barra);

  let pendiente = false;
  function actualizar() {
    pendiente = false;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const progreso = max > 0 ? window.scrollY / max : 0;
    barra.style.transform = `scaleX(${progreso})`;
  }
  window.addEventListener("scroll", () => {
    if (!pendiente) {
      pendiente = true;
      requestAnimationFrame(actualizar);
    }
  }, { passive: true });
  actualizar();
}

document.addEventListener("DOMContentLoaded", crearBarraProgreso);

// Brillo dorado que sigue al mouse dentro de las tarjetas grandes.
function activarFocoTarjetas() {
  if (SIN_MOVIMIENTO || !window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
  document.querySelectorAll(".opcion-grande, .tarjeta-extra").forEach((tarjeta) => {
    tarjeta.addEventListener("pointermove", (e) => {
      const r = tarjeta.getBoundingClientRect();
      tarjeta.style.setProperty("--mx", `${e.clientX - r.left}px`);
      tarjeta.style.setProperty("--my", `${e.clientY - r.top}px`);
    });
  });
}

document.addEventListener("DOMContentLoaded", activarFocoTarjetas);

/**
 * Fondo parallax con imágenes, visible en todas las páginas que cargan
 * este script. Cada "capa" es una imagen que se mueve a su propia
 * velocidad al hacer scroll (las más lentas se sienten "más atrás").
 * Para agregar una imagen nueva, solo hay que añadir un objeto aquí
 * con su archivo (en static/images/parallax/) y su velocidad (0 = fija,
 * 1 = se mueve igual que la página). Si la lista está vacía, simplemente
 * no se crea ninguna capa — no rompe nada.
 */
const PARALLAX_CAPAS = [
  // Ejemplo de cómo agregar una capa cuando haya una imagen real:
  // { archivo: "capa_hojas.webp", velocidad: 0.2 },
  // { archivo: "capa_tigre.webp", velocidad: 0.45 },
];

function crearFondoParallax() {
  if (!PARALLAX_CAPAS.length || document.getElementById("fondo-parallax")) return;

  const contenedor = document.createElement("div");
  contenedor.id = "fondo-parallax";
  contenedor.className = "fondo-parallax";
  contenedor.setAttribute("aria-hidden", "true");

  const capas = PARALLAX_CAPAS.map((capa) => {
    const img = document.createElement("img");
    img.className = "parallax-capa";
    img.src = `/static/images/parallax/${capa.archivo}`;
    img.dataset.velocidad = capa.velocidad;
    img.alt = "";
    contenedor.appendChild(img);
    return img;
  });

  document.body.prepend(contenedor);

  function actualizar() {
    const scrollY = window.scrollY || window.pageYOffset;
    capas.forEach((img) => {
      const velocidad = parseFloat(img.dataset.velocidad) || 0;
      img.style.transform = `translateY(${scrollY * velocidad}px)`;
    });
  }

  window.addEventListener("scroll", actualizar, { passive: true });
  actualizar();
}

document.addEventListener("DOMContentLoaded", crearFondoParallax);

/**
 * Parallax del banner del hero: la imagen se desplaza más lento que el
 * scroll (se ve "más atrás"), mientras el texto y el botón debajo se
 * mueven normal. Se escala un poco de más para que el contenedor
 * (overflow: hidden) nunca deje ver un borde vacío al desplazarla.
 */
function crearParallaxHero() {
  const img = document.querySelector(".hero-banner-img");
  if (!img) return;

  const DESPLAZAMIENTO_MAXIMO = 18; // px — la imagen es un banner corto, no un hero de pantalla completa

  function actualizar() {
    const rect = img.getBoundingClientRect();
    const centro = rect.top + rect.height / 2 - window.innerHeight / 2;
    let desplazamiento = centro * -0.08;
    desplazamiento = Math.max(-DESPLAZAMIENTO_MAXIMO, Math.min(DESPLAZAMIENTO_MAXIMO, desplazamiento));
    img.style.transform = `scale(1.08) translateY(${desplazamiento}px)`;
  }

  window.addEventListener("scroll", actualizar, { passive: true });
  window.addEventListener("resize", actualizar);
  actualizar();
}

document.addEventListener("DOMContentLoaded", crearParallaxHero);

const GRUPOS_ESCALONADOS = ".tarjetas, .opciones, .tarjetas-extra, .redes-grid, .video-landing-grid, .ayuda-grid, .recursos-grid";

function activarRevelado(selector = ".reveal") {
  const elementos = document.querySelectorAll(selector);
  if (!elementos.length) return;

  // Las tarjetas dentro de una sección aparecen una tras otra, no todas a la vez.
  document.querySelectorAll(GRUPOS_ESCALONADOS).forEach((grupo) => {
    Array.from(grupo.children).forEach((hijo, i) => {
      hijo.classList.add("escalonado");
      hijo.style.setProperty("--i", i);
    });
  });

  if (!("IntersectionObserver" in window)) {
    elementos.forEach((el) => el.classList.add("visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entradas) => {
      entradas.forEach((entrada) => {
        if (entrada.isIntersecting) {
          entrada.target.classList.add("visible");
          observer.unobserve(entrada.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  elementos.forEach((el) => observer.observe(el));
}

function crearToggleSonido(boton, opciones = {}) {
  if (!boton) return;
  const textoActivo = opciones.textoActivo || "Sonido";
  const textoSilenciado = opciones.textoSilenciado || "Sonido silenciado";

  const actualizar = () => {
    const on = Sonidos.activo();
    boton.textContent = on ? textoActivo : textoSilenciado;
    boton.classList.toggle("silenciado", !on);
  };

  boton.addEventListener("click", () => {
    Sonidos.desbloquear();
    Sonidos.establecer(!Sonidos.activo());
    actualizar();
  });

  actualizar();
}

function crearBotonMusica(boton, playlistId) {
  if (!boton) return;
  const panel = document.getElementById("panel-musica");
  if (!panel) return;
  const lista = playlistId || (typeof SPOTIFY_PLAYLIST_LOFI !== "undefined" ? SPOTIFY_PLAYLIST_LOFI : "37i9dQZF1DWWQRwui0ExPn");

  boton.addEventListener("click", () => {
    if (panel.classList.contains("visible")) {
      panel.classList.remove("visible");
      panel.innerHTML = "";
      return;
    }
    panel.innerHTML = `<iframe
      src="https://open.spotify.com/embed/playlist/${lista}?utm_source=generator&theme=0"
      width="100%" height="152" frameborder="0"
      allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
      loading="lazy"></iframe>`;
    panel.classList.add("visible");
  });
}

/**
 * Paleta de fondos disponible para los chats. Un solo lugar para las tres
 * pantallas de chat (estudiante, asistente, psicóloga) en vez de repetirla.
 */
const FONDOS_DISPONIBLES = {
  claro: { tipo: "color", valor: "#f6f3ec" },
  verde: { tipo: "color", valor: "#e3efe6" },
  azul: { tipo: "color", valor: "#e1f0fb" },
  dorado: { tipo: "color", valor: "#fbead2" },
  rosa: { tipo: "color", valor: "#fbe4ec" },
  morado: { tipo: "color", valor: "#ece1fb" },
  coral: { tipo: "color", valor: "#fde3da" },
  menta: { tipo: "color", valor: "#dff5ec" },
  gris: { tipo: "color", valor: "#ececec" },
  oscuro: { tipo: "color", valor: "#2c2c2a" },
  rosa_cuadros: { tipo: "imagen", valor: "/static/images/fondos/fondo_rosa_cuadros.webp", titulo: "Rosa de cuadros" },
  naranja_hojas: { tipo: "imagen", valor: "/static/images/fondos/fondo_naranja_hojas.webp", titulo: "Naranja de hojas" },
};

function crearSelectorFondo(contenedorId, mensajesEl, storageKey) {
  const contenedor = document.getElementById(contenedorId);
  if (!contenedor || !mensajesEl) return;

  function aplicar(nombre) {
    const fondo = FONDOS_DISPONIBLES[nombre] || FONDOS_DISPONIBLES.claro;
    if (fondo.tipo === "imagen") {
      mensajesEl.style.background = `center / cover no-repeat url("${fondo.valor}")`;
    } else {
      mensajesEl.style.background = fondo.valor;
    }
    localStorage.setItem(storageKey, nombre);
    contenedor.querySelectorAll(".fondo-swatch").forEach((btn) => {
      btn.classList.toggle("activo", btn.dataset.fondo === nombre);
    });
  }

  Object.entries(FONDOS_DISPONIBLES).forEach(([nombre, fondo]) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.classList.add("fondo-swatch");
    if (fondo.tipo === "imagen") {
      btn.style.backgroundImage = `url("${fondo.valor}")`;
    } else {
      btn.style.background = fondo.valor;
    }
    btn.dataset.fondo = nombre;
    btn.title = fondo.titulo || nombre.charAt(0).toUpperCase() + nombre.slice(1);
    btn.addEventListener("click", () => aplicar(nombre));
    contenedor.appendChild(btn);
  });

  aplicar(localStorage.getItem(storageKey) || "claro");
}

/**
 * Avatares de la psicóloga para el chat del estudiante. Es opcional:
 * si no se elige ninguno, se sigue viendo la letra "P" de siempre.
 */
const AVATARES_PSICOLOGA_DISPONIBLES = {
  lego: { valor: "/static/images/avatares/avatar_lego.png", titulo: "Avatar Lego" },
  chica: { valor: "/static/images/avatares/avatar_chica.png", titulo: "Avatar chica" },
  realista: { valor: "/static/images/avatares/avatar_realista.webp", titulo: "Avatar realista" },
  sticker: { valor: "/static/images/avatares/avatar_sticker.webp", titulo: "Avatar sticker" },
};

function obtenerAvatarPsicologaElegido(storageKey) {
  const nombre = localStorage.getItem(storageKey);
  const avatar = nombre && AVATARES_PSICOLOGA_DISPONIBLES[nombre];
  return avatar ? avatar.valor : null;
}

function crearSelectorAvatar(contenedorId, storageKey, alCambiar) {
  const contenedor = document.getElementById(contenedorId);
  if (!contenedor) return;

  function marcarActivo(nombre) {
    contenedor.querySelectorAll(".fondo-swatch").forEach((btn) => {
      btn.classList.toggle("activo", btn.dataset.avatar === nombre);
    });
  }

  function aplicar(nombre) {
    if (nombre) {
      localStorage.setItem(storageKey, nombre);
    } else {
      localStorage.removeItem(storageKey);
    }
    marcarActivo(nombre);
    if (typeof alCambiar === "function") alCambiar();
  }

  const btnNinguno = document.createElement("button");
  btnNinguno.type = "button";
  btnNinguno.classList.add("fondo-swatch");
  btnNinguno.style.background = "var(--verde-liceo)";
  btnNinguno.dataset.avatar = "";
  btnNinguno.title = "Usar la letra P (por defecto)";
  btnNinguno.addEventListener("click", () => aplicar(""));
  contenedor.appendChild(btnNinguno);

  Object.entries(AVATARES_PSICOLOGA_DISPONIBLES).forEach(([nombre, avatar]) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.classList.add("fondo-swatch");
    btn.style.backgroundImage = `url("${avatar.valor}")`;
    btn.dataset.avatar = nombre;
    btn.title = avatar.titulo;
    btn.addEventListener("click", () => aplicar(nombre));
    contenedor.appendChild(btn);
  });

  marcarActivo(localStorage.getItem(storageKey) || "");
}

/**
 * Muestra el aviso de apoyo de emergencia junto con un campo OPCIONAL para
 * dejar un número de WhatsApp/Telegram. Nunca se pide el nombre — es
 * voluntario, y solo aparece cuando ya se disparó una alerta real de riesgo.
 */
function mostrarApoyoEmergencia(apoyoDiv, socket, token, mensaje) {
  if (!apoyoDiv) return;
  apoyoDiv.innerHTML = "";
  apoyoDiv.hidden = false;

  const texto = document.createElement("p");
  texto.className = "apoyo-texto";
  texto.textContent = mensaje;
  apoyoDiv.appendChild(texto);

  // Si ya se dejó un contacto en esta sesión, no se vuelve a pedir.
  if (sessionStorage.getItem("contacto_emergencia_enviado_" + token)) return;

  const form = document.createElement("form");
  form.className = "form-contacto-emergencia";
  form.innerHTML = `
    <p class="contacto-pregunta">¿Quieres dejarnos un número para contactarte directamente? Es opcional.</p>
    <div class="contacto-campos">
      <select name="plataforma">
        <option value="whatsapp">WhatsApp</option>
        <option value="telegram">Telegram</option>
      </select>
      <input type="tel" name="telefono" placeholder="Tu número" autocomplete="tel" maxlength="20">
      <button type="submit">Enviar</button>
    </div>
  `;
  apoyoDiv.appendChild(form);

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const telefono = form.telefono.value.trim();
    if (!telefono) return;
    socket.emit("guardar_contacto_emergencia", {
      token,
      telefono,
      plataforma: form.plataforma.value,
    });
    sessionStorage.setItem("contacto_emergencia_enviado_" + token, "1");
    form.remove();
  });
}
