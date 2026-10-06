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
        "imagen": "images/avatares/avatar_chica.png",
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
        "imagen": "images/avatares/avatar_realista.webp",
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
        "imagen": "images/avatares/avatar_lego.png",
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
        "id": "apoyo_a_otros",
        "patrones": [r"\bayudar a (alguien|mi amigo)\b", r"\btodos vienen a m[ií] con sus problemas\b", r"\bnadie me escucha a m[ií]\b", r"\bmi amigo depende demasiado de m[ií]\b", r"\bdejar sola a mi amiga\b"],
        "respuestas": [
            "Debe ser agotador estar disponible para todos y sentir que nadie está ahí cuando tú lo necesitas. Tú también mereces ser escuchado/a.",
            "Es válido poner límites. Puedes decir: \"te quiero ayudar, pero ahora yo también necesito descansar\". Ayudar a otros no significa abandonarte a ti mismo/a.",
            "Puedes querer mucho a tu amigo/a y aun así no ser responsable de mantenerlo/a emocionalmente estable. Si está en riesgo real, es importante involucrar a un adulto cuanto antes — no tienes que cargar solo/a con algo tan serio.",
            "No necesitas tener las palabras perfectas para acompañar a alguien. Puedes decir: \"estoy aquí contigo, ¿buscamos ayuda juntos?\".",
        ],
    },
    {
        "patrones": [r"\btriste\b", r"\bmal\b", r"\bdeprimid[oa]\b", r"\bsin ganas\b", r"\bya no disfruto\b", r"\btan sensible\b", r"\bcualquier cosa me hace llorar\b"],
        "respuestas": [
            "Gracias por contarlo. Sentirte así no significa que algo esté mal contigo — a veces solo necesitamos hablarlo. ¿Quieres contarme desde cuándo te sientes así?",
            "Entiendo que no es fácil. Está bien no estar bien todo el tiempo. ¿Hay algo puntual que haya pasado?",
            "Lo que sientes es válido. No tienes que explicarlo perfecto, solo cuéntame a tu ritmo.",
            "Cuando dejamos de disfrutar cosas que antes nos gustaban vale la pena prestar atención. No significa que tengas algo grave, pero sí es una señal para cuidarte. ¿Desde cuándo lo notas?",
            "A veces las emociones se acumulan poco a poco hasta que sentimos todo con más intensidad. No significa que estés exagerando — quizá necesitas descansar y hablar un poco de lo que estás viviendo.",
        ],
    },
    {
        "patrones": [
            r"\bestr[eé]s\b", r"\bexamen(es)?\b", r"\bnervios\b", r"\bpresi[oó]n\b",
            r"\bme quedo en blanco\b", r"\bhablar frente a (la )?clase\b",
            r"\bcoraz[oó]n.*r[aá]pido\b", r"\bnudo en la garganta\b",
        ],
        "respuestas": [
            "Los exámenes pueden pesar mucho. Algo que ayuda a bajar la ansiedad es respirar lento 4 segundos, sostener 4, soltar 4. ¿Quieres contarme qué es lo que más te preocupa de esto?",
            "Es normal sentir presión antes de algo importante. ¿Qué parte se te hace más difícil ahora mismo?",
            "Un examen no define lo que vales. Vamos paso a paso: ¿qué es lo primero que te agobia?",
            "Quedarte en blanco no significa que no hayas estudiado — los nervios pueden interferir un momento con la memoria. Si pasa, detente unos segundos, respira, y empieza por lo que sí recuerdes.",
            "Hablar frente a otros genera ansiedad en mucha gente. Podemos practicar respiración y prepararte poco a poco para que se sienta menos pesado.",
            "El estrés y la ansiedad también se sienten en el cuerpo — un nudo en la garganta, el corazón acelerado. Si eso es muy frecuente o te cuesta respirar de verdad, también vale la pena comentarlo con un profesional de salud.",
        ],
    },
    {
        "id": "rendimiento_academico",
        "patrones": [r"\bnotas (est[aá]n )?bajando\b", r"\bbajaron mis notas\b", r"\bmalas notas\b", r"\bsaco malas notas\b", r"\bsi saco una mala nota\b"],
        "respuestas": [
            "Una bajada en las calificaciones no significa que hayas perdido tu capacidad. Puede haber cansancio, estrés o dificultad para entender algún tema. Veamos juntos qué está pasando.",
            "Entiendo lo frustrante que es esforzarte y no ver el resultado que esperabas. Antes de pensar que no eres bueno/a para estudiar, revisemos cómo estás estudiando — a veces no hace falta más horas, sino una forma distinta de aprender.",
            "Una calificación mide tu desempeño en algo puntual, no tu valor ni toda tu capacidad. Te dice qué reforzar, no quién eres.",
        ],
    },
    {
        "patrones": [r"\bmolestan\b", r"\bbullying\b", r"\bse burlan\b", r"\bacoso\b", r"\btodos se r[ií]en\b"],
        "respuestas": [
            "Lo que describes no está bien, y no es tu culpa. ¿Quieres que le cuente a la psicóloga para que te ayude con esto directamente?",
            "Nadie merece que lo traten así. Mereces sentirte seguro/a en tu propio liceo. ¿Desde cuándo pasa esto?",
            "Que se rían cuando participas puede afectar mucho tu confianza. Si son burlas repetidas, es importante contárselo a un adulto responsable — no tienes que soportarlo en silencio.",
        ],
    },
    {
        "id": "conflicto_padres",
        "patrones": [r"\bse est[aá]n separando\b", r"\bse van a divorciar\b", r"\bdivorcio\b", r"\bpadres pelean\b", r"\bpelean demasiado\b"],
        "respuestas": [
            "Una separación puede traer tristeza, enojo, miedo y confusión al mismo tiempo. Recuerda algo importante: los problemas entre los adultos no son responsabilidad de los hijos.",
            "Vivir discusiones constantes en casa puede generar mucho estrés. Antes que nada quiero saber: ¿tú y las demás personas en casa están seguros? Si hay violencia o amenazas, busca ahora mismo a un adulto de confianza.",
        ],
    },
    {
        "patrones": [r"\bfamilia\b", r"\bpap[aá]\b", r"\bmam[aá]\b", r"\bcasa\b", r"\bpadres\b"],
        "respuestas": [
            "Los temas de familia a veces son los más difíciles de hablar. Estoy aquí para escuchar, sin juzgar. ¿Qué está pasando?",
            "A veces en casa es donde más cuesta que nos entiendan. Cuéntame qué pasó.",
            "Que te comparen con otras personas puede afectar mucho tu autoestima. Cada quien tiene habilidades y ritmos distintos — no tienes que seguir exactamente el mismo camino que nadie más.",
            "Sentir que tienes que cumplir las expectativas de tu familia puede pesar mucho. ¿Qué expectativa sientes que está pesando más sobre ti ahora mismo?",
        ],
    },
    {
        "patrones": [r"\bsolo\b", r"\bsola\b", r"\bnadie me entiende\b", r"\baislad[oa]\b", r"\bnadie me quiere\b"],
        "respuestas": [
            "Sentirte solo/a pesa mucho, aunque estés rodeado/a de gente. Aquí no lo estás, ahora mismo alguien te está leyendo.",
            "Eso que sientes es más común de lo que parece. ¿Desde hace cuánto te sientes así?",
            "Sé que ahora mismo esa sensación puede parecer completamente real, pero una emoción no siempre representa toda la realidad. Que te sientas así no significa que no le importes a nadie. ¿Qué pasó para que te sintieras así?",
        ],
    },
    {
        "patrones": [r"\bcansad[oa]\b", r"\bagotad[oa]\b", r"\bfingir que estoy bien\b", r"\btodos creen que soy feliz\b"],
        "respuestas": [
            "Sentirte agotado/a así también es una señal de que necesitas descanso de verdad, no solo dormir. ¿Qué es lo que más te está desgastando?",
            "El cansancio que no se quita con dormir suele ser emocional. Cuéntame qué ha estado pasando.",
            "No tienes que fingir aquí. Puedes decir cómo te sientes en realidad, sin esconderlo.",
        ],
    },
    {
        "patrones": [
            r"\bmiedo\b", r"\basustad[oa]\b", r"\bansiedad\b",
            r"\bmiedo de salir\b", r"\bmiedo de estar solo\b", r"\balgo malo pase\b",
            r"\bme van a castigar\b",
        ],
        "respuestas": [
            "El miedo es una señal, no una debilidad. ¿Me cuentas a qué le tienes miedo ahora mismo?",
            "Está bien sentir miedo. Vamos a ir despacio: ¿qué es lo que más te preocupa?",
            "Equivocarse no significa que seas incapaz — significa que estás aprendiendo. No tienes que hacerlo todo perfecto.",
            "Pedir ayuda a la psicóloga no es nada de lo que avergonzarse. La salud emocional es parte de la salud, igual que cualquier otra.",
            "Antes de decidir qué hacer, podemos pensar juntos en qué ocurrió y qué adulto de confianza podría ayudarte a manejarlo de forma segura. Si existe peligro real, tu seguridad siempre es la prioridad.",
        ],
    },
    {
        "patrones": [r"\bno sirvo\b", r"\bsoy un[a]? fracas[oa]\b", r"\bno valgo\b", r"\bno soy (suficientemente )?inteligente\b", r"\btodos son mejores que yo\b", r"\bnunca hago nada bien\b"],
        "respuestas": [
            "Eso que piensas de ti mismo/a no es un hecho, es una idea que a veces se instala cuando estamos mal. No es cierto. ¿Qué pasó para que te sientas así?",
            "La inteligencia no se mide solo con notas. Hay distintas formas de aprender y resolver problemas — tener dificultad en algo no significa que no seas capaz.",
            "Compararte todo el tiempo hace que olvides tus propias capacidades. En vez de preguntarte quién es mejor, ¿qué te gustaría mejorar en ti?",
            "Cuando estamos frustrados, un error se puede sentir como una conclusión sobre toda tu vida. ¿Qué fue específicamente lo que salió mal? Eso es distinto a decir que haces todo mal.",
        ],
    },
    {
        "id": "autocuidado",
        "patrones": [r"\bno duermo\b", r"\bmal dormid[oa]\b", r"\bno tengo hambre\b", r"\bno como\b", r"\bno me cuido\b", r"\bno puedo dormir\b", r"\bduermo demasiado\b"],
        "respuestas": [
            "Cuidar lo básico —dormir, comer algo, tomar agua— no arregla todo, pero sí te ayuda a sostenerte mientras trabajas el resto. ¿Cómo has estado durmiendo últimamente?",
            "Cuando algo pesa mucho, hasta comer o dormir bien se vuelve difícil. Es una señal más de que necesitas apoyo, no de que algo esté mal contigo. ¿Desde cuándo notas esto?",
            "Cuando la mente se queda muy activa de noche, cuesta descansar. Podemos revisar qué pensamientos aparecen y armar una rutina que ayude a bajar el ritmo antes de dormir.",
        ],
    },
    {
        "id": "hobbies",
        "patrones": [r"\baburrid[oa]\b", r"\bno s[eé] qu[eé] hacer\b", r"\btodo el (d[ií]a|tiempo) pensando\b", r"\bno dejo de pensar\b", r"\bno puedo concentrarme\b", r"\bme cuesta concentrarme\b"],
        "respuestas": [
            "A veces ayuda tener algo que hacer con las manos o la cabeza, para no darle tantas vueltas a lo mismo. ¿Has probado dibujar, escribir, hacer ejercicio, tocar algún instrumento o alguna manualidad? No tiene que salirte bien, solo distraerte un rato.",
            "Aprender algo nuevo, aunque sea pequeño, ayuda a que la mente descanse un poco de lo que pesa. ¿Te llama la atención algo como el deporte, la música, el dibujo o cocinar?",
            "La concentración se ve afectada por estrés, cansancio o preocupaciones — no es falta de voluntad. ¿Cuándo notas que más te cuesta concentrarte?",
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
        "id": "enojo",
        "patrones": [r"\benojad[oa]\b", r"\bno puedo controlar mi enojo\b", r"\bme arrepiento.*enojo\b"],
        "respuestas": [
            "El enojo muchas veces esconde otra emoción debajo: tristeza, miedo, cansancio. No significa que seas una mala persona. ¿Qué situaciones te están provocando ese enojo?",
            "Que te cueste controlar el enojo no significa que no puedas aprenderlo. Podemos identificar qué señales aparecen antes de explotar, para detenerte un poco antes.",
            "Es bueno que puedas reconocerlo. No se trata de fingir que nunca te enojas, sino de aprender a responder sin que te haga daño a ti ni a otros.",
        ],
    },
    {
        "id": "llanto",
        "patrones": [r"\bllorando\b", r"\bno puedo parar de llorar\b", r"\bno quiero llorar porque estoy en el colegio\b"],
        "respuestas": [
            "Está bien llorar. No tienes que disculparte por tener emociones. Si puedes, siéntate, respira lento, y date unos minutos antes de contarme qué pasó.",
            "Si necesitas llorar no tienes que sentir vergüenza. Busca un lugar seguro si lo necesitas — tus emociones no desaparecen solo porque estés en el colegio.",
        ],
    },
    {
        "id": "vacio",
        "patrones": [r"\bvac[ií]o\b"],
        "respuestas": [
            "Gracias por decirlo. Esa sensación puede ser difícil de explicar y no tienes que encontrar las palabras perfectas. ¿Desde cuándo te sientes así?",
        ],
    },
    {
        "id": "apatia",
        "patrones": [r"\bno tengo ganas de hacer nada\b", r"\bno quiero hacer nada\b"],
        "respuestas": [
            "Cuando perdemos las ganas incluso de lo que antes disfrutábamos, suele ser señal de que algo emocional está pesando. No tienes que resolverlo todo hoy — ¿cómo te has sentido, sobre todo al despertar?",
        ],
    },
    {
        "id": "rechazo_escolar",
        "patrones": [r"\bno quiero (ir|venir) al (colegio|liceo|escuela)\b"],
        "respuestas": [
            "Gracias por contarlo. A veces las ganas de evitar el colegio vienen de problemas académicos, sociales, familiares o emocionales. No quiero asumir qué te pasa — cuéntame qué es lo que más te preocupa de ir.",
        ],
    },
    {
        "id": "pareja",
        "patrones": [r"\bnovi[oa]\b", r"\brevisa (el|mi) tel[eé]fono\b", r"\bcelos[oa]\b", r"\bterminamos\b", r"\bextra[ñn]o a alguien\b"],
        "respuestas": [
            "Las relaciones pueden traer emociones muy intensas, sobre todo cuando estamos aprendiendo a comunicarnos y poner límites. Cuéntame qué ocurrió, sin que te juzgue.",
            "Una relación sana necesita confianza y respeto por tu privacidad. Que alguien sea tu pareja no le da derecho automático a revisar tus conversaciones o contraseñas.",
            "Los celos pueden aparecer, pero controlar con quién hablas o dónde estás no es una forma sana de manejarlos. Mereces una relación basada en confianza.",
            "Una ruptura puede sentirse como una pérdida real. No tienes que superarlo de inmediato — date permiso de sentir y busca compañía de alguien que te haga sentir seguro/a.",
            "Puedes extrañar a alguien y al mismo tiempo reconocer que esa relación te hizo daño. Las emociones no siempre siguen la lógica — extrañarlo no significa que tengas que volver.",
        ],
    },
    {
        "id": "imagen_corporal",
        "patrones": [r"\bodio mi cuerpo\b", r"\bme siento fe[oa]\b", r"\bmirarme al espejo\b", r"\bcomentario sobre mi cuerpo\b", r"\btodos son m[aá]s bonitos\b", r"\bninguna foto de m[ií]\b", r"\bsubir fotos porque van a criticarme\b"],
        "respuestas": [
            "Tu cuerpo no necesita cumplir un estándar para merecer respeto. Los comentarios y las redes sociales pueden hacer muy difícil sentirse cómodo con la apariencia — podemos trabajar en una relación más amable con tu cuerpo.",
            "Tu apariencia no determina tu valor. ¿Qué hizo que hoy te sintieras así contigo mismo/a?",
            "Las redes muestran momentos seleccionados, no la vida completa de nadie. Compararte con esa versión editada puede ser muy injusto contigo.",
            "El miedo a la opinión de otros puede ser muy fuerte, pero publicar algo no debería ser una prueba de tu valor. Tienes derecho a proteger tu privacidad.",
            "Aunque la otra persona diga que era una broma, los comentarios sobre el cuerpo pueden dejar huella. Que alguien opine sobre tu apariencia no lo hace verdad.",
        ],
    },
    {
        "id": "alimentacion_cuidado",
        "patrones": [r"\bdejar de comer para adelgazar\b", r"\bme siento demasiado gord[oa]\b", r"\bculpable después de comer\b", r"\bno quiero comer delante de\b", r"\brevisar mi peso\b", r"\bobsesionad[oa] con las calor[ií]as\b", r"\bno puedo parar de pensar en mi peso\b"],
        "respuestas": [
            "Entiendo que quieras sentirte cómodo/a con tu cuerpo, pero dejar de alimentarte bien puede hacerte daño. Tu cuerpo necesita energía para estudiar y crecer. Si estás restringiendo mucho tu comida, hablemos con un adulto de confianza y un profesional de salud.",
            "Comer no es algo por lo que debas sentir culpa. Si esa culpa aparece seguido, sería importante hablarlo con un profesional que te pueda ayudar bien.",
            "Cuando el peso ocupa gran parte de tu mente, puede afectar tu autoestima y tu relación con la comida. No tienes que manejar esto solo/a — mereces apoyo sin ser juzgado/a.",
        ],
    },
    {
        "id": "futuro",
        "patrones": [r"\bmiedo (a|de) (mi )?futuro\b", r"\bno s[eé] qu[eé] (quiero )?estudiar\b", r"\bdesperdiciando mi vida\b", r"\bmiedo de lo que pueda pasar ma[ñn]ana\b"],
        "respuestas": [
            "Es comprensible sentir incertidumbre por el futuro, sobre todo cuando sientes que tienes que decidir una carrera o cumplir expectativas. No tienes que tener toda tu vida resuelta ahora.",
            "No saberlo todavía no significa que estés atrasado/a. Elegir qué estudiar es un proceso — puedes explorar tus intereses y habilidades antes de decidir.",
            "No podemos controlar todo el futuro, pero sí lo que está bajo tu control hoy. ¿Qué puedes hacer esta noche para ayudar a tu yo de mañana?",
        ],
    },
    {
        "id": "confidencialidad",
        "patrones": [r"\bnadie sepa lo que te estoy contando\b", r"\bnunca le he contado a nadie\b"],
        "respuestas": [
            "Entiendo tu preocupación por la privacidad. Aquí se respeta la confidencialidad, dentro de ciertos límites: si existe un riesgo serio de que tú u otra persona puedan sufrir daño, es necesario buscar ayuda y protección.",
            "Puedes contarme lo que necesites, a tu ritmo. Si se trata de algo que pone en riesgo tu seguridad o la de alguien más, será importante involucrar a un adulto responsable para protegerte.",
        ],
    },
    {
        "id": "verguenza",
        "patrones": [r"\bverg[uü]enza\b"],
        "respuestas": [
            "No tienes que convertirte de golpe en alguien súper sociable. La seguridad social se construye poco a poco, paso a paso.",
            "Pedir ayuda no es algo de lo que avergonzarse. Reconocer que necesitas apoyo requiere valentía, no debilidad.",
            "No tienes que sentir vergüenza por pedir ayuda. Puedes contar solo lo que estés listo/a para contar.",
        ],
    },
    {
        "id": "no_preocupar",
        "patrones": [r"\bno quiero preocupar a nadie\b", r"\bno quiero preocupar a mis amigos\b"],
        "respuestas": [
            "Entiendo que quieras proteger a las personas que quieres, pero no tienes que cargar solo/a con todo para evitarlo. A quienes te quieren les gustaría saber que estás pasando un momento difícil, para poder apoyarte.",
        ],
    },
    {
        "id": "confusion_emocional",
        "patrones": [r"\bno s[eé] qu[eé] siento\b", r"^no s[eé]\.?$"],
        "respuestas": [
            "Está bien no tener una respuesta clara. A veces sabemos que algo no anda bien antes de poder ponerle nombre. ¿Qué notas en tu cuerpo o en tus pensamientos últimamente?",
            "No pasa nada. Podemos ir poco a poco. ¿Cómo te has sentido hoy?",
        ],
    },
    {
        "id": "solo_escuchar",
        "patrones": [r"\bsolo necesito que alguien me escuche\b", r"\bnecesito que me escuchen\b"],
        "respuestas": [
            "Claro. No siempre necesitamos una solución inmediata — a veces necesitamos sentir que podemos hablar sin ser juzgados. Te escucho.",
        ],
    },
    {
        "id": "sin_problema_grave",
        "patrones": [r"\bno tenga un problema grave\b", r"\bsin un problema grave\b", r"\bsuficientemente importante para pedir ayuda\b"],
        "respuestas": [
            "Claro que puedes escribir aunque no sea una crisis. No necesitas esperar a estar completamente agotado/a para pedir ayuda — si algo afecta tu sueño, tus estudios o tu tranquilidad, ya merece ser escuchado.",
        ],
    },
    {
        "id": "como_empezar",
        "patrones": [r"\bno s[eé] c[oó]mo empezar\b", r"\bno s[eé] por d[oó]nde empezar\b"],
        "respuestas": [
            "Empieza por lo más sencillo: \"Últimamente me siento...\" y termina la frase con lo primero que venga a tu mente. No necesitas encontrar las palabras perfectas.",
            "No necesitas cambiar todo de una vez. Elige una sola cosa pequeña que puedas hacer hoy — los cambios grandes empiezan con pasos pequeños y constantes.",
        ],
    },
    {
        "id": "validacion",
        "patrones": [r"\best[aá] mal sentirme as[ií]\b", r"\bsi aparentemente todo est[aá] bien\b", r"\bexagerando\b"],
        "respuestas": [
            "No necesariamente. Las emociones no son buenas ni malas — son señales de que algo está pasando. Lo importante es aprender a entenderlas.",
            "Puedes sentirte mal aunque desde afuera parezca que todo está bien. No necesitamos preguntarnos si \"tienes derecho\" a sentirte así, sino qué necesitas ahora.",
            "No quiero decirte que estás exagerando sin conocer la situación. Tus sentimientos son válidos — cuéntame qué pasó y podemos verlo juntos.",
        ],
    },
    {
        "id": "mejoria",
        "patrones": [r"\bme siento mejor\b"],
        "respuestas": [
            "Me alegra que hablar haya ayudado un poco. Puedes construir, además de esto, una red de personas con quienes hablar antes de que las cosas se sientan demasiado pesadas.",
        ],
    },
    {
        "id": "pensamiento_catastrofico",
        "patrones": [r"\bsiempre pienso en lo peor\b", r"\bno puedo dejar de pensar en algo que pas[oó]\b"],
        "respuestas": [
            "A veces la mente imagina los peores escenarios como forma de protegerse, pero termina manteniéndonos en alerta todo el tiempo. Podemos practicar cómo cuestionar esos pensamientos.",
            "Cuando algo nos afecta profundamente, la mente puede volver una y otra vez al mismo recuerdo. No significa que quieras quedarte en el pasado — podemos trabajar en procesarlo.",
        ],
    },
    {
        "id": "culpa",
        "patrones": [r"\bme arrepiento de algo\b", r"\bno puedo perdonarme\b", r"\bsiento culpa por todo\b", r"\btodo es mi culpa\b", r"\bme siento culpable\b"],
        "respuestas": [
            "Sentir arrepentimiento duele, pero también puede enseñarnos. Si puedes reparar lo que hiciste, pensemos cómo. Y si ya no se puede cambiar, trabajemos en aprender sin castigarte para siempre.",
            "Perdonarte no es decir que lo ocurrido estuvo bien — es reconocerlo, aprender, y dejar de castigarte eternamente por algo que ya pasó.",
            "La culpa puede aparecer incluso sin ser realmente tu responsabilidad. ¿Era algo que estaba bajo tu control? ¿Qué parte sí puedes reparar?",
        ],
    },
    {
        "id": "limites",
        "patrones": [r"\bme cuesta decir que no\b", r"\bse enojen conmigo si digo que no\b", r"\btodos se aprovechan de m[ií]\b", r"\bno s[eé] (c[oó]mo )?poner l[ií]mites\b"],
        "respuestas": [
            "Aprender a poner límites puede dar miedo, sobre todo si estás acostumbrado/a a complacer a otros. Decir \"no\" no te hace mala persona — tus límites también merecen respeto.",
            "Una relación sana permite que expreses tus límites sin sentir que tienes que aceptarlo todo para conservar a alguien cerca.",
            "Puedes empezar con frases simples: \"no me siento cómodo/a con eso\", \"prefiero no hacerlo\", \"necesito pensarlo\". No necesitas una explicación enorme para que un límite sea válido.",
        ],
    },
    {
        "id": "confianza",
        "patrones": [r"\bme cuesta confiar\b", r"\bme traicion[oó]\b", r"\bme qued[eé] sin amigos\b", r"\balejando a las personas\b"],
        "respuestas": [
            "Si has vivido situaciones donde te lastimaron o traicionaron, tiene sentido que tu mente quiera protegerte. No tienes que confiar de inmediato — la confianza se construye poco a poco.",
            "Una traición puede doler muchísimo, sobre todo viniendo de alguien en quien confiabas. Tienes derecho a sentir tristeza o enojo — date tiempo antes de decidir algo.",
            "En vez de etiquetarte como \"el problema\", podemos revisar qué ocurre exactamente en tus relaciones y qué patrones se repiten.",
        ],
    },
    {
        "id": "miedo_abandono",
        "patrones": [r"\bmiedo.*me abandonen\b", r"\balguien me responda siempre\b", r"\bpienso que est[aá] enojado conmigo\b", r"\breviso.*si alguien est[aá] conectado\b"],
        "respuestas": [
            "Ese miedo puede hacer que busquemos confirmación constante de que las personas van a quedarse. Podemos trabajar en construir seguridad emocional sin depender completamente de que alguien más nos tranquilice.",
            "Nuestra mente puede llenar los silencios con explicaciones negativas. Antes de asumir que alguien está molesto, pregúntate: ¿qué evidencia tengo realmente de eso?",
        ],
    },
    {
        "id": "redes_comparacion",
        "patrones": [r"\bredes sociales.*inferior\b", r"\bno puedo dejar de compararme\b"],
        "respuestas": [
            "Las redes muestran momentos seleccionados, no la vida completa de nadie. Comparar tu realidad con la versión editada de otra persona puede ser muy injusto contigo.",
            "La comparación es humana, pero puede volverse una fuente constante de sufrimiento. Prueba cambiar la pregunta de \"¿por qué no soy como esa persona?\" a \"¿qué quiero mejorar en mí?\".",
        ],
    },
    {
        "id": "procrastinacion",
        "patrones": [r"\bdejo todo para última hora\b", r"\bsoy demasiado floj[oa]\b", r"\bno tengo motivaci[oó]n para estudiar\b", r"\bme distraigo con el tel[eé]fono\b"],
        "respuestas": [
            "La procrastinación no siempre es flojera — puede estar ligada a ansiedad, miedo a equivocarte o sentirte abrumado/a. Dividamos la tarea grande en pasos pequeños y empecemos solo por el primero.",
            "En vez de \"soy flojo/a\", prueba decir \"me está costando empezar\". Eso sí nos deja buscar una solución.",
            "La motivación no siempre aparece antes de empezar — muchas veces aparece después del primer paso. Empecemos con una meta pequeña.",
        ],
    },
    {
        "id": "dificultad_academica",
        "patrones": [r"\bme siento in[uú]til porque no entiendo\b", r"\bel profesor me cae mal\b", r"\bprofesor me tiene algo personal\b", r"\bmiedo.*participar\b", r"\bme cuesta pedir ayuda en clase\b"],
        "respuestas": [
            "No entender algo de inmediato no significa que seas incapaz. Quizás necesitas otra explicación, más práctica o algo de tiempo extra. Una dificultad no define tu inteligencia.",
            "No tienes que llevarte perfecto con todos. Puedes mantener una relación respetuosa mientras buscas estrategias para manejar lo que te molesta.",
            "Una respuesta incorrecta no define tu inteligencia. Participar también es una forma de aprender — puedes empezar por lo que te da más seguridad.",
            "Pedir ayuda no te hace menos inteligente, significa que quieres comprender. Puedes empezar con algo simple: \"¿me lo puede explicar de nuevo?\".",
        ],
    },
    {
        "id": "perfeccionismo",
        "patrones": [r"\btengo que ser perfect[oa]\b", r"\bmiedo.*fallar\b", r"\bno quiero decepcionar a nadie\b", r"\btengo que ser fuerte todo el tiempo\b"],
        "respuestas": [
            "Nadie cumple perfectamente todas las expectativas. Intentemos reemplazar \"perfección\" por \"progreso\".",
            "El fracaso puede doler, pero también enseña. Pregúntate: ¿qué puedo aprender de esto?, ¿qué haría diferente la próxima vez?",
            "Es bonito querer que las personas que quieres se sientan orgullosas, pero no puedes vivir cumpliendo todas las expectativas de todos. ¿Qué quieres tú?",
            "Ser fuerte no significa nunca llorar o pedir ayuda. A veces la verdadera fortaleza es reconocer que necesitas apoyo.",
        ],
    },
    {
        "id": "abrumado",
        "patrones": [r"\btodo me supera\b", r"\bdemasiadas cosas encima\b", r"\bdescansar pero siento culpa\b", r"\bculpable cuando hago algo por m[ií]\b"],
        "respuestas": [
            "No intentes resolver todo de una vez. Primero busca un lugar seguro, respira, toma agua, y habla con alguien de confianza. Después dividimos el problema en partes más pequeñas.",
            "Cuando todo parece urgente la mente se bloquea. Hagamos una cosa a la vez: ¿cuál de todos tus problemas es el que más te está afectando hoy?",
            "Descansar no es perder el tiempo — tu mente y tu cuerpo lo necesitan para funcionar. Cuidarte no es egoísmo.",
        ],
    },
    {
        "id": "legitimidad_ayuda",
        "patrones": [r"\best[aá] bien pedir ayuda\b", r"\bme van a castigar\b", r"\bque no estoy solo\b", r"\bsiento que no soy suficiente para mi familia\b", r"\bquiero cambiar mi vida\b"],
        "respuestas": [
            "Sí, está bien pedir ayuda, incluso por cosas que no parecen graves. Aprender a cuidar tu salud emocional es parte de crecer, no te hace menos independiente.",
            "No estás solo/a. Lo que sientes merece ser escuchado, y no tienes que cargarlo completamente por tu cuenta.",
            "Tu valor no depende de cuánto logres ni de cumplir las expectativas de los demás. Estás en un proceso de crecer y aprender.",
            "Me alegra que quieras hacer cambios. No necesitas transformar todo de golpe — elijamos un área primero y un paso pequeño y concreto.",
        ],
    },
    {
        "id": "vergonzoso_contar",
        "patrones": [r"\bme pas[oó] algo y me da verg[uü]enza contarlo\b", r"\bculpable porque me pas[oó] algo\b", r"\bhice algo malo y tengo miedo de contarlo\b"],
        "respuestas": [
            "No tienes que sentir vergüenza por pedir ayuda. Puedes contar solo lo que estés preparado/a para contar, a tu ritmo.",
            "Que algo te haya ocurrido no significa automáticamente que sea tu culpa. Separemos lo que tú podías controlar de lo que no.",
            "Entiendo que tengas miedo. Antes de decidir qué hacer, pensemos en qué pasó, si alguien está en peligro, y qué adulto podría ayudarte a manejarlo con seguridad.",
        ],
    },
    {
        "id": "peticion_ayuda_corta",
        "patrones": [r"^ayuda\.?$", r"^ay[uú]dame\.?$"],
        "respuestas": [
            "Claro. Cuéntame qué está pasando. Si estás en peligro ahora mismo, busca también a un adulto de confianza que pueda estar contigo.",
            "Claro, no tienes que explicar todo perfecto. Empieza diciéndome qué está pasando ahora.",
        ],
    },
    {
        "id": "gracias",
        "patrones": [r"\bgracias\b"],
        "respuestas": [
            "Con gusto. Aquí estoy cuando lo necesites.",
            "Para eso estoy. Puedes volver a escribir cuando quieras.",
            "Me alegra poder acompañarte un poco. Vuelve cuando quieras.",
            "Gracias a ti por confiar en este espacio. Pedir apoyo cuando lo necesitas también es una forma de cuidarte.",
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
