const HISTORIAS = [
  "Antes de empezar: esto no busca imponerte nada. Si esto no es para ti, puedes volver cuando quieras. Pero si crees en Dios, o simplemente quieres algo de esperanza, aquí van algunas historias.",
  "Hubo un hombre llamado Job que lo perdió todo en muy poco tiempo: su salud, sus bienes, hasta su familia. Y aun así, no dejó de sostenerse. Con el tiempo, todo lo que había perdido le fue devuelto, y más.",
  "José fue traicionado por sus propios hermanos, vendido como esclavo, y encarcelado por algo que no hizo. Pasaron años difíciles. Pero terminó siendo la persona que salvó a un país entero del hambre — y cuando volvió a ver a sus hermanos, los perdonó.",
  "David era solo un pastor de ovejas, el más joven de su familia, a quien nadie tomaba en serio. Se enfrentó a un gigante que todos los demás temían. No ganó por ser el más fuerte, sino por atreverse a actuar aunque tenía miedo.",
  "Hay una historia de un hijo que se equivocó mucho, se alejó de su casa y sintió que ya no merecía volver. Cuando por fin regresó, su padre no lo reprochó — corrió a abrazarlo antes de que terminara de explicarse.",
  "Todas estas historias tienen algo en común: pasaron por momentos que sentían imposibles de superar. Y salieron adelante. Lo que estás viviendo ahora, por difícil que se sienta, no es el final de tu historia.",
];

let indice = 0;
const mensajesDiv = document.getElementById("mensajes");
const btnSiguiente = document.getElementById("btn-siguiente");
const progresoDiv = document.getElementById("progreso-historias");

// Puntos de progreso: uno por historia
HISTORIAS.forEach(() => {
  const punto = document.createElement("span");
  punto.classList.add("progreso-punto");
  progresoDiv.appendChild(punto);
});

function actualizarProgreso() {
  const puntos = progresoDiv.querySelectorAll(".progreso-punto");
  puntos.forEach((p, i) => p.classList.toggle("activo", i === indice));
}

function mostrarSiguiente() {
  if (indice >= HISTORIAS.length) return;

  actualizarProgreso();

  const div = document.createElement("div");
  div.classList.add("msg", "fe");
  div.textContent = HISTORIAS[indice];
  mensajesDiv.appendChild(div);
  mensajesDiv.scrollTop = mensajesDiv.scrollHeight;

  Sonidos.desbloquear();
  Sonidos.suaveDoble();

  indice++;

  if (indice >= HISTORIAS.length) {
    btnSiguiente.textContent = "Hablar con alguien ahora →";
    btnSiguiente.onclick = () => { window.location.href = "/"; };
  }
}

btnSiguiente.addEventListener("click", mostrarSiguiente);

// Muestra el primer mensaje automáticamente al cargar
mostrarSiguiente();
