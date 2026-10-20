// Voz en los chats, según lo que le sea más cómodo a cada persona:
//  - Hablar: graba lo que dices, lo convierte en texto y lo envía al chat.
//  - Respuestas en voz: quien responde (Sami, Leo, Nia o la psicóloga) lee su
//    mensaje en voz alta.
//  - Modo voz: pantalla completa con quien te responde; hablas, te contesta
//    con voz y subtítulos, y vuelve a escucharte. Sin tocar nada.
// El audio se convierte en texto en el servidor (Whisper en Groq) y no se guarda.
// Si eso no está disponible, se usa el reconocimiento de voz del navegador.
// El texto se envía como un mensaje normal, así que pasa por el filtro de riesgo.
const Voz = (() => {
  const meta = (n) => document.querySelector(`meta[name="${n}"]`)?.content || "";
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const puedeGrabar = !!(navigator.mediaDevices?.getUserMedia && window.MediaRecorder);
  const servidor = meta("voz-activa") === "1" && puedeGrabar;
  const sintesis = "speechSynthesis" in window ? window.speechSynthesis : null;
  const guardar = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };
  const leer = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };

  let cfg = null;
  let respuestasEnVoz = leer("voz-respuestas") === "1";
  let enLlamada = false;
  let grabando = null;      // { detener() }
  let ocupado = false;      // esperando transcripción o respuesta
  let ui = {};
  // Avisa a la página qué está pasando (lo usa la cara del Tigre para mover los ojos).
  const avisar = (estado) => window.dispatchEvent(new CustomEvent("voz-estado", { detail: estado }));

  // ---------- Grabar y convertir en texto ----------
  function grabarServidor(alTerminar, conSilencio) {
    return navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } }).then((flujo) => {
      const tipo = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4"].find((t) => MediaRecorder.isTypeSupported?.(t)) || "";
      const rec = new MediaRecorder(flujo, tipo ? { mimeType: tipo } : undefined);
      const trozos = [];
      rec.ondataavailable = (e) => { if (e.data.size) trozos.push(e.data); };
      // Detecta cuando la persona deja de hablar (para no tener que tocar "detener").
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const analizador = ctx.createAnalyser();
      analizador.fftSize = 1024;
      ctx.createMediaStreamSource(flujo).connect(analizador);
      const datos = new Uint8Array(analizador.fftSize);
      let hablo = false, silencioDesde = 0, inicio = Date.now(), cuadro = 0;
      const medir = () => {
        analizador.getByteTimeDomainData(datos);
        let suma = 0;
        for (const v of datos) suma += (v - 128) * (v - 128);
        const volumen = Math.sqrt(suma / datos.length);
        ui.onda?.style.setProperty("--vol", Math.min(1, volumen / 30).toFixed(2));
        if (volumen > 9) { hablo = true; silencioDesde = 0; }
        else if (hablo && !silencioDesde) silencioDesde = Date.now();
        const callado = conSilencio && hablo && silencioDesde && Date.now() - silencioDesde > 1500;
        const largo = Date.now() - inicio > 45000;
        const nunca = conSilencio && !hablo && Date.now() - inicio > 12000;
        if (callado || largo || nunca) { detener(); return; }
        cuadro = requestAnimationFrame(medir);
      };
      const detener = () => { if (rec.state !== "inactive") rec.stop(); };
      rec.onstop = () => {
        cancelAnimationFrame(cuadro);
        flujo.getTracks().forEach((t) => t.stop());
        ctx.close();
        grabando = null;
        const blob = new Blob(trozos, { type: rec.mimeType || "audio/webm" });
        if (!hablo || blob.size < 800) { alTerminar(""); return; }
        alTerminar(null, blob);
      };
      rec.start();
      medir();
      grabando = { detener };
    });
  }

  function enviarAudio(blob) {
    const datos = new FormData();
    datos.append("audio", blob, "voz");
    return fetch("/api/voz/transcribir", { method: "POST", headers: { "X-CSRF": meta("csrf-token") }, body: datos })
      .then((r) => r.json().then((j) => ({ ok: r.ok, j })))
      .then(({ ok, j }) => { if (!ok) throw new Error(j.error || "error"); return j.texto || ""; });
  }

  function grabarNavegador(alTerminar) {
    const rec = new SR();
    rec.lang = "es-419";
    rec.interimResults = true;
    rec.maxAlternatives = 1;
    let final = "";
    rec.onresult = (e) => {
      let parcial = "";
      for (const r of e.results) (r.isFinal ? (final += r[0].transcript + " ") : (parcial += r[0].transcript));
      mostrarSubtitulo((final + parcial).trim(), true);
    };
    rec.onerror = () => {};
    rec.onend = () => { grabando = null; alTerminar(final.trim()); };
    rec.start();
    grabando = { detener: () => rec.stop() };
    return Promise.resolve();
  }

  // Escucha una vez y entrega el texto (o "" si no se entendió).
  function escuchar() {
    return new Promise((resolver) => {
      const conSilencio = true;
      const terminar = (texto, blob) => {
        if (blob) {
          ponerEstado("pensando", "Entendiendo lo que dijiste…");
          enviarAudio(blob).then(resolver).catch(() => resolver(SR ? null : ""));
        } else resolver(texto || "");
      };
      ponerEstado("escuchando", "Te escucho… habla con calma");
      const arrancar = servidor ? grabarServidor(terminar, conSilencio) : SR ? grabarNavegador(terminar) : Promise.reject();
      arrancar.catch(() => {
        ponerEstado("error", "No se pudo usar el micrófono. Revisa el permiso del navegador.");
        resolver(null);
      });
    });
  }

  // ---------- Hablar (leer en voz alta) ----------
  function elegirVoz() {
    const voces = sintesis ? sintesis.getVoices().filter((v) => v.lang?.toLowerCase().startsWith("es")) : [];
    if (!voces.length) return null;
    const masculina = /jorge|pablo|raul|raúl|diego|enrique|carlos|juan|alvaro|álvaro|male|hombre/i;
    const femenina = /paulina|sabina|helena|laura|elvira|dalia|mónica|monica|lucia|lucía|female|mujer|google/i;
    const quiere = cfg?.vozMasculina ? masculina : femenina;
    const latam = (v) => /es-(mx|us|419|hn|co|ar|cl|pe)/i.test(v.lang);
    return voces.find((v) => quiere.test(v.name) && latam(v)) || voces.find((v) => quiere.test(v.name)) || voces.find(latam) || voces[0];
  }

  function limpiarParaVoz(texto) {
    return String(texto)
      .replace(/https?:\/\/\S+/g, "")
      .replace(/[*_#>`~]/g, "")
      .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function hablar(texto) {
    return new Promise((resolver) => {
      const limpio = limpiarParaVoz(texto);
      if (!sintesis || !limpio) { resolver(); return; }
      sintesis.cancel();
      const frase = new SpeechSynthesisUtterance(limpio);
      frase.lang = "es-MX";
      const voz = elegirVoz();
      if (voz) { frase.voice = voz; frase.lang = voz.lang; }
      frase.rate = cfg?.velocidad || 1;
      frase.pitch = cfg?.tono || 1;
      frase.onstart = () => { avisar("hablando"); ponerEstado("hablando", `${cfg.nombre} está hablando…`); };
      frase.onend = frase.onerror = () => { avisar("listo"); resolver(); };
      sintesis.speak(frase);
    });
  }

  // ---------- Pantalla del modo voz ----------
  function ponerEstado(estado, texto) {
    if (!ui.llamada) return;
    avisar(estado);
    ui.llamada.dataset.estado = estado;
    ui.estado.textContent = texto;
    const escuchando = estado === "escuchando";
    ui.mic.setAttribute("aria-pressed", escuchando ? "true" : "false");
    ui.mic.querySelector("span").textContent = escuchando ? "Listo, ya terminé" : "Hablar";
  }

  function mostrarSubtitulo(texto, esPersona) {
    if (!ui.subtitulo) return;
    ui.subtitulo.textContent = texto;
    ui.subtitulo.classList.toggle("voz-yo", !!esPersona);
  }

  function crearLlamada() {
    const caja = document.createElement("div");
    caja.className = "voz-llamada";
    caja.hidden = true;
    caja.setAttribute("role", "dialog");
    caja.setAttribute("aria-modal", "true");
    caja.setAttribute("aria-label", `Conversación por voz con ${cfg.nombre}`);
    caja.innerHTML = `
      <div class="voz-llamada-caja">
        <p class="voz-quien">${cfg.etiqueta}</p>
        <div class="voz-avatar" aria-hidden="true">
          <span class="voz-aro"></span><span class="voz-aro voz-aro-2"></span>
          ${cfg.cara || (cfg.imagen ? `<img src="${cfg.imagen}" alt="">` : `<span class="voz-letra">${cfg.nombre[0]}</span>`)}
        </div>
        <h2 class="voz-nombre">${cfg.nombre}</h2>
        <p class="voz-estado" aria-live="polite">Toca "Hablar" cuando quieras</p>
        <div class="voz-onda" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
        <p class="voz-subtitulo" aria-live="polite"></p>
        <div class="voz-opciones" role="group" aria-label="Cómo quieres que te responda">
          <button type="button" class="voz-modo" data-modo="voz"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4Z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg> Me responde con voz</button>
          <button type="button" class="voz-modo" data-modo="texto"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M20 12a8 8 0 0 1-11.8 7L4 20l1-4A8 8 0 1 1 20 12Z"/></svg> Me responde con texto</button>
        </div>
        <div class="voz-botones">
          <button type="button" class="voz-mic" aria-pressed="false"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg><span>Hablar</span></button>
          <button type="button" class="voz-colgar">Terminar</button>
        </div>
        <p class="voz-nota">Lo que digas se convierte en texto y aparece en el chat. El audio no se guarda.</p>
      </div>`;
    document.body.appendChild(caja);
    ui.llamada = caja;
    ui.estado = caja.querySelector(".voz-estado");
    ui.subtitulo = caja.querySelector(".voz-subtitulo");
    ui.onda = caja.querySelector(".voz-onda");
    ui.mic = caja.querySelector(".voz-mic");
    const pintarModos = () => caja.querySelectorAll(".voz-modo").forEach((b) => b.setAttribute("aria-pressed", String((b.dataset.modo === "voz") === respuestasEnVoz)));
    caja.querySelectorAll(".voz-modo").forEach((b) => b.addEventListener("click", () => {
      fijarRespuestasEnVoz(b.dataset.modo === "voz");
      pintarModos();
    }));
    pintarModos();
    ui.mic.addEventListener("click", () => {
      if (grabando) { grabando.detener(); return; }
      if (sintesis?.speaking) sintesis.cancel();
      turno();
    });
    caja.querySelector(".voz-colgar").addEventListener("click", cerrarLlamada);
    caja.addEventListener("keydown", (e) => { if (e.key === "Escape") cerrarLlamada(); });
  }

  // Un turno de la conversación: escuchar → enviar al chat → (la respuesta llega por alResponder).
  function turno() {
    if (!enLlamada || ocupado) return;
    ocupado = true;
    escuchar().then((texto) => {
      ocupado = false;
      if (!enLlamada) return;
      if (texto === null) {
        if (SR && servidor) {  // si el servidor no pudo, probar con el navegador
          ponerEstado("listo", "Toca \"Hablar\" otra vez");
        }
        return;
      }
      if (!texto) { ponerEstado("listo", "No te escuché bien. Toca \"Hablar\" y vuelve a intentarlo."); return; }
      mostrarSubtitulo(texto, true);
      ponerEstado("pensando", cfg.esperando);
      ocupado = true;
      cfg.enviar(texto);
    });
  }

  function abrirLlamada() {
    if (!ui.llamada) crearLlamada();
    enLlamada = true;
    ui.llamada.hidden = false;
    document.body.classList.add("voz-abierta");
    mostrarSubtitulo("", false);
    ponerEstado("listo", "Toca \"Hablar\" cuando quieras");
    ui.mic.focus();
  }

  function cerrarLlamada() {
    enLlamada = false;
    ocupado = false;
    grabando?.detener();
    sintesis?.cancel();
    if (ui.llamada) ui.llamada.hidden = true;
    document.body.classList.remove("voz-abierta");
    ui.botonLlamada?.focus();
  }

  function fijarRespuestasEnVoz(si) {
    respuestasEnVoz = si;
    guardar("voz-respuestas", si ? "1" : "0");
    if (ui.botonVoz) {
      ui.botonVoz.setAttribute("aria-pressed", si ? "true" : "false");
      ui.botonVoz.title = si ? "Las respuestas se leen en voz alta" : "Las respuestas solo se leen en pantalla";
    }
    if (!si) sintesis?.cancel();
  }

  // ---------- Botones en el chat ----------
  function botonesDelChat() {
    const form = cfg.form, input = cfg.input;
    if (servidor || SR) {
      const mic = document.createElement("button");
      mic.type = "button";
      mic.className = "voz-dictar";
      mic.setAttribute("aria-label", "Hablar en vez de escribir");
      mic.title = "Hablar en vez de escribir";
      mic.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>';
      form.insertBefore(mic, form.querySelector('[type="submit"]'));
      mic.addEventListener("click", () => {
        if (grabando) { grabando.detener(); return; }
        mic.classList.add("grabando");
        avisar("escuchando");
        mic.setAttribute("aria-label", "Detener y enviar");
        const placeholder = input.placeholder;
        input.placeholder = "Te escucho… toca el micrófono para terminar";
        const terminar = (texto, blob) => {
          const fin = (t) => {
            mic.classList.remove("grabando");
            avisar("listo");
            mic.setAttribute("aria-label", "Hablar en vez de escribir");
            input.placeholder = placeholder;
            if (t) { input.value = t; cfg.enviar(t); input.value = ""; }
            else if (t === "") { input.placeholder = "No te escuché bien, intenta otra vez"; setTimeout(() => { input.placeholder = placeholder; }, 2500); }
          };
          if (blob) { input.placeholder = "Escribiendo lo que dijiste…"; enviarAudio(blob).then(fin).catch(() => fin("")); }
          else fin(texto || "");
        };
        const arrancar = servidor ? grabarServidor(terminar, true) : grabarNavegador(terminar);
        arrancar.catch(() => { mic.classList.remove("grabando"); avisar("listo"); input.placeholder = "No se pudo usar el micrófono"; });
      });
    }
    const barra = cfg.barra;
    if (!barra) return;
    if (sintesis) {
      const voz = document.createElement("button");
      voz.type = "button";
      voz.className = "btn-sonido wa-icono voz-boton";
      voz.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4Z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg> Voz';
      voz.setAttribute("aria-label", "Escuchar las respuestas en voz alta");
      ui.botonVoz = voz;
      voz.addEventListener("click", () => {
        fijarRespuestasEnVoz(!respuestasEnVoz);
        if (respuestasEnVoz) hablar(`Listo. Voy a leerte las respuestas de ${cfg.nombre} en voz alta.`);
      });
      barra.prepend(voz);
      fijarRespuestasEnVoz(respuestasEnVoz);
    }
    if ((servidor || SR) && sintesis) {
      const llamar = document.createElement("button");
      llamar.type = "button";
      llamar.className = "btn-sonido wa-icono voz-boton voz-boton-llamar";
      llamar.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2Z"/></svg> Modo voz';
      llamar.setAttribute("aria-label", `Conversar por voz con ${cfg.nombre}`);
      ui.botonLlamada = llamar;
      llamar.addEventListener("click", abrirLlamada);
      barra.prepend(llamar);
    }
  }

  return {
    iniciar(opciones) {
      cfg = { etiqueta: "", esperando: "Pensando…", ...opciones };
      if (sintesis) sintesis.getVoices();  // algunos navegadores cargan las voces tarde
      botonesDelChat();
    },
    // Llega un mensaje de quien responde (asistente o psicóloga).
    alResponder(texto) {
      if (!cfg) return;
      if (enLlamada) {
        ocupado = false;
        mostrarSubtitulo(texto, false);
        const seguir = () => { if (enLlamada) turno(); };
        if (respuestasEnVoz && sintesis) hablar(texto).then(seguir);
        else { ponerEstado("listo", "Te respondió en el chat"); setTimeout(seguir, Math.min(6000, 1500 + texto.length * 35)); }
        return;
      }
      if (respuestasEnVoz) hablar(texto);
    },
    // Si aparece el apoyo de emergencia, se cierra el modo voz para que se vean las líneas de ayuda.
    emergencia() {
      cerrarLlamada();
    },
  };
})();
