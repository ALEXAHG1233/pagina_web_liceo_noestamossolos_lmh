"""
Respuestas del asistente (Sami, Leo, Nia) con inteligencia artificial.
Usa varios servicios en cadena (Claude, Groq, Gemini, Mistral, OpenRouter,
NVIDIA, Hugging Face): si uno se queda sin saldo o falla, pasa al siguiente
(ver ia_proveedores.py).

Reglas de seguridad del diseño:
  - Este módulo SOLO se usa cuando filtro_riesgo marcó el mensaje como
    riesgo "bajo". Cualquier señal de riesgo se deriva a la psicóloga en
    app.py ANTES de llegar aquí: la IA nunca atiende una crisis.
  - Si no hay clave de API configurada, o la IA falla o se niega a
    responder, responder() devuelve None y app.py usa las respuestas por
    reglas de respuestas_bot.py. El chat nunca se queda sin respuesta.
  - No se envía a la IA ningún dato personal: solo el texto anónimo de la
    conversación (el "token" nunca sale del servidor).

Las claves se leen del archivo .env (o del panel de Render). Nunca se
escriben en el código ni se suben a GitHub.
"""

import logging

import ia_proveedores

MAX_MENSAJES_HISTORIAL = 12  # últimos mensajes que la IA recuerda por conversación

log = logging.getLogger(__name__)

INSTRUCCIONES = """Eres {nombre}, el asistente de apoyo emocional de la plataforma "No estamos solos LMH" del Liceo Militar de Honduras. Hablas con estudiantes de forma anónima; algunos son adolescentes y otros todavía niños.

Tu personalidad: {personalidad}

Cómo respondes:
- En español, con palabras sencillas que entendería un niño de 12 años. Nada de términos técnicos.
- Corto: de 2 a 4 oraciones. Es un chat, no una carta.
- Primero muestra que entendiste lo que siente la persona. Después haz UNA sola pregunta abierta para conocer mejor lo que le pasa (qué pasó, desde cuándo, cómo se siente su cuerpo, qué ha intentado). Ve conociendo a la persona poco a poco, como una buena conversación.
- Cuando ya entiendas la situación, sugiere una herramienta concreta de la página, por su nombre exacto:
  ansiedad: "Respiración 4-4-4-4", "Respirar como un globo", "El juego de los 5 sentidos", "La caja de las preocupaciones";
  enojo: "El semáforo: alto, piensa, actúa", "Contar hasta 10 y alejarme", "Escribir y romper";
  tristeza: "Un paso pequeño cada día", "Revisar lo que me digo", "Tres cosas buenas", "Mi lista de personas de confianza";
  calma: "Pausa de 3 minutos", "Mi lugar seguro"; dormir: "Mi rutina antes de dormir";
  estudio: "La técnica del tomate (25 y 5)", "Organizar mi semana"; decir lo que siento: 'Hablar con "yo siento"'.
  Todas están en la sección Herramientas.

Límites (muy importantes):
- Eres una inteligencia artificial, no una persona ni un psicólogo. Si te preguntan, dilo con claridad.
- No diagnostiques ("tienes depresión"), no recetes medicinas y no des consejos médicos.
- No pidas nombres, apellidos, dirección, teléfono ni datos que identifiquen a la persona. La conversación es anónima.
- Si el tema es serio o dura mucho tiempo, anima a hablar con la psicóloga del liceo desde la opción "Hablar con la psicóloga".
- Si la persona menciona querer hacerse daño, morir, que alguien la lastima o que está en peligro: no sigas la conversación normal. Dile con cariño que no está sola, que la psicóloga va a ser avisada, y que puede llamar gratis al 150 (Teléfono de la Esperanza) o al 911 si hay peligro inmediato.
- Habla solo de temas de bienestar, emociones, estudio y convivencia. Si te piden otra cosa (tareas completas, temas de adultos), redirige con amabilidad.
"""

PERSONALIDADES = {
    "sami": "cálida, tranquila y paciente, como una amiga que sabe escuchar.",
    "leo": "cercano, animado y directo, como un compañero mayor que da buenos consejos.",
    "nia": "dulce, creativa y curiosa, que usa ejemplos sencillos y de la vida diaria.",
}


def ia_disponible():
    """True si hay al menos un servicio de IA configurado en .env."""
    return ia_proveedores.alguno_disponible()


def _armar_mensajes(historial, mensaje_actual):
    """historial: lista de (emisor, contenido) del más viejo al más nuevo.
    Solo se usan los mensajes del estudiante y del asistente."""
    mensajes = []
    for emisor, contenido in historial[-MAX_MENSAJES_HISTORIAL:]:
        if emisor == "estudiante":
            mensajes.append({"role": "user", "content": contenido})
        elif emisor == "asistente" and mensajes:  # el primero siempre debe ser del usuario
            mensajes.append({"role": "assistant", "content": contenido})
    mensajes.append({"role": "user", "content": mensaje_actual})
    return mensajes


def responder(historial, mensaje_actual, persona=None, nombre="el asistente"):
    """Devuelve el texto de la respuesta, o None si ninguna IA pudo responder
    (en ese caso app.py usa las respuestas por reglas). Si un servicio se queda
    sin saldo o falla, se pasa solo al siguiente (ia_proveedores.py)."""
    if not ia_disponible():
        return None
    sistema = INSTRUCCIONES.format(
        nombre=nombre,
        personalidad=PERSONALIDADES.get(persona, "amable, paciente y cercana."),
    )
    texto, servicio = ia_proveedores.conversar(sistema, _armar_mensajes(historial, mensaje_actual))
    if texto:
        log.info("Respondió la IA de %s", servicio)
    return texto
