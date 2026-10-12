"""
Autoevaluaciones informativas (NO son pruebas clínicas ni diagnósticas).

Cada test es una serie de preguntas de opción múltiple con un puntaje (0-3
por respuesta). El resultado SIEMPRE se presenta como una señal para
reflexionar, nunca como una etiqueta o diagnóstico ("tienes ansiedad",
"tienes un trastorno"). Cuando el puntaje es alto, el mensaje invita con
calidez a hablar con la psicóloga — igual que el resto de la plataforma,
nunca se decide nada por la persona, solo se le ayuda a ver un patrón.
"""

TESTS = {
    "habitos_estudio": {
        "titulo": "Mis hábitos de estudio",
        "descripcion": "Para ver qué te ayuda y qué te cuesta al estudiar. No mide qué tan inteligente eres, solo cómo estudias.",
        "preguntas": [
            {
                "texto": "¿Tienes un lugar tranquilo y ordenado para estudiar?",
                "opciones": ["Siempre", "La mayoría de las veces", "Pocas veces", "Casi nunca"],
            },
            {
                "texto": "¿Estudias con tiempo, o dejas todo para el último día?",
                "opciones": ["Con tiempo", "Casi siempre con tiempo", "Muchas veces al último", "Siempre al último"],
            },
            {
                "texto": "Mientras estudias, ¿el celular te distrae?",
                "opciones": ["Casi nunca", "A veces", "Seguido", "Todo el tiempo"],
            },
            {
                "texto": "¿Tomas pequeños descansos cuando estudias mucho tiempo?",
                "opciones": ["Siempre", "La mayoría de las veces", "Pocas veces", "Nunca"],
            },
            {
                "texto": "Después de estudiar, ¿puedes explicar el tema con tus palabras?",
                "opciones": ["Sí, casi siempre", "La mayoría de las veces", "Pocas veces", "Casi nunca"],
            },
            {
                "texto": "¿Duermes bien la noche antes de un examen?",
                "opciones": ["Siempre", "La mayoría de las veces", "Pocas veces", "Casi nunca"],
            },
        ],
        "resultados": [
            (0.75, "Tienes buenos hábitos de estudio: organizas tu tiempo y cuidas tu descanso. Sigue así, y prueba la técnica del tomate si quieres rendir todavía más."),
            (0.45, "Tienes algunas cosas a tu favor y otras que puedes mejorar. Mira las herramientas \"Para estudiar mejor\": organizar tu semana y estudiar en ratos cortos puede cambiar mucho."),
            (0.0, "Estudiar se te está haciendo pesado, y eso le pasa a mucha gente: no significa que no seas capaz. Empieza por una sola herramienta de \"Para estudiar mejor\". Si el estrés por las notas te está afectando, habla con la psicóloga."),
        ],
    },
    "estres": {
        "titulo": "Mi nivel de estrés",
        "descripcion": "Para ver cómo ha estado tu cuerpo y tu cabeza últimamente, no para ponerte una etiqueta.",
        "preguntas": [
            {
                "texto": "En las últimas dos semanas, ¿cómo ha estado tu sueño?",
                "opciones": ["Duermo bien", "Algo irregular", "Me cuesta dormir", "Casi no puedo dormir"],
            },
            {
                "texto": "¿Te cuesta concentrarte en tus tareas o clases?",
                "opciones": ["Nada", "Un poco", "Bastante", "Mucho, no puedo enfocarme"],
            },
            {
                "texto": "¿Te sientes irritable o con los nervios de punta por cosas pequeñas?",
                "opciones": ["Nunca", "A veces", "Seguido", "Casi todo el tiempo"],
            },
            {
                "texto": "¿Has sentido síntomas físicos como dolor de cabeza, de estómago o tensión muscular?",
                "opciones": ["Casi nunca", "A veces", "Seguido", "Casi a diario"],
            },
            {
                "texto": "¿Sientes que tienes más cosas encima de las que puedes manejar?",
                "opciones": ["No", "Un poco", "Bastante", "Siento que no puedo con todo"],
            },
            {
                "texto": "¿Has tenido ganas de alejarte de todo o de todos últimamente?",
                "opciones": ["No", "A veces", "Seguido", "Casi todo el tiempo"],
            },
        ],
        "resultados": [
            (0.75, "Tu nivel de estrés parece estar bastante manejable ahora mismo. Igual, no está de más cuidar tu descanso y tus tiempos de pausa."),
            (0.45, "Traes un nivel de estrés notorio. Nada alarmante todavía, pero es buen momento para bajarle: dormir mejor, soltar una carga, o simplemente hablarlo con alguien."),
            (0.0, "Lo que describes suena a un estrés bastante alto y sostenido — el tipo que, si sigue así, puede afectar tu salud y tu ánimo. No tienes que cargar con esto solo/a; hablar con la psicóloga puede ayudarte a aligerar esto."),
        ],
    },
    "alimentacion": {
        "titulo": "Mi relación con la comida",
        "descripcion": (
            "Esto es una autoevaluación informativa, no un diagnóstico. Si algo de esto te hace "
            "ruido, lo mejor que puedes hacer es hablarlo con la psicóloga — entre antes, más fácil."
        ),
        "preguntas": [
            {
                "texto": "¿Piensas en la comida, en tu peso o en tu cuerpo durante gran parte del día?",
                "opciones": ["Casi nunca", "A veces", "Seguido", "Casi todo el tiempo"],
            },
            {
                "texto": "¿Sientes culpa o ansiedad después de comer?",
                "opciones": ["Nunca", "A veces", "Seguido", "Casi siempre"],
            },
            {
                "texto": "¿Evitas comer frente a otras personas, o escondes cuánto o qué comes?",
                "opciones": ["No", "A veces", "Seguido", "Casi siempre"],
            },
            {
                "texto": "¿Sientes que tu estado de ánimo depende mucho de cómo te ves ese día?",
                "opciones": ["No", "Un poco", "Bastante", "Totalmente"],
            },
            {
                "texto": "¿Alguien cercano te ha comentado que está preocupado por cómo comes o por tu peso?",
                "opciones": ["No", "Una vez", "Más de una vez", "Varias personas, varias veces"],
            },
        ],
        "resultados": [
            (0.75, "Lo que describes suena a una relación tranquila con la comida y tu cuerpo. Sigue cuidando eso."),
            (0.45, "Hay algunas señales de que la comida o tu cuerpo te están pesando más de lo que deberían. No es necesariamente grave, pero sí vale la pena hablarlo con la psicóloga antes de que crezca."),
            (0.0, "Esto que describes merece una conversación real con la psicóloga, pronto. No es un diagnóstico — solo tú y un profesional pueden ver esto con claridad — pero las señales que marcaste son de las que no conviene dejar pasar."),
        ],
    },
}


def obtener_test(test_id):
    return TESTS.get(test_id)


NIVELES = ["bien", "medio", "alerta"]


def calcular_resultado(test_id, respuestas):
    """
    respuestas: lista de índices (0-3) elegidos por pregunta, 0 = mejor, 3 = peor.
    Devuelve (mensaje, nivel) — nivel es solo para estadísticas agregadas
    ("bien"/"medio"/"alerta"), nunca se guarda ninguna respuesta individual.
    """
    test = TESTS.get(test_id)
    if not test or not respuestas:
        return None, None

    maximo_por_pregunta = 3
    puntaje_invertido = sum((maximo_por_pregunta - r) for r in respuestas)
    proporcion = puntaje_invertido / (maximo_por_pregunta * len(respuestas))

    for i, (umbral, mensaje) in enumerate(test["resultados"]):
        if proporcion >= umbral:
            return mensaje, NIVELES[i]
    return test["resultados"][-1][1], NIVELES[-1]


# Video que acompaña algunas autoevaluaciones (ID verificado en YouTube).
TESTS["estres"]["video_youtube_id"] = "Nvtr6Ms4bmo"  # Respiración en 4 tiempos (PrepaTec)
