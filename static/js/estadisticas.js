// Gráfica de Estadísticas: conversaciones por día, apiladas por el riesgo más
// alto de cada conversación ese día. Los datos vienen de la página
// (window.CONVERSACIONES_POR_DIA) y se dibujan en SVG, sin librerías.
(function () {
  const NIVELES = [
    { id: "bajo", nombre: "Bajo", color: "#45a368" },
    { id: "medio", nombre: "Medio", color: "#dba62a" },
    { id: "alto", nombre: "Alto", color: "#e0602f" },
    { id: "critico", nombre: "Crítico", color: "#a8243a" },
  ];
  const datos = window.CONVERSACIONES_POR_DIA || [];
  const porFecha = Object.fromEntries(datos.map((d) => [d.fecha, d]));

  const svg = document.getElementById("grafica");
  const area = document.getElementById("grafica-area");
  const tooltip = document.getElementById("grafica-tooltip");
  const vacia = document.getElementById("grafica-vacia");
  const totalPeriodo = document.getElementById("total-periodo");
  const tabla = document.getElementById("tabla-cuerpo");
  const botones = document.querySelectorAll(".grafica-rango button");
  const NS = "http://www.w3.org/2000/svg";
  let diasElegidos = 30;

  // Leyenda: color + nombre (el color nunca va solo)
  const leyenda = document.getElementById("grafica-leyenda");
  NIVELES.forEach((n) => {
    const li = document.createElement("li");
    li.innerHTML = `<span class="muestra" style="background:${n.color}"></span>${n.nombre}`;
    leyenda.appendChild(li);
  });

  function fechaLocal(texto) {
    const [a, m, d] = texto.split("-").map(Number);
    return new Date(a, m - 1, d);
  }
  function hoyLocal() {
    const h = new Date();
    return new Date(h.getFullYear(), h.getMonth(), h.getDate());
  }
  const formatoCorto = (d) => d.toLocaleDateString("es", { day: "numeric", month: "short" });
  const formatoLargo = (d) => d.toLocaleDateString("es", { weekday: "long", day: "numeric", month: "long", year: "numeric" });

  // Todos los días del período, con ceros donde no hubo conversaciones
  function diasDelPeriodo() {
    const fin = hoyLocal();
    let inicio;
    if (diasElegidos) {
      inicio = new Date(fin);
      inicio.setDate(fin.getDate() - diasElegidos + 1);
    } else {
      inicio = datos.length ? fechaLocal(datos[0].fecha) : new Date(fin);
    }
    const lista = [];
    for (let d = new Date(inicio); d <= fin; d.setDate(d.getDate() + 1)) {
      const clave = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
      const fila = porFecha[clave] || { bajo: 0, medio: 0, alto: 0, critico: 0 };
      const total = NIVELES.reduce((s, n) => s + fila[n.id], 0);
      lista.push({ ...fila, fecha: new Date(d), total });
    }
    return lista;
  }

  function tope(maximo) {
    if (maximo <= 4) return { max: 4, paso: 1 };
    const paso = Math.ceil(maximo / 4);
    return { max: paso * 4, paso };
  }

  // Rectángulo con las esquinas de arriba redondeadas (el extremo de la barra)
  function barraRedonda(x, y, w, h, r) {
    r = Math.min(r, w / 2, h);
    return `M${x},${y + h} V${y + r} Q${x},${y} ${x + r},${y} H${x + w - r} Q${x + w},${y} ${x + w},${y + r} V${y + h} Z`;
  }

  function nodo(tipo, attrs, padre) {
    const el = document.createElementNS(NS, tipo);
    Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
    padre.appendChild(el);
    return el;
  }

  function dibujar() {
    const dias = diasDelPeriodo();
    const suma = dias.reduce((s, d) => s + d.total, 0);
    // Conversaciones distintas: la que habló varios días cuenta una sola vez
    totalPeriodo.textContent = new Set(dias.flatMap((d) => d.ids || [])).size;
    vacia.hidden = suma > 0;

    const ancho = area.clientWidth;
    const alto = 260;
    const m = { arriba: 12, derecha: 8, abajo: 28, izquierda: 32 };
    const anchoUtil = ancho - m.izquierda - m.derecha;
    const altoUtil = alto - m.arriba - m.abajo;
    svg.setAttribute("viewBox", `0 0 ${ancho} ${alto}`);
    svg.setAttribute("width", ancho);
    svg.setAttribute("height", alto);
    svg.innerHTML = "";

    const { max, paso } = tope(Math.max(...dias.map((d) => d.total), 0));
    const y = (v) => m.arriba + altoUtil - (v / max) * altoUtil;

    // Líneas de guía y números del eje (tenues)
    for (let v = 0; v <= max; v += paso) {
      nodo("line", { x1: m.izquierda, x2: ancho - m.derecha, y1: y(v), y2: y(v), class: v === 0 ? "eje-base" : "eje-guia" }, svg);
      const t = nodo("text", { x: m.izquierda - 8, y: y(v) + 4, class: "eje-texto", "text-anchor": "end" }, svg);
      t.textContent = v;
    }

    const banda = anchoUtil / dias.length;
    const anchoBarra = Math.max(2, Math.min(28, banda * 0.7));
    const separacion = 2;  // espacio entre colores de una misma barra

    // Fechas del eje de abajo: las que quepan sin encimarse (unos 64px cada una)
    const cuantas = Math.max(2, Math.min(6, Math.floor(anchoUtil / 64)));
    const cada = Math.max(1, Math.ceil(dias.length / cuantas));
    dias.forEach((d, i) => {
      if (i % cada !== 0 && i !== dias.length - 1) return;
      if (i !== dias.length - 1 && dias.length - 1 - i < cada * 0.6) return;
      const t = nodo("text", { x: m.izquierda + banda * i + banda / 2, y: alto - 8, class: "eje-texto", "text-anchor": "middle" }, svg);
      t.textContent = formatoCorto(d.fecha);
    });

    const grupos = [];
    dias.forEach((d, i) => {
      const x = m.izquierda + banda * i + (banda - anchoBarra) / 2;
      const g = nodo("g", { class: "barra" }, svg);
      const presentes = NIVELES.filter((n) => d[n.id] > 0);
      let base = y(0);
      presentes.forEach((n, j) => {
        const h = (d[n.id] / max) * altoUtil;
        const esTope = j === presentes.length - 1;
        const hDibujo = Math.max(1, h - (esTope ? 0 : separacion));
        const yArriba = base - h + (esTope ? 0 : separacion);
        nodo("path", { d: barraRedonda(x, yArriba, anchoBarra, hDibujo, esTope ? 4 : 0), fill: n.color }, g);
        base -= h;
      });
      grupos.push(g);

      // Zona para pasar el mouse: más grande que la barra
      const zona = nodo("rect", { x: m.izquierda + banda * i, y: m.arriba, width: banda, height: altoUtil, class: "zona" }, svg);
      zona.addEventListener("mouseenter", () => mostrar(d, i, x + anchoBarra / 2));
      zona.addEventListener("mouseleave", ocultar);
      zona.addEventListener("click", () => mostrar(d, i, x + anchoBarra / 2));
    });

    function mostrar(d, i, centro) {
      grupos.forEach((g, k) => g.classList.toggle("apagada", k !== i));
      const filas = NIVELES.map((n) =>
        `<li><span class="muestra" style="background:${n.color}"></span>${n.nombre}<b>${d[n.id]}</b></li>`).join("");
      tooltip.innerHTML = `<strong>${formatoLargo(d.fecha)}</strong><ul>${filas}</ul><p>Total <b>${d.total}</b></p>`;
      tooltip.hidden = false;
      const izquierda = Math.min(Math.max(centro - tooltip.offsetWidth / 2, 0), ancho - tooltip.offsetWidth);
      tooltip.style.left = izquierda + "px";
      tooltip.style.top = "0px";
    }
    function ocultar() {
      grupos.forEach((g) => g.classList.remove("apagada"));
      tooltip.hidden = true;
    }
    area.onmouseleave = ocultar;
    tooltip.hidden = true;  // al redibujar (cambiar período o tamaño) no queda uno viejo

    // Tabla (lo mismo en números), del día más nuevo al más viejo
    tabla.innerHTML = dias.slice().reverse().filter((d) => d.total > 0).map((d) =>
      `<tr><td>${formatoCorto(d.fecha)} ${d.fecha.getFullYear()}</td>${NIVELES.map((n) => `<td>${d[n.id]}</td>`).join("")}<td><b>${d.total}</b></td></tr>`
    ).join("") || `<tr><td colspan="6">Sin conversaciones en este período.</td></tr>`;
  }

  botones.forEach((b) => b.addEventListener("click", () => {
    diasElegidos = Number(b.dataset.dias);
    botones.forEach((o) => {
      o.classList.toggle("activo", o === b);
      o.setAttribute("aria-pressed", o === b ? "true" : "false");
    });
    dibujar();
  }));

  let espera;
  window.addEventListener("resize", () => { clearTimeout(espera); espera = setTimeout(dibujar, 120); });
  dibujar();
})();
