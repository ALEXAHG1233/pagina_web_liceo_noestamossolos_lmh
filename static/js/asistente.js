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
crearSelectorFondo("selector-fondo", mensajesDiv, "fondo_chat_asistente_" + (PERSONA || "general"));

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
  burbuja.textContent = contenido;

  const hora = document.createElement("span");
  hora.classList.add("msg-hora");
  hora.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  contenedor.appendChild(burbuja);
  contenedor.appendChild(hora);
  fila.appendChild(avatar);
  fila.appendChild(contenedor);
  mensajesDiv.appendChild(fila);
  mensajesDiv.scrollTop = mensajesDiv.scrollHeight;
}

function mostrarEscribiendo() {
  if (filaEscribiendo) return;
  filaEscribiendo = document.createElement("div");
  filaEscribiendo.classList.add("msg-fila", "asistente", "escribiendo");
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
    agregarMensaje(data.emisor, data.contenido);
    Sonidos.recibido();
  }, espera);
});

socket.on("apoyo_emergencia", (data) => {
  ocultarEscribiendo();
  mostrarApoyoEmergencia(apoyoDiv, socket, TOKEN, data.mensaje);
});

socket.on("contacto_emergencia_confirmado", (data) => {
  const aviso = document.createElement("p");
  aviso.className = "apoyo-confirmacion";
  aviso.textContent = data.mensaje;
  apoyoDiv.appendChild(aviso);
});
