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
    '<svg viewBox="0 0 32 32" width="28" height="28" fill="#fff"><path d="M16 3C9 3 3.2 8.7 3.2 15.8c0 2.6.7 5 2 7.1L3 29l6.3-2.1c2 1.1 4.3 1.7 6.7 1.7 7 0 12.8-5.7 12.8-12.8C28.8 8.7 23 3 16 3zm0 23.3c-2.1 0-4.1-.6-5.8-1.6l-.4-.2-3.8 1.3 1.3-3.7-.3-.4a10.4 10.4 0 0 1-1.7-5.7C5.3 9.9 10.1 5.1 16 5.1S26.7 9.9 26.7 15.8 21.9 26.3 16 26.3zm5.7-7.8c-.3-.2-1.8-.9-2.1-1-.3-.1-.5-.2-.7.2s-.8 1-1 1.2c-.2.2-.4.2-.7.1a8.6 8.6 0 0 1-2.5-1.5 9.3 9.3 0 0 1-1.7-2.1c-.2-.3 0-.5.1-.7l.4-.5c.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-1-2.3c-.2-.6-.5-.5-.7-.5h-.6a1.2 1.2 0 0 0-.8.4 3.5 3.5 0 0 0-1.1 2.6c0 1.6 1.1 3.1 1.3 3.3.2.2 2.2 3.4 5.4 4.7.8.3 1.4.5 1.8.6.8.3 1.5.2 2-.1.6-.4 1.8-1.2 2.1-1.9.3-.7.3-1.3.2-1.4-.1-.2-.3-.3-.6-.4z"/></svg>';
  document.body.appendChild(boton);
}

document.addEventListener("DOMContentLoaded", crearBotonWhatsAppFlotante);

function activarRevelado(selector = ".reveal") {
  const elementos = document.querySelectorAll(selector);
  if (!elementos.length) return;

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
  if (!boton || typeof abrirMusicaAmbiental !== "function") return;
  boton.addEventListener("click", () => abrirMusicaAmbiental(playlistId));
}

/**
 * Paleta de fondos disponible para los chats. Un solo lugar para las tres
 * pantallas de chat (estudiante, asistente, psicóloga) en vez de repetirla.
 */
const FONDOS_DISPONIBLES = {
  claro: "#f6f3ec",
  verde: "#e3efe6",
  azul: "#e1f0fb",
  dorado: "#fbead2",
  rosa: "#fbe4ec",
  morado: "#ece1fb",
  coral: "#fde3da",
  menta: "#dff5ec",
  gris: "#ececec",
  oscuro: "#2c2c2a",
};

function crearSelectorFondo(contenedorId, mensajesEl, storageKey) {
  const contenedor = document.getElementById(contenedorId);
  if (!contenedor || !mensajesEl) return;

  function aplicar(nombre) {
    mensajesEl.style.background = FONDOS_DISPONIBLES[nombre] || FONDOS_DISPONIBLES.claro;
    localStorage.setItem(storageKey, nombre);
    contenedor.querySelectorAll(".fondo-swatch").forEach((btn) => {
      btn.classList.toggle("activo", btn.dataset.fondo === nombre);
    });
  }

  Object.entries(FONDOS_DISPONIBLES).forEach(([nombre, color]) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.classList.add("fondo-swatch");
    btn.style.background = color;
    btn.dataset.fondo = nombre;
    btn.title = nombre.charAt(0).toUpperCase() + nombre.slice(1);
    btn.addEventListener("click", () => aplicar(nombre));
    contenedor.appendChild(btn);
  });

  aplicar(localStorage.getItem(storageKey) || "claro");
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
