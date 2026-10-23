const socket = io();

const listaTokens = document.getElementById("lista-tokens");
const listaVacia = document.getElementById("lista-vacia");
const mensajesDiv = document.getElementById("mensajes");
const chatTitulo = document.getElementById("chat-titulo");
const chatRiesgo = document.getElementById("chat-riesgo");
const buscarCorreo = document.getElementById("buscar-correo");
const botonesFiltro = document.querySelectorAll(".filtro-riesgo button");
const form = document.getElementById("form-mensaje");
const input = document.getElementById("input-mensaje");

let chatActivo = null;
let filtroNivel = "todos";
// token -> { correo, nivelRiesgo, categorias, ultimo (milisegundos), sinLeer, mensajes: [], cargado }
const chats = {};
let sonidoActivado = false;
let filaEscribiendo = null;

const ORDEN = { bajo: 0, medio: 1, alto: 2, critico: 3 };
const NOMBRE_NIVEL = { bajo: "Bajo", medio: "Medio", alto: "Alto", critico: "Crítico" };

document.getElementById("btn-activar-sonido").addEventListener("click", (e) => {
  Sonidos.desbloquear();
  Sonidos.establecer(true);
  sonidoActivado = true;
  e.target.textContent = "Alertas sonoras activadas";
  e.target.disabled = true;
});

crearSelectorFondo("selector-fondo", mensajesDiv, "fondo_chat_psicologa");

// Cada vez que se conecta (también al reconectarse tras un corte de internet)
// vuelve a entrar a la sala del panel; si no, esta cuenta dejaría de recibir
// los mensajes nuevos hasta recargar la página.
socket.on("connect", () => {
  socket.emit("unirse_panel");
  if (chatActivo) socket.emit("unirse", { token: chatActivo });
});

const textoCategorias = (lista) => lista.map((c) => c.replace(/_/g, " ")).join(", ");

function chipNivel(nivel) {
  const chip = document.createElement("span");
  chip.classList.add("nivel-chip", "nivel-" + nivel);
  chip.textContent = NOMBRE_NIVEL[nivel] || nivel;
  return chip;
}

function obtenerChat(token, correo) {
  if (!chats[token]) {
    chats[token] = { correo: null, nivelRiesgo: "bajo", categorias: [], ultimo: 0, sinLeer: 0, mensajes: [], cargado: false };
  }
  if (correo) chats[token].correo = correo;
  return chats[token];
}

function subirRiesgo(chat, nivel, categorias) {
  if ((ORDEN[nivel] ?? 0) > (ORDEN[chat.nivelRiesgo] ?? 0)) chat.nivelRiesgo = nivel;
  (categorias || []).forEach((c) => { if (!chat.categorias.includes(c)) chat.categorias.push(c); });
}

// Fecha del último mensaje: hoy solo la hora, ayer "Ayer" y si no el día.
function textoFecha(ms) {
  const d = new Date(ms);
  const hoy = new Date();
  const ayer = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate() - 1);
  const hora = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  if (d.toDateString() === hoy.toDateString()) return "Hoy, " + hora;
  if (d.toDateString() === ayer.toDateString()) return "Ayer, " + hora;
  return d.toLocaleDateString([], { day: "2-digit", month: "short", year: "numeric" }) + ", " + hora;
}

// La lista: arriba el chat que acaba de recibir un mensaje, como en WhatsApp.
// El riesgo se ve en la etiqueta de color y con los filtros de arriba.
function dibujarLista() {
  const conteo = { todos: 0, bajo: 0, medio: 0, alto: 0, critico: 0 };
  const texto = buscarCorreo.value.trim().toLowerCase();
  const tokens = Object.keys(chats).sort((a, b) => chats[b].ultimo - chats[a].ultimo);

  listaTokens.innerHTML = "";
  tokens.forEach((token) => {
    const chat = chats[token];
    conteo.todos++;
    conteo[chat.nivelRiesgo]++;
    if (filtroNivel !== "todos" && chat.nivelRiesgo !== filtroNivel) return;
    if (texto && !(chat.correo || token).toLowerCase().includes(texto)) return;

    const item = document.createElement("li");
    item.classList.add("chat-item", "riesgo-" + chat.nivelRiesgo);
    if (token === chatActivo) item.classList.add("activo");
    if (chat.alertaNueva) item.classList.add("alerta");

    const fila = document.createElement("span");
    fila.classList.add("chat-item-fila");
    const nombre = document.createElement("span");
    nombre.classList.add("chat-correo");
    nombre.textContent = chat.correo || token;
    fila.append(nombre);
    if (chat.sinLeer) {
      item.classList.add("sin-leer");
      const globo = document.createElement("span");
      globo.classList.add("sin-leer-globo");
      globo.textContent = chat.sinLeer;
      globo.title = chat.sinLeer === 1 ? "1 mensaje nuevo" : chat.sinLeer + " mensajes nuevos";
      fila.append(globo);
    }
    fila.append(chipNivel(chat.nivelRiesgo));
    item.appendChild(fila);

    if (chat.ultimo) {
      const fecha = document.createElement("span");
      fecha.classList.add("chat-fecha");
      fecha.textContent = textoFecha(chat.ultimo);
      fecha.title = new Date(chat.ultimo).toLocaleString();
      item.appendChild(fecha);
    }
    if (chat.categorias.length) {
      const etiqueta = document.createElement("span");
      etiqueta.classList.add("etiqueta");
      etiqueta.textContent = textoCategorias(chat.categorias);
      item.appendChild(etiqueta);
    }
    if (chat.contacto) item.appendChild(enlaceContacto(chat.contacto));
    item.addEventListener("click", () => abrirChat(token));
    listaTokens.appendChild(item);
  });

  botonesFiltro.forEach((b) => { b.querySelector("span").textContent = conteo[b.dataset.nivel]; });
  listaVacia.hidden = listaTokens.children.length > 0;
}

botonesFiltro.forEach((boton) => boton.addEventListener("click", () => {
  filtroNivel = boton.dataset.nivel;
  botonesFiltro.forEach((b) => {
    b.classList.toggle("activo", b === boton);
    b.setAttribute("aria-pressed", b === boton ? "true" : "false");
  });
  dibujarLista();
}));
buscarCorreo.addEventListener("input", dibujarLista);

function dibujarCabecera() {
  const chat = chats[chatActivo];
  if (!chat) return;
  chatTitulo.textContent = chat.correo || chatActivo;
  chatRiesgo.hidden = false;
  chatRiesgo.innerHTML = "Filtro de riesgo: ";
  chatRiesgo.appendChild(chipNivel(chat.nivelRiesgo));
  if (chat.categorias.length) chatRiesgo.append(" " + textoCategorias(chat.categorias));
}

async function abrirChat(token) {
  chatActivo = token;
  const chat = chats[token];
  chat.alertaNueva = false;
  chat.sinLeer = 0;
  socket.emit("unirse", { token });
  dibujarLista();
  dibujarCabecera();
  ocultarEscribiendo();
  mensajesDiv.innerHTML = "";

  if (!chat.cargado) {
    try {
      const r = await fetch(`/psicologa/api/conversacion/${encodeURIComponent(token)}`);
      if (r.ok) {
        // Los que llegaron en vivo antes de cargar ya están en la base de datos.
        chat.mensajes = await r.json();
        chat.cargado = true;
        chat.mensajes.forEach((m) => { if (m.emisor === "estudiante") subirRiesgo(chat, m.nivel, m.categorias); });
      }
    } catch (e) { /* sin conexión: se muestra lo que llegó en vivo */ }
    if (chatActivo !== token) return;
    dibujarLista();
    dibujarCabecera();
  }
  mensajesDiv.innerHTML = "";
  chat.mensajes.forEach((m) => agregarMensajeDOM(m));
}

const AVATARES = { estudiante: "E", psicologa: "P", asistente: "A" };

function agregarMensajeDOM({ emisor, contenido, nivel, categorias, fecha, autor }) {
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
  const cuando = fecha ? new Date(fecha) : new Date();
  hora.textContent = cuando.toLocaleString([], { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });

  // Todas las cuentas ven la misma conversación: cada respuesta dice quién la escribió.
  if (emisor === "psicologa" && autor) {
    const quien = document.createElement("span");
    quien.classList.add("msg-autor");
    quien.textContent = autor;
    contenedor.appendChild(quien);
  }
  contenedor.appendChild(burbuja);
  // Cada mensaje del estudiante lleva el nivel que le dio el filtro de riesgo.
  if (emisor === "estudiante" && nivel) {
    const riesgo = document.createElement("span");
    riesgo.classList.add("msg-riesgo");
    riesgo.appendChild(chipNivel(nivel));
    if (categorias && categorias.length) riesgo.append(" " + textoCategorias(categorias));
    contenedor.appendChild(riesgo);
  }
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

// Al abrir el panel se cargan todas las conversaciones guardadas.
fetch("/psicologa/api/conversaciones")
  .then((r) => (r.ok ? r.json() : []))
  .then((lista) => {
    lista.forEach((c) => {
      const chat = obtenerChat(c.token, c.correo);
      subirRiesgo(chat, c.nivel);
      // La fecha guardada es hora local sin zona; Date la lee igual que la del navegador.
      const cuando = Date.parse(c.ultimo || "") || 0;
      if (cuando > chat.ultimo) chat.ultimo = cuando;
    });
    dibujarLista();
  })
  .catch(() => dibujarLista());

socket.on("nuevo_mensaje_panel", (data) => {
  const chat = obtenerChat(data.token, data.correo);
  const mensaje = {
    emisor: data.emisor,
    contenido: data.contenido,
    nivel: data.nivel_riesgo,
    categorias: data.categorias || [],
    fecha: new Date().toISOString(),
    autor: data.autor,
  };
  chat.mensajes.push(mensaje);
  chat.ultimo = Date.now();  // sube al principio de la lista
  if (data.emisor === "estudiante") {
    subirRiesgo(chat, data.nivel_riesgo, data.categorias);
    if (data.token !== chatActivo) {
      chat.sinLeer = (chat.sinLeer || 0) + 1;
      if (sonidoActivado) Sonidos.recibido();
    }
  }
  dibujarLista();

  if (data.token === chatActivo) {
    dibujarCabecera();
    if (data.emisor === "estudiante") ocultarEscribiendo();
    agregarMensajeDOM(mensaje);
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
  const chat = obtenerChat(data.token, data.correo);
  subirRiesgo(chat, data.nivel, data.categorias);
  if (data.token !== chatActivo) chat.alertaNueva = true;
  dibujarLista();
  if (data.token === chatActivo) dibujarCabecera();
});

function enlaceContacto(contacto) {
  const enlace = document.createElement("a");
  enlace.classList.add("enlace-contacto");
  enlace.target = "_blank";
  enlace.rel = "noopener noreferrer";
  enlace.addEventListener("click", (e) => e.stopPropagation());
  const soloNumeros = contacto.telefono.replace(/[^\d+]/g, "");
  if (contacto.plataforma === "whatsapp") {
    enlace.href = `https://wa.me/${soloNumeros.replace("+", "")}`;
    enlace.textContent = `Abrir WhatsApp (${contacto.telefono})`;
  } else {
    enlace.href = "#";
    enlace.textContent = `Telegram: ${contacto.telefono}`;
    enlace.onclick = (e) => { e.preventDefault(); e.stopPropagation(); };
  }
  return enlace;
}

socket.on("contacto_emergencia_panel", (data) => {
  const chat = obtenerChat(data.token);
  chat.contacto = { telefono: data.telefono, plataforma: data.plataforma };
  dibujarLista();
});
