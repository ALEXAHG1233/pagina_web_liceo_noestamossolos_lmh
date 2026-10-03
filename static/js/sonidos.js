/**
 * Motor de sonido ligero para Tu Espacio Seguro.
 * No usa archivos de audio: genera tonos suaves con la Web Audio API,
 * así el proyecto no depende de assets externos con licencia dudosa.
 * El estado (activado/silenciado) se recuerda por navegador en localStorage.
 */
const Sonidos = (() => {
  const CLAVE = "espacio_seguro_sonido";
  let ctx = null;

  function activo() {
    return localStorage.getItem(CLAVE) !== "0";
  }

  function establecer(valor) {
    localStorage.setItem(CLAVE, valor ? "1" : "0");
  }

  function obtenerContexto() {
    if (!ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return null;
      ctx = new AudioCtx();
    }
    if (ctx.state === "suspended") ctx.resume();
    return ctx;
  }

  function tono({ frecuencia = 440, duracion = 0.15, tipo = "sine", volumen = 0.12, retardo = 0 }) {
    if (!activo()) return;
    const audio = obtenerContexto();
    if (!audio) return;
    try {
      const osc = audio.createOscillator();
      const gain = audio.createGain();
      osc.type = tipo;
      osc.frequency.value = frecuencia;
      const inicio = audio.currentTime + retardo;
      gain.gain.setValueAtTime(0.0001, inicio);
      gain.gain.linearRampToValueAtTime(volumen, inicio + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, inicio + duracion);
      osc.connect(gain).connect(audio.destination);
      osc.start(inicio);
      osc.stop(inicio + duracion + 0.05);
    } catch (e) {
      console.warn("No se pudo reproducir el sonido:", e);
    }
  }

  return {
    activo,
    establecer,
    // Debe llamarse tras un gesto del usuario (clic/tecla) para desbloquear el audio.
    desbloquear: obtenerContexto,
    enviar: () => tono({ frecuencia: 640, duracion: 0.08, volumen: 0.07 }),
    recibido: () => tono({ frecuencia: 500, duracion: 0.16, volumen: 0.1 }),
    suaveDoble: () => {
      tono({ frecuencia: 660, duracion: 0.12, volumen: 0.09 });
      tono({ frecuencia: 880, duracion: 0.18, volumen: 0.09, retardo: 0.12 });
    },
    alerta: () => {
      [0, 0.25].forEach((retardo) => tono({ frecuencia: 880, duracion: 0.2, volumen: 0.16, retardo }));
    },
    logro: () => {
      [523.25, 659.25, 783.99].forEach((frecuencia, i) =>
        tono({ frecuencia, duracion: 0.28, volumen: 0.11, retardo: i * 0.1 })
      );
    },
  };
})();

/**
 * Música ambiental: abre la lista "lofi beats" de Spotify (oficial, con
 * licencia de Spotify) en una ventanita aparte, con nombre fijo. Al usar
 * siempre el mismo nombre de ventana, un segundo clic (incluso desde otra
 * página del sitio) reutiliza esa misma ventana en vez de abrir otra —
 * así la música sigue sonando aunque el estudiante navegue entre páginas,
 * algo que un <audio> normal no puede hacer en un sitio de páginas múltiples.
 */
const NOMBRE_VENTANA_MUSICA = "espacio_seguro_musica_ambiental";

function abrirMusicaAmbiental(playlistId = "37i9dQZF1DWWQRwui0ExPn") {
  const url = `https://open.spotify.com/embed/playlist/${playlistId}?utm_source=generator&theme=0`;
  const ventana = window.open(
    url,
    NOMBRE_VENTANA_MUSICA,
    "width=380,height=300,noopener,noreferrer"
  );
  if (ventana) ventana.focus();
  return ventana;
}
