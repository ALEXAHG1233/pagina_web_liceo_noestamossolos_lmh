const socket = io();

const listaTokens = document.getElementById("lista-tokens");
const mensajesDiv = document.getElementById("mensajes");
const chatTitulo = document.getElementById("chat-titulo");
const form = document.getElementById("form-mensaje");
const input = document.getElementById("input-mensaje");

let chatActivo = null;
const chats = {}; // token -> { nivelRiesgo, mensajes: [] }
let sonidoActivado = false;
let filaEscribiendo = null;

document.getElementById("btn-activar-sonido").addEventListener("click", (e) => {
  Sonidos.desbloquear();
  Sonidos.establecer(true);
  sonidoActivado = true;
  e.target.textContent = "Alertas sonoras activadas";
  e.target.disabled = true;
});

crearSelectorFondo("selector-fondo", mensajesDiv, "fondo_chat_psicologa");

socket.emit("unirse_panel");

function obtenerOCrearItem(token) {
  let item = document.getElementById("item-" + token);
  if (!item) {
    item = document.createElement("li");
    item.id = "item-" + token;
    item.classList.add("chat-item");
    item.innerHTML = `${token}<span class="etiqueta"></span>`;
    item.addEventListener("click", () => abrirChat(token));
    listaTokens.prepend(item);
    chats[token] = { nivelRiesgo: "bajo", mensajes: [] };
  }
  return item;
}

function abrirChat(token) {
  chatActivo = token;
  chatTitulo.textContent = token;
  socket.emit("unirse", { token });

  document.querySelectorAll(".chat-item").forEach((el) => el.classList.remove("activo"));
  document.getElementById("item-" + token).classList.add("activo");

  ocultarEscribiendo();
  mensajesDiv.innerHTML = "";
  (chats[token]?.mensajes || []).forEach((m) => agregarMensajeDOM(m.emisor, m.contenido));
}

const AVATARES = { estudiante: "E", psicologa: "P", asistente: "A" };

function agregarMensajeDOM(emisor, contenido) {
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
  filaEscribiendo.classList.add("msg-fila", "estudiante", "escribiendo");
  filaEscribiendo.innerHTML = `
    <div class="avatar">E</div>
    <div class="msg-contenido">
      <div class="msg estudiante"><span class="typing-dots"><span></span><span></span><span></span></span></div>
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
  if (!texto || !chatActivo) return;
  socket.emit("mensaje_psicologa", { token: chatActivo, contenido: texto });
  socket.emit("dejo_de_escribir", { token: chatActivo, quien: "psicologa" });
  input.value = "";
});

let temporizadorEscritura = null;
input.addEventListener("input", () => {
  if (!chatActivo) return;
  socket.emit("escribiendo", { token: chatActivo, quien: "psicologa" });
  clearTimeout(temporizadorEscritura);
  temporizadorEscritura = setTimeout(() => {
    socket.emit("dejo_de_escribir", { token: chatActivo, quien: "psicologa" });
  }, 1500);
});

socket.on("nuevo_mensaje_panel", (data) => {
  obtenerOCrearItem(data.token);
  chats[data.token].mensajes.push({ emisor: data.emisor, contenido: data.contenido });

  if (data.token === chatActivo) {
    if (data.emisor === "estudiante") ocultarEscribiendo();
    agregarMensajeDOM(data.emisor, data.contenido);
    if (data.emisor !== "psicologa") Sonidos.recibido();
  }
});

socket.on("alguien_escribiendo", (data) => {
  if (data.quien === "estudiante" && data.token === chatActivo) mostrarEscribiendo();
});

socket.on("alguien_dejo_de_escribir", (data) => {
  if (data.quien === "estudiante" && data.token === chatActivo) ocultarEscribiendo();
});

socket.on("alerta_riesgo", (data) => {
  if (sonidoActivado) Sonidos.alerta();
  const item = obtenerOCrearItem(data.token);
  chats[data.token].nivelRiesgo = data.nivel;
  item.classList.add("alerta");
  item.querySelector(".etiqueta").textContent =
    `Alerta: ${data.nivel} (${data.categorias.join(", ")})`;
  listaTokens.prepend(item); // sube al inicio de la lista
});

socket.on("contacto_emergencia_panel", (data) => {
  const item = obtenerOCrearItem(data.token);
  chats[data.token].contacto = { telefono: data.telefono, plataforma: data.plataforma };

  let enlaceContacto = item.querySelector(".enlace-contacto");
  if (!enlaceContacto) {
    enlaceContacto = document.createElement("a");
    enlaceContacto.classList.add("enlace-contacto");
    enlaceContacto.target = "_blank";
    enlaceContacto.rel = "noopener noreferrer";
    item.appendChild(enlaceContacto);
  }

  const soloNumeros = data.telefono.replace(/[^\d+]/g, "");
  if (data.plataforma === "whatsapp") {
    enlaceContacto.href = `https://wa.me/${soloNumeros.replace("+", "")}`;
    enlaceContacto.textContent = `Abrir WhatsApp (${data.telefono})`;
  } else {
    enlaceContacto.href = "#";
    enlaceContacto.textContent = `Telegram: ${data.telefono}`;
    enlaceContacto.onclick = (e) => e.preventDefault();
  }
});
