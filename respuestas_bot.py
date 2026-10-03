"""
Asistente automático por reglas (Opción A) — versión ampliada.

Cambios respecto a la primera versión:
  - Muchas más categorías y frases por categoría.
  - Nunca repite la misma frase dos veces seguidas para el mismo
    estudiante (se guarda un historial en memoria por token).
  - A veces (no siempre, para no sonar a guion) agrega una frase de
    ánimo o un recordatorio de que su familia lo quiere.
  - Si el riesgo es medio o más, deriva a la psicóloga E incluye
    su número de contacto directo.
"""

import random
import re

# --- Reemplaza esto con el número real de la psicóloga del liceo ---
NUMERO_PSICOLOGA = "XXXX-XXXX"
NOMBRE_PSICOLOGA = "la psicóloga del liceo"

# Historial en memoria: token -> lista de las últimas respuestas usadas.
# Se reinicia si el servidor se reinicia (no es información sensible, es solo
# para variar el texto, no hace falta guardarlo en la base de datos).
_HISTORIAL = {}
_MAX_HISTORIAL = 12

# --- Personajes del asistente ---
# Son variaciones de tono/nombre sobre el MISMO asistente automático por reglas.
# Ninguno reemplaza a la psicóloga ni finge ser una persona real: solo cambia
# el saludo y la despedida para que se sientan distintos entre sí.
PERSONAJES = {
    "sami": {
        "nombre": "Sami",
        "avatar": "S",
        "color": "#c9a227",
        "tagline": "Cálido y directo, va al grano con cariño.",
        "saludos": [
            "Hola, soy Sami. Qué bueno que decidiste escribir. ¿Cómo va tu día?",
            "Hola, aquí estoy. Cuéntame qué traes en mente, sin filtro.",
        ],
        "despedidas": [
            "Con gusto. Aquí sigo si quieres seguir hablando.",
            "Para eso estoy. Vuelve cuando quieras, aquí voy a estar.",
        ],
    },
    "leo": {
        "nombre": "Leo",
        "avatar": "L",
        "color": "#0072ce",
        "tagline": "Tranquilo y reflexivo, con calma para pensar juntos.",
        "saludos": [
            "Hola, soy Leo. Vamos con calma: ¿qué tal ha estado tu día?",
            "Hola. Tómate tu tiempo, no hay prisa aquí. ¿Qué tienes en mente?",
        ],
        "despedidas": [
            "Con gusto te acompaño. Aquí sigo, a tu ritmo.",
            "Cuando quieras seguimos pensándolo juntos.",
        ],
    },
    "nia": {
        "nombre": "Nia",
        "avatar": "N",
        "color": "#1f4d2c",
        "tagline": "Positiva, con humor ligero cuando el momento lo permite.",
        "saludos": [
            "¡Hola! Soy Nia. ¿Cómo va todo por tu mundo hoy?",
            "Hola, qué gusto verte por aquí. ¿Qué me cuentas?",
        ],
        "despedidas": [
            "¡Con mucho gusto! Aquí ando cuando me necesites.",
            "Para eso estoy. Vuelve cuando quieras, te leo con gusto.",
        ],
    },
}


def _elegir_sin_repetir(token, opciones):
    usados = _HISTORIAL.get(token, [])
    candidatas = [o for o in opciones if o not in usados] or opciones
    elegida = random.choice(candidatas)

    usados.append(elegida)
    _HISTORIAL[token] = usados[-_MAX_HISTORIAL:]
    return elegida


REGLAS = [
    {
        "id": "saludo",
        "patrones": [r"\bhola\b", r"\bbuenas\b", r"\bqu[eé] tal\b"],
        "respuestas": [
            "Hola, qué bueno que decidiste escribir. ¿Cómo te sientes hoy?",
            "Hola, este es tu espacio. Cuéntame, ¿qué tienes en mente?",
            "Hola, me alegra que estés aquí. ¿Qué tal va tu día?",
        ],
    },
    {
        "patrones": [r"\btriste\b", r"\bmal\b", r"\bdeprimid[oa]\b", r"\bsin ganas\b"],
        "respuestas": [
            "Gracias por contarlo. Sentirte así no significa que algo esté mal contigo — a veces solo necesitamos hablarlo. ¿Quieres contarme desde cuándo te sientes así?",
            "Entiendo que no es fácil. Está bien no estar bien todo el tiempo. ¿Hay algo puntual que haya pasado?",
            "Lo que sientes es válido. No tienes que explicarlo perfecto, solo cuéntame a tu ritmo.",
        ],
    },
    {
        "patrones": [r"\bestr[eé]s\b", r"\bexamen(es)?\b", r"\bnervios\b", r"\bpresi[oó]n\b"],
        "respuestas": [
            "Los exámenes pueden pesar mucho. Algo que ayuda a bajar la ansiedad es respirar lento 4 segundos, sostener 4, soltar 4. ¿Quieres contarme qué es lo que más te preocupa de esto?",
            "Es normal sentir presión antes de algo importante. ¿Qué parte se te hace más difícil ahora mismo?",
            "Un examen no define lo que vales. Vamos paso a paso: ¿qué es lo primero que te agobia?",
        ],
    },
    {
        "patrones": [r"\bmolestan\b", r"\bbullying\b", r"\bse burlan\b", r"\bacoso\b"],
        "respuestas": [
            "Lo que describes no está bien, y no es tu culpa. ¿Quieres que le cuente a la psicóloga para que te ayude con esto directamente?",
            "Nadie merece que lo traten así. Mereces sentirte seguro/a en tu propio liceo. ¿Desde cuándo pasa esto?",
        ],
    },
    {
        "patrones": [r"\bfamilia\b", r"\bpap[aá]\b", r"\bmam[aá]\b", r"\bcasa\b"],
        "respuestas": [
            "Los temas de familia a veces son los más difíciles de hablar. Estoy aquí para escuchar, sin juzgar. ¿Qué está pasando?",
            "A veces en casa es donde más cuesta que nos entiendan. Cuéntame qué pasó.",
        ],
    },
    {
        "patrones": [r"\bsolo\b", r"\bsola\b", r"\bnadie me entiende\b", r"\baislad[oa]\b"],
        "respuestas": [
            "Sentirte solo/a pesa mucho, aunque estés rodeado/a de gente. Aquí no lo estás, ahora mismo alguien te está leyendo.",
            "Eso que sientes es más común de lo que parece. ¿Desde hace cuánto te sientes así?",
        ],
    },
    {
        "patrones": [r"\bcansad[oa]\b", r"\bagotad[oa]\b", r"\bno puedo m[aá]s\b"],
        "respuestas": [
            "Sentirte agotado/a así también es una señal de que necesitas descanso de verdad, no solo dormir. ¿Qué es lo que más te está desgastando?",
            "El cansancio que no se quita con dormir suele ser emocional. Cuéntame qué ha estado pasando.",
        ],
    },
    {
        "patrones": [r"\bmiedo\b", r"\basustad[oa]\b", r"\bansiedad\b"],
        "respuestas": [
            "El miedo es una señal, no una debilidad. ¿Me cuentas a qué le tienes miedo ahora mismo?",
            "Está bien sentir miedo. Vamos a ir despacio: ¿qué es lo que más te preocupa?",
        ],
    },
    {
        "patrones": [r"\bno sirvo\b", r"\bsoy un[a]? fracas[oa]\b", r"\bno valgo\b"],
        "respuestas": [
            "Eso que piensas de ti mismo/a no es un hecho, es una idea que a veces se instala cuando estamos mal. No es cierto. ¿Qué pasó para que te sientas así?",
        ],
    },
    {
        "id": "autocuidado",
        "patrones": [r"\bno duermo\b", r"\bmal dormid[oa]\b", r"\bno tengo hambre\b", r"\bno como\b", r"\bno me cuido\b"],
        "respuestas": [
            "Cuidar lo básico —dormir, comer algo, tomar agua— no arregla todo, pero sí te ayuda a sostenerte mientras trabajas el resto. ¿Cómo has estado durmiendo últimamente?",
            "Cuando algo pesa mucho, hasta comer o dormir bien se vuelve difícil. Es una señal más de que necesitas apoyo, no de que algo esté mal contigo. ¿Desde cuándo notas esto?",
        ],
    },
    {
        "id": "hobbies",
        "patrones": [r"\baburrid[oa]\b", r"\bno s[eé] qu[eé] hacer\b", r"\btodo el (d[ií]a|tiempo) pensando\b", r"\bno dejo de pensar\b"],
        "respuestas": [
            "A veces ayuda tener algo que hacer con las manos o la cabeza, para no darle tantas vueltas a lo mismo. ¿Has probado dibujar, escribir, hacer ejercicio, tocar algún instrumento o alguna manualidad? No tiene que salirte bien, solo distraerte un rato.",
            "Aprender algo nuevo, aunque sea pequeño, ayuda a que la mente descanse un poco de lo que pesa. ¿Te llama la atención algo como el deporte, la música, el dibujo o cocinar?",
        ],
    },
    {
        "id": "vinculos",
        "patrones": [r"\bamig[oa]s?\b", r"\bcon qui[eé]n hablar\b", r"\bnadie con qui[eé]n\b"],
        "respuestas": [
            "¿Tienes a alguien —un amigo, un familiar, alguien del liceo— con quien puedas pasar un rato o platicar de vez en cuando? No hace falta que sepan todo lo que sientes; a veces con solo estar acompañado/a ya ayuda.",
            "Mantener aunque sea un vínculo, por pequeño que sea, hace diferencia. ¿Hay alguien con quien te sientas cómodo/a ahora mismo?",
        ],
    },
    {
        "id": "gracias",
        "patrones": [r"\bgracias\b"],
        "respuestas": [
            "Con gusto. Aquí estoy cuando lo necesites.",
            "Para eso estoy. Puedes volver a escribir cuando quieras.",
            "Me alegra poder acompañarte un poco. Vuelve cuando quieras.",
        ],
    },
]

RESPUESTAS_GENERICAS = [
    "Te escucho. Cuéntame un poco más de eso.",
    "Entiendo. ¿Cómo te hace sentir eso?",
    "Gracias por compartirlo. ¿Desde cuándo sientes esto?",
    "Estoy aquí para ti. Sigue contándome, a tu ritmo.",
    "Sigue contándome, quiero entender bien lo que te pasa.",
]

FRASES_ANIMO = [
    "Y aunque no lo sientas hoy: sí puedes con esto.",
    "Has llegado hasta aquí escribiendo esto — eso ya es valiente.",
    "Esto que sientes hoy no va a durar para siempre.",
    "Un paso a la vez, no tienes que resolverlo todo hoy.",
]

RECORDATORIOS_FAMILIA = [
    "Y algo más: tus papás te quieren, aunque a veces cueste sentirlo o decirlo.",
    "No lo olvides: para tu mamá y tu papá eres muy importante.",
]

FRASES_AUTOCUIDADO = [
    "Algo pequeño que puede ayudar hoy: toma agua y come algo, aunque no tengas mucha hambre.",
    "Si puedes, sal un rato al aire libre o camina unos minutos — ayuda más de lo que parece.",
    "Intenta dormir a una hora razonable hoy, aunque la cabeza siga dando vueltas.",
]

RESPUESTA_DERIVACION = (
    "Lo que me cuentas es importante y merece más atención de la que puedo darte yo. "
    "Voy a avisarle a {psicologa} para que te escriba pronto. "
    "También puedes buscarla directamente al {numero} si prefieres hablarlo ya. "
    "Mientras tanto, no estás solo/a."
).format(psicologa=NOMBRE_PSICOLOGA, numero=NUMERO_PSICOLOGA)


def generar_respuesta(mensaje, token, personaje=None):
    """Devuelve una respuesta según reglas. Se usa SOLO cuando el riesgo es bajo.

    `personaje` (opcional) es una clave de PERSONAJES: solo cambia el tono del
    saludo y la despedida, para que cada "amigo" se sienta distinto. El resto
    de las reglas (contenido emocional real) es idéntico para todos, porque
    esas respuestas sí están cuidadosamente calibradas y no deben variar.
    """
    texto = mensaje.lower().strip()
    datos_personaje = PERSONAJES.get(personaje)

    respuesta_base = None
    for regla in REGLAS:
        for patron in regla["patrones"]:
            if re.search(patron, texto):
                if datos_personaje and regla.get("id") == "saludo":
                    respuesta_base = _elegir_sin_repetir(token, datos_personaje["saludos"])
                elif datos_personaje and regla.get("id") == "gracias":
                    respuesta_base = _elegir_sin_repetir(token, datos_personaje["despedidas"])
                else:
                    respuesta_base = _elegir_sin_repetir(token, regla["respuestas"])
                break
        if respuesta_base:
            break

    if respuesta_base is None:
        respuesta_base = _elegir_sin_repetir(token, RESPUESTAS_GENERICAS)

    # 1 de cada 4 mensajes, agrega una frase extra (ánimo, familia o autocuidado — nunca varias a la vez)
    if random.random() < 0.25:
        extra_pool = random.choice([FRASES_ANIMO, RECORDATORIOS_FAMILIA, FRASES_AUTOCUIDADO])
        extra = _elegir_sin_repetir(token + "_extra", extra_pool)
        respuesta_base = f"{respuesta_base} {extra}"

    return respuesta_base
