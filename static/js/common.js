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

const GRUPOS_ESCALONADOS = ".tarjetas, .opciones, .redes-grid, .video-landing-grid";

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
  // Fondo tipo WhatsApp: beige con un patrón de puntitos verdes.
  whatsapp: { tipo: "color", valor: "radial-gradient(rgba(18, 46, 27, 0.09) 1.3px, transparent 1.5px) 0 0 / 18px 18px, #efeae2", titulo: "WhatsApp" },
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

function crearSelectorFondo(contenedorId, mensajesEl, storageKey, porDefecto = "claro") {
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

  aplicar(localStorage.getItem(storageKey) || porDefecto);
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

  // Líneas de ayuda que se pueden llamar con un toque desde el celular.
  const lineas = document.createElement("div");
  lineas.className = "apoyo-lineas";
  [
    ["tel:150", "Llamar al 150", "Teléfono de la Esperanza, gratis y anónimo"],
    ["tel:911", "Llamar al 911", "Emergencias"],
  ].forEach(([href, titulo, detalle]) => {
    const enlace = document.createElement("a");
    enlace.href = href;
    enlace.className = "apoyo-linea";
    const fuerte = document.createElement("strong");
    fuerte.textContent = titulo;
    const chico = document.createElement("small");
    chico.textContent = detalle;
    enlace.append(fuerte, chico);
    lineas.appendChild(enlace);
  });
  apoyoDiv.appendChild(lineas);

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

// Texto que se transforma de una palabra a otra (portada). Lee las
// palabras de data-palabras ("A|B|C") y cada cuánto cambian de
// data-intervalo (ms). El cruce dura MORPH_DURACION; el resto del
// intervalo la palabra se queda quieta.
const MORPH_DURACION = 1000;

function activarMorphTexto() {
  document.querySelectorAll(".morph").forEach((caja) => {
    const palabras = (caja.dataset.palabras || "").split("|").filter(Boolean);
    const [texto1, texto2] = caja.querySelectorAll(".morph-texto");
    if (palabras.length < 2 || !texto1 || !texto2) return;
    const intervalo = Math.max(Number(caja.dataset.intervalo) || 2500, MORPH_DURACION + 300);
    let indice = 0;

    if (SIN_MOVIMIENTO) {
      // Sin animaciones: solo cambia la palabra, sin desenfoque.
      texto2.style.opacity = "0";
      setInterval(() => {
        indice = (indice + 1) % palabras.length;
        texto1.textContent = palabras[indice];
      }, intervalo);
      return;
    }

    function pintar(fraccion) {
      // texto2 = palabra que entra, texto1 = palabra que sale.
      texto2.style.filter = `blur(${Math.min(8 / fraccion - 8, 100)}px)`;
      texto2.style.opacity = `${Math.pow(fraccion, 0.4) * 100}%`;
      const inversa = 1 - fraccion;
      texto1.style.filter = `blur(${Math.min(8 / inversa - 8, 100)}px)`;
      texto1.style.opacity = `${Math.pow(inversa, 0.4) * 100}%`;
    }

    function quieta() {
      texto2.style.filter = "none";
      texto2.style.opacity = "100%";
      texto1.style.filter = "none";
      texto1.style.opacity = "0%";
    }

    texto1.textContent = palabras[0];
    texto2.textContent = palabras[0];
    quieta();
    let inicioCiclo = performance.now();
    let cruzando = false;

    function cuadro(ahora) {
      const transcurrido = ahora - inicioCiclo;
      const pausa = intervalo - MORPH_DURACION;
      if (transcurrido >= intervalo) {
        indice = (indice + 1) % palabras.length;
        inicioCiclo = ahora;
        cruzando = false;
        quieta();
      } else if (transcurrido >= pausa) {
        if (!cruzando) {
          cruzando = true;
          texto1.textContent = palabras[indice];
          texto2.textContent = palabras[(indice + 1) % palabras.length];
        }
        pintar(Math.max((transcurrido - pausa) / MORPH_DURACION, 0.0001));
      }
      requestAnimationFrame(cuadro);
    }
    requestAnimationFrame(cuadro);
  });
}

document.addEventListener("DOMContentLoaded", activarMorphTexto);

// Carrusel en perspectiva. La imagen activa va al centro y de frente; las
// demás se inclinan hacia atrás a los lados. Se cambia con las flechas, los
// puntos, el teclado, deslizando el dedo o tocando una imagen de los lados.
// Tocar la imagen del centro abre su sección.
function activarCarruselPerspectiva() {
  document.querySelectorAll("[data-perspectiva]").forEach((escena) => {
    const seccion = escena.closest(".carrusel-perspectiva") || escena.parentElement;
    const slides = Array.from(escena.querySelectorAll(".perspectiva-slide"));
    const n = slides.length;
    if (!n) return;
    const puntosCaja = seccion.querySelector("[data-perspectiva-puntos]");
    let activo = Math.min(Number(escena.dataset.activo) || 0, n - 1);

    const puntos = slides.map((slide, i) => {
      const punto = document.createElement("button");
      punto.type = "button";
      punto.className = "perspectiva-punto";
      punto.setAttribute("aria-label", `Ir a ${slide.querySelector(".perspectiva-titulo").textContent}`);
      punto.addEventListener("click", () => ir(i));
      if (puntosCaja) puntosCaja.appendChild(punto);
      return punto;
    });

    function pintar() {
      const ancho = slides[0].offsetWidth;
      slides.forEach((slide, i) => {
        // Distancia más corta, dando la vuelta (el carrusel es circular).
        let d = i - activo;
        if (d > n / 2) d -= n;
        if (d < -n / 2) d += n;
        const lado = Math.sign(d);
        const lejos = Math.abs(d);
        const x = lejos ? lado * (ancho * 0.62 + (lejos - 1) * ancho * 0.32) : 0;
        const giro = -lado * Math.min(lejos, 1) * 42;
        const escala = lejos ? Math.max(0.82 - (lejos - 1) * 0.1, 0.5) : 1;
        slide.style.transform = `translateX(${x}px) translateZ(${-lejos * 120}px) rotateY(${giro}deg) scale(${escala})`;
        slide.style.zIndex = String(n - lejos);
        slide.style.opacity = lejos > 2 ? "0" : String(1 - lejos * 0.18);
        slide.style.filter = lejos ? `brightness(${1 - lejos * 0.18})` : "none";
        slide.style.pointerEvents = lejos > 2 ? "none" : "auto";
        slide.classList.toggle("activo", lejos === 0);
        slide.tabIndex = lejos === 0 ? 0 : -1;
        puntos[i].classList.toggle("activo", lejos === 0);
        puntos[i].setAttribute("aria-current", lejos === 0 ? "true" : "false");
      });
    }

    function ir(i) {
      activo = (i + n) % n;
      pintar();
    }

    seccion.querySelector("[data-perspectiva-anterior]")?.addEventListener("click", () => ir(activo - 1));
    seccion.querySelector("[data-perspectiva-siguiente]")?.addEventListener("click", () => ir(activo + 1));
    seccion.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") { e.preventDefault(); ir(activo - 1); }
      if (e.key === "ArrowRight") { e.preventDefault(); ir(activo + 1); }
    });

    // Tocar una imagen de los lados la trae al centro (no abre el enlace).
    slides.forEach((slide, i) => {
      slide.addEventListener("click", (e) => {
        if (i !== activo) { e.preventDefault(); ir(i); }
      });
    });

    // Deslizar con el dedo o arrastrar con el mouse.
    let inicioX = null;
    let movido = false;
    escena.addEventListener("pointerdown", (e) => { inicioX = e.clientX; movido = false; });
    escena.addEventListener("pointermove", (e) => {
      if (inicioX === null) return;
      if (Math.abs(e.clientX - inicioX) > 40) {
        ir(activo + (e.clientX < inicioX ? 1 : -1));
        inicioX = e.clientX;
        movido = true;
      }
    });
    const soltar = () => { inicioX = null; };
    escena.addEventListener("pointerup", soltar);
    escena.addEventListener("pointercancel", soltar);
    escena.addEventListener("pointerleave", soltar);
    escena.addEventListener("click", (e) => {
      if (movido) { e.preventDefault(); e.stopPropagation(); movido = false; }
    }, { capture: true });

    pintar();
    window.addEventListener("resize", pintar);
  });
}

document.addEventListener("DOMContentLoaded", activarCarruselPerspectiva);

// Buscador de la portada: botón de lupa en el menú o Ctrl+K / ⌘K.
// Busca en el índice que manda el servidor (secciones, artículos,
// técnicas y autoevaluaciones) sin importar mayúsculas ni tildes.
function normalizarBusqueda(texto) {
  return (texto || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}

function activarBuscador() {
  const dialogo = document.getElementById("buscador");
  const datos = document.getElementById("indice-busqueda");
  const boton = document.getElementById("nav-buscar");
  if (!dialogo || !datos || typeof dialogo.showModal !== "function") {
    if (boton) boton.hidden = true;
    return;
  }
  const entrada = document.getElementById("buscador-input");
  const lista = document.getElementById("buscador-resultados");
  const indice = JSON.parse(datos.textContent).map((item) => ({
    ...item,
    nombreNorm: normalizarBusqueda(item.nombre),
    todoNorm: normalizarBusqueda(`${item.nombre} ${item.meta} ${item.tipo} ${item.palabras}`),
  }));
  let opciones = [];
  let seleccion = 0;

  function buscar(consulta) {
    const terminos = normalizarBusqueda(consulta).split(/\s+/).filter(Boolean);
    if (!terminos.length) return indice.filter((i) => i.tipo === "Sección").slice(0, 8);
    return indice
      .filter((i) => terminos.every((t) => i.todoNorm.includes(t)))
      .map((i) => {
        let puntos = 0;
        terminos.forEach((t) => {
          if (i.nombreNorm.startsWith(t)) puntos += 3;
          else if (i.nombreNorm.includes(t)) puntos += 2;
          else puntos += 1;
        });
        if (i.tipo === "Sección") puntos += 0.5;
        return { i, puntos };
      })
      .sort((a, b) => b.puntos - a.puntos)
      .slice(0, 12)
      .map((r) => r.i);
  }

  // Pinta el nombre resaltando el primer término encontrado, sin innerHTML.
  function nombreResaltado(nombre, consulta) {
    const span = document.createElement("span");
    span.className = "buscador-nombre";
    const termino = normalizarBusqueda(consulta).trim().split(/\s+/)[0];
    const pos = termino ? normalizarBusqueda(nombre).indexOf(termino) : -1;
    if (pos < 0) {
      span.textContent = nombre;
      return span;
    }
    const marca = document.createElement("mark");
    marca.textContent = nombre.slice(pos, pos + termino.length);
    span.append(nombre.slice(0, pos), marca, nombre.slice(pos + termino.length));
    return span;
  }

  function pintar() {
    const consulta = entrada.value;
    const resultados = buscar(consulta);
    lista.replaceChildren();
    opciones = [];
    seleccion = 0;
    if (!resultados.length) {
      const vacio = document.createElement("li");
      vacio.className = "buscador-vacio";
      vacio.textContent = "No encontramos nada con esa palabra. Prueba con otra, o habla con la psicóloga.";
      lista.append(vacio);
      entrada.removeAttribute("aria-activedescendant");
      return;
    }
    const titulo = document.createElement("li");
    titulo.className = "buscador-grupo";
    titulo.setAttribute("role", "presentation");
    titulo.textContent = consulta.trim() ? "Resultados" : "Sugerencias";
    lista.append(titulo);
    resultados.forEach((item, n) => {
      const li = document.createElement("li");
      li.className = "buscador-opcion";
      li.id = `buscador-op-${n}`;
      li.setAttribute("role", "option");
      const enlace = document.createElement("a");
      enlace.href = item.url;
      enlace.tabIndex = -1;
      const texto = document.createElement("span");
      texto.className = "buscador-texto";
      const meta = document.createElement("span");
      meta.className = "buscador-meta";
      meta.textContent = item.meta;
      texto.append(nombreResaltado(item.nombre, consulta), meta);
      const tipo = document.createElement("span");
      tipo.className = "buscador-tipo";
      tipo.textContent = item.tipo;
      enlace.append(texto, tipo);
      enlace.addEventListener("click", () => dialogo.close());
      li.addEventListener("pointermove", () => marcar(n));
      li.append(enlace);
      lista.append(li);
      opciones.push(li);
    });
    marcar(0);
  }

  function marcar(n) {
    if (!opciones.length) return;
    seleccion = (n + opciones.length) % opciones.length;
    opciones.forEach((li, i) => li.setAttribute("aria-selected", i === seleccion ? "true" : "false"));
    entrada.setAttribute("aria-activedescendant", opciones[seleccion].id);
    opciones[seleccion].scrollIntoView({ block: "nearest" });
  }

  function abrir() {
    if (dialogo.open) return;
    entrada.value = "";
    pintar();
    dialogo.showModal();
    entrada.focus();
  }

  entrada.addEventListener("input", pintar);
  entrada.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") { e.preventDefault(); marcar(seleccion + 1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); marcar(seleccion - 1); }
    else if (e.key === "Enter" && opciones.length) {
      e.preventDefault();
      opciones[seleccion].querySelector("a").click();
    }
  });
  // Clic fuera de la caja (en el fondo oscuro) cierra la ventana.
  dialogo.addEventListener("click", (e) => { if (e.target === dialogo) dialogo.close(); });
  if (boton) boton.addEventListener("click", abrir);
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      if (dialogo.open) dialogo.close();
      else abrir();
    }
  });
}

document.addEventListener("DOMContentLoaded", activarBuscador);

// Barra de íconos de abajo: un globito que se desliza entre íconos al
// pasar el mouse (o al moverse con Tab), y un puntito verde en la
// psicóloga cuando tiene su panel abierto.
function activarDock() {
  const dock = document.getElementById("dock");
  if (!dock) return;
  const tooltip = dock.querySelector(".dock-tooltip");
  const texto = tooltip.querySelector(".dock-tooltip-texto");
  const insignia = dock.querySelector(".dock-insignia");
  let psicologaConectada = false;

  function mostrar(item) {
    texto.replaceChildren(item.dataset.etiqueta);
    if (item.dataset.insignia === "psicologa" && psicologaConectada) {
      const enLinea = document.createElement("span");
      enLinea.className = "dock-en-linea";
      enLinea.textContent = "En línea";
      texto.append(enLinea);
    }
    if (item.dataset.atajo) {
      item.dataset.atajo.split("|").forEach((tecla) => {
        const kbd = document.createElement("kbd");
        kbd.textContent = /Mac|iPhone|iPad/.test(navigator.platform) && tecla === "Ctrl" ? "⌘" : tecla;
        texto.append(kbd);
      });
    }
    // Si el globito ya estaba visible, se desliza; si no, aparece en su lugar.
    tooltip.classList.toggle("deslizando", tooltip.classList.contains("visible"));
    const caja = dock.getBoundingClientRect();
    const r = item.getBoundingClientRect();
    tooltip.style.left = `${r.left - caja.left + r.width / 2}px`;
    tooltip.classList.add("visible");
  }

  function ocultar() {
    tooltip.classList.remove("visible", "deslizando");
  }

  dock.querySelectorAll(".dock-item").forEach((item) => {
    item.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") mostrar(item); });
    item.addEventListener("focus", () => { if (item.matches(":focus-visible")) mostrar(item); });
    item.addEventListener("blur", ocultar);
  });
  dock.addEventListener("pointerleave", ocultar);

  const buscar = document.getElementById("dock-buscar");
  const botonBuscarMenu = document.getElementById("nav-buscar");
  if (buscar && botonBuscarMenu && !botonBuscarMenu.hidden) {
    buscar.addEventListener("click", () => botonBuscarMenu.click());
  } else if (buscar) {
    buscar.hidden = true;
  }

  async function revisarPsicologa() {
    try {
      const r = await fetch("/api/estado-psicologa", { cache: "no-store" });
      if (!r.ok) return;
      psicologaConectada = Boolean((await r.json()).conectada);
      if (insignia) insignia.hidden = !psicologaConectada;
    } catch (e) {
      // Sin conexión: simplemente no se muestra el puntito.
    }
  }
  revisarPsicologa();
  setInterval(revisarPsicologa, 60000);
}

document.addEventListener("DOMContentLoaded", activarDock);

// "Dynamic Island" de música en la portada: idle → expandida (carga el
// reproductor de Spotify) → mini (sigue sonando, recortado) → cerrar
// (quita el reproductor y vuelve a idle).
function activarIslaMusica(playlistId) {
  const isla = document.getElementById("isla-musica");
  if (!isla) return;
  const barra = document.getElementById("isla-boton");
  const reproductor = isla.querySelector(".isla-reproductor");
  const lista = playlistId || (typeof SPOTIFY_PLAYLIST_LOFI !== "undefined" ? SPOTIFY_PLAYLIST_LOFI : "37i9dQZF1DWWQRwui0ExPn");

  function cambiarVista(vista) {
    isla.dataset.vista = vista;
    barra.setAttribute("aria-expanded", vista === "expandida" ? "true" : "false");
    if (vista === "expandida" && !reproductor.firstChild) {
      const iframe = document.createElement("iframe");
      iframe.src = `https://open.spotify.com/embed/playlist/${lista}?utm_source=generator&theme=0`;
      iframe.title = "Reproductor de Spotify: música relajante";
      iframe.allow = "autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture";
      iframe.loading = "lazy";
      reproductor.append(iframe);
    }
    if (vista === "idle") reproductor.replaceChildren();
  }

  barra.addEventListener("click", () => cambiarVista("expandida"));
  isla.querySelector(".isla-minimizar").addEventListener("click", () => {
    cambiarVista("mini");
    barra.focus();
  });
  isla.querySelectorAll(".isla-cerrar").forEach((boton) => {
    boton.addEventListener("click", () => {
      cambiarVista("idle");
      barra.focus();
    });
  });
  isla.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && isla.dataset.vista === "expandida") {
      cambiarVista("mini");
      barra.focus();
    }
  });
}

// Texto con letras que ruedan (lema del Liceo). Parte el texto en letras
// con dos copias cada una; el CSS hace el movimiento al pasar el mouse.
// En pantallas táctiles rueda una vez sola al aparecer en pantalla.
const ROLL_RETRASO = 28; // ms entre una letra y la siguiente

function activarTextoRodante() {
  document.querySelectorAll("[data-roll]").forEach((el) => {
    const textoCompleto = el.textContent.trim();
    const letras = Array.from(textoCompleto);
    const desdeCentro = el.hasAttribute("data-roll-centro");
    const centro = (letras.length - 1) / 2;
    el.setAttribute("aria-label", textoCompleto);
    // Las letras se agrupan por palabra para que el texto solo se parta
    // entre palabras completas, nunca a mitad de una.
    const piezas = [];
    let palabra = null;
    letras.forEach((letra, i) => {
      if (letra === " ") {
        palabra = null;
        const espacio = document.createElement("span");
        espacio.className = "roll-espacio";
        espacio.setAttribute("aria-hidden", "true");
        piezas.push(espacio);
        return;
      }
      if (!palabra) {
        palabra = document.createElement("span");
        palabra.className = "roll-palabra";
        palabra.setAttribute("aria-hidden", "true");
        piezas.push(palabra);
      }
      const caja = document.createElement("span");
      caja.className = "roll-letra";
      const orden = desdeCentro ? Math.abs(i - centro) : i;
      caja.style.setProperty("--retraso", `${Math.round(orden * ROLL_RETRASO)}ms`);
      const arriba = document.createElement("span");
      const abajo = document.createElement("span");
      arriba.textContent = letra;
      abajo.textContent = letra;
      caja.append(arriba, abajo);
      palabra.append(caja);
    });
    el.replaceChildren(...piezas);
  });

  const tactil = window.matchMedia("(hover: none)").matches;
  if (!tactil || SIN_MOVIMIENTO || !("IntersectionObserver" in window)) return;
  const observador = new IntersectionObserver((entradas) => {
    entradas.forEach((entrada) => {
      if (!entrada.isIntersecting) return;
      const el = entrada.target;
      observador.unobserve(el);
      setTimeout(() => el.classList.add("rodando"), 300);
    });
  }, { threshold: 0.6 });
  document.querySelectorAll("[data-roll]").forEach((el) => observador.observe(el));
}

document.addEventListener("DOMContentLoaded", activarTextoRodante);

// Línea de fondo de la portada: muestra del 50 % al 100 % del trazo
// según cuánto se ha bajado por la página.
function activarLineaFondo() {
  const trazo = document.getElementById("linea-fondo-trazo");
  if (!trazo || SIN_MOVIMIENTO) return;
  let pendiente = false;

  function actualizar() {
    pendiente = false;
    const recorrido = document.documentElement.scrollHeight - window.innerHeight;
    const progreso = recorrido > 0 ? Math.min(Math.max(window.scrollY / recorrido, 0), 1) : 1;
    const visible = 0.5 + progreso * 0.5;
    trazo.style.strokeDashoffset = String(1 - visible);
  }

  window.addEventListener("scroll", () => {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(actualizar);
  }, { passive: true });
  window.addEventListener("resize", actualizar);
  actualizar();
}

document.addEventListener("DOMContentLoaded", activarLineaFondo);

// Textos de los cuadros que entran palabra por palabra al aparecer en
// pantalla. Solo se aplica a párrafos de texto simple (sin negritas ni
// enlaces adentro) para no romper su contenido.
const STAGGER_SELECTOR = [
  ".tarjeta p", ".opcion p", ".historia p",
  ".seccion h2:not(.sr-only)", ".seccion-subtitulo", ".cta-elegir-subtitulo",
  ".recurso-titulo", ".recurso-resumen",
].join(", ");

function activarTextoEscalonado() {
  if (SIN_MOVIMIENTO || !("IntersectionObserver" in window)) return;
  const parrafos = Array.from(document.querySelectorAll(STAGGER_SELECTOR))
    .filter((p) => p.children.length === 0 && p.textContent.trim());
  if (!parrafos.length) return;

  parrafos.forEach((p) => {
    const palabras = p.textContent.trim().split(/\s+/);
    const piezas = [];
    palabras.forEach((palabra, i) => {
      const span = document.createElement("span");
      span.className = "stagger-palabra";
      span.style.setProperty("--i", i);
      span.textContent = palabra;
      piezas.push(span);
      if (i < palabras.length - 1) piezas.push(" ");
    });
    p.replaceChildren(...piezas);
  });

  const observador = new IntersectionObserver((entradas) => {
    entradas.forEach((entrada) => {
      if (!entrada.isIntersecting) return;
      entrada.target.classList.add("stagger-visible");
      observador.unobserve(entrada.target);
    });
  }, { threshold: 0.3 });
  parrafos.forEach((p) => observador.observe(p));
}

document.addEventListener("DOMContentLoaded", activarTextoEscalonado);

// Libro de "¿Cómo podemos ayudarte?": botones ← →, flechas del teclado
// y deslizar con el dedo. Solo la página abierta se puede enfocar
// (las demás quedan "inert") para que el teclado no salte a páginas ocultas.
function activarLibro() {
  document.querySelectorAll("[data-libro]").forEach((libro) => {
    const paginas = Array.from(libro.querySelectorAll(".libro-pagina"));
    const anterior = libro.querySelector("[data-libro-anterior]");
    const siguiente = libro.querySelector("[data-libro-siguiente]");
    const contador = libro.querySelector("[data-libro-contador]");
    let actual = 0;

    function pintar() {
      paginas.forEach((pagina, i) => {
        pagina.style.setProperty("--z", String(paginas.length - i));
        pagina.classList.toggle("volteada", i < actual);
        pagina.inert = i !== actual;
      });
      contador.textContent = `${actual + 1} / ${paginas.length}`;
      anterior.disabled = actual === 0;
      siguiente.disabled = actual === paginas.length - 1;
    }

    function ir(n) {
      const destino = Math.min(Math.max(n, 0), paginas.length - 1);
      if (destino === actual) return;
      actual = destino;
      pintar();
    }

    anterior.addEventListener("click", () => ir(actual - 1));
    siguiente.addEventListener("click", () => ir(actual + 1));
    libro.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") { e.preventDefault(); ir(actual + 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); ir(actual - 1); }
    });

    // Deslizar con el dedo sobre las páginas.
    const zona = libro.querySelector(".libro-paginas");
    let inicioX = null;
    zona.addEventListener("pointerdown", (e) => { inicioX = e.clientX; });
    zona.addEventListener("pointerup", (e) => {
      if (inicioX === null) return;
      const dx = e.clientX - inicioX;
      inicioX = null;
      if (Math.abs(dx) > 40) ir(actual + (dx < 0 ? 1 : -1));
    });
    zona.style.touchAction = "pan-y";

    pintar();
  });
}

document.addEventListener("DOMContentLoaded", activarLibro);

// Cuadros "cyber" de la portada: les agrega los adornos (esquinas,
// brillo, línea de escaneo, partículas) y, con mouse, los inclina hacia
// donde apunta el cursor (hasta 10° arriba/abajo y 8° a los lados).
const CYBER_SELECTOR = ".seccion :is(.tarjeta, .opcion, .playlist-card)";

// Los demás cuadros de todas las páginas reciben los mismos 4 adornos
// (esquinas, brillo, escaneo y partículas), sin la inclinación 3D.
const ADORNOS_SELECTOR = [
  ".recurso-card", ".contador", ".bento-cuadro", ".pasos-caja", ".emergencia",
  ".test-grande", ".test-pregunta", ".test-resultado",
  ".herramienta-completa", ".categoria-sintomas", ".articulo-completo", ".glosario-item",
  ".racha-card", ".stat-card", ".login-card", ".muro-card", ".resena-card",
  ".playlist-card", ".amigo-card", ".futuro-panel",
].join(", ");

function agregarAdornos(cuadro) {
  if (cuadro.querySelector(":scope > .cyber-deco")) return;
  const deco = document.createElement("span");
  deco.className = "cyber-deco";
  deco.setAttribute("aria-hidden", "true");
  deco.innerHTML =
    '<span class="cyber-brillo"></span>' +
    '<span class="cyber-esquinas"><i></i><i></i><i></i><i></i></span>' +
    '<span class="cyber-scan"></span>' +
    '<span class="cyber-particulas"><i></i><i></i><i></i><i></i><i></i><i></i></span>';
  cuadro.prepend(deco);
}

function activarAdornosEnTodo() {
  document.querySelectorAll(ADORNOS_SELECTOR).forEach((cuadro) => {
    if (cuadro.matches(CYBER_SELECTOR)) return;   // esos ya los maneja activarCuadrosCyber
    cuadro.classList.add("con-adornos");
    agregarAdornos(cuadro);
  });
}

document.addEventListener("DOMContentLoaded", activarAdornosEnTodo);

function activarCuadrosCyber() {
  const cuadros = document.querySelectorAll(CYBER_SELECTOR);
  cuadros.forEach(agregarAdornos);

  const conMouse = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (!conMouse || SIN_MOVIMIENTO) return;
  cuadros.forEach((cuadro) => {
    cuadro.addEventListener("pointermove", (e) => {
      const r = cuadro.getBoundingClientRect();
      const fx = (e.clientX - r.left) / r.width;
      const fy = (e.clientY - r.top) / r.height;
      cuadro.classList.add("cyber-activo");
      cuadro.style.transform =
        `perspective(800px) rotateX(${((0.5 - fy) * 20).toFixed(2)}deg) rotateY(${((fx - 0.5) * 16).toFixed(2)}deg)`;
    });
    cuadro.addEventListener("pointerleave", () => {
      cuadro.classList.remove("cyber-activo");
      cuadro.style.transform = "";
    });
  });
}

document.addEventListener("DOMContentLoaded", activarCuadrosCyber);

// Estela de tinta líquida detrás del cursor (splash_cursor.js). Solo en
// computadoras con mouse y si no se pidió reducir el movimiento: en
// celular gastaría batería y se activaría al hacer scroll con el dedo.
function cargarEstelaCursor() {
  const conMouse = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (!conMouse || SIN_MOVIMIENTO || document.getElementById("script-estela")) return;
  const script = document.createElement("script");
  script.id = "script-estela";
  script.src = "/static/js/splash_cursor.js";
  script.defer = true;
  document.head.appendChild(script);
}

document.addEventListener("DOMContentLoaded", cargarEstelaCursor);

// Imágenes de la portada que "se voltean" al pasar el mouse: se envuelven
// en un contenedor que hereda el margen, el ancho máximo y las esquinas
// de la imagen, y se les agrega un letrero con su texto alternativo.
const VOLTEO_SELECTOR = ".banner-seccion-img, .prevencion-banner-img, .hero-banner-img";

function activarImagenesVolteo() {
  document.querySelectorAll(VOLTEO_SELECTOR).forEach((img) => {
    if (img.parentElement.classList.contains("img-volteo")) return;
    const estilo = getComputedStyle(img);
    const caja = document.createElement("span");
    caja.className = "img-volteo";
    // Centrada como la imagen original (los lados quedan en auto).
    caja.style.margin = `${estilo.marginTop} auto ${estilo.marginBottom}`;
    caja.style.maxWidth = estilo.maxWidth;
    caja.style.borderRadius = estilo.borderRadius;
    img.style.margin = "0";
    img.parentNode.insertBefore(caja, img);
    caja.appendChild(img);

    const texto = document.createElement("span");
    texto.className = "img-volteo-texto";
    texto.setAttribute("aria-hidden", "true");
    // "Muro interactivo — Describe tu experiencia": la primera parte va
    // grande y lo que sigue al guion, más pequeño debajo.
    const [titulo, ...resto] = img.alt.split(" — ");
    texto.append(titulo);
    if (resto.length) {
      const detalle = document.createElement("small");
      detalle.textContent = resto.join(" · ");
      texto.append(detalle);
    }
    caja.appendChild(texto);
  });
}

document.addEventListener("DOMContentLoaded", activarImagenesVolteo);

// "← Volver": si llegaste desde otra página de este sitio, regresa a ella
// como el botón Atrás del navegador, que te deja en la misma parte donde
// estabas (en vez de mandarte al principio de la portada).
function activarVolverSinPerderLugar() {
  let vieneDeAqui = false;
  try { vieneDeAqui = new URL(document.referrer).origin === location.origin; } catch (e) {}
  if (!vieneDeAqui || history.length < 2) return;
  document.querySelectorAll("a.volver").forEach((enlace) => {
    enlace.addEventListener("click", (evento) => {
      evento.preventDefault();
      history.back();
    });
  });
}

document.addEventListener("DOMContentLoaded", activarVolverSinPerderLugar);

// Videos que se cargan solo al tocarlos: así una página con muchos videos
// (Herramientas, Infórmate) carga rápido, y el video se ve ahí mismo.
function activarVideosLigeros() {
  document.querySelectorAll(".video-ligero[data-video]").forEach((boton) => {
    boton.addEventListener("click", () => {
      const caja = document.createElement("div");
      caja.className = "video-reproduciendo";
      const iframe = document.createElement("iframe");
      iframe.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(boton.dataset.video)}?autoplay=1&rel=0`;
      iframe.title = boton.getAttribute("aria-label") || "Video";
      iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
      iframe.allowFullscreen = true;
      caja.appendChild(iframe);
      boton.replaceWith(caja);
    });
  });
}

document.addEventListener("DOMContentLoaded", activarVideosLigeros);

// Buscador de Infórmate: muestra solo los artículos que tienen la palabra
// escrita (en el título o en el texto), sin cambiar de página.
function activarFiltroArticulos() {
  const campo = document.querySelector("[data-filtro-articulos]");
  if (!campo) return;
  const aviso = document.querySelector("[data-filtro-vacio]");
  const normalizar = (texto) => texto.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  const articulos = Array.from(document.querySelectorAll(".articulo-completo"))
    .map((el) => ({ el, texto: normalizar(el.textContent) }));
  const secciones = document.querySelectorAll(".informate-categoria");

  campo.addEventListener("input", () => {
    const buscado = normalizar(campo.value.trim());
    let visibles = 0;
    articulos.forEach(({ el, texto }) => {
      const coincide = !buscado || texto.includes(buscado);
      el.hidden = !coincide;
      if (coincide) visibles += 1;
    });
    secciones.forEach((seccion) => {
      seccion.hidden = !seccion.querySelector(".articulo-completo:not([hidden])");
    });
    if (aviso) aviso.hidden = visibles > 0;
  });
}

document.addEventListener("DOMContentLoaded", activarFiltroArticulos);

// Al llegar con un enlace a una parte de la página (#efecto-halo), el
// navegador baja ahí antes de que todo termine de acomodarse y puede quedar
// en otro lugar. Cuando la página ya cargó, se vuelve a bajar al lugar correcto.
window.addEventListener("load", () => {
  if (!location.hash) return;
  let destino = null;
  try { destino = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (e) {}
  if (destino) destino.scrollIntoView({ block: "start" });
});

// Contadores de la portada: cuentan desde 0 hasta el número real cuando
// aparecen en pantalla (data-contar = número final, data-duracion = segundos).
function activarContadores() {
  const numeros = document.querySelectorAll("[data-contar]");
  if (!numeros.length) return;
  const formato = new Intl.NumberFormat("es-HN");
  const animar = (el) => {
    const final = Number(el.dataset.contar) || 0;
    const duracion = (Number(el.dataset.duracion) || 2) * 1000;
    const inicio = performance.now();
    const paso = (ahora) => {
      const avance = Math.min((ahora - inicio) / duracion, 1);
      const suave = 1 - Math.pow(1 - avance, 3);
      el.textContent = formato.format(Math.round(final * suave));
      if (avance < 1) requestAnimationFrame(paso);
    };
    requestAnimationFrame(paso);
  };
  if (SIN_MOVIMIENTO || !("IntersectionObserver" in window)) {
    numeros.forEach((el) => { el.textContent = formato.format(Number(el.dataset.contar) || 0); });
    return;
  }
  const observador = new IntersectionObserver((entradas) => {
    entradas.forEach((entrada) => {
      if (!entrada.isIntersecting) return;
      animar(entrada.target);
      observador.unobserve(entrada.target);
    });
  }, { threshold: 0.4 });
  numeros.forEach((el) => { el.textContent = "0"; observador.observe(el); });
}

document.addEventListener("DOMContentLoaded", activarContadores);


// Bienvenida de la portada: una portada con el escudo y "Bienvenido/a"
// dibujada en un canvas, que se disuelve con ruido (como arena, con borde
// dorado) según cuánto bajes, dejando ver el banner que está debajo.
function activarBienvenidaDisuelta() {
  const seccion = document.querySelector("[data-disolver]");
  if (!seccion || SIN_MOVIMIENTO) return;
  const lienzo = seccion.querySelector(".bienvenida-frente");
  const marco = seccion.querySelector(".bienvenida-marco");
  const ctx = lienzo.getContext("2d");
  if (!ctx) return;

  // Ruido suave (value noise de 3 capas) en baja resolución.
  const RW = 192, RH = 108;
  let semilla = 7;
  const azar = () => ((semilla = (semilla * 16807) % 2147483647) / 2147483647);
  const ruido = new Float32Array(RW * RH);
  [[12, 0.55], [24, 0.3], [48, 0.15]].forEach(([celda, peso]) => {
    const gw = Math.ceil(RW / celda) + 2, gh = Math.ceil(RH / celda) + 2;
    const rejilla = Array.from({ length: gw * gh }, azar);
    for (let y = 0; y < RH; y++) {
      for (let x = 0; x < RW; x++) {
        const fx = x / celda, fy = y / celda;
        const x0 = Math.floor(fx), y0 = Math.floor(fy);
        const tx = fx - x0, ty = fy - y0;
        const sx = tx * tx * (3 - 2 * tx), sy = ty * ty * (3 - 2 * ty);
        const v = (i, j) => rejilla[(y0 + j) * gw + (x0 + i)];
        const a = v(0, 0) + (v(1, 0) - v(0, 0)) * sx;
        const b = v(0, 1) + (v(1, 1) - v(0, 1)) * sx;
        ruido[y * RW + x] += (a + (b - a) * sy) * peso;
      }
    }
  });

  const mascara = document.createElement("canvas");
  mascara.width = RW; mascara.height = RH;
  const mctx = mascara.getContext("2d");
  const datosMascara = mctx.createImageData(RW, RH);
  const brillo = document.createElement("canvas");
  brillo.width = RW; brillo.height = RH;
  const bctx = brillo.getContext("2d");
  const datosBrillo = bctx.createImageData(RW, RH);

  // La portada de bienvenida se dibuja una vez en otro canvas.
  const frente = document.createElement("canvas");
  const escudo = new Image();
  escudo.src = lienzo.dataset.escudo;

  function dibujarFrente() {
    const w = lienzo.width, h = lienzo.height;
    frente.width = w; frente.height = h;
    const f = frente.getContext("2d");
    const fondo = f.createRadialGradient(w / 2, h * 0.4, 0, w / 2, h * 0.4, w * 0.75);
    fondo.addColorStop(0, "#2e6b41");
    fondo.addColorStop(1, "#0d2415");
    f.fillStyle = fondo;
    f.fillRect(0, 0, w, h);
    const lado = h * 0.38;
    if (escudo.complete && escudo.naturalWidth) {
      // El escudo viene en un cuadro blanco: se recorta en círculo con borde dorado.
      const cx = w / 2, cy = h * 0.1 + lado / 2, r = lado / 2;
      f.save();
      f.beginPath();
      f.arc(cx, cy, r, 0, Math.PI * 2);
      f.clip();
      const escala = Math.max(lado / escudo.naturalWidth, lado / escudo.naturalHeight) * 1.08;
      const ancho = escudo.naturalWidth * escala, alto = escudo.naturalHeight * escala;
      f.drawImage(escudo, cx - ancho / 2, cy - alto / 2, ancho, alto);
      f.restore();
      f.strokeStyle = "#c9a227";
      f.lineWidth = Math.max(2, h * 0.008);
      f.beginPath();
      f.arc(cx, cy, r, 0, Math.PI * 2);
      f.stroke();
    }
    f.textAlign = "center";
    f.fillStyle = "#ffc83d";
    f.font = `700 ${Math.round(h * 0.13)}px Fraunces, Georgia, serif`;
    f.fillText("Bienvenido/a", w / 2, h * 0.66);
    f.fillStyle = "#ffffff";
    f.font = `600 ${Math.round(h * 0.06)}px Montserrat, Arial, sans-serif`;
    f.fillText("a No estamos solos LMH", w / 2, h * 0.79);
    f.fillStyle = "rgba(255, 255, 255, 0.75)";
    f.font = `500 ${Math.round(h * 0.042)}px Montserrat, Arial, sans-serif`;
    f.fillText("Un espacio seguro y anónimo del Liceo Militar de Honduras", w / 2, h * 0.88);
  }

  function medir() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    lienzo.width = Math.min(Math.round(marco.clientWidth * dpr), 2000);
    lienzo.height = Math.round(lienzo.width * 9 / 16);
    dibujarFrente();
    pintar();
  }

  function pintar() {
    const caja = seccion.getBoundingClientRect();
    const recorrido = caja.height - window.innerHeight;
    const avance = recorrido > 0 ? Math.min(Math.max(-caja.top / recorrido, 0), 1) : 0;
    const umbral = avance * 1.25 - 0.1;   // de -0.1 (entero) a 1.15 (desaparecido)
    const md = datosMascara.data, bd = datosBrillo.data;
    for (let i = 0; i < RW * RH; i++) {
      const d = ruido[i] - umbral;
      md[i * 4 + 3] = d <= 0 ? 0 : d >= 0.03 ? 255 : (d / 0.03) * 255;
      const g = d > -0.015 && d < 0.05 ? 1 - Math.abs(d - 0.015) / 0.035 : 0;
      bd[i * 4] = 255; bd[i * 4 + 1] = 200; bd[i * 4 + 2] = 61;
      bd[i * 4 + 3] = Math.max(g, 0) * 255;
    }
    mctx.putImageData(datosMascara, 0, 0);
    bctx.putImageData(datosBrillo, 0, 0);

    const w = lienzo.width, h = lienzo.height;
    ctx.globalCompositeOperation = "source-over";
    ctx.clearRect(0, 0, w, h);
    if (umbral < 1.1) {
      ctx.drawImage(frente, 0, 0);
      ctx.globalCompositeOperation = "destination-in";
      ctx.imageSmoothingEnabled = true;
      ctx.drawImage(mascara, 0, 0, w, h);
      ctx.globalCompositeOperation = "lighter";
      ctx.drawImage(brillo, 0, 0, w, h);
      ctx.globalCompositeOperation = "source-over";
    }
    seccion.classList.toggle("revelada", avance > 0.85);
  }

  let pendiente = false;
  window.addEventListener("scroll", () => {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(() => { pendiente = false; pintar(); });
  }, { passive: true });
  window.addEventListener("resize", medir);
  escudo.addEventListener("load", medir);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(medir);
  seccion.classList.add("lista");
  medir();
}

document.addEventListener("DOMContentLoaded", activarBienvenidaDisuelta);


// Teclado que escribe solo: arma las teclas, escribe cada frase letra por
// letra (con una velocidad al azar entre los dos números de
// data-velocidad, en milisegundos) y hunde la tecla de cada letra.
const FILAS_TECLADO = [
  ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
  ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
  ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ñ"],
  ["shift", "z", "x", "c", "v", "b", "n", "m", ",", "."],
  ["?", "espacio", ":", "/"],
];

function activarTecladoEscritor() {
  document.querySelectorAll("[data-teclado]").forEach((demo) => {
    const caja = demo.querySelector("[data-teclado-teclas]");
    const salida = demo.querySelector("[data-teclado-texto]");
    const frases = (demo.dataset.frases || "").split("|").filter(Boolean);
    const [lento, rapido] = (demo.dataset.velocidad || "50,130").split(",").map(Number);
    const teclas = {};

    FILAS_TECLADO.forEach((fila) => {
      const div = document.createElement("div");
      div.className = "teclado-fila";
      fila.forEach((clave) => {
        const tecla = document.createElement("span");
        tecla.className = "tecla";
        if (clave === "shift") { tecla.classList.add("tecla-ancha"); tecla.textContent = "⇧"; }
        else if (clave === "espacio") { tecla.classList.add("tecla-espacio"); tecla.textContent = ""; }
        else tecla.textContent = clave;
        teclas[clave] = tecla;
        div.appendChild(tecla);
      });
      caja.appendChild(div);
    });

    if (!frases.length) return;
    if (SIN_MOVIMIENTO) { salida.textContent = frases[0]; return; }

    // á → a, ¿ → ?, mayúscula → shift + letra.
    const teclaDe = (letra) => {
      if (letra === " ") return ["espacio"];
      if (letra === "¿") return ["?"];
      const base = letra === "ñ" || letra === "Ñ" ? letra : letra.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      const minus = base.toLowerCase();
      if (!teclas[minus]) return [];
      return base !== minus ? ["shift", minus] : [minus];
    };
    const presionar = (claves) => {
      claves.forEach((c) => {
        const t = teclas[c];
        if (!t) return;
        t.classList.add("presionada");
        setTimeout(() => t.classList.remove("presionada"), 110);
      });
    };
    const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
    const azar = () => lento + Math.random() * (rapido - lento);

    let visible = false;
    const observador = new IntersectionObserver((e) => { visible = e[0].isIntersecting; }, { threshold: 0.2 });
    observador.observe(demo);

    (async function bucle() {
      let i = 0;
      for (;;) {
        while (!visible || document.hidden) await esperar(400);
        const frase = frases[i % frases.length];
        for (const letra of frase) {
          presionar(teclaDe(letra));
          salida.textContent += letra;
          await esperar(azar());
        }
        await esperar(1800);
        while (salida.textContent.length) {
          salida.textContent = salida.textContent.slice(0, -1);
          await esperar(22);
        }
        await esperar(350);
        i += 1;
      }
    })();
  });
}

document.addEventListener("DOMContentLoaded", activarTecladoEscritor);


// Estante de libros: tocar un lomo muestra ese libro (pestañas accesibles,
// también con las flechas del teclado).
function activarEstanteLibros() {
  document.querySelectorAll("[data-estante]").forEach((estante) => {
    const lomos = Array.from(estante.querySelectorAll(".estante-lomo"));
    const elegir = (lomo, enfocar) => {
      lomos.forEach((l) => {
        const activo = l === lomo;
        l.classList.toggle("activo", activo);
        l.setAttribute("aria-selected", activo ? "true" : "false");
        l.tabIndex = activo ? 0 : -1;
        const panel = document.getElementById(l.getAttribute("aria-controls"));
        if (panel) panel.hidden = !activo;
      });
      if (enfocar) lomo.focus();
    };
    lomos.forEach((lomo, i) => {
      lomo.tabIndex = lomo.classList.contains("activo") ? 0 : -1;
      lomo.addEventListener("click", () => elegir(lomo, false));
      lomo.addEventListener("keydown", (e) => {
        if (e.key === "ArrowRight") { e.preventDefault(); elegir(lomos[(i + 1) % lomos.length], true); }
        if (e.key === "ArrowLeft") { e.preventDefault(); elegir(lomos[(i - 1 + lomos.length) % lomos.length], true); }
      });
    });
  });
}

document.addEventListener("DOMContentLoaded", activarEstanteLibros);


// Marquesina: el foco sigue al mouse y las palabras cercanas se iluminan
// y se acercan un poco a él (efecto imán).
function activarMarquesina() {
  document.querySelectorAll("[data-marquesina]").forEach((marq) => {
    if (SIN_MOVIMIENTO) return;
    const items = marq.querySelectorAll(".marquesina-item");
    marq.addEventListener("pointermove", (e) => {
      const caja = marq.getBoundingClientRect();
      marq.style.setProperty("--fx", `${e.clientX - caja.left}px`);
      marq.style.setProperty("--fy", `${e.clientY - caja.top}px`);
      items.forEach((item) => {
        const r = item.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2);
        const dy = e.clientY - (r.top + r.height / 2);
        const dist = Math.hypot(dx, dy);
        if (dist < 130) {
          const fuerza = (1 - dist / 130) * 0.35;
          item.style.setProperty("--mx", `${dx * fuerza}px`);
          item.style.setProperty("--my", `${dy * fuerza}px`);
          item.classList.toggle("cerca", dist < 70);
        } else {
          item.style.removeProperty("--mx");
          item.style.removeProperty("--my");
          item.classList.remove("cerca");
        }
      });
    });
    marq.addEventListener("pointerleave", () => {
      marq.style.setProperty("--fx", "-200px");
      items.forEach((item) => {
        item.style.removeProperty("--mx");
        item.style.removeProperty("--my");
        item.classList.remove("cerca");
      });
    });
  });
}

document.addEventListener("DOMContentLoaded", activarMarquesina);

// Mural de psicología: cada cuadro tiene su pequeña actividad.
const ANIMO_SUGERENCIAS = {
  ansiedad: ["Prueba la respiración 4-4-4-4: cuatro lados de 4 segundos. Baja los nervios en un minuto.", "ansiedad-respiracion"],
  enojo: ["Usa el semáforo: alto (detente), piensa (¿qué siento?), actúa (elige qué hacer).", "enojo"],
  tristeza: ["Da un paso pequeño hoy: algo sencillo que te haga bien, aunque no tengas ganas.", "tristeza"],
  dormir: ["Esta noche prueba una rutina antes de dormir: sin pantalla 30 minutos antes.", "dormir"],
  bien: ["¡Qué bueno! Hoy puedes anotar tres cosas buenas que te pasaron, para recordarlas.", "tristeza"],
};
const MITOS = [
  ["Ir al psicólogo es solo para personas \"locas\".", "mito", "Cualquier persona puede ir: igual que vas al médico para cuidar tu cuerpo, el psicólogo ayuda a cuidar tu mente."],
  ["Llorar es señal de debilidad.", "mito", "Llorar es una forma natural de soltar emociones. Lo hacen personas de todas las edades y es sano."],
  ["En la adolescencia el cerebro cambia mucho con lo que practicas.", "realidad", "Se llama neuroplasticidad: en esta etapa es muy fuerte, por eso los hábitos que entrenas hoy cuentan."],
  ["Preguntarle a alguien si piensa en suicidarse le da la idea.", "mito", "Preguntar con cariño no da la idea; al contrario, abre la puerta para que la persona pida ayuda."],
  ["Moverte un rato puede ayudar a bajar el estrés.", "realidad", "La actividad física ayuda al cuerpo a gastar la energía del estrés y mejora el ánimo."],
  ["Si alguien está triste, solo necesita \"echarle ganas\".", "mito", "La tristeza profunda no se quita con fuerza de voluntad; necesita apoyo, comprensión y a veces ayuda profesional."],
];
const FRASES_MURAL = [
  "Lo que sientes es válido, aunque nadie más lo vea.",
  "Pedir ayuda también es ser valiente.",
  "No tienes que resolverlo todo hoy: un paso a la vez.",
  "Un mal día no es una mala vida.",
  "Tu valor no depende de una nota.",
  "Está bien descansar. Descansar no es rendirse.",
];

function activarMural() {
  const mural = document.querySelector(".bento");
  if (!mural) return;

  // Brillo que sigue al mouse dentro de cada cuadro.
  mural.querySelectorAll(".bento-cuadro").forEach((cuadro) => {
    cuadro.addEventListener("pointermove", (e) => {
      const r = cuadro.getBoundingClientRect();
      cuadro.style.setProperty("--bx", `${e.clientX - r.left}px`);
      cuadro.style.setProperty("--by", `${e.clientY - r.top}px`);
    });
  });

  // Respira conmigo: 4 fases de 4 segundos, 4 vueltas.
  const respira = mural.querySelector("[data-respira]");
  if (respira) {
    const circulo = respira.querySelector("[data-respira-circulo]");
    const fase = respira.querySelector("[data-respira-fase]");
    const cuenta = respira.querySelector("[data-respira-cuenta]");
    const boton = respira.querySelector("[data-respira-boton]");
    const FASES = [["Inhala", true], ["Sostén", true], ["Exhala", false], ["Espera", false]];
    let temporizador = null;
    const parar = (mensaje) => {
      clearInterval(temporizador);
      temporizador = null;
      circulo.classList.remove("grande");
      fase.textContent = "Listo";
      cuenta.textContent = mensaje;
      boton.textContent = "Empezar";
    };
    boton.addEventListener("click", () => {
      if (temporizador) { parar("Puedes volver a empezar cuando quieras."); return; }
      let paso = 0;
      boton.textContent = "Parar";
      const tic = () => {
        const indice = Math.floor(paso / 4) % 4;
        const vuelta = Math.floor(paso / 16) + 1;
        if (vuelta > 4) { parar("¡Muy bien! ¿Cómo te sientes ahora?"); return; }
        const [nombre, grande] = FASES[indice];
        fase.textContent = nombre;
        circulo.classList.toggle("grande", grande);
        cuenta.textContent = `${4 - (paso % 4)} · vuelta ${vuelta} de 4`;
        paso += 1;
      };
      tic();
      temporizador = setInterval(tic, 1000);
    });
  }

  // ¿Cómo te sientes hoy?
  const animo = mural.querySelector("[data-animo-rapido]");
  if (animo) {
    const respuesta = animo.querySelector("[data-animo-respuesta]");
    const enlace = animo.querySelector("[data-animo-enlace]");
    const base = enlace.getAttribute("href").split("#")[0];
    animo.querySelectorAll("[data-animo]").forEach((btn) => {
      btn.setAttribute("aria-pressed", "false");
      btn.addEventListener("click", () => {
        animo.querySelectorAll("[data-animo]").forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
        const [texto, ancla] = ANIMO_SUGERENCIAS[btn.dataset.animo];
        respuesta.textContent = texto;
        enlace.href = `${base}#${ancla}`;
        enlace.hidden = false;
      });
    });
  }

  // ¿Mito o realidad?
  const mito = mural.querySelector("[data-mito]");
  if (mito) {
    const frase = mito.querySelector("[data-mito-frase]");
    const respuesta = mito.querySelector("[data-mito-respuesta]");
    const botones = mito.querySelectorAll("[data-mito-elegir]");
    let actual = Math.floor(Math.random() * MITOS.length);
    const mostrar = () => {
      frase.textContent = MITOS[actual][0];
      respuesta.textContent = "";
      botones.forEach((b) => b.classList.remove("elegido"));
    };
    botones.forEach((b) => b.addEventListener("click", () => {
      const [, correcta, explicacion] = MITOS[actual];
      botones.forEach((x) => x.classList.toggle("elegido", x === b));
      const acierto = b.dataset.mitoElegir === correcta;
      respuesta.textContent = `${acierto ? "¡Correcto!" : "No exactamente."} Es ${correcta}. ${explicacion}`;
    }));
    mito.querySelector("[data-mito-otra]").addEventListener("click", () => {
      actual = (actual + 1) % MITOS.length;
      mostrar();
    });
    mostrar();
  }

  // Dato de psicología (del glosario de Infórmate).
  const dato = mural.querySelector("[data-dato]");
  if (dato) {
    let lista = [];
    try { lista = JSON.parse(dato.dataset.glosario || "[]"); } catch (e) {}
    const termino = dato.querySelector("[data-dato-termino]");
    const def = dato.querySelector("[data-dato-def]");
    const enlace = dato.querySelector("[data-dato-enlace]");
    let i = Math.floor(Math.random() * (lista.length || 1));
    const mostrar = () => {
      if (!lista.length) return;
      const [t, d, slug] = lista[i % lista.length];
      termino.textContent = t;
      def.textContent = d;
      enlace.href = `${dato.dataset.base}#${slug}`;
    };
    dato.querySelector("[data-dato-otro]").addEventListener("click", () => { i += 1; mostrar(); });
    mostrar();
  }

  // Cerebro: tocar una parte la resalta.
  mural.querySelectorAll("[data-cerebro]").forEach((parte, _, todas) => {
    parte.addEventListener("click", () => {
      todas.forEach((p) => p.setAttribute("aria-pressed", String(p === parte)));
    });
  });

  // Frase para hoy.
  const frase = mural.querySelector("[data-frase]");
  if (frase) {
    const texto = frase.querySelector("[data-frase-texto]");
    let i = 0;
    frase.querySelector("[data-frase-otra]").addEventListener("click", () => {
      i = (i + 1) % FRASES_MURAL.length;
      texto.textContent = FRASES_MURAL[i];
    });
  }
}

document.addEventListener("DOMContentLoaded", activarMural);


// Multitud que camina: personas sencillas dibujadas en canvas (cabeza,
// cabello, cuerpo y piernas que se mueven), con colores variados. Cada
// una cruza de un lado al otro a su propio ritmo y vuelve a entrar.
function activarMultitud() {
  const lienzo = document.querySelector("[data-multitud]");
  if (!lienzo) return;
  const ctx = lienzo.getContext("2d");
  const PIELES = ["#f2c9a0", "#e0ac7e", "#c68a5b", "#a0673f", "#7a4a2a", "#5a3520"];
  const ROPA = ["#1f4d2c", "#2e6b41", "#c9a227", "#0072ce", "#c94b4b", "#5a2d91", "#e8732a", "#183020", "#f4f1e8"];
  const PELO = ["#1b120c", "#3b2416", "#6b4423", "#a8742f", "#2b2b2b"];
  const azar = (a, b) => a + Math.random() * (b - a);
  const elegir = (lista) => lista[Math.floor(Math.random() * lista.length)];
  let ancho = 0, alto = 0, personas = [];

  function nuevaPersona(enCualquierLugar) {
    const escala = azar(0.75, 1.15);
    const dir = Math.random() < 0.5 ? 1 : -1;
    return {
      escala,
      dir,
      x: enCualquierLugar ? azar(0, ancho) : (dir === 1 ? -40 : ancho + 40),
      fondo: azar(0, 1),            // 0 = atrás, 1 = adelante
      vel: azar(28, 60) * escala,   // px por segundo
      fase: azar(0, Math.PI * 2),
      piel: elegir(PIELES),
      camisa: elegir(ROPA),
      pantalon: elegir(["#183020", "#2b2b2b", "#1d3d6b", "#5b4322"]),
      pelo: elegir(PELO),
      peinado: Math.floor(azar(0, 3)),
    };
  }

  function medir() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    ancho = lienzo.clientWidth;
    alto = lienzo.clientHeight;
    lienzo.width = ancho * dpr;
    lienzo.height = alto * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const cuantas = Math.max(10, Math.round(ancho / 34));
    personas = Array.from({ length: cuantas }, () => nuevaPersona(true));
  }

  function dibujar(p) {
    const s = p.escala * (0.8 + p.fondo * 0.35);
    const suelo = alto - 8 - (1 - p.fondo) * 70;
    const paso = Math.sin(p.fase);
    const rebote = Math.abs(Math.cos(p.fase)) * 3 * s;
    ctx.save();
    ctx.translate(p.x, suelo - rebote);
    ctx.scale(s * p.dir, s);
    ctx.lineCap = "round";
    // Piernas
    ctx.strokeStyle = p.pantalon;
    ctx.lineWidth = 9;
    ctx.beginPath(); ctx.moveTo(0, -46); ctx.lineTo(paso * 11, 0); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, -46); ctx.lineTo(-paso * 11, 0); ctx.stroke();
    // Brazo de atrás
    ctx.strokeStyle = p.piel;
    ctx.lineWidth = 7;
    ctx.beginPath(); ctx.moveTo(0, -84); ctx.lineTo(-paso * 12, -58); ctx.stroke();
    // Cuerpo
    ctx.fillStyle = p.camisa;
    ctx.beginPath();
    ctx.roundRect(-13, -92, 26, 50, 11);
    ctx.fill();
    // Brazo de adelante
    ctx.strokeStyle = p.piel;
    ctx.beginPath(); ctx.moveTo(0, -84); ctx.lineTo(paso * 12, -58); ctx.stroke();
    // Cabeza
    ctx.fillStyle = p.piel;
    ctx.beginPath(); ctx.arc(0, -106, 12, 0, Math.PI * 2); ctx.fill();
    // Cabello
    ctx.fillStyle = p.pelo;
    ctx.beginPath();
    if (p.peinado === 0) ctx.arc(0, -109, 12.5, Math.PI, 0);
    else if (p.peinado === 1) { ctx.arc(0, -108, 13, Math.PI * 0.95, Math.PI * 0.05); ctx.rect(-13, -110, 6, 22); }
    else { ctx.arc(0, -110, 12, Math.PI, 0); ctx.arc(-9, -98, 5, 0, Math.PI * 2); }
    ctx.fill();
    ctx.restore();
  }

  let anterior = performance.now();
  let visible = false;
  function cuadro(ahora) {
    const dt = Math.min((ahora - anterior) / 1000, 0.05);
    anterior = ahora;
    if (visible && !document.hidden) {
      ctx.clearRect(0, 0, ancho, alto);
      personas.sort((a, b) => a.fondo - b.fondo);
      personas.forEach((p, i) => {
        if (!SIN_MOVIMIENTO) {
          p.x += p.vel * p.dir * dt;
          p.fase += dt * p.vel / 9;
        }
        if (p.x < -60 || p.x > ancho + 60) personas[i] = nuevaPersona(false);
        dibujar(personas[i]);
      });
    }
    requestAnimationFrame(cuadro);
  }

  new IntersectionObserver((e) => { visible = e[0].isIntersecting; }).observe(lienzo);
  window.addEventListener("resize", medir);
  medir();
  requestAnimationFrame(cuadro);
}

document.addEventListener("DOMContentLoaded", activarMultitud);

// Tarjetas que se apilan al bajar: la sección es alta y su contenido
// queda fijo; según cuánto bajes, cada tarjeta sube desde abajo y la
// anterior se achica (hasta 0.7) y se inclina 5 grados.
function activarPilaTarjetas() {
  const pila = document.querySelector("[data-pila]");
  if (!pila || SIN_MOVIMIENTO) return;
  const tarjetas = Array.from(pila.querySelectorAll(".pila-tarjeta"));
  const n = tarjetas.length;
  if (n < 2) return;
  pila.classList.add("lista");

  function pintar() {
    const caja = pila.getBoundingClientRect();
    const recorrido = caja.height - window.innerHeight;
    const avance = recorrido > 0 ? Math.min(Math.max(-caja.top / recorrido, 0), 1) * (n - 1) : 0;
    tarjetas.forEach((t, i) => {
      // Cuánto ha subido esta tarjeta (0 = abajo, fuera; 1 = en su lugar).
      const subida = i === 0 ? 1 : Math.min(Math.max(avance - (i - 1), 0), 1);
      // Cuánto la ha tapado la siguiente.
      const tapada = Math.min(Math.max(avance - i, 0), 1);
      const y = (1 - subida) * 110;
      const escala = 1 - tapada * 0.3;
      const giro = tapada * 5;
      t.style.transform = `translateY(${y}%) scale(${escala}) rotate(${giro}deg)`;
      t.style.zIndex = String(i + 1);
      t.style.filter = tapada ? `brightness(${1 - tapada * 0.35})` : "none";
    });
  }

  let pendiente = false;
  window.addEventListener("scroll", () => {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(() => { pendiente = false; pintar(); });
  }, { passive: true });
  window.addEventListener("resize", pintar);
  pintar();
}

document.addEventListener("DOMContentLoaded", activarPilaTarjetas);


// MacBook que se abre al bajar: según cuánto has bajado dentro de la
// sección (0 a 1), la pantalla pasa de inclinada (-28°) a derecha, crece
// y baja; el título sube y se desvanece al principio.
function activarMacbook() {
  const seccion = document.querySelector("[data-macbook]");
  if (!seccion) return;
  const pantalla = seccion.querySelector("[data-macbook-pantalla]");
  const titulo = seccion.querySelector("[data-macbook-titulo]");
  const entre = (v, a, b) => Math.min(Math.max((v - a) / (b - a), 0), 1);
  const mezclar = (a, b, t) => a + (b - a) * t;

  function pintar() {
    const celular = window.innerWidth < 768;
    const caja = seccion.getBoundingClientRect();
    // Igual que offset ["start start", "end start"]: 0 cuando el inicio de
    // la sección toca arriba, 1 cuando su final pasa por arriba.
    const p = SIN_MOVIMIENTO ? 0.3 : entre(-caja.top, 0, caja.height);
    const t = entre(p, 0, 0.3);
    const escalaX = mezclar(1.2, celular ? 1 : 1.5, t);
    const escalaY = mezclar(0.6, celular ? 1 : 1.5, t);
    const giro = p < 0.12 ? -28 : mezclar(-28, 0, entre(p, 0.12, 0.3));
    const bajar = SIN_MOVIMIENTO ? 0 : mezclar(0, 1500, p);
    pantalla.style.transform = `translateY(${bajar}px) rotateX(${giro}deg) scaleX(${escalaX}) scaleY(${escalaY})`;
    titulo.style.transform = `translateY(${mezclar(0, 100, t)}px)`;
    titulo.style.opacity = String(1 - entre(p, 0, 0.2));
  }

  let pendiente = false;
  window.addEventListener("scroll", () => {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(() => { pendiente = false; pintar(); });
  }, { passive: true });
  window.addEventListener("resize", pintar);
  pintar();
}

document.addEventListener("DOMContentLoaded", activarMacbook);

// Texto ondulado (squiggly) en los títulos grandes: un filtro SVG de ruido
// deforma un poco las letras, y cada pocos milisegundos cambia el ruido
// (semilla y fuerza al azar dentro de un rango), así parece dibujado a mano
// y "vibra". Si la persona pidió menos movimiento, no se aplica.
const ONDULADO_SELECTOR = [
  ".seccion h2:not(.sr-only)", ".multitud-texto h2", ".pila-titulo", ".macbook-titulo",
  ".diario-header h1", ".informate-categoria-titulo", ".categoria-titulo", ".hero-amigos h1",
].join(", ");
const ONDULADOS = [
  { id: "ondulado-suave", escala: [4, 5], paso: 90 },
  { id: "ondulado-fuerte", escala: [6, 9], paso: 70 },
];

function activarTextoOndulado() {
  if (SIN_MOVIMIENTO) return;
  const titulos = document.querySelectorAll(ONDULADO_SELECTOR);
  if (!titulos.length) return;

  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("focusable", "false");
  svg.style.cssText = "position:absolute;width:0;height:0;overflow:hidden";
  const filtros = ONDULADOS.map((cfg) => {
    const filtro = document.createElementNS(ns, "filter");
    filtro.id = cfg.id;
    const ruido = document.createElementNS(ns, "feTurbulence");
    ruido.setAttribute("type", "fractalNoise");
    ruido.setAttribute("baseFrequency", "0.02");
    ruido.setAttribute("numOctaves", "3");
    ruido.setAttribute("result", "ruido");
    const mover = document.createElementNS(ns, "feDisplacementMap");
    mover.setAttribute("in", "SourceGraphic");
    mover.setAttribute("in2", "ruido");
    mover.setAttribute("xChannelSelector", "R");
    mover.setAttribute("yChannelSelector", "G");
    filtro.append(ruido, mover);
    svg.appendChild(filtro);
    return { ...cfg, ruido, mover };
  });
  document.body.appendChild(svg);

  // El título principal de cada página va más fuerte; los demás, suave.
  titulos.forEach((t) => {
    const fuerte = t.matches(".diario-header h1, .hero-amigos h1, .multitud-texto h2, .macbook-titulo");
    t.classList.add(fuerte ? "ondulado-fuerte" : "ondulado-suave");
  });

  filtros.forEach((f) => {
    const [min, max] = f.escala;
    const cambiar = () => {
      f.ruido.setAttribute("seed", String(Math.floor(Math.random() * 1000)));
      f.mover.setAttribute("scale", (min + Math.random() * (max - min)).toFixed(1));
    };
    cambiar();
    setInterval(() => { if (!document.hidden) cambiar(); }, f.paso);
  });
}

document.addEventListener("DOMContentLoaded", activarTextoOndulado);

// Imágenes que se enderezan al bajar (como "container scroll"): cada
// banner grande va dentro de un marco que entra inclinado hacia atrás
// (20°) y un poco más grande, y queda derecho cuando llega al centro de
// la pantalla. Usa las imágenes ya envueltas por activarImagenesVolteo.
function activarImagenesScroll() {
  const cajas = Array.from(document.querySelectorAll(".img-volteo"));
  if (!cajas.length || SIN_MOVIMIENTO) return;
  const marcos = cajas.map((caja) => {
    const marco = document.createElement("div");
    marco.className = "marco-scroll";
    // El marco toma el lugar (margen y ancho) que tenía la imagen.
    marco.style.margin = caja.style.margin;
    marco.style.maxWidth = caja.style.maxWidth;
    caja.style.margin = "0";
    caja.parentNode.insertBefore(marco, caja);
    marco.appendChild(caja);
    return marco;
  });
  const visibles = new Set();
  const observador = new IntersectionObserver((entradas) => {
    entradas.forEach((e) => (e.isIntersecting ? visibles.add(e.target) : visibles.delete(e.target)));
    pintar();
  });
  marcos.forEach((m) => observador.observe(m));

  function pintar() {
    const alto = window.innerHeight;
    const celular = window.innerWidth < 768;
    visibles.forEach((m) => {
      const r = m.getBoundingClientRect();
      // 0 cuando el marco asoma por abajo, 1 cuando su centro llega al centro.
      const p = Math.min(Math.max((alto - r.top) / (alto / 2 + r.height / 2), 0), 1);
      const giro = 20 * (1 - p);
      const escala = (celular ? 0.9 : 1.05) + (1 - (celular ? 0.9 : 1.05)) * p;
      m.style.transform = `perspective(1000px) rotateX(${giro.toFixed(2)}deg) scale(${escala.toFixed(3)})`;
    });
  }

  let pendiente = false;
  window.addEventListener("scroll", () => {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(() => { pendiente = false; pintar(); });
  }, { passive: true });
  window.addEventListener("resize", pintar);
}

document.addEventListener("DOMContentLoaded", activarImagenesScroll);
