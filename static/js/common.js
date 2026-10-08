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

// Carrusel en cilindro 3D. Coloca cada imagen alrededor de un cilindro,
// lo hace girar despacio y deja arrastrarlo. Se detiene al pasar el
// mouse o enfocar una imagen con el teclado, para poder hacer clic.
const CILINDRO_VELOCIDAD = 9; // grados por segundo

function activarCarruselCilindro() {
  document.querySelectorAll(".cilindro-escena").forEach((escena) => {
    const anillo = escena.querySelector(".cilindro-anillo");
    const caras = Array.from(anillo.children);
    const n = caras.length;
    if (n < 3) return;
    const paso = 360 / n;
    let radio = 0;
    let angulo = 0;
    let pausado = false;
    let arrastre = null;

    function colocar() {
      const ancho = caras[0].offsetWidth;
      radio = Math.round(ancho / 2 / Math.tan(Math.PI / n)) + 14;
      caras.forEach((cara, i) => {
        cara.style.transform = `rotateY(${i * paso}deg) translateZ(${radio}px)`;
      });
      pintar();
    }

    function pintar() {
      anillo.style.transform = `translateZ(${-radio}px) rotateY(${angulo}deg)`;
    }

    let anterior = performance.now();
    function cuadro(ahora) {
      const dt = Math.min((ahora - anterior) / 1000, 0.1);
      anterior = ahora;
      if (!pausado && !arrastre && !SIN_MOVIMIENTO) {
        angulo -= CILINDRO_VELOCIDAD * dt;
        pintar();
      }
      requestAnimationFrame(cuadro);
    }

    escena.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") pausado = true; });
    escena.addEventListener("pointerleave", () => { pausado = false; });
    escena.addEventListener("focusin", () => { pausado = true; });
    escena.addEventListener("focusout", () => { pausado = false; });

    escena.addEventListener("pointerdown", (e) => {
      arrastre = { x: e.clientX, angulo, movido: false };
    });
    window.addEventListener("pointermove", (e) => {
      if (!arrastre) return;
      const dx = e.clientX - arrastre.x;
      if (Math.abs(dx) > 5 && !arrastre.movido) {
        arrastre.movido = true;
        escena.classList.add("arrastrando");
      }
      if (arrastre.movido) {
        angulo = arrastre.angulo + dx * 0.35;
        pintar();
      }
    });
    window.addEventListener("pointerup", () => {
      if (!arrastre) return;
      // Si fue un arrastre, el clic que viene después no debe abrir la imagen.
      if (arrastre.movido) {
        const bloquear = (e) => e.preventDefault();
        escena.addEventListener("click", bloquear, { capture: true, once: true });
        setTimeout(() => escena.removeEventListener("click", bloquear, { capture: true }), 0);
      }
      arrastre = null;
      escena.classList.remove("arrastrando");
    });

    colocar();
    window.addEventListener("resize", colocar);
    requestAnimationFrame(cuadro);
  });
}

document.addEventListener("DOMContentLoaded", activarCarruselCilindro);

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

function activarCuadrosCyber() {
  const cuadros = document.querySelectorAll(CYBER_SELECTOR);
  cuadros.forEach((cuadro) => {
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
  });

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
