"""
Generador de mensajes para "¿Qué te gustaría ser en el futuro?".

Es el mismo tipo de motor por reglas que respuestas_bot.py: nada de IA
generativa, solo coincidencia de palabras clave contra una lista curada de
respuestas ya escritas. Si no reconoce lo que el estudiante escribió, cae en
una respuesta genérica cálida que igual usa sus propias palabras.

El filtro de riesgo (filtro_riesgo.py) se aplica ANTES de llamar a este
módulo, desde app.py — aquí solo se genera contenido positivo, nunca se
decide si algo es seguro de mostrar.
"""

import re

ASPIRACIONES = [
    {
        "patrones": [r"m[eé]dic[oa]", r"doctor(a)?"],
        "nombre": "médico/a",
        "texto": (
            "Ser médico/a es dedicar tu vida a algo muy simple y muy grande a la vez: que la gente sufra "
            "menos y viva mejor. Vas a estar presente en los momentos más difíciles de las personas, y "
            "también en los más felices, como cuando alguien se recupera o nace una vida nueva. Pocas cosas "
            "se sienten tan reales como poder ayudar a alguien con tus propias manos y lo que sabes."
        ),
    },
    {
        "patrones": [r"enfermer[oa]"],
        "nombre": "enfermero/a",
        "texto": (
            "Ser enfermero/a es estar ahí justo en los momentos en que más se necesita a alguien: sosteniendo "
            "una mano, explicando con paciencia, cuidando incluso cuando nadie más está mirando. La gente "
            "recuerda toda su vida a quien la cuidó bien en un momento difícil — y esa persona puedes ser tú."
        ),
    },
    {
        "patrones": [r"maestr[oa]", r"profesor(a)?", r"docente"],
        "nombre": "maestro/a",
        "texto": (
            "Ser maestro/a es una de las formas más silenciosas y poderosas de cambiar el mundo: un salón de "
            "clases a la vez. Vas a ser, para algunos estudiantes, la razón por la que entendieron que sí "
            "podían, o la persona que les creyó cuando nadie más lo hacía. Años después, alguien va a recordar "
            "tu nombre y decir 'ella/él me ayudó a llegar hasta aquí'."
        ),
    },
    {
        "patrones": [r"psic[oó]log[oa]", r"terapeuta"],
        "nombre": "psicólogo/a",
        "texto": (
            "Ser psicólogo/a es aprender a escuchar de verdad — no para arreglar a la gente, sino para "
            "acompañarla mientras se entiende a sí misma. Ayudar a que una persona deje de sentirse sola con "
            "lo que carga es un trabajo profundamente humano, y tú ya sabes lo que se siente necesitar que "
            "alguien te escuche así."
        ),
    },
    {
        "patrones": [r"ingenier[oa]"],
        "nombre": "ingeniero/a",
        "texto": (
            "Ser ingeniero/a es convertir problemas reales en soluciones que la gente usa todos los días, "
            "muchas veces sin darse cuenta de todo el pensamiento detrás. Tu forma de pensar puede hacerle la "
            "vida más fácil a muchísimas personas. Es un camino para quienes disfrutan entender cómo funcionan "
            "las cosas y mejorarlas."
        ),
    },
    {
        "patrones": [r"abogad[oa]", r"\bderecho\b"],
        "nombre": "abogado/a",
        "texto": (
            "Ser abogado/a es ponerte del lado de alguien cuando más lo necesita, cuando siente que el sistema "
            "es más grande que él o ella. Vas a defender causas y a veces ser la única voz que alguien tiene en "
            "un momento difícil. Es un camino para quienes creen que la justicia vale la pena pelearla."
        ),
    },
    {
        "patrones": [r"veterinari[oa]"],
        "nombre": "veterinario/a",
        "texto": (
            "Ser veterinario/a es cuidar a quienes no pueden explicar con palabras que algo les duele, y aun "
            "así confían en ti completamente. Ese amor incondicional que reciben los animales, tú vas a poder "
            "devolverlo cuidándolos."
        ),
    },
    {
        "patrones": [r"militar", r"soldado", r"ej[eé]rcito"],
        "nombre": "militar",
        "texto": (
            "Ser militar es elegir un camino de disciplina, servicio y sacrificio por algo más grande que uno "
            "mismo: tu país y la gente que lo forma. Es exigente, pero también forja un carácter fuerte y un "
            "profundo sentido de honor y hermandad con quienes caminan a tu lado. Ya estás en un liceo militar "
            "— probablemente ya conoces algo de esa disciplina, y eso también es parte del camino."
        ),
    },
    {
        "patrones": [r"pilot[oa]"],
        "nombre": "piloto",
        "texto": (
            "Ser piloto es una mezcla poco común de precisión técnica y libertad: llevar a cientos de personas "
            "de un lugar a otro, con la responsabilidad de que lleguen bien y la emoción de ver el mundo desde "
            "arriba. Es un camino para quienes disfrutan la disciplina tanto como el asombro de volar."
        ),
    },
    {
        "patrones": [r"polic[ií]a"],
        "nombre": "policía",
        "texto": (
            "Ser policía es elegir proteger a otros incluso cuando eso significa exponerte tú primero. Vas a "
            "estar presente en los momentos en que la gente más necesita sentirse segura. Es un camino que "
            "exige valentía todos los días, no solo una vez."
        ),
    },
    {
        "patrones": [r"bomber[oa]"],
        "nombre": "bombero/a",
        "texto": (
            "Ser bombero/a es correr hacia el peligro cuando todos los demás corren en dirección contraria, "
            "para salvar vidas y hogares. Pocas profesiones dejan una huella tan directa y visible de ayuda a "
            "la comunidad."
        ),
    },
    {
        "patrones": [r"arquitect[oa]"],
        "nombre": "arquitecto/a",
        "texto": (
            "Ser arquitecto/a es diseñar los espacios donde la gente va a vivir su vida: sus casas, sus "
            "escuelas, los lugares donde van a ser felices o van a crecer. Cada diseño tuyo puede mejorar la "
            "forma en que alguien vive su día a día."
        ),
    },
    {
        "patrones": [r"cient[ií]fic[oa]", r"investigador(a)?"],
        "nombre": "científico/a",
        "texto": (
            "Ser científico/a es dedicarte a hacer las preguntas que todavía nadie ha respondido. Cada pequeño "
            "descubrimiento tuyo puede sumarse a algo mucho más grande: una cura, una tecnología, una mejor "
            "forma de entender el mundo."
        ),
    },
    {
        "patrones": [r"artista", r"pintor(a)?", r"dibujante"],
        "nombre": "artista",
        "texto": (
            "Ser artista es encontrar una forma de decir lo que a veces no se puede decir solo con palabras. Tu "
            "arte puede hacer que alguien se sienta menos solo/a al ver algo que refleja justo lo que sentía."
        ),
    },
    {
        "patrones": [r"m[uú]sic[oa]", r"cantante"],
        "nombre": "músico/a",
        "texto": (
            "Ser músico/a es crear algo que puede acompañar a otra persona en su peor día y en su mejor día "
            "también. Una canción tuya puede terminar significando algo enorme para alguien que ni siquiera "
            "conoces."
        ),
    },
    {
        "patrones": [r"deportista", r"atleta", r"futbolista", r"jugador(a)? de"],
        "nombre": "deportista",
        "texto": (
            "Ser deportista es aprender, antes que nada, disciplina y constancia: presentarte a entrenar "
            "incluso los días en que no tienes ganas. Ese esfuerzo silencioso, sostenido en el tiempo, también "
            "te va a enseñar a levantarte después de perder."
        ),
    },
    {
        "patrones": [r"chef", r"cociner[oa]", r"cocinar"],
        "nombre": "chef",
        "texto": (
            "Ser chef es una forma muy concreta de cuidar a la gente: alimentarla bien y, muchas veces, darle "
            "un momento feliz alrededor de una mesa. La comida guarda recuerdos — vas a poder crear los tuyos "
            "para otras personas."
        ),
    },
    {
        "patrones": [r"escritor(a)?", r"escribir libros"],
        "nombre": "escritor/a",
        "texto": (
            "Ser escritor/a es poner en palabras lo que muchos sienten pero no saben cómo decir. Un libro tuyo "
            "podría ser justo lo que alguien necesitaba leer en el momento correcto de su vida."
        ),
    },
    {
        "patrones": [r"programador(a)?", r"desarrollador(a)?", r"ingenier[oa] (en|de) sistemas"],
        "nombre": "programador/a",
        "texto": (
            "Ser programador/a es construir herramientas que otras personas van a usar para resolver problemas "
            "reales, muchas veces sin ver todo el trabajo detrás. Es resolver acertijos todos los días — y ver "
            "cómo algo que empezó como una idea tuya termina funcionando de verdad."
        ),
    },
    {
        "patrones": [r"astronauta"],
        "nombre": "astronauta",
        "texto": (
            "Ser astronauta es de los sueños más grandes que existen: representar a toda la humanidad mirando "
            "la Tierra desde afuera. Exige muchísima disciplina y estudio, pero también recuerda que soñar en "
            "grande, incluso desde donde estás ahora, siempre vale la pena."
        ),
    },
    {
        "patrones": [r"buena persona", r"alguien bueno"],
        "nombre": "una buena persona",
        "texto": (
            "Querer ser una buena persona es, quizás, la meta más importante de todas — y la mejor parte es "
            "que no depende de ninguna profesión: depende de tus decisiones de todos los días. Ya vas por buen "
            "camino solo por estar pensando en esto."
        ),
    },
    {
        "patrones": [r"ayudar a (los dem[aá]s|otros|la gente)", r"servir a los dem[aá]s"],
        "nombre": "alguien que ayuda a los demás",
        "texto": (
            "Querer dedicar tu vida a ayudar a otros es un propósito hermoso, sin importar la forma exacta que "
            "tome después. El mundo necesita más personas que piensen así, y tú ya tienes esa intención, que es "
            "el primer paso."
        ),
    },
    {
        "patrones": [r"\bfeliz\b"],
        "nombre": "feliz",
        "texto": (
            "Querer ser feliz no es una meta pequeña — es, en el fondo, la meta de todas las demás. No tienes "
            "que tenerlo resuelto ya: la felicidad se construye en cosas pequeñas, en la gente que eliges tener "
            "cerca, y en cómo te tratas a ti mismo/a en el camino."
        ),
    },
    {
        "patrones": [r"\bmam[aá]\b", r"\bpap[aá]\b"],
        "nombre": "mamá o papá",
        "texto": (
            "Querer formar una familia algún día es un sueño profundamente humano. Vas a poder darle a alguien "
            "más el amor y el cuidado que ojalá también hayas sentido tú — y eso, con el tiempo, puede sanar "
            "mucho."
        ),
    },
]

RESPUESTA_GENERICA = (
    "Querer ser {texto} dice algo hermoso de ti: significa que ya tienes un sueño con el que soñar "
    "despierto/a. No hace falta tenerlo todo resuelto todavía — lo bonito es que ya empezaste a imaginar "
    "quién quieres llegar a ser. Sigue dándole forma a eso, un paso a la vez; el camino para llegar ahí "
    "también va a formar parte de tu historia."
)


def generar_mensaje_futuro(texto_usuario):
    """Devuelve (nombre_bonito, mensaje) para lo que el estudiante escribió."""
    texto = texto_usuario.lower().strip()

    for aspiracion in ASPIRACIONES:
        for patron in aspiracion["patrones"]:
            if re.search(patron, texto):
                return aspiracion["nombre"], aspiracion["texto"]

    return texto_usuario, RESPUESTA_GENERICA.format(texto=texto_usuario)
