// Página "Habla con el Tigre": le hablas (o le escribes) y te responde con su voz.
// Los mensajes van por el mismo camino que el chat ("mensaje_chatbot"), así que
// pasan por el filtro de riesgo: si hay peligro, la psicóloga recibe el aviso y
// nunca responde la IA. La voz la pone voz.js y los ojos cara_tigre.js.
(() => {
  const socket = io();
  const estado = document.getElementById("tigre-estado");
  const dijiste = document.getElementById("tigre-dijiste");
  const respuesta = document.getElementById("tigre-respuesta");
  const microfono = document.getElementById("tigre-microfono");
  const botonEscribir = document.getElementById("tigre-escribir");
  const formulario = document.getElementById("tigre-formulario");
  const cajaMensaje = document.getElementById("tigre-mensaje");
  const conVoz = document.getElementById("tigre-con-voz");
  const historial = document.getElementById("tigre-historial");
  const lista = document.getElementById("tigre-historial-lista");
  const apoyoDiv = document.getElementById("apoyo-emergencia");
  const avisar = (e) => window.dispatchEvent(new CustomEvent("voz-estado", { detail: e }));

  let escuchando = false;
  let esperando = false;

  socket.emit("unirse", { token: TOKEN });

  Voz.configurar({
    nombre: NOMBRE_ASISTENTE,
    vozMasculina: true,
    tono: 0.9,
    alEstado: (e, texto) => {
      if (e === "escuchando") estado.textContent = "Te estoy escuchando... habla con calma.";
      else if (e === "pensando" && texto) estado.textContent = texto;
      else if (e === "hablando") estado.textContent = "El Tigre te está respondiendo.";
      else if (e === "error" && texto) estado.textContent = texto;
    },
  });

  try { conVoz.checked = localStorage.getItem("tigre-con-voz") !== "0"; } catch (e) {}
  if (!Voz.puedeHablar) conVoz.closest("label").hidden = true;
  conVoz.addEventListener("change", () => {
    try { localStorage.setItem("tigre-con-voz", conVoz.checked ? "1" : "0"); } catch (e) {}
    if (!conVoz.checked) Voz.callar();
  });

  function anotar(quien, texto) {
    historial.hidden = false;
    const p = document.createElement("p");
    p.className = "tigre-linea tigre-linea-" + quien;
    const fuerte = document.createElement("strong");
    fuerte.textContent = quien === "yo" ? "Tú: " : "Tigre: ";
    p.append(fuerte, texto);
    lista.appendChild(p);
  }

  function enviar(texto) {
    texto = (texto || "").trim();
    if (!texto || esperando) return;
    esperando = true;
    dijiste.hidden = false;
    dijiste.textContent = "Dijiste: " + texto;
    estado.textContent = "El Tigre está pensando...";
    avisar("pensando");
    socket.emit("mensaje_chatbot", { token: TOKEN, contenido: texto, persona: "tigre" });
  }

  function marcarMicrofono(activo) {
    escuchando = activo;
    microfono.setAttribute("aria-pressed", String(activo));
    microfono.querySelector("span").textContent = activo ? "LISTO, YA TERMINÉ" : "HABLAR CON EL TIGRE";
  }

  // Botón del micrófono: escucha una vez y manda lo que entendió.
  if (!Voz.puedeEscuchar) {
    microfono.disabled = true;
    microfono.querySelector("span").textContent = "EL MICRÓFONO NO ESTÁ DISPONIBLE";
    estado.textContent = "Tu navegador no deja usar el micrófono aquí. Puedes escribirle al Tigre.";
  }
  microfono.addEventListener("click", () => {
    if (escuchando) { Voz.detener(); return; }
    if (esperando) return;
    Voz.callar();
    marcarMicrofono(true);
    Voz.escuchar().then((texto) => {
      marcarMicrofono(false);
      if (texto) enviar(texto);
      else {
        avisar("listo");
        if (texto === "") estado.textContent = "No te escuché bien. Toca el botón y vuelve a intentarlo.";
      }
    });
  });

  // Escribirle en vez de hablar.
  botonEscribir.addEventListener("click", () => {
    const abrir = formulario.hidden;
    formulario.hidden = !abrir;
    botonEscribir.setAttribute("aria-expanded", String(abrir));
    if (abrir) cajaMensaje.focus();
  });
  formulario.addEventListener("submit", (e) => {
    e.preventDefault();
    const texto = cajaMensaje.value;
    cajaMensaje.value = "";
    enviar(texto);
  });
  cajaMensaje.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); formulario.requestSubmit(); }
  });

  socket.on("nuevo_mensaje", (data) => {
    if (data.emisor === "estudiante") { anotar("yo", data.contenido); return; }
    esperando = false;
    anotar("tigre", data.contenido);
    respuesta.hidden = false;
    respuesta.textContent = data.contenido;
    estado.textContent = "Aquí sigo. Cuéntame más cuando quieras.";
    if (conVoz.checked && Voz.puedeHablar) Voz.hablar(data.contenido);
    else avisar("listo");
  });

  // Riesgo: se muestran las líneas de ayuda y la psicóloga ya recibió el aviso.
  socket.on("apoyo_emergencia", (data) => {
    esperando = false;
    avisar("crisis");
    estado.textContent = "No estás solo. La psicóloga ya recibió un aviso.";
    mostrarApoyoEmergencia(apoyoDiv, socket, TOKEN, data.mensaje);
    apoyoDiv.scrollIntoView({ behavior: "smooth", block: "center" });
  });
  socket.on("contacto_emergencia_confirmado", (data) => {
    const aviso = document.createElement("p");
    aviso.className = "apoyo-confirmacion";
    aviso.textContent = data.mensaje;
    apoyoDiv.appendChild(aviso);
  });

  socket.on("connect_error", () => {
    esperando = false;
    estado.textContent = "No me puedo conectar ahora. Revisa tu internet e intenta otra vez.";
    avisar("listo");
  });
})();
