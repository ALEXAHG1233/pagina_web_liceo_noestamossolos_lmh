"""
Hace que el asistente por reglas (sin IA) converse más como un
acompañamiento psicológico:

  1. Preguntas de seguimiento: después de responder, pregunta algo para
     entender mejor (una sola pregunta, sin repetir las ya hechas).
  2. Memoria del tema: si la persona sigue contando sin repetir la palabra
     clave, el asistente sabe que siguen hablando del mismo tema.
  3. Reflejo de la emoción: nombra lo que la persona parece sentir
     ("suena a que te sientes con mucho estrés").
  4. Herramienta sugerida: desde el segundo mensaje de un tema, recomienda
     una herramienta de la página por su nombre exacto, una sola vez.

Solo se usa con mensajes de riesgo "bajo": las crisis las deriva app.py a
la psicóloga antes de llegar aquí. La memoria vive en el servidor y se
pierde al reiniciarlo; nunca se guarda nada que identifique a la persona.
"""

import random
import re

# Ids para las reglas de respuestas_bot que no tenían uno, según su primer patrón.
IDS_POR_PRIMER_PATRON = {
    r"\btriste\b": "triste",
    r"\bestr[eé]s\b": "estres",
    r"\bmolestan\b": "bullying",
    r"\bfamilia\b": "familia",
    r"\bsolo\b": "soledad",
    r"\bcansad[oa]\b": "cansancio",
    r"\bmiedo\b": "miedo",
    r"\bno sirvo\b": "autoestima",
}

PREGUNTAS_GENERALES = [
    "¿Desde cuándo te sientes así?",
    "¿Qué pasó hoy que te hizo sentir de esta forma?",
    "¿Cómo se siente eso en tu cuerpo?",
    "¿Con quién has podido hablar de esto?",
    "¿Qué te ha ayudado otras veces cuando te sentiste así?",
]

PREGUNTAS_ESTUDIO = [
    "¿En qué materia te está costando más?",
    "¿Cómo estás estudiando ahora?",
    "¿Qué es lo que más te distrae cuando estudias?",
]

# Por tema: preguntas de seguimiento y la herramienta que conviene sugerir
# (el nombre debe ser igual al de herramientas_bot.py).
TEMAS = {
    "triste": {
        "preguntas": [
            "¿Desde cuándo te sientes así de triste?",
            "¿Pasó algo en especial, o es una tristeza que llegó sin aviso?",
            "¿Hay algo que antes disfrutabas y ahora ya no?",
        ],
        "herramienta": "Un paso pequeño cada día",
    },
    "estres": {
        "preguntas": [
            "¿Qué es lo que más te está estresando ahora?",
            "¿Cómo has estado durmiendo con todo esto?",
            "¿Qué tienes pendiente que más te preocupa?",
        ],
        "herramienta": "Respiración 4-4-4",
    },
    "bullying": {
        "preguntas": [
            "¿Desde cuándo pasa esto?",
            "¿Pasa en el liceo, en redes o en los dos lugares?",
            "¿Algún adulto sabe lo que está pasando?",
        ],
        "herramienta": None,  # aquí lo importante es hablar con la psicóloga
    },
    "familia": {
        "preguntas": [
            "¿Qué pasó en casa?",
            "¿Con quién de tu familia te llevas mejor?",
            "¿Cómo te sentiste después de eso?",
        ],
        "herramienta": "Hablar con \"yo siento\"",
    },
    "conflicto_padres": {
        "preguntas": [
            "¿Cómo te estás sintiendo tú con todo esto?",
            "¿Tienes a alguien con quien hablarlo fuera de casa?",
        ],
        "herramienta": "Mi lista de personas de confianza",
    },
    "soledad": {
        "preguntas": [
            "¿Desde cuándo te sientes así?",
            "¿Hay alguien con quien te sientas un poco más cómodo/a?",
            "¿Qué te gustaría que fuera diferente?",
        ],
        "herramienta": "Mi lista de personas de confianza",
    },
    "cansancio": {
        "preguntas": [
            "¿Cuántas horas estás durmiendo?",
            "¿Qué es lo que más te desgasta en el día?",
        ],
        "herramienta": "Mi rutina antes de dormir",
    },
    "miedo": {
        "preguntas": [
            "¿A qué le tienes miedo ahora mismo?",
            "¿Qué es lo peor que imaginas que podría pasar?",
            "¿Qué te ayudaría a sentirte un poco más seguro/a?",
        ],
        "herramienta": "El juego de los 5 sentidos (5-4-3-2-1)",
    },
    "autoestima": {
        "preguntas": [
            "¿Qué pasó para que pienses eso de ti?",
            "¿Qué le dirías a un amigo que pensara eso de sí mismo?",
            "¿Qué cosas sí te salen bien, aunque sean pequeñas?",
        ],
        "herramienta": "Revisar lo que me digo",
    },
    "enojo": {
        "preguntas": [
            "¿Qué fue lo que te hizo enojar?",
            "¿Qué hiciste cuando sentiste el enojo?",
            "¿Con quién estás enojado/a?",
        ],
        "herramienta": "El semáforo: alto, piensa, actúa",
    },
    "autocuidado": {
        "preguntas": [
            "¿Qué es lo que te quita el sueño en la noche?",
            "¿Usas el celular antes de dormir?",
        ],
        "herramienta": "Respiración 4-7-8 para dormir",
    },
    "rendimiento_academico": {"preguntas": PREGUNTAS_ESTUDIO, "herramienta": "La técnica del tomate (25 y 5)"},
    "procrastinacion": {"preguntas": PREGUNTAS_ESTUDIO, "herramienta": "La técnica del tomate (25 y 5)"},
    "dificultad_academica": {"preguntas": PREGUNTAS_ESTUDIO, "herramienta": "Explicárselo a alguien"},
    "abrumado": {"preguntas": PREGUNTAS_GENERALES, "herramienta": "Respiración 4-4-4"},
    "pensamiento_catastrofico": {"preguntas": PREGUNTAS_GENERALES, "herramienta": "Revisar lo que me digo"},
    "perfeccionismo": {"preguntas": PREGUNTAS_GENERALES, "herramienta": "Revisar lo que me digo"},
    "culpa": {"preguntas": PREGUNTAS_GENERALES, "herramienta": "Revisar lo que me digo"},
    "limites": {"preguntas": PREGUNTAS_GENERALES, "herramienta": "Pedir algo o decir que no, con respeto"},
    "llanto": {"preguntas": PREGUNTAS_GENERALES, "herramienta": "Respirar como un globo"},
    "vacio": {"preguntas": PREGUNTAS_GENERALES, "herramienta": "Un paso pequeño cada día"},
    "apatia": {"preguntas": PREGUNTAS_GENERALES, "herramienta": "Un paso pequeño cada día"},
    "futuro": {"preguntas": PREGUNTAS_GENERALES, "herramienta": "La caja de las preocupaciones"},
    "redes_comparacion": {"preguntas": PREGUNTAS_GENERALES, "herramienta": "Tres cosas buenas"},
    "mejoria": {"preguntas": ["¿Qué crees que te ayudó a sentirte mejor?"], "herramienta": None},
    "apoyo_a_otros": {"preguntas": ["¿Y tú cómo estás con todo esto?"], "herramienta": None},
}

# Para temas sin preguntas propias (confidencialidad, vergüenza, etc.).
PREGUNTAS_ABIERTAS = [
    "¿Quieres contarme un poco más?",
    "¿Qué más te gustaría contarme?",
    "¿Cómo te sientes ahora mismo?",
]

# Palabras que delatan una emoción, para reflejarla ("suena a que te sientes...").
EMOCIONES = [
    (r"\b(triste|tristeza|deprimid[oa]|bajonead[oa])\b", "triste"),
    (r"\b(enojad[oa]|enojo|furios[oa]|rabia|molest[oa])\b", "con mucho enojo"),
    (r"\b(nervios[oa]|nervios|ansios[oa]|ansiedad|angustiad[oa])\b", "con nervios o ansiedad"),
    (r"\b(estresad[oa]|estr[eé]s|presionad[oa])\b", "con mucho estrés"),
    (r"\b(sol[oa]|solitari[oa])\b", "solo/a"),
    (r"\b(cansad[oa]|agotad[oa])\b", "muy cansado/a"),
    (r"\b(miedo|asustad[oa])\b", "con miedo"),
    (r"\b(confundid[oa]|perdid[oa])\b", "confundido/a"),
]

CONTINUACIONES = [
    "Gracias por contarme más.",
    "Te entiendo. Tiene sentido que te sientas así.",
    "Eso que cuentas es importante.",
    "Te sigo escuchando.",
]

# Para respuestas muy cortas ("ok", "no", "sí").
CONTINUACIONES_CORTAS = [
    "Está bien, vamos a tu ritmo.",
    "Te sigo escuchando.",
    "Aquí sigo contigo.",
]

MAX_TURNOS_TEMA = 5  # después de esto el tema se considera cerrado

_estado = {}             # token -> {"tema", "turnos", "herramienta_dada", "textos"}
_preguntas_hechas = {}   # token -> preguntas ya hechas (para no repetir)


def asignar_ids(reglas):
    """Pone id a las reglas que no lo tenían (se llama una vez desde respuestas_bot)."""
    for regla in reglas:
        if not regla.get("id"):
            regla["id"] = IDS_POR_PRIMER_PATRON.get(regla["patrones"][0])


def olvidar(token):
    _estado.pop(token, None)
    _preguntas_hechas.pop(token, None)


def tema_activo(token):
    """Tema del que se venía hablando, si la conversación sigue abierta."""
    estado = _estado.get(token)
    if estado and estado["turnos"] < MAX_TURNOS_TEMA:
        return estado["tema"]
    return None


def reflejar_emocion(texto):
    for patron, emocion in EMOCIONES:
        if re.search(patron, texto):
            return f"Suena a que te sientes {emocion}."
    return None


PALABRAS_COMUNES = {"algo", "pasa", "está", "esto", "todo", "cómo", "para", "hace", "eres", "otra", "otras", "veces", "ahora", "mismo"}
MENCIONA_TIEMPO =r"\b(hace|desde|semanas?|mes(es)?|años?|d[ií]as?|ayer|siempre)\b"


def _ya_respondida(pregunta, texto):
    """True si el mensaje ya contesta la pregunta: si ya dijo cuándo empezó,
    no se pregunta "¿desde cuándo?"; si dijo "en redes", no se pregunta por redes."""
    if "cuándo" in pregunta and re.search(MENCIONA_TIEMPO, texto):
        return True
    palabras = [p for p in re.findall(r"\w{4,}", pregunta.lower()) if p not in PALABRAS_COMUNES]
    return any(re.search(rf"\b{p}\b", texto) for p in palabras)


def _pregunta(token, tema, texto=""):
    opciones = TEMAS.get(tema, {}).get("preguntas") or PREGUNTAS_ABIERTAS
    hechas = _preguntas_hechas.setdefault(token, [])
    nuevas = [p for p in opciones if p not in hechas and not _ya_respondida(p, texto)] or [
        p for p in PREGUNTAS_ABIERTAS if p not in hechas
    ]
    if not nuevas:  # ya se hicieron todas: se empieza de nuevo
        hechas.clear()
        nuevas = list(opciones)
    elegida = random.choice(nuevas)
    hechas.append(elegida)
    return elegida


def responder(token, tema, base, texto, continuacion=False):
    """Arma la respuesta final a partir de la respuesta base de la regla.

    tema: id del tema (o None). continuacion=True cuando el mensaje no trajo
    tema nuevo pero sigue la conversación anterior."""
    estado = _estado.get(token)
    if estado and estado["tema"] == tema:
        estado["turnos"] += 1
    else:
        estado = {"tema": tema, "turnos": 1, "herramienta_dada": False, "textos": []}
        _estado[token] = estado
    # Lo dicho sobre este tema, para no preguntar lo que ya contó antes.
    estado["textos"] = (estado["textos"] + [texto])[-MAX_TURNOS_TEMA:]

    partes = []
    if continuacion:
        corta = len(texto.split()) <= 2
        partes.append(random.choice(CONTINUACIONES_CORTAS if corta else CONTINUACIONES))
        emocion = reflejar_emocion(texto)
        if emocion:
            partes.append(emocion)
    else:
        partes.append(base)

    herramienta = TEMAS.get(tema, {}).get("herramienta")
    if herramienta and estado["turnos"] >= 2 and not estado["herramienta_dada"]:
        partes.append(f"Algo que te puede servir: la herramienta «{herramienta}», en la sección Herramientas.")
        estado["herramienta_dada"] = True
    elif tema == "bullying" and estado["turnos"] >= 2 and not estado["herramienta_dada"]:
        partes.append("Esto es algo que la psicóloga del liceo puede ayudarte a resolver; puedes escribirle de forma anónima.")
        estado["herramienta_dada"] = True

    # Una sola pregunta, al final. Si la respuesta ya pregunta algo, no se agrega otra.
    if not any("?" in parte for parte in partes):
        partes.append(_pregunta(token, tema, " ".join(estado["textos"])))
    return " ".join(partes)
