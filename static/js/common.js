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

// Cursor con estela brillante (como GlowCursor): una línea dorada que
// sigue al mouse y se desvanece en 1.4 segundos, con resplandor, y un
// estallido de chispas al hacer clic. Solo en computadoras con mouse y si
// no se pidió reducir el movimiento.
function activarCursorBrillante() {
  const conMouse = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (!conMouse || SIN_MOVIMIENTO) return;
  const AJUSTES = { color: [255, 200, 61], intensidad: 1.3, grosor: 3, duracion: 1.4, resplandor: 1.2 };
  const [R, G, B] = AJUSTES.color;
  const lienzo = document.createElement("canvas");
  lienzo.className = "cursor-brillante";
  lienzo.setAttribute("aria-hidden", "true");
  document.body.appendChild(lienzo);
  const ctx = lienzo.getContext("2d");
  let dpr = 1;
  const medir = () => {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    lienzo.width = window.innerWidth * dpr;
    lienzo.height = window.innerHeight * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  medir();
  window.addEventListener("resize", medir);

  const puntos = [];       // { x, y, t }
  const estallidos = [];   // chispas del clic
  let animando = false;
  window.addEventListener("pointermove", (e) => {
    if (e.pointerType !== "mouse") return;
    puntos.push({ x: e.clientX, y: e.clientY, t: performance.now() });
    if (puntos.length > 120) puntos.shift();
    empezar();
  }, { passive: true });
  window.addEventListener("pointerdown", (e) => {
    if (e.pointerType !== "mouse") return;
    for (let i = 0; i < 14; i++) {
      const a = (i / 14) * Math.PI * 2;
      const v = 1.5 + Math.random() * 2.5;
      estallidos.push({ x: e.clientX, y: e.clientY, vx: Math.cos(a) * v, vy: Math.sin(a) * v, vida: 1 });
    }
    empezar();
  }, { passive: true });

  function empezar() { if (!animando) { animando = true; requestAnimationFrame(cuadro); } }

  function cuadro(ahora) {
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    const vida = AJUSTES.duracion * 1000;
    while (puntos.length && ahora - puntos[0].t > vida) puntos.shift();
    ctx.globalCompositeOperation = "lighter";
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.shadowColor = "rgba(" + R + "," + G + "," + B + ",0.9)";
    ctx.shadowBlur = 14 * AJUSTES.resplandor;
    for (let i = 1; i < puntos.length; i++) {
      const p0 = puntos[i - 1], p1 = puntos[i];
      const frescura = 1 - (ahora - p1.t) / vida;
      ctx.strokeStyle = "rgba(" + R + "," + G + "," + B + "," + Math.min(1, frescura * 0.8 * AJUSTES.intensidad).toFixed(3) + ")";
      ctx.lineWidth = AJUSTES.grosor * (0.4 + frescura * 0.8);
      ctx.beginPath();
      ctx.moveTo(p0.x, p0.y);
      ctx.lineTo(p1.x, p1.y);
      ctx.stroke();
    }
    for (let i = estallidos.length - 1; i >= 0; i--) {
      const c = estallidos[i];
      c.x += c.vx; c.y += c.vy; c.vx *= 0.94; c.vy *= 0.94; c.vida -= 0.035;
      if (c.vida <= 0) { estallidos.splice(i, 1); continue; }
      ctx.fillStyle = "rgba(" + R + "," + G + "," + B + "," + c.vida.toFixed(2) + ")";
      ctx.beginPath();
      ctx.arc(c.x, c.y, 2.2 * c.vida + 0.6, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.shadowBlur = 0;
    ctx.globalCompositeOperation = "source-over";
    if (puntos.length > 1 || estallidos.length) requestAnimationFrame(cuadro);
    else { animando = false; ctx.clearRect(0, 0, window.innerWidth, window.innerHeight); }
  }
}

document.addEventListener("DOMContentLoaded", activarCursorBrillante);

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


// Texto ondulado (squiggly) en los títulos grandes: un filtro SVG de ruido
// deforma un poco las letras, y cada pocos milisegundos cambia el ruido
// (semilla y fuerza al azar dentro de un rango), así parece dibujado a mano
// y "vibra". Si la persona pidió menos movimiento, no se aplica.
const ONDULADO_SELECTOR = [
  ".seccion h2:not(.sr-only)", ".multitud-texto h2", ".pila-titulo",
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
    const fuerte = t.matches(".diario-header h1, .hero-amigos h1, .multitud-texto h2");
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


// Tarjetas que se voltean (como FlipCard): al tocarlas o arrastrarlas de
// lado giran en Y con un pequeño rebote; adelante queda el título y atrás
// el resto. Si la tarjeta es un enlace, el primer toque la voltea y el
// segundo abre la página. Además, todas las tarjetas tienen un brillo que
// sigue al mouse y se inclinan un poco (máximo 12°).
const GIRAR_SELECTOR = ".tarjetas > .tarjeta, .contador, .recurso-card, .glosario-item, .test-grande";
const GIRAR_FRENTE = "h2, h3, .recurso-numero, .recurso-titulo, .glosario-termino, .contador-numero, .contador-texto, .test-icono, .test-titulo, .cyber-deco";
const SOLO_BRILLO = ".articulo-completo, .herramienta-completa, .test-pregunta, .emergencia, .bento-cuadro, .categoria-sintomas, .login-card, .playlist-card, .pasos-caja, .test-resultado";
const PISTA_GIRAR = "↻ Toca para voltear";

function prepararGiro(tarjeta) {
  const esEnlace = tarjeta.tagName === "A";
  const caja = document.createElement("div");
  caja.className = "girar-caja";
  const interior = document.createElement("div");
  interior.className = "girar-interior";
  tarjeta.parentNode.insertBefore(caja, tarjeta);
  caja.appendChild(interior);

  const atras = document.createElement("div");
  atras.className = (tarjeta.className + " girar-atras").replace("cyber-activo", "");
  atras.setAttribute("aria-hidden", "true");
  Array.from(tarjeta.children).forEach((hijo) => {
    if (!hijo.matches(GIRAR_FRENTE)) atras.appendChild(hijo);
  });
  if (!atras.children.length && tarjeta.matches(".contador")) {
    const p = document.createElement("p");
    p.className = "girar-texto";
    p.textContent = "Se cuenta de forma anónima: nunca se guarda quién eres.";
    atras.appendChild(p);
  }
  if (esEnlace) {
    const ir = document.createElement("span");
    ir.className = "girar-ir";
    ir.textContent = "Toca otra vez para abrir →";
    atras.appendChild(ir);
  }
  const titulo = tarjeta.textContent.trim().replace(/\s+/g, " ").slice(0, 80);
  const pista = document.createElement("span");
  pista.className = "girar-pista";
  pista.setAttribute("aria-hidden", "true");
  pista.textContent = PISTA_GIRAR;
  tarjeta.appendChild(pista);
  interior.append(tarjeta, atras);
  agregarAdornos(atras);

  if (!esEnlace) {
    tarjeta.tabIndex = 0;
    tarjeta.setAttribute("role", "button");
  }
  tarjeta.setAttribute("aria-label", titulo + " (toca para voltear)");

  const voltear = (si) => {
    const volteada = typeof si === "boolean" ? si : !caja.classList.contains("volteada");
    caja.classList.toggle("volteada", volteada);
    atras.setAttribute("aria-hidden", volteada ? "false" : "true");
  };

  // Arrastrar de lado también la voltea (y bloquea el clic que sigue).
  let arrastre = null;
  caja.addEventListener("pointerdown", (e) => { arrastre = { x: e.clientX, dx: 0 }; });
  caja.addEventListener("pointermove", (e) => {
    if (!arrastre) return;
    arrastre.dx = e.clientX - arrastre.x;
    if (Math.abs(arrastre.dx) > 8) {
      const base = caja.classList.contains("volteada") ? 180 : 0;
      const giro = Math.max(-90, Math.min(90, arrastre.dx * 0.6));
      interior.style.transition = "none";
      interior.style.transform = "rotateY(" + (base + giro) + "deg)";
    }
  });
  const soltar = () => {
    if (!arrastre) return;
    const dx = arrastre.dx;
    arrastre = null;
    interior.style.transition = "";
    interior.style.transform = "";
    if (Math.abs(dx) > 60) {
      voltear();
      const bloquear = (ev) => { ev.preventDefault(); ev.stopPropagation(); };
      caja.addEventListener("click", bloquear, { capture: true, once: true });
      setTimeout(() => caja.removeEventListener("click", bloquear, { capture: true }), 0);
    }
  };
  caja.addEventListener("pointerup", soltar);
  caja.addEventListener("pointercancel", soltar);
  caja.addEventListener("pointerleave", soltar);

  tarjeta.addEventListener("click", (e) => {
    if (e.target.closest("button, input, textarea, select")) return;
    e.preventDefault();
    voltear(true);
  });
  atras.addEventListener("click", (e) => {
    if (e.target.closest("button, input, textarea, select, a")) return;
    if (esEnlace) { window.location.href = tarjeta.href; return; }
    voltear(false);
  });
  tarjeta.addEventListener("keydown", (e) => {
    if (!esEnlace && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); voltear(); }
  });
  return caja;
}

function agregarBrilloEInclinacion(elemento, inclinar) {
  const brillo = document.createElement("span");
  brillo.className = "girar-brillo";
  brillo.setAttribute("aria-hidden", "true");
  const destino = elemento.matches(".girar-caja") ? elemento.querySelector(".girar-interior > :first-child") : elemento;
  destino.appendChild(brillo);
  if (!elemento.matches(".girar-caja")) elemento.classList.add("con-brillo");
  const conMouse = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (!conMouse || SIN_MOVIMIENTO) return;
  elemento.addEventListener("pointermove", (e) => {
    const r = elemento.getBoundingClientRect();
    const fx = (e.clientX - r.left) / r.width, fy = (e.clientY - r.top) / r.height;
    brillo.style.setProperty("--gx", (fx * 100) + "%");
    brillo.style.setProperty("--gy", (fy * 100) + "%");
    if (inclinar) {
      elemento.style.transform = "perspective(1100px) rotateX(" + ((0.5 - fy) * 24).toFixed(2) +
        "deg) rotateY(" + ((fx - 0.5) * 24).toFixed(2) + "deg) scale(1.03)";
    }
  });
  elemento.addEventListener("pointerleave", () => {
    if (inclinar) elemento.style.transform = "";
  });
}

function activarTarjetasGiratorias() {
  document.querySelectorAll(GIRAR_SELECTOR).forEach((t) => {
    if (t.closest(".girar-caja")) return;
    agregarBrilloEInclinacion(prepararGiro(t), true);
  });
  document.querySelectorAll(ADORNOS_SELECTOR + ", " + CYBER_SELECTOR).forEach((t) => {
    if (t.closest(".girar-caja") || t.querySelector(":scope > .girar-brillo")) return;
    // Los cuadros "cyber" ya se inclinan solos; los de mucho texto o con
    // botones adentro solo llevan el brillo, para poder leerlos y usarlos.
    const inclinar = !t.matches(SOLO_BRILLO) && !t.matches(CYBER_SELECTOR);
    agregarBrilloEInclinacion(t, inclinar);
  });
}

document.addEventListener("DOMContentLoaded", activarTarjetasGiratorias);


// Foco de luz en las tarjetas de redes: el foco sigue al mouse con
// suavidad, y se empieza a encender cuando el mouse está a menos de 80 px
// de la tarjeta (antes de entrar), como "proximity" del original.
function activarFocoRedes() {
  const grupo = document.querySelector("[data-foco-redes]");
  if (!grupo) return;
  const tarjetas = Array.from(grupo.querySelectorAll(".red-card"));
  tarjetas.forEach((t) => {
    const destello = document.createElement("span");
    destello.className = "red-destello";
    destello.setAttribute("aria-hidden", "true");
    t.appendChild(destello);
  });
  const conMouse = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (!conMouse || SIN_MOVIMIENTO) return;

  const CERCA = 80, SUAVE = 0.3;
  const estado = tarjetas.map(() => ({ x: 0.5, y: 0.5, o: 0, ox: 0.5, oy: 0.5, oo: 0 }));
  let mouse = null, animando = false;

  function paso() {
    let seguir = false;
    tarjetas.forEach((t, i) => {
      const e = estado[i];
      if (mouse) {
        const r = t.getBoundingClientRect();
        const dx = Math.max(r.left - mouse.x, 0, mouse.x - r.right);
        const dy = Math.max(r.top - mouse.y, 0, mouse.y - r.bottom);
        const dist = Math.hypot(dx, dy);
        e.ox = (mouse.x - r.left) / r.width;
        e.oy = (mouse.y - r.top) / r.height;
        e.oo = dist >= CERCA ? 0 : 1 - dist / CERCA;
      } else {
        e.oo = 0;
      }
      e.x += (e.ox - e.x) * SUAVE;
      e.y += (e.oy - e.y) * SUAVE;
      e.o += (e.oo - e.o) * SUAVE;
      t.style.setProperty("--fx", (e.x * 100).toFixed(1) + "%");
      t.style.setProperty("--fy", (e.y * 100).toFixed(1) + "%");
      t.style.setProperty("--fo", e.o.toFixed(3));
      if (Math.abs(e.ox - e.x) + Math.abs(e.oy - e.y) + Math.abs(e.oo - e.o) > 0.002) seguir = true;
    });
    animando = seguir;
    if (seguir) requestAnimationFrame(paso);
  }
  const empezar = () => { if (!animando) { animando = true; requestAnimationFrame(paso); } };
  window.addEventListener("pointermove", (e) => { mouse = { x: e.clientX, y: e.clientY }; empezar(); }, { passive: true });
  document.addEventListener("pointerleave", () => { mouse = null; empezar(); });
}

document.addEventListener("DOMContentLoaded", activarFocoRedes);


// Texto con profundidad 3D en los títulos grandes (los mismos del texto
// ondulado). Cada título lleva capas copiadas detrás (translateZ hacia
// atrás) con un color más oscuro. Se inclina hasta 7.5° hacia el mouse;
// si el mouse no se mueve, gira despacio solo. Solo se animan los títulos
// que se ven en pantalla. El ondulado se pasa a la cara del texto, porque
// un filtro en el título aplanaría el 3D.
function activarTextoProfundo() {
  if (SIN_MOVIMIENTO) return;
  const titulos = Array.from(document.querySelectorAll(ONDULADO_SELECTOR));
  if (!titulos.length) return;
  const INCLINACION = 7.5, SUAVE = 0.14, GIRO = 0.35;

  const items = titulos.map((t) => {
    const tamano = parseFloat(getComputedStyle(t).fontSize) || 24;
    const capas = Math.round(Math.min(16, Math.max(8, tamano / 2.4)));
    const paso = Math.max(0.6, tamano * 0.028);   // px entre capas
    const texto = t.textContent;
    const cara = document.createElement("span");
    cara.className = "profundidad-cara";
    while (t.firstChild) cara.appendChild(t.firstChild);
    ["ondulado-suave", "ondulado-fuerte"].forEach((c) => {
      if (t.classList.contains(c)) { t.classList.remove(c); cara.classList.add(c); }
    });
    const cuerpo = document.createElement("span");
    cuerpo.className = "profundidad-cuerpo";
    for (let i = capas; i >= 1; i--) {
      const capa = document.createElement("span");
      capa.className = "profundidad-capa";
      capa.setAttribute("aria-hidden", "true");
      capa.textContent = texto;
      capa.style.transform = "translateZ(" + (-i * paso).toFixed(2) + "px)";
      capa.style.opacity = (0.55 + 0.45 * (1 - i / capas)).toFixed(2);
      cuerpo.appendChild(capa);
    }
    cuerpo.appendChild(cara);
    const escena = document.createElement("span");
    escena.className = "profundidad-escena";
    escena.appendChild(cuerpo);
    t.appendChild(escena);
    t.classList.add("profundidad", "profundidad-sombra");
    return { t, cuerpo, rx: 0, ry: 0, visible: false };
  });

  const observador = new IntersectionObserver((entradas) => {
    entradas.forEach((e) => {
      const item = items.find((i) => i.t === e.target);
      if (item) item.visible = e.isIntersecting;
    });
  });
  items.forEach((i) => observador.observe(i.t));

  let mouse = null, ultimo = -1e9;
  window.addEventListener("pointermove", (e) => {
    mouse = { x: e.clientX, y: e.clientY };
    ultimo = performance.now();
  }, { passive: true });

  const inicio = performance.now();
  let anterior = 0;
  function cuadro(ahora) {
    requestAnimationFrame(cuadro);
    if (document.hidden || ahora - anterior < 33) return;
    anterior = ahora;
    const t = (ahora - inicio) / 1000;
    const siguiendo = mouse && ahora - ultimo < 2500;
    items.forEach((it) => {
      if (!it.visible) return;
      let ox, oy;
      if (siguiendo) {
        const r = it.t.getBoundingClientRect();
        const fx = Math.max(-1, Math.min(1, (mouse.x - (r.left + r.width / 2)) / (window.innerWidth / 2)));
        const fy = Math.max(-1, Math.min(1, (mouse.y - (r.top + r.height / 2)) / (window.innerHeight / 2)));
        ox = -fy * INCLINACION;
        oy = fx * INCLINACION;
      } else {
        ox = Math.sin(t * GIRO * 1.3) * INCLINACION * 0.5;
        oy = Math.sin(t * GIRO) * INCLINACION;
      }
      it.rx += (ox - it.rx) * SUAVE;
      it.ry += (oy - it.ry) * SUAVE;
      it.cuerpo.style.transform = "rotateX(" + it.rx.toFixed(2) + "deg) rotateY(" + it.ry.toFixed(2) + "deg)";
    });
  }
  requestAnimationFrame(cuadro);
}

document.addEventListener("DOMContentLoaded", activarTextoProfundo);


// Bola de plasma (como CrystalizedBall) alrededor del círculo de
// "Respira conmigo": un halo que respira con el círculo, rayos eléctricos
// que salen del centro y chisporrotean, destellos, chispas y partículas
// cuadradas que suben como polvo. Los rayos se inclinan hacia el mouse.
// Dorado, como el círculo. Solo se anima cuando el cuadro se ve.
function activarBolaPlasma() {
  const lienzo = document.querySelector("[data-bola-plasma]");
  if (!lienzo) return;
  const ctx = lienzo.getContext("2d");
  const circulo = lienzo.parentElement.querySelector("[data-respira-circulo]");
  const AJUSTES = {
    color: [255, 200, 61], rayos: 6, chisporroteo: 0.85, destellos: 0.65, brillo: 0.9,
    chispas: 0.6, particulas: 260, vaiven: 0.5, titileo: 0.5, bruma: 0.7, fuerzaMouse: 0.7,
  };
  const [R, G, B] = AJUSTES.color;
  const rgba = (a) => "rgba(" + R + "," + G + "," + B + "," + a.toFixed(3) + ")";
  let ancho = 0, alto = 0, dpr = 1, visible = false, mouse = null;

  function medir() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    ancho = lienzo.clientWidth; alto = lienzo.clientHeight;
    lienzo.width = ancho * dpr; lienzo.height = alto * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  const azar = (a, b) => a + Math.random() * (b - a);
  const particulas = Array.from({ length: AJUSTES.particulas }, () => nuevaParticula(true));
  function nuevaParticula(cualquierAltura) {
    return {
      x: azar(0, 1), y: cualquierAltura ? azar(0, 1) : 1.05,
      vel: azar(0.02, 0.08), tam: azar(1, 2.6), fase: azar(0, 6.28), luz: azar(0.2, 0.8),
    };
  }
  const chispas = [];

  // Un rayo: línea quebrada del centro hacia afuera.
  function rayo(cx, cy, angulo, largo, grosor, alfa) {
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    const pasos = 9;
    for (let i = 1; i <= pasos; i++) {
      const t = i / pasos;
      const desvio = (Math.random() - 0.5) * 22 * AJUSTES.chisporroteo * Math.sin(t * Math.PI);
      const a = angulo + desvio / (largo * t + 20);
      ctx.lineTo(cx + Math.cos(a) * largo * t, cy + Math.sin(a) * largo * t);
    }
    ctx.strokeStyle = rgba(alfa);
    ctx.lineWidth = grosor;
    ctx.shadowColor = rgba(0.9);
    ctx.shadowBlur = 12 * AJUSTES.brillo;
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  const angulos = Array.from({ length: AJUSTES.rayos }, (_, i) => (i / AJUSTES.rayos) * Math.PI * 2);
  const inicio = performance.now();
  let anterior = 0;

  function cuadro(ahora) {
    requestAnimationFrame(cuadro);
    if (!visible || document.hidden || ahora - anterior < 33) return;
    anterior = ahora;
    const t = (ahora - inicio) / 1000;
    const entrada = Math.min(t / 1.2, 1);
    ctx.clearRect(0, 0, ancho, alto);
    const cx = ancho / 2, cy = alto / 2;
    const rc = circulo.getBoundingClientRect();
    const radio = Math.max(rc.width, 40) / 2;   // crece y se encoge con el círculo
    ctx.globalAlpha = entrada;

    // Bruma y halo.
    const halo = ctx.createRadialGradient(cx, cy, radio * 0.6, cx, cy, radio * 2.4);
    halo.addColorStop(0, rgba(0.35 * AJUSTES.brillo));
    halo.addColorStop(0.5, rgba(0.12 * AJUSTES.bruma));
    halo.addColorStop(1, rgba(0));
    ctx.fillStyle = halo;
    ctx.fillRect(0, 0, ancho, alto);

    // Partículas cuadradas que suben (polvo).
    particulas.forEach((p, i) => {
      p.y -= p.vel * 0.033;
      p.x += Math.sin(t * 0.8 + p.fase) * 0.0008 * AJUSTES.vaiven;
      if (p.y < -0.05) particulas[i] = nuevaParticula(false);
      const tit = 1 - AJUSTES.titileo * 0.5 * (1 + Math.sin(t * 3 + p.fase));
      ctx.fillStyle = rgba(p.luz * tit * 0.8);
      ctx.fillRect(p.x * ancho, p.y * alto, p.tam, p.tam);
    });

    // Rayos eléctricos: giran despacio; con el mouse cerca, se inclinan hacia él.
    let anguloMouse = null;
    if (mouse) {
      const rl = lienzo.getBoundingClientRect();
      const mx = mouse.x - rl.left, my = mouse.y - rl.top;
      if (mx > -40 && my > -40 && mx < ancho + 40 && my < alto + 40) anguloMouse = Math.atan2(my - cy, mx - cx);
    }
    angulos.forEach((a, i) => {
      let ang = a + t * 0.4 + Math.sin(t * 1.3 + i) * 0.3;
      if (anguloMouse !== null) {
        let d = Math.atan2(Math.sin(anguloMouse - ang), Math.cos(anguloMouse - ang));
        ang += d * AJUSTES.fuerzaMouse * 0.6;
      }
      const largo = radio * azar(1.25, 1.75);
      rayo(cx, cy, ang, largo, azar(1, 2.2), azar(0.45, 0.85));
      // Destello en la punta.
      if (Math.random() < AJUSTES.destellos * 0.5) {
        const px = cx + Math.cos(ang) * largo, py = cy + Math.sin(ang) * largo;
        const d = ctx.createRadialGradient(px, py, 0, px, py, 12);
        d.addColorStop(0, "rgba(255,255,255,0.9)");
        d.addColorStop(1, rgba(0));
        ctx.fillStyle = d;
        ctx.fillRect(px - 12, py - 12, 24, 24);
        // Chispas que saltan de la punta.
        if (Math.random() < AJUSTES.chispas) {
          chispas.push({ x: px, y: py, vx: azar(-1.5, 1.5), vy: azar(-1.5, 1.5), vida: 1 });
        }
      }
    });

    // Chispas.
    for (let i = chispas.length - 1; i >= 0; i--) {
      const c = chispas[i];
      c.x += c.vx; c.y += c.vy; c.vida -= 0.06;
      if (c.vida <= 0) { chispas.splice(i, 1); continue; }
      ctx.fillStyle = "rgba(255,255,255," + c.vida.toFixed(2) + ")";
      ctx.fillRect(c.x, c.y, 2, 2);
    }

    // Borde de cristal de la bola.
    ctx.beginPath();
    ctx.arc(cx, cy, radio * 1.75, 0, Math.PI * 2);
    ctx.strokeStyle = rgba(0.25);
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  window.addEventListener("pointermove", (e) => { mouse = { x: e.clientX, y: e.clientY }; }, { passive: true });
  new IntersectionObserver((e) => { visible = e[0].isIntersecting; }).observe(lienzo);
  window.addEventListener("resize", medir);
  medir();
  if (SIN_MOVIMIENTO) { visible = true; cuadro(performance.now() + 2000); visible = false; return; }
  requestAnimationFrame(cuadro);
}

document.addEventListener("DOMContentLoaded", activarBolaPlasma);


// Letras elásticas (como ElasticMesh, material "globo") en los textos
// pequeños de color amarillo: cada letra es como un globito; cuando el
// mouse se acerca (70 px) las letras se estiran hacia él, al presionar se
// aplastan, y al soltar rebotan con un resorte hasta quedarse quietas.
function activarLetrasElasticas() {
  if (SIN_MOVIMIENTO) return;
  const AMARILLO = "rgb(255, 200, 61)";
  const candidatos = document.querySelectorAll("h3, h4, .glosario-termino, .cerebro-parte strong, .categoria-sintomas strong");
  const letras = [];
  candidatos.forEach((el) => {
    if (el.children.length || !el.textContent.trim()) return;
    const estilo = getComputedStyle(el);
    if (estilo.color !== AMARILLO || parseFloat(estilo.fontSize) > 26) return;
    const texto = el.textContent;
    el.setAttribute("aria-label", texto.trim());
    el.classList.add("texto-globo");
    const piezas = [];
    texto.split(/(\s+)/).forEach((trozo) => {
      if (!trozo) return;
      if (/^\s+$/.test(trozo)) { piezas.push(document.createTextNode(" ")); return; }
      const palabra = document.createElement("span");
      palabra.className = "globo-palabra";
      palabra.setAttribute("aria-hidden", "true");
      Array.from(trozo).forEach((c) => {
        const l = document.createElement("span");
        l.className = "globo-letra";
        l.textContent = c;
        palabra.appendChild(l);
        letras.push({ el: l, x: 0, y: 0, vx: 0, vy: 0, s: 1, vs: 0 });
      });
      piezas.push(palabra);
    });
    el.replaceChildren(...piezas);
  });
  if (!letras.length) return;
  const conMouse = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (!conMouse) return;

  const RADIO = 70, ESTIRAR = 0.5, RIGIDEZ = 0.5, VAIVEN = 0.6;
  let mouse = null, presionado = false, animando = false;
  window.addEventListener("pointermove", (e) => { mouse = { x: e.clientX, y: e.clientY }; empezar(); }, { passive: true });
  window.addEventListener("pointerdown", () => { presionado = true; empezar(); }, { passive: true });
  window.addEventListener("pointerup", () => { presionado = false; empezar(); }, { passive: true });

  function empezar() { if (!animando) { animando = true; requestAnimationFrame(paso); } }

  function paso() {
    let movimiento = 0;
    letras.forEach((l) => {
      let ox = 0, oy = 0, os = 1;
      if (mouse) {
        const r = l.el.getBoundingClientRect();
        if (r.bottom > -50 && r.top < window.innerHeight + 50) {
          const cx = r.left + r.width / 2 - l.x, cy = r.top + r.height / 2 - l.y;
          const dx = mouse.x - cx, dy = mouse.y - cy;
          const d = Math.hypot(dx, dy);
          if (d < RADIO) {
            const f = 1 - d / RADIO;
            ox = dx * f * ESTIRAR * 0.35;
            oy = dy * f * ESTIRAR * 0.35;
            os = presionado ? 1 - f * 0.35 : 1 + f * 0.25;
          }
        }
      }
      // Resorte con un poco de rebote (wobble).
      const k = 0.12 + RIGIDEZ * 0.18, amort = 0.9 - VAIVEN * 0.25;
      l.vx = (l.vx + (ox - l.x) * k) * amort;
      l.vy = (l.vy + (oy - l.y) * k) * amort;
      l.vs = (l.vs + (os - l.s) * k) * amort;
      l.x += l.vx; l.y += l.vy; l.s += l.vs;
      movimiento += Math.abs(l.vx) + Math.abs(l.vy) + Math.abs(l.vs) * 20 + Math.abs(ox - l.x) + Math.abs(oy - l.y);
      const quieto = Math.abs(l.x) < 0.05 && Math.abs(l.y) < 0.05 && Math.abs(l.s - 1) < 0.003;
      l.el.style.transform = quieto ? "" :
        "translate(" + l.x.toFixed(2) + "px," + l.y.toFixed(2) + "px) scale(" + (2 - l.s).toFixed(3) + "," + l.s.toFixed(3) + ")";
    });
    if (movimiento > 0.05) requestAnimationFrame(paso);
    else animando = false;
  }
}

document.addEventListener("DOMContentLoaded", activarLetrasElasticas);


// Alto del encabezado fijo de las páginas internas: lo usan la barra de
// categorías (que se pega justo debajo) y los saltos a un artículo.
function medirEncabezado() {
  const encabezado = document.querySelector(".diario-header");
  if (!encabezado) return;
  const poner = () => document.documentElement.style.setProperty("--alto-encabezado", encabezado.offsetHeight + "px");
  poner();
  window.addEventListener("resize", poner);
}

document.addEventListener("DOMContentLoaded", medirEncabezado);


// Borde eléctrico (como ElectricBorder): 3 rayos dorados que recorren el
// borde redondeado del cuadro, temblando con ruido, con resplandor. Se
// pone en la bienvenida, las imágenes grandes, "Hablar ayuda", los pasos,
// las tarjetas de "¿Por qué hablar ayuda?", las opciones de Herramientas e
// Infórmate y los recursos de psicología. Solo se animan los que se ven.
const ELECTRICO_SELECTOR = [
  ".bienvenida-marco", ".marco-scroll", ".multitud", ".pasos-caja",
  ".tarjetas > .girar-caja", ".opcion-recurso", ".recursos-grid > .girar-caja",
].join(", ");

function activarBordeElectrico() {
  const AJUSTES = { color: [255, 200, 61], velocidad: 1, caos: 0.5, separacion: 0.6, rayos: 3, grosor: 1.5, radio: 24 };
  const [R, G, B] = AJUSTES.color;
  const MARGEN = 16;
  const items = [];

  document.querySelectorAll(ELECTRICO_SELECTOR).forEach((el) => {
    let host = el;
    if (getComputedStyle(el).overflow !== "visible" || el.matches(".multitud")) {
      // Envolver para que el resplandor no quede recortado.
      const caja = document.createElement("div");
      caja.className = "borde-electrico";
      const estilo = getComputedStyle(el);
      caja.style.margin = estilo.margin;
      caja.style.maxWidth = estilo.maxWidth;
      caja.style.width = el.matches(".bienvenida-marco") ? estilo.width : "";
      el.style.margin = "0";
      if (el.matches(".bienvenida-marco")) el.style.width = "100%";
      el.parentNode.insertBefore(caja, el);
      caja.appendChild(el);
      host = caja;
    } else {
      host.classList.add("borde-electrico-host");
    }
    const lienzo = document.createElement("canvas");
    lienzo.className = "borde-electrico-lienzo";
    lienzo.setAttribute("aria-hidden", "true");
    host.appendChild(lienzo);
    const radio = parseFloat(getComputedStyle(el).borderTopLeftRadius) || AJUSTES.radio;
    items.push({ host, lienzo, ctx: lienzo.getContext("2d"), radio, visible: false, w: 0, h: 0, semilla: Math.random() * 100 });
  });
  if (!items.length) return;

  // Ruido suave en 1D (valor interpolado), para que los rayos tiemblen.
  const tabla = Array.from({ length: 512 }, () => Math.random() * 2 - 1);
  const ruido = (x) => {
    const i = Math.floor(x), f = x - i;
    const a = tabla[i & 511], b = tabla[(i + 1) & 511];
    const s = f * f * (3 - 2 * f);
    return a + (b - a) * s;
  };

  // Punto y normal en el perímetro de un rectángulo redondeado (s de 0 a 1).
  function perimetro(w, h, r, s) {
    r = Math.min(r, w / 2, h / 2);
    const rectos = [w - 2 * r, h - 2 * r, w - 2 * r, h - 2 * r];
    const arco = (Math.PI * r) / 2;
    const total = rectos.reduce((a, b) => a + b, 0) + arco * 4;
    let d = s * total;
    const esquinas = [[w - r, r], [w - r, h - r], [r, h - r], [r, r]];
    const dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]];
    const inicios = [[r, 0], [w, r], [w - r, h], [0, h - r]];
    for (let lado = 0; lado < 4; lado++) {
      if (d <= rectos[lado]) {
        const [x0, y0] = inicios[lado], [dx, dy] = dirs[lado];
        return { x: x0 + dx * d, y: y0 + dy * d, nx: dy, ny: -dx };
      }
      d -= rectos[lado];
      if (d <= arco) {
        const [cx, cy] = esquinas[lado];
        const ang = -Math.PI / 2 + lado * (Math.PI / 2) + d / r;
        return { x: cx + Math.cos(ang) * r, y: cy + Math.sin(ang) * r, nx: Math.cos(ang), ny: Math.sin(ang) };
      }
      d -= arco;
    }
    return { x: r, y: 0, nx: 0, ny: -1 };
  }

  function medir(it) {
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    it.w = it.host.offsetWidth;
    it.h = it.host.offsetHeight;
    it.lienzo.width = Math.round((it.w + MARGEN * 2) * dpr);
    it.lienzo.height = Math.round((it.h + MARGEN * 2) * dpr);
    it.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function dibujar(it, t) {
    const { ctx, w, h } = it;
    if (!w || !h) return;
    ctx.clearRect(0, 0, w + MARGEN * 2, h + MARGEN * 2);
    const largo = 2 * (w + h);
    const puntos = Math.min(400, Math.max(60, Math.round(largo / 7)));
    const amplitud = 6 * AJUSTES.separacion;
    for (let k = 0; k < AJUSTES.rayos; k++) {
      ctx.beginPath();
      for (let i = 0; i <= puntos; i++) {
        const s = i / puntos;
        const p = perimetro(w, h, it.radio, s);
        const n = ruido(s * largo * 0.02 * (1 + AJUSTES.caos) + t * 2.2 * AJUSTES.velocidad + k * 37 + it.semilla)
                + 0.5 * ruido(s * largo * 0.06 + t * 4.1 * AJUSTES.velocidad + k * 11);
        const desv = n * amplitud * (0.6 + AJUSTES.caos);
        const x = MARGEN + p.x + p.nx * desv, y = MARGEN + p.y + p.ny * desv;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.closePath();
      // Resplandor (línea gruesa y transparente) y luego el rayo fino y brillante.
      ctx.strokeStyle = "rgba(" + R + "," + G + "," + B + ",0.18)";
      ctx.lineWidth = AJUSTES.grosor * 5;
      ctx.stroke();
      ctx.strokeStyle = "rgba(" + R + "," + G + "," + B + "," + (0.55 + 0.15 * k).toFixed(2) + ")";
      ctx.lineWidth = AJUSTES.grosor;
      ctx.stroke();
    }
  }

  const observador = new IntersectionObserver((entradas) => {
    entradas.forEach((e) => {
      const it = items.find((i) => i.host === e.target);
      if (it) { it.visible = e.isIntersecting; if (it.visible) medir(it); }
    });
  });
  items.forEach((it) => observador.observe(it.host));
  window.addEventListener("resize", () => items.forEach(medir));

  if (SIN_MOVIMIENTO) {
    setTimeout(() => items.forEach((it) => { medir(it); dibujar(it, 0); }), 300);
    return;
  }
  const inicio = performance.now();
  let anterior = 0;
  function cuadro(ahora) {
    requestAnimationFrame(cuadro);
    if (document.hidden || ahora - anterior < 40) return;   // ~25 cuadros por segundo
    anterior = ahora;
    const t = (ahora - inicio) / 1000;
    items.forEach((it) => {
      if (!it.visible) return;
      if (it.host.offsetWidth !== it.w || it.host.offsetHeight !== it.h) medir(it);
      dibujar(it, t);
    });
  }
  requestAnimationFrame(cuadro);
}

document.addEventListener("DOMContentLoaded", activarBordeElectrico);


// Destello que barre al pasar el mouse, en todos los cuadros y todas las
// imágenes grandes de las páginas.
const BARRIDO_IMAGENES = ".img-volteo, .perspectiva-foto, .pila-tarjeta, .bienvenida-marco, .libro3d-tapa, .video-ligero";

function activarBarrido() {
  document.querySelectorAll(ADORNOS_SELECTOR + ", " + CYBER_SELECTOR + ", " + BARRIDO_IMAGENES + ", .red-card").forEach((el) => {
    if (el.querySelector(":scope > .barrido")) return;
    const capa = document.createElement("span");
    capa.className = "barrido";
    capa.setAttribute("aria-hidden", "true");
    el.appendChild(capa);
    el.classList.add("con-barrido");
  });
}

document.addEventListener("DOMContentLoaded", activarBarrido);
