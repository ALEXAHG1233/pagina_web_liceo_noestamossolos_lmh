const socket = io();

const mensajesDiv = document.getElementById("mensajes");
const form = document.getElementById("form-mensaje");
const input = document.getElementById("input-mensaje");
const apoyoDiv = document.getElementById("apoyo-emergencia");
const btnSonido = document.getElementById("btn-sonido");
const btnMusica = document.getElementById("btn-musica");

socket.emit("unirse", { token: TOKEN });
crearToggleSonido(btnSonido);
crearBotonMusica(btnMusica);
crearSelectorFondo("selector-fondo", mensajesDiv, "fondo_chat_asistente_" + (PERSONA || "general"), "whatsapp");

// Botón "Fondo" de la cabecera: muestra u oculta la fila de fondos.
const btnFondos = document.getElementById("wa-fondos");
const selectorFondo = document.getElementById("selector-fondo");
if (btnFondos && selectorFondo) {
  btnFondos.addEventListener("click", () => {
    selectorFondo.hidden = !selectorFondo.hidden;
    btnFondos.setAttribute("aria-expanded", selectorFondo.hidden ? "false" : "true");
  });
}

// Debajo del nombre, como en WhatsApp: "en línea" o "escribiendo…".
const estadoHeader = document.getElementById("wa-estado");
function ponerEstado(texto) {
  if (estadoHeader) estadoHeader.textContent = texto;
}

const AVATARES = { estudiante: "E", psicologa: "P", asistente: AVATAR_ASISTENTE || "A" };
let filaEscribiendo = null;

function agregarMensaje(emisor, contenido) {
  const fila = document.createElement("div");
  fila.classList.add("msg-fila", emisor);

  const avatar = document.createElement("div");
  avatar.classList.add("avatar");
  avatar.textContent = AVATARES[emisor] || "?";

  const contenedor = document.createElement("div");
  contenedor.classList.add("msg-contenido");

  const burbuja = document.createElement("div");
  burbuja.classList.add("msg", emisor);
  const texto = document.createElement("span");
  texto.classList.add("msg-texto");
  texto.textContent = contenido;
  burbuja.appendChild(texto);

  // La hora (y las palomitas en los mensajes propios) van dentro de la
  // burbuja, abajo a la derecha, como en WhatsApp.
  const hora = document.createElement("span");
  hora.classList.add("msg-hora");
  hora.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  if (emisor === "estudiante") {
    const palomitas = document.createElement("span");
    palomitas.classList.add("wa-palomitas");
    palomitas.setAttribute("aria-label", "Enviado");
    palomitas.innerHTML = '<svg viewBox="0 0 18 12" width="16" height="11" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 6.5 4.5 10 11 2"/><path d="M7 10 7.6 10.4 14 2.5"/></svg>';
    hora.appendChild(palomitas);
  }
  burbuja.appendChild(hora);

  // Si el mensaje anterior es del mismo emisor, esta burbuja no lleva "colita".
  const anterior = mensajesDiv.lastElementChild;
  if (anterior && anterior.classList.contains("msg-fila") && anterior.classList.contains(emisor)) {
    fila.classList.add("seguido");
  }

  contenedor.appendChild(burbuja);
  fila.appendChild(avatar);
  fila.appendChild(contenedor);
  mensajesDiv.appendChild(fila);
  mensajesDiv.scrollTop = mensajesDiv.scrollHeight;
}

function mostrarEscribiendo() {
  if (filaEscribiendo) return;
  filaEscribiendo = document.createElement("div");
  filaEscribiendo.classList.add("msg-fila", "asistente", "escribiendo");
  ponerEstado("escribiendo…");
  window.dispatchEvent(new CustomEvent("voz-estado", { detail: "pensando" }));
  filaEscribiendo.innerHTML = `
    <div class="avatar">${AVATAR_ASISTENTE || "A"}</div>
    <div class="msg-contenido">
      <div class="msg asistente"><span class="typing-dots"><span></span><span></span><span></span></span></div>
    </div>`;
  mensajesDiv.appendChild(filaEscribiendo);
  mensajesDiv.scrollTop = mensajesDiv.scrollHeight;
}

function ocultarEscribiendo() {
  if (filaEscribiendo) {
    filaEscribiendo.remove();
    filaEscribiendo = null;
  }
  ponerEstado("en línea");
  window.dispatchEvent(new CustomEvent("voz-estado", { detail: "listo" }));
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  Sonidos.desbloquear();
  const texto = input.value.trim();
  if (!texto) return;
  socket.emit("mensaje_chatbot", { token: TOKEN, contenido: texto, persona: PERSONA });
  Sonidos.enviar();
  input.value = "";
});

socket.on("nuevo_mensaje", (data) => {
  if (data.emisor === "estudiante") {
    agregarMensaje(data.emisor, data.contenido);
    mostrarEscribiendo();
    return;
  }

  // Pequeña pausa antes de mostrar la respuesta del asistente, para que se sienta
  // como una conversación real y no un volcado instantáneo de texto.
  const espera = 500 + Math.random() * 600;
  setTimeout(() => {
    ocultarEscribiendo();
    // Al contestar, los mensajes enviados quedan "leídos" (palomitas azules).
    mensajesDiv.querySelectorAll(".wa-palomitas:not(.leido)").forEach((p) => {
      p.classList.add("leido");
      p.setAttribute("aria-label", "Leído");
    });
    agregarMensaje(data.emisor, data.contenido);
    Sonidos.recibido();
    Voz.alResponder(data.contenido);
  }, espera);
});

socket.on("apoyo_emergencia", (data) => {
  ocultarEscribiendo();
  window.dispatchEvent(new CustomEvent("voz-estado", { detail: "crisis" }));
  Voz.emergencia();
  mostrarApoyoEmergencia(apoyoDiv, socket, TOKEN, data.mensaje);
});

socket.on("contacto_emergencia_confirmado", (data) => {
  const aviso = document.createElement("p");
  aviso.className = "apoyo-confirmacion";
  aviso.textContent = data.mensaje;
  apoyoDiv.appendChild(aviso);
});

// Voz: hablar en vez de escribir, escuchar las respuestas y el modo voz.
Voz.iniciar({
  form,
  input,
  barra: document.querySelector(".wa-acciones"),
  nombre: NOMBRE_ASISTENTE,
  imagen: IMAGEN_ASISTENTE,
  etiqueta: ASISTENTE_ES_IA ? "Asistente con inteligencia artificial · no es una persona" : "Asistente virtual · no es una persona",
  esperando: `${NOMBRE_ASISTENTE} está pensando…`,
  vozMasculina: PERSONA === "sami" || PERSONA === "tigre",
  tono: { sami: 0.8, nia: 1.15, tigre: 0.9 }[PERSONA] || 1,
  enviar: (texto) => {
    Sonidos.desbloquear();
    socket.emit("mensaje_chatbot", { token: TOKEN, contenido: texto, persona: PERSONA });
    Sonidos.enviar();
  },
});
