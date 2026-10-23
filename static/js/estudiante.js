const socket = io();
// Sin correo no se puede escribir: el servidor manda a la página del correo.
socket.on("pide_correo", (data) => { location.href = data.ir + "?siguiente=" + encodeURIComponent(location.pathname); });

const mensajesDiv = document.getElementById("mensajes");
const form = document.getElementById("form-mensaje");
const input = document.getElementById("input-mensaje");
const apoyoDiv = document.getElementById("apoyo-emergencia");
const btnSonido = document.getElementById("btn-sonido");
const btnMusica = document.getElementById("btn-musica");

socket.emit("unirse", { token: TOKEN, quien: "estudiante" });
crearToggleSonido(btnSonido);
crearBotonMusica(btnMusica);
crearSelectorFondo("selector-fondo", mensajesDiv, "fondo_chat_estudiante");

const AVATAR_PSICOLOGA_STORAGE_KEY = "avatar_psicologa_estudiante";
crearSelectorAvatar("selector-avatar", AVATAR_PSICOLOGA_STORAGE_KEY, () => {
  document.querySelectorAll(".msg-fila.psicologa .avatar").forEach(aplicarImagenAvatar);
});

const AVATARES = { estudiante: "E", psicologa: "P", asistente: "A" };
let filaEscribiendo = null;

function aplicarImagenAvatar(avatarEl) {
  const url = obtenerAvatarPsicologaElegido(AVATAR_PSICOLOGA_STORAGE_KEY);
  if (url) {
    avatarEl.classList.add("con-imagen");
    avatarEl.innerHTML = `<img src="${url}" alt="Avatar de la psicóloga">`;
  } else {
    avatarEl.classList.remove("con-imagen");
    avatarEl.textContent = "P";
  }
}

function agregarMensaje(emisor, contenido) {
  const fila = document.createElement("div");
  fila.classList.add("msg-fila", emisor);

  const avatar = document.createElement("div");
  avatar.classList.add("avatar");
  if (emisor === "psicologa") {
    aplicarImagenAvatar(avatar);
  } else {
    avatar.textContent = AVATARES[emisor] || "?";
  }

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
  filaEscribiendo.classList.add("msg-fila", "psicologa", "escribiendo");
  filaEscribiendo.innerHTML = `
    <div class="avatar"></div>
    <div class="msg-contenido">
      <div class="msg psicologa"><span class="typing-dots"><span></span><span></span><span></span></span></div>
    </div>`;
  aplicarImagenAvatar(filaEscribiendo.querySelector(".avatar"));
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
  socket.emit("mensaje_estudiante", { token: TOKEN, contenido: texto });
  socket.emit("dejo_de_escribir", { token: TOKEN, quien: "estudiante" });
  Sonidos.enviar();
  input.value = "";
});

let temporizadorEscritura = null;
input.addEventListener("input", () => {
  socket.emit("escribiendo", { token: TOKEN, quien: "estudiante" });
  clearTimeout(temporizadorEscritura);
  temporizadorEscritura = setTimeout(() => {
    socket.emit("dejo_de_escribir", { token: TOKEN, quien: "estudiante" });
  }, 1500);
});

socket.on("nuevo_mensaje", (data) => {
  ocultarEscribiendo();
  agregarMensaje(data.emisor, data.contenido);
  if (data.emisor !== "estudiante") Sonidos.recibido();
  if (data.emisor === "psicologa") Voz.alResponder(data.contenido);
});

socket.on("alguien_escribiendo", (data) => {
  if (data.quien === "psicologa") mostrarEscribiendo();
});

socket.on("alguien_dejo_de_escribir", (data) => {
  if (data.quien === "psicologa") ocultarEscribiendo();
});

socket.on("apoyo_emergencia", (data) => {
  Voz.emergencia();
  mostrarApoyoEmergencia(apoyoDiv, socket, TOKEN, data.mensaje);
});

socket.on("contacto_emergencia_confirmado", (data) => {
  const aviso = document.createElement("p");
  aviso.className = "apoyo-confirmacion";
  aviso.textContent = data.mensaje;
  apoyoDiv.appendChild(aviso);
});

socket.on("estado_psicologa", (data) => {
  const fila = document.createElement("div");
  fila.classList.add("msg-fila", "sistema");
  fila.innerHTML = `
    <div class="avatar">i</div>
    <div class="msg-contenido">
      <div class="msg sistema"></div>
    </div>`;
  fila.querySelector(".msg").textContent = data.mensaje;
  mensajesDiv.appendChild(fila);
  mensajesDiv.scrollTop = mensajesDiv.scrollHeight;
});

// Voz: hablar en vez de escribir, escuchar lo que responde la psicóloga y el modo voz.
Voz.iniciar({
  form,
  input,
  barra: document.querySelector(".acciones-header"),
  nombre: "La psicóloga",
  imagen: IMAGEN_PSICOLOGA,
  etiqueta: "Psicóloga del liceo · persona real",
  esperando: "Tu mensaje llegó. La psicóloga te responde en cuanto pueda…",
  enviar: (texto) => {
    Sonidos.desbloquear();
    socket.emit("mensaje_estudiante", { token: TOKEN, contenido: texto });
    Sonidos.enviar();
  },
});
