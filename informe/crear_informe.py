"""Informe institucional del proyecto "No estamos solos LMH".

Arma el informe como HTML con estilos de Word; convertir_informe.ps1 lo abre con
Microsoft Word y lo guarda como .docx (con índice automático, numeración de
páginas e imágenes incrustadas) y como PDF.

Formato tomado del informe de referencia del liceo: carta, márgenes de 2.54 cm,
Calibri, doble portada institucional, títulos numerados, texto justificado,
tablas y figuras numeradas, referencias en APA 7.

Uso:  python crear_informe.py  ->  informe.html
"""
import html
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
CAPTURAS = os.path.join(AQUI, "..", "presentacion", "recursos", "capturas")
FECHA = "21/10/2026"
PENDIENTE = "[pendiente de confirmar]"

partes = []
n_tabla = [0]
n_figura = [0]


def e(t):
    return html.escape(t, quote=False)


def h1(t):
    partes.append(f"<h1>{e(t)}</h1>")


def h2(t):
    partes.append(f"<h2>{e(t)}</h2>")


def p(t, clase=""):
    c = f' class="{clase}"' if clase else ""
    partes.append(f"<p{c}>{t}</p>")


def ul(items):
    partes.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")


def ol(items):
    partes.append("<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>")


def tabla(titulo, encabezado, filas, anchos=None, fuente=None):
    n_tabla[0] += 1
    partes.append(f'<p class="titulo-tabla">Tabla {n_tabla[0]}. {e(titulo)}</p>')
    cols = "".join(f'<col width="{a}%">' for a in anchos) if anchos else ""
    cab = "".join(f"<th>{e(c)}</th>" for c in encabezado)
    cuerpo = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in fila) + "</tr>" for fila in filas)
    partes.append(f'<table class="datos"><colgroup>{cols}</colgroup><tr>{cab}</tr>{cuerpo}</table>')
    if fuente:
        partes.append(f'<p class="fuente">Fuente: {fuente}</p>')


def figura(archivo, descripcion, ancho_cm=15.5):
    n_figura[0] += 1
    ruta = os.path.abspath(os.path.join(CAPTURAS, archivo)).replace("\\", "/")
    ancho_px = int(ancho_cm / 2.54 * 96)
    partes.append(f'<p class="figura"><img src="file:///{ruta}" width="{ancho_px}"></p>')
    partes.append(f'<p class="pie-figura">Figura {n_figura[0]}. {e(descripcion)}</p>')
    return n_figura[0]


def salto():
    partes.append('<br clear="all" style="page-break-before:always">')


def portada(lineas):
    for t in lineas:
        if t is None:
            partes.append('<p class="portada">&nbsp;</p>')
        elif t.startswith(">"):
            partes.append(f'<p class="portada-fecha">{e(t[1:])}</p>')
        elif t.startswith("<"):
            partes.append(f'<p class="portada-izq">{e(t[1:])}</p>')
        else:
            partes.append(f'<p class="portada">{e(t)}</p>')


# ===========================================================================
# 1. Portada institucional (doble, como el formato del liceo)
# ===========================================================================
portada(["INSTITUTO DE PREVISIÓN MILITAR", "LICEO MILITAR DE HONDURAS", "San Pedro Sula, Cortés", None, None,
         "Asignatura:", "[Asignatura — pendiente de confirmar]", None, "Docente:", "[Nombre del docente — pendiente de confirmar]",
         None, None, None, "<San Pedro Sula, Cortés", f">{FECHA}"])
salto()
portada(["INSTITUTO DE PREVISIÓN MILITAR", "LICEO MILITAR DE HONDURAS", "San Pedro Sula, Cortés", None,
         "TEMA:", "INFORME DEL PROYECTO «NO ESTAMOS SOLOS LMH»:", "PLATAFORMA WEB ANÓNIMA DE APOYO EMOCIONAL", None,
         "PRESENTADO POR:", "ALEXA PADILLA GARAY", None,
         "ÁREA:", "BACHILLERATO TÉCNICO PROFESIONAL EN INFORMÁTICA", None,
         "ASESOR(A):", "[Nombre del asesor — pendiente de confirmar]", None, "AÑO ACADÉMICO 2026",
         None, "<San Pedro Sula, Cortés", f">{FECHA}"])
salto()

h1("Dedicatoria")
p("[Texto de la dedicatoria — lo redacta la autora.]", "pendiente")
h1("Agradecimientos")
p("[Texto de los agradecimientos — lo redacta la autora. Se sugiere mencionar al Liceo Militar de Honduras y al área de Informática, "
  "a la psicóloga del liceo, al asesor o asesora del proyecto, a SULA, Bodega 6, por la práctica profesional, y a la familia.]", "pendiente")
salto()

# ===========================================================================
# 2. Índice general
# ===========================================================================
partes.append('<p class="titulo-indice">Índice general</p>')
partes.append('<p class="marca-indice">[[INDICE]]</p>')
salto()

# ===========================================================================
# 3. Resumen ejecutivo
# ===========================================================================
h1("1. Resumen ejecutivo")
p("El presente informe documenta el desarrollo de «No estamos solos LMH», una plataforma web de apoyo emocional dirigida a los estudiantes del "
  "Liceo Militar de Honduras y vinculada al programa psicopedagógico de la institución. El proyecto responde a una necesidad concreta: muchos "
  "estudiantes no solicitan ayuda a tiempo por temor a ser identificados, por la disponibilidad limitada de atención psicológica fuera del horario "
  "escolar y por la dificultad de que una señal de riesgo llegue oportunamente a quien puede atenderla.")
p("La solución consiste en una aplicación web, instalable en el celular, que permite conversar de forma anónima con la psicóloga del liceo y con "
  "asistentes conversacionales basados en inteligencia artificial, consultar contenido psicoeducativo, realizar ejercicios guiados y "
  "autoevaluaciones, y registrar el estado de ánimo. Cada mensaje es analizado por un filtro de riesgo con ocho categorías; cuando se detectan "
  "señales de riesgo medio, alto o crítico, el mensaje no es respondido por la inteligencia artificial, sino que se deriva a la psicóloga mediante "
  "una alerta en tiempo real y se muestran al estudiante las líneas de ayuda 150 y 911.")
p("El desarrollo se realizó con una metodología iterativa e incremental entre el 2 y el 21 de octubre de 2026, con más de cien cambios registrados "
  "en el control de versiones Git. A la fecha de este informe, la plataforma funciona en un entorno local y su código se encuentra en un repositorio "
  "de GitHub; se verificaron mediante pruebas funcionales del desarrollador el filtro de riesgo, la cadena de servicios de inteligencia artificial, "
  "la transcripción de voz y la adaptación a pantallas de celular. Quedan pendientes la publicación en un servicio de alojamiento, las pruebas con "
  "estudiantes y la validación del contenido por parte de la psicóloga del liceo.")
p("Se concluye que la plataforma cumple los objetivos técnicos planteados y constituye un canal complementario —no sustitutivo— de la atención "
  "psicológica institucional. Se recomienda su publicación en un plan de alojamiento con almacenamiento persistente, la definición de un protocolo "
  "institucional de crisis y una fase piloto supervisada con estudiantes.")

# ===========================================================================
# 4. Introducción
# ===========================================================================
h1("2. Introducción")
p("La salud emocional de los adolescentes incide directamente en su rendimiento académico, su convivencia y su permanencia escolar. En un entorno "
  "de formación militar como el del Liceo Militar de Honduras, en el que la disciplina y la exigencia académica forman parte de la vida diaria, "
  "resulta especialmente relevante contar con canales que faciliten que los estudiantes expresen lo que sienten y soliciten apoyo cuando lo necesitan.")
p("La iniciativa surge como proyecto tecnológico del Bachillerato Técnico Profesional en Informática, con el propósito de aplicar los conocimientos "
  "de programación, bases de datos y redes al servicio de una necesidad institucional: acercar la ayuda psicológica a los estudiantes sin exponer su "
  "identidad. La finalidad del proyecto es ofrecer un canal anónimo, disponible en cualquier momento, que apoye la labor de la psicóloga del liceo y "
  "le avise oportunamente cuando un estudiante pueda encontrarse en riesgo.")
p("El documento se organiza en veintidós capítulos: los primeros describen el contexto, el problema, la justificación, los objetivos y el alcance; "
  "los siguientes presentan el marco conceptual, la metodología, la solución desarrollada, el cronograma y el presupuesto; posteriormente se "
  "documentan la implementación, las pruebas, los resultados, el impacto, los riesgos y la sostenibilidad; finalmente se exponen las conclusiones, "
  "las recomendaciones, las referencias y los anexos.")

# ===========================================================================
# 5. Antecedentes y contexto institucional
# ===========================================================================
h1("3. Antecedentes y contexto institucional")
h2("3.1 Contexto institucional")
p("El Liceo Militar de Honduras, perteneciente al Instituto de Previsión Militar, es un centro educativo ubicado en San Pedro Sula, Cortés, que "
  "ofrece formación académica con disciplina militar e incluye el Bachillerato Técnico Profesional en Informática. La institución cuenta con un "
  "programa psicopedagógico atendido por una psicóloga. Los datos institucionales específicos —número de estudiantes atendidos, horario de "
  "atención y protocolos vigentes— no fueron proporcionados para este informe y se identifican como pendientes de confirmar.")
h2("3.2 Antecedentes del problema")
p("Según el Fondo de las Naciones Unidas para la Infancia (UNICEF, 2021), más del 15 % de los adolescentes de 10 a 19 años de América Latina y el "
  "Caribe vive con un trastorno mental diagnosticado. Este dato regional ofrece un marco de referencia; no se dispone de datos propios del liceo que "
  "permitan estimar la situación de su población estudiantil.")
h2("3.3 Referentes tecnológicos")
p("Para el diseño de la solución se tomaron como referencia dos servicios de apoyo emocional en línea: Yana, aplicación de acompañamiento "
  "emocional con un asistente conversacional disponible las 24 horas, y Psonríe, servicio de atención psicológica en línea con profesionales. De "
  "ambos se adoptaron principios como la disponibilidad permanente, la atención sin cita y la privacidad. Las fuentes consultadas sobre estos "
  "referentes deben citarse formalmente; se identifican como pendientes de confirmar.")
h2("3.4 Práctica profesional de la autora")
p("De manera paralela al desarrollo del proyecto, la autora realizó su práctica profesional en SULA, Bodega 6, donde se desempeñó como analista. "
  "Entre las actividades realizadas se encuentran la trazabilidad de productos y lotes de LEYDE, la asignación de furgones y la creación de "
  "reservas, el control y traspaso de MIGOS, el manejo de formatos y la programación de LEYDE, los cambios INLACSA y la elaboración de rótulos de "
  "exportación, y la realización de inventario. Como resultado de su desempeño, la gerente Julissa García le ofreció una oportunidad laboral en la "
  "empresa. Las fechas de la práctica y la descripción institucional de la empresa se identifican como pendientes de confirmar.")

# ===========================================================================
# 6. Planteamiento del problema
# ===========================================================================
h1("4. Planteamiento del problema")
p("El problema central consiste en que los estudiantes del Liceo Militar de Honduras que atraviesan situaciones emocionales difíciles no siempre "
  "solicitan ayuda a tiempo. A partir del análisis realizado durante la formulación del proyecto se identifican tres causas principales:")
ol(["<b>Temor a ser identificados.</b> Los estudiantes temen que sus compañeros, sus superiores o su familia se enteren de lo que les sucede, y "
    "prefieren no hablar.",
    "<b>Disponibilidad limitada de la atención.</b> La atención psicológica depende del horario escolar; fuera de él no existe un canal institucional "
    "al que acudir ni una forma de priorizar los casos urgentes.",
    "<b>Señales de riesgo que llegan tarde.</b> Sin un canal adecuado, una señal de crisis puede no llegar nunca a la persona capaz de atenderla."])
p("Las consecuencias posibles incluyen el agravamiento de problemas emocionales que podrían atenderse de forma temprana, el deterioro del "
  "rendimiento académico y la convivencia, y, en los casos más graves, situaciones de riesgo para la integridad del estudiante. La población "
  "afectada es el estudiantado del liceo. No se dispone de evidencias cuantitativas propias de la institución (encuestas o registros de atención); "
  "su recolección se plantea como recomendación.")

# ===========================================================================
# 7. Justificación
# ===========================================================================
h1("5. Justificación")
p("El proyecto se justifica desde cuatro perspectivas:")
ul(["<b>Pertinencia institucional:</b> complementa el programa psicopedagógico del liceo con un canal disponible en cualquier momento, que "
    "prioriza los casos de riesgo y respeta el anonimato del estudiante.",
    "<b>Beneficio para los estudiantes:</b> reduce la barrera del temor a ser identificado y ofrece herramientas de autocuidado, información "
    "confiable y acceso inmediato a las líneas de ayuda 150 y 911.",
    "<b>Aporte académico y tecnológico:</b> integra programación del lado del servidor y del cliente, comunicación en tiempo real, bases de datos, "
    "inteligencia artificial, reconocimiento de voz y aplicaciones web instalables, competencias propias del Bachillerato Técnico en Informática.",
    "<b>Viabilidad económica:</b> se construye con software libre y con niveles gratuitos de servicios de inteligencia artificial, de modo que la "
    "inversión se concentra en el alojamiento y en los equipos recomendados."])

# ===========================================================================
# 8. Objetivos
# ===========================================================================
h1("6. Objetivos")
h2("6.1 Objetivo general")
p("Desarrollar una plataforma web anónima de apoyo emocional que permita a los estudiantes del Liceo Militar de Honduras solicitar ayuda en "
  "cualquier momento y que alerte a la psicóloga del liceo cuando un mensaje presente señales de riesgo.")
h2("6.2 Objetivos específicos")
ol(["Implementar un chat anónimo en tiempo real entre los estudiantes y la psicóloga del liceo.",
    "Incorporar asistentes conversacionales con inteligencia artificial, por texto y por voz, con respuestas de respaldo cuando el servicio no esté disponible.",
    "Detectar automáticamente señales de riesgo en los mensajes y alertar a la psicóloga sin que la inteligencia artificial atienda las situaciones de crisis.",
    "Reunir contenido psicoeducativo, ejercicios guiados y autoevaluaciones en un mismo sitio.",
    "Proporcionar a la psicóloga un panel para supervisar conversaciones y alertas y actualizar el contenido sin necesidad de programar.",
    "Preparar la plataforma para su publicación en internet y su instalación en el celular."])

# ===========================================================================
# 9. Alcance y limitaciones
# ===========================================================================
h1("7. Alcance y limitaciones")
h2("7.1 Alcance")
p("El proyecto comprende el diseño, la programación y la verificación funcional de la plataforma web, que incluye: chat anónimo con la psicóloga; "
  "cuatro asistentes conversacionales (Sami, Leo, Nia y el Tigre LMH); filtro de riesgo; artículos, glosario, herramientas, autoevaluaciones, "
  "diario de ánimo, muro anónimo, reseñas, música y videos; cuentas opcionales con apodo; panel de la psicóloga; voz en los chats; y aplicación "
  "instalable. Incluye también la preparación para su publicación y la estimación de costos.")
h2("7.2 Fuera del alcance")
ul(["La atención psicológica en sí misma, que corresponde exclusivamente a la psicóloga del liceo.",
    "El diagnóstico clínico: la plataforma no diagnostica ni prescribe tratamientos.",
    "La publicación definitiva en internet y en las tiendas de aplicaciones, que requiere aprobación y financiamiento institucional.",
    "La evaluación del efecto de la plataforma en el bienestar de los estudiantes, que exige una fase piloto posterior."])
h2("7.3 Limitaciones y restricciones")
ul(["Los servicios gratuitos de inteligencia artificial tienen límites de uso; cuando se agotan, la plataforma recurre a respuestas preparadas.",
    "El filtro de riesgo se basa en patrones de texto: puede no reconocer expresiones nuevas o indirectas, y debe ser revisado periódicamente por la psicóloga.",
    "La plataforma depende de que el estudiante disponga de un dispositivo con conexión a internet.",
    "En el plan gratuito de alojamiento los datos se borran al reiniciarse el servicio, por lo que el uso real requiere un plan pagado."])

# ===========================================================================
# 10. Marco conceptual y técnico
# ===========================================================================
h1("8. Marco conceptual y técnico")
h2("8.1 Conceptos")
ul(["<b>Apoyo emocional en línea:</b> acompañamiento que se brinda a través de medios digitales y que complementa, sin reemplazar, la atención profesional presencial.",
    "<b>Anonimato:</b> condición en la que el sistema no solicita ni almacena el nombre del estudiante; cada conversación se identifica con un código aleatorio.",
    "<b>Derivación:</b> procedimiento por el cual un caso que excede las capacidades del sistema se traslada a una persona calificada; en este proyecto, a la psicóloga.",
    "<b>Inteligencia artificial conversacional:</b> modelos de lenguaje que generan respuestas a partir de instrucciones; en la plataforma operan con límites explícitos y nunca atienden crisis.",
    "<b>Aplicación web progresiva (PWA):</b> sitio web que puede instalarse en el celular con un ícono propio y funcionar parcialmente sin conexión."])
h2("8.2 Tecnologías y herramientas")
tabla("Tecnologías utilizadas y su función en la plataforma", ["Herramienta", "Uso en el proyecto"], [
    ["Python 3.11 y Flask 3.0", "Servidor web: rutas, plantillas, sesiones y lógica de la plataforma."],
    ["Flask-SocketIO 5.3 (WebSocket)", "Comunicación en tiempo real: mensajes del chat y alertas para la psicóloga."],
    ["SQLite", "Base de datos local: sesiones anónimas, mensajes, ánimo, autoevaluaciones, muro, reseñas, cuentas y contenido editable."],
    ["HTML5, CSS3 y JavaScript", "Interfaz: portada por capítulos, chats, mural interactivo, animaciones y adaptación a celulares."],
    ["Servicios de inteligencia artificial en cadena", "Claude (Anthropic), Groq, Google Gemini, Mistral, OpenRouter, NVIDIA, Hugging Face y B.AI; si uno falla, responde el siguiente."],
    ["Whisper (mediante Groq) y Web Speech API", "Conversión de voz a texto y lectura en voz alta de las respuestas."],
    ["Werkzeug", "Cifrado de las contraseñas de las cuentas opcionales."],
    ["Service Worker y manifiesto web", "Instalación como aplicación y página de aviso sin conexión."],
    ["Gunicorn y Eventlet", "Ejecución del servidor en producción con soporte de tiempo real."],
    ["Git y GitHub", "Control de versiones y respaldo del código."],
    ["Render (previsto)", "Alojamiento en internet; configuración preparada en el archivo render.yaml."],
], anchos=[34, 66])

# ===========================================================================
# 11. Metodología de desarrollo
# ===========================================================================
h1("9. Metodología de desarrollo")
h2("9.1 Enfoque")
p("Se aplicó una metodología iterativa e incremental. Cada mejora se implementó, se verificó en el navegador y se registró como un cambio en Git "
  "antes de continuar con la siguiente. Este enfoque permitió incorporar progresivamente las funciones, corregir los errores detectados y ajustar el "
  "diseño según las observaciones de la autora.")
h2("9.2 Fases de trabajo")
p("Las fases y sus fechas se obtienen del historial de cambios del repositorio. La fase de análisis y planificación es anterior al primer cambio "
  "registrado y sus fechas exactas se identifican como pendientes de confirmar.")
ol(["Análisis y planificación: definición del problema, la necesidad y los referentes.",
    "Desarrollo base (2 al 5 de octubre): chat anónimo, asistente por reglas y filtro de riesgo.",
    "Funciones y diseño (7 y 8 de octubre): diario de ánimo, autoevaluaciones, Infórmate e identidad visual del liceo.",
    "Inteligencia artificial y herramientas (12 al 15 de octubre): asistente con IA, línea 150, mural interactivo, panel de contenido y aplicación instalable.",
    "Varias IA, voz y rediseño (17 al 19 de octubre): cadena de ocho servicios de IA, voz en los chats y portada por capítulos.",
    "Tigre por voz y contenidos (20 de octubre): página y sección del Tigre LMH, artículos de bullying y de acoso, e imágenes de los temas.",
    "Pruebas, publicación y entrega: pendiente."])
h2("9.3 Criterios de verificación")
p("Cada función se consideró terminada cuando: se ejecutaba sin errores en la consola del navegador; producía el resultado esperado en una prueba "
  "manual; se visualizaba correctamente en computadora y en celular; y, en el caso del filtro de riesgo, impedía que un mensaje de riesgo fuera "
  "respondido por la inteligencia artificial.")
h2("9.4 Responsables")
p("El desarrollo estuvo a cargo de la autora, con el acompañamiento del asesor o asesora del proyecto ([pendiente de confirmar]). La validación del "
  "contenido psicológico corresponde a la psicóloga del liceo y se encuentra pendiente.")

# ===========================================================================
# 12. Descripción de la propuesta
# ===========================================================================
h1("10. Descripción de la solución")
h2("10.1 Usuarios")
ul(["<b>Estudiante:</b> accede sin registrarse; puede crear una cuenta opcional con apodo y avatar, sin nombre real.",
    "<b>Psicóloga:</b> accede con usuario y contraseña a un panel donde atiende conversaciones, recibe alertas, consulta estadísticas anónimas y edita el contenido."])
h2("10.2 Componentes principales")
ul(["<b>Portada por capítulos:</b> «Hablar», «Si es urgente», «Cuídate hoy», «Entiende lo que sientes» y «Comunidad», con el botón «Necesito ayuda ahora» siempre visible.",
    "<b>Chat con la psicóloga:</b> anónimo y en tiempo real.",
    "<b>Asistentes conversacionales:</b> Sami, Leo y Nia, por chat, y el Tigre LMH, por voz, en la portada y en una página propia.",
    "<b>Filtro de riesgo:</b> analiza cada mensaje y lo clasifica en riesgo bajo, medio, alto o crítico.",
    "<b>Contenido psicoeducativo:</b> 66 artículos, un glosario de 26 conceptos, 17 temas destacados con imagen y 7 libros recomendados.",
    "<b>Herramientas:</b> 24 ejercicios guiados en 7 categorías (ansiedad, enojo, tristeza, calma, decir lo que siento, dormir y estudiar).",
    "<b>Autoevaluaciones:</b> hábitos de estudio, nivel de estrés y relación con la comida.",
    "<b>Comunidad:</b> muro anónimo moderable, reseñas y diario de ánimo.",
    "<b>Panel de la psicóloga:</b> conversaciones, alertas, estadísticas y edición de artículos, herramientas y textos."])
figura("portada_bienvenida.jpg", "Portada de la plataforma con las tres opciones para pedir ayuda y las líneas de emergencia visibles.")
figura("con_quien_hablar.jpg", "Sección «¿Con quién deseas hablar hoy?»: psicóloga, asistente o el Tigre por voz.")
h2("10.3 Arquitectura")
p("La plataforma sigue una arquitectura cliente-servidor. El navegador del estudiante se comunica con el servidor mediante HTTPS y WebSocket; el "
  "servidor, desarrollado en Python con Flask, guarda la información en SQLite y consulta los servicios de inteligencia artificial y de voz. Las "
  "claves de estos servicios se almacenan únicamente en el servidor y nunca se envían al navegador ni se publican en el repositorio.")
figura("diagrama_arquitectura.png", "Arquitectura cliente-servidor de la plataforma.", 14)
h2("10.4 Flujo de un mensaje y filtro de riesgo")
p("Cuando un estudiante envía un mensaje, este se guarda asociado a su código anónimo y pasa por el filtro de riesgo. Si el riesgo es bajo, "
  "responde el asistente; si es medio, alto o crítico, se envía un mensaje de apoyo, se alerta a la psicóloga en su panel y, en el nivel crítico, se "
  "muestran los botones para llamar al 150 y al 911.")
figura("diagrama_flujo.png", "Flujo de un mensaje según el nivel de riesgo detectado.", 14)
tabla("Categorías del filtro de riesgo", ["Categoría", "Peso", "Ejemplos de señales"], [
    ["Ideación suicida", "10", "Expresiones de no querer vivir o de tener un plan para hacerse daño."],
    ["Autolesión", "9", "Intención o pensamientos de lastimarse."],
    ["Riesgo de un tercero", "8", "Un amigo o familiar que quiere hacerse daño."],
    ["Abuso digital", "8", "Amenazas, chantaje o solicitud de fotografías íntimas."],
    ["Abuso o violencia", "8", "Golpes, abuso o miedo de regresar a casa."],
    ["Síntomas psicóticos", "7", "Escuchar voces o sentirse observado."],
    ["Bullying", "6", "Burlas o acoso escolar repetido."],
    ["Desesperanza", "4", "Sentir que nada tiene sentido o que nadie le importa."],
], anchos=[26, 10, 64], fuente="archivo filtro_riesgo.py del proyecto. Umbrales: crítico ≥ 9, alto ≥ 6, medio ≥ 3.")
h2("10.5 Inteligencia artificial en cadena")
p("Los asistentes utilizan ocho servicios de inteligencia artificial en un orden establecido. Si un servicio se queda sin saldo, alcanza su límite "
  "de uso o falla, la plataforma pasa automáticamente al siguiente; cada intento tiene un máximo de 25 segundos y el conjunto, de 50 segundos. Si "
  "ningún servicio responde, el asistente utiliza respuestas preparadas por reglas. Ninguna situación de crisis llega a la inteligencia artificial.")
figura("diagrama_ia.png", "Orden de los servicios de inteligencia artificial.", 14)
h2("10.6 Voz y el Tigre LMH")
p("Los chats permiten dictar los mensajes —la voz se convierte en texto mediante el modelo Whisper y el audio no se guarda—, escuchar las "
  "respuestas en voz alta y conversar en un «modo voz» de pantalla completa. El Tigre LMH, mascota del programa, cuenta con una interfaz propia "
  "cuyos ojos siguen al usuario y reaccionan al escuchar, pensar y hablar. Lo expresado por voz pasa por el mismo filtro de riesgo que el texto.")
figura("tigre_pagina.jpg", "Interfaz del Tigre LMH para conversar por voz.", 11)

# ===========================================================================
# 13. Plan de trabajo y cronograma
# ===========================================================================
h1("11. Plan de trabajo y cronograma")
tabla("Cronograma ejecutado del proyecto", ["Fase", "Fechas", "Entregable", "Estado"], [
    ["Análisis y planificación", "Antes del 2 de octubre " + PENDIENTE, "Problema, necesidad y referentes definidos", "Ejecutada"],
    ["Desarrollo base", "2 al 5 de octubre de 2026", "Chat anónimo, asistente por reglas y filtro de riesgo", "Ejecutada"],
    ["Funciones y diseño", "7 y 8 de octubre de 2026", "Diario, autoevaluaciones, Infórmate e identidad visual", "Ejecutada"],
    ["IA y herramientas", "12 al 15 de octubre de 2026", "Asistente con IA, mural, panel de contenido y app instalable", "Ejecutada"],
    ["Varias IA, voz y rediseño", "17 al 19 de octubre de 2026", "Cadena de IA, voz en los chats y portada por capítulos", "Ejecutada"],
    ["Tigre por voz y contenidos", "20 de octubre de 2026", "Tigre LMH, artículos de bullying y acoso, imágenes", "Ejecutada"],
    ["Pruebas, publicación y entrega", "Por definir", "Plataforma publicada y entregada al liceo", "Planificada"],
], anchos=[24, 24, 38, 14], fuente="historial de cambios del repositorio Git (más de cien cambios registrados).")
figura("diagrama_cronograma.png", "Cronograma de ejecución: seis de siete fases cumplidas.", 14)

# ===========================================================================
# 14. Recursos y presupuesto
# ===========================================================================
h1("12. Recursos y presupuesto")
h2("12.1 Recursos humanos")
ul(["Autora del proyecto: análisis, diseño, programación, pruebas y documentación.",
    "Asesor o asesora del proyecto: orientación y revisión " + PENDIENTE + ".",
    "Psicóloga del liceo: validación del contenido y del filtro de riesgo (pendiente)."])
h2("12.2 Recursos tecnológicos existentes")
p("Para el desarrollo se utilizaron una computadora personal, la red de internet y software libre o gratuito, sin costo de licencias. Los "
  "servicios de inteligencia artificial se emplearon en sus niveles gratuitos.")
h2("12.3 Cotización de equipos")
p("Se cotizaron equipos en cuatro tiendas de Honduras para el funcionamiento institucional de la plataforma. Los precios corresponden a las "
  "capturas de las tiendas tomadas en octubre de 2026 y deben verificarse antes de la compra.")
tabla("Cotización de equipos", ["Equipo", "Tienda", "Modelo", "Precio (L)", "Uso propuesto"], [
    ["Tablet", "Elektra", "Samsung Galaxy Tab A11, 64 GB", "<b>4,499</b>", "Estación de autoayuda para hablar con el Tigre (recomendada)"],
    ["Tablet", "Jetstereo", "Samsung Galaxy Tab A11, 8\", 64 GB", "4,795", "Mismo uso"],
    ["Tablet", "Jetstereo", "Samsung Galaxy Tab S10 Lite, 10.9\", 128 GB", "9,495", "Charlas y talleres de la psicóloga"],
    ["Celular", "La Curacao", "Samsung Galaxy A17, 4 GB + 128 GB", "<b>5,997</b>", "Alertas y WhatsApp de la psicóloga (recomendado)"],
    ["Celular", "La Curacao", "Xiaomi Redmi 17, 4 GB + 128 GB", "6,599", "Mismo uso"],
    ["Celular", "Elektra", "Infinix Smart 20, 4 GB + 128 GB", "4,599", "Mismo uso, opción económica"],
    ["Laptop", "Geek Store", "Dell Latitude 5420, i5, 8 GB, 256 GB", "<b>9,200</b>", "Panel de la psicóloga y servidor local de respaldo (recomendada)"],
    ["Laptop", "Geek Store", "Galaxy Book Pro 2 360, i5, 8 GB", "13,200", "Pantalla táctil para charlas"],
    ["Laptop", "Geek Store", "Galaxy Book Pro 2 360, i7, 16 GB", "16,400", "Uso intensivo"],
], anchos=[11, 13, 30, 12, 34], fuente="capturas de los sitios de Jetstereo, La Curacao, Elektra y Geek Store, octubre de 2026. En las laptops debe confirmarse si son nuevas o reacondicionadas y su garantía.")
h2("12.4 Servicios")
tabla("Costos de alojamiento, dominio y tiendas de aplicaciones", ["Servicio", "Costo", "Observación"], [
    ["Render: plan Starter (512 MB, 0.5 CPU)", "US$7.00 al mes", "Servidor siempre encendido, con chat en tiempo real y HTTPS."],
    ["Render: disco persistente de 1 GB", "US$0.25 al mes", "Conserva los datos; copia automática cada 24 horas."],
    ["Render: espacio de trabajo Hobby", "US$0", "Incluye 5 GB de tráfico al mes; el excedente cuesta US$0.15 por GB."],
    ["Dominio .com, primer año", "≈ US$11", "Valor de referencia; la renovación puede ser mayor."],
    ["Google Play (cuenta de desarrollador)", "US$25, una sola vez", "Si la cuenta es personal, exige una prueba con 12 personas durante 14 días."],
    ["Apple App Store (programa de desarrolladores)", "US$99 al año", "Requiere una computadora Mac y la revisión de Apple."],
    ["Servicios de inteligencia artificial", "US$0", "Niveles gratuitos; un plan pagado es opcional y su costo está pendiente de estimar."],
], anchos=[36, 20, 44], fuente="sitios oficiales de Render, Google y Apple, consultados en octubre de 2026. Tasa de referencia: L 26.80 por dólar.")
h2("12.5 Resumen de la inversión estimada")
tabla("Inversión estimada del primer año", ["Concepto", "Monto (L)"], [
    ["Equipos recomendados (tablet, celular y laptop)", "19,696"],
    ["Alojamiento con disco (12 meses) y dominio", "2,626"],
    ["Cuenta de Google Play", "670"],
    ["<b>Total con Google Play</b>", "<b>22,992</b>"],
    ["Total si además se publica en la App Store (+ L 2,653)", "25,645"],
], anchos=[75, 25], fuente="elaboración propia con base en las cotizaciones anteriores. Estimación sujeta a variaciones de precio y del tipo de cambio.")
p("Desde el segundo año, el costo recurrente se reduce al alojamiento y la renovación del dominio, estimados en aproximadamente L 2,800 anuales, "
  "más la cuota de Apple si la aplicación se publica en esa tienda.")

# ===========================================================================
# 15. Implementación y desarrollo
# ===========================================================================
h1("13. Implementación y desarrollo")
p("Durante la implementación se tomaron las siguientes decisiones técnicas y se efectuaron los ajustes que se describen:")
ul(["<b>Anonimato desde el diseño:</b> se decidió que ninguna tabla almacene nombres reales; las conversaciones usan un código aleatorio y las cuentas, un apodo con contraseña cifrada. La base de datos se excluyó del repositorio.",
    "<b>Crisis fuera del alcance de la IA:</b> el filtro de riesgo se ejecuta antes de cualquier respuesta automática, de modo que la inteligencia artificial solo responde mensajes de riesgo bajo.",
    "<b>Resiliencia de la inteligencia artificial:</b> ante los límites de los servicios gratuitos se implementó una cadena de ocho servicios con varios modelos cada uno y respuestas de respaldo.",
    "<b>Contenido editable:</b> se creó un panel para que la psicóloga agregue, edite u oculte artículos, herramientas y textos sin modificar el código.",
    "<b>Voz:</b> se incorporó el dictado con Whisper y la lectura en voz alta; el Tigre LMH se integró primero en el chat y, a solicitud de la autora, se trasladó a una sección y una página propias.",
    "<b>Rendimiento:</b> se detectó que los efectos visuales reducían la fluidez del desplazamiento; se optimizaron para pausarse cuando no son visibles.",
    "<b>Seguridad de las claves:</b> las claves de los servicios se guardan en un archivo de entorno excluido del repositorio; en producción deben configurarse en el panel del servicio de alojamiento.",
    "<b>Incidencias resueltas:</b> identificadores de modelos de IA obsoletos, archivos guardados en caché por el navegador y textos con bajo contraste en algunas secciones fueron corregidos durante el desarrollo."])

# ===========================================================================
# 16. Pruebas, validación y evaluación
# ===========================================================================
h1("14. Pruebas, validación y evaluación")
p("Las pruebas realizadas son pruebas funcionales efectuadas por la autora en un entorno local. No se han realizado pruebas con estudiantes ni una "
  "validación formal del contenido por parte de la psicóloga, y el proyecto no cuenta con pruebas automatizadas; estas actividades se recomiendan "
  "antes de su publicación.")
tabla("Pruebas funcionales realizadas", ["Prueba", "Procedimiento", "Resultado observado"], [
    ["Filtro de riesgo", "Clasificación de mensajes de prueba con y sin señales de riesgo.",
     "«me quiero morir» → crítico; «mi amigo se quiere matar» → alto; «hoy estoy nervioso por el examen» → bajo."],
    ["Derivación de crisis", "Verificación de que los mensajes de riesgo no lleguen a la IA.", "Los mensajes de riesgo medio, alto o crítico se derivan a la psicóloga."],
    ["Cadena de IA", "Simulación de un servicio sin saldo y de un modelo saturado.", "La plataforma pasó al siguiente servicio y al siguiente modelo, respectivamente."],
    ["Respuesta de un asistente", "Mensaje de riesgo bajo enviado al Tigre LMH.", "Respuesta generada por un servicio de IA de la cadena."],
    ["Transcripción de voz", "Audio de prueba en español enviado al servicio Whisper.", "El audio se convirtió correctamente en texto."],
    ["Adaptación a celular", "Visualización a 375 píxeles de ancho.", "Sin desbordamiento horizontal; botón de ayuda visible."],
    ["Rendimiento", "Medición de cuadros por segundo durante el desplazamiento.", "De 16 a 59 cuadros por segundo tras la optimización."],
], anchos=[20, 38, 42], fuente="registros de prueba del desarrollo, octubre de 2026.")

# ===========================================================================
# 17. Resultados
# ===========================================================================
h1("15. Resultados")
h2("15.1 Resultados verificados")
ul(["Plataforma web funcional en entorno local, con 43 rutas y 9 eventos de comunicación en tiempo real.",
    "Contenido disponible: 66 artículos, 26 conceptos de glosario, 24 herramientas en 7 categorías, 3 autoevaluaciones y 7 libros recomendados.",
    "Cuatro asistentes conversacionales y una cadena de ocho servicios de inteligencia artificial con respaldo por reglas.",
    "Filtro de riesgo con ocho categorías y cuatro niveles, verificado con mensajes de prueba.",
    "Voz en los chats y la interfaz del Tigre LMH.",
    "Panel de la psicóloga con edición de contenido.",
    "Código respaldado en GitHub con más de cien cambios registrados."])
figura("chat_sami.jpg", "Chat con el asistente Sami: aviso de que es una inteligencia artificial y de que la conversación es anónima.", 12)
figura("recursos_psicologia.jpg", "Recursos de psicología, con los temas de bullying y de acoso y ciberacoso.")
h2("15.2 Beneficios esperados (no medidos)")
p("Se espera que la plataforma facilite que más estudiantes soliciten ayuda, que la psicóloga conozca oportunamente los casos de riesgo y que la "
  "comunidad estudiantil disponga de información confiable sobre salud emocional. Estos beneficios no han sido medidos y requieren una fase piloto "
  "con indicadores definidos.")

# ===========================================================================
# 18. Impacto institucional
# ===========================================================================
h1("16. Impacto institucional")
p("El impacto se valora de forma prevista, a partir de las funciones verificadas, y no de mediciones en la población estudiantil. Se identifican "
  "los siguientes efectos esperados:")
ul(["<b>Estudiantes:</b> un canal anónimo y disponible en cualquier momento para expresar lo que sienten y acceder a herramientas de autocuidado.",
    "<b>Psicóloga:</b> priorización de los casos de riesgo mediante alertas y estadísticas anónimas para orientar su labor.",
    "<b>Institución:</b> fortalecimiento del programa psicopedagógico con una herramienta de bajo costo y fácil mantenimiento."])
p("Para valorar el impacto real se proponen como criterios: el número de conversaciones iniciadas, el número de alertas atendidas, el tiempo entre "
  "una alerta y su atención, y la percepción de los estudiantes y de la psicóloga recogida mediante encuestas anónimas.")

# ===========================================================================
# 19. Riesgos y medidas de mitigación
# ===========================================================================
h1("17. Riesgos y medidas de mitigación")
tabla("Riesgos identificados y medidas de mitigación", ["Riesgo", "Impacto", "Medida de mitigación", "Responsable"], [
    ["El filtro no reconoce una expresión de riesgo", "Alto", "Revisión periódica de las frases por la psicóloga y protocolo de crisis institucional.", "Psicóloga y administrador"],
    ["Exposición de datos de estudiantes", "Alto", "Anonimato, contraseñas cifradas, HTTPS y exclusión de la base de datos del repositorio.", "Administrador"],
    ["Pérdida de datos en el servidor", "Medio", "Plan con disco persistente y respaldo semanal de la base de datos.", "Administrador"],
    ["Agotamiento de los servicios gratuitos de IA", "Medio", "Cadena de servicios y respuestas de respaldo; plan pagado opcional.", "Administrador"],
    ["Exposición de las claves de los servicios", "Alto", "Claves solo en el servidor; renovación inmediata si se exponen.", "Administrador"],
    ["Dependencia de una sola persona", "Medio", "Dos administradores y documentación del mantenimiento.", "Dirección del liceo " + PENDIENTE],
    ["Uso indebido del muro anónimo", "Medio", "Moderación desde el panel y filtro de contenido ofensivo.", "Psicóloga"],
], anchos=[26, 10, 44, 20])

# ===========================================================================
# 20. Sostenibilidad y mantenimiento
# ===========================================================================
h1("18. Sostenibilidad y mantenimiento")
ul(["<b>Contenido:</b> la psicóloga puede actualizar artículos, herramientas y textos desde su panel, sin conocimientos de programación.",
    "<b>Técnica:</b> se requieren al menos dos administradores con acceso al repositorio y al servicio de alojamiento, revisión mensual de la facturación y de los registros, y respaldo semanal de la base de datos.",
    "<b>Financiera:</b> el costo recurrente estimado es de aproximadamente L 2,800 anuales; se recomienda que la cuenta de alojamiento esté a nombre de la institución.",
    "<b>Mejora continua:</b> revisión semestral del filtro de riesgo y del contenido, e incorporación de las sugerencias de estudiantes y de la psicóloga."])

# ===========================================================================
# 21. Conclusiones
# ===========================================================================
h1("19. Conclusiones")
ol(["Se cumplió el objetivo general en su dimensión técnica: la plataforma permite a los estudiantes solicitar apoyo de forma anónima en cualquier momento y alerta a la psicóloga cuando un mensaje presenta señales de riesgo.",
    "La separación entre la detección de riesgo y la inteligencia artificial garantiza, según las pruebas realizadas, que las situaciones de crisis sean derivadas a una persona y no respondidas por un sistema automático.",
    "La cadena de servicios de inteligencia artificial y las respuestas de respaldo permiten que los asistentes sigan funcionando aun cuando algún servicio deja de estar disponible.",
    "Es posible construir la plataforma con software libre y servicios gratuitos; la inversión necesaria se concentra en el alojamiento y en los equipos recomendados.",
    "La metodología iterativa permitió incorporar funciones y correcciones de manera ordenada, con trazabilidad en el control de versiones.",
    "La plataforma no reemplaza la atención psicológica: la complementa y depende de la validación y la supervisión de la psicóloga del liceo."])

# ===========================================================================
# 22. Recomendaciones
# ===========================================================================
h1("20. Recomendaciones")
p("Se proponen las siguientes acciones, en orden de prioridad:")
ol(["Validar con la psicóloga del liceo el contenido y las frases del filtro de riesgo antes de cualquier uso con estudiantes.",
    "Definir un protocolo institucional de crisis que indique quién atiende las alertas, en qué horario y cómo se actúa.",
    "Publicar la plataforma en el plan Starter de Render con disco persistente, con la cuenta a nombre de la institución y dos administradores.",
    "Realizar una fase piloto supervisada con un grupo de estudiantes y medir los indicadores propuestos en el capítulo 16.",
    "Respaldar la base de datos semanalmente y revisar mensualmente el funcionamiento y los costos.",
    "Evaluar la publicación en Google Play como segundo paso y en la App Store solo si se cuenta con una computadora Mac y presupuesto anual.",
    "Incorporar pruebas automatizadas del filtro de riesgo para evitar errores al modificarlo."])

# ===========================================================================
# 23. Referencias
# ===========================================================================
h1("21. Referencias")
for ref in [
    "Apple Inc. (s. f.). <i>Apple Developer Program</i>. https://developer.apple.com/programs/",
    "Google. (s. f.). <i>App testing requirements for new personal developer accounts</i>. Play Console Help. https://support.google.com/googleplay/android-developer/answer/14151465",
    "Groq. (2026). <i>Speech to text</i>. https://console.groq.com/docs/speech-to-text",
    "Grinberg, M. (s. f.). <i>Flask-SocketIO documentation</i>. https://flask-socketio.readthedocs.io/",
    "Mozilla Developer Network. (s. f.). <i>Web Speech API</i>. https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API",
    "Pallets. (s. f.). <i>Flask documentation (3.0.x)</i>. https://flask.palletsprojects.com/",
    "Python Software Foundation. (s. f.). <i>Python 3.11 documentation</i>. https://docs.python.org/3.11/",
    "Render. (2026). <i>Persistent disks</i>. https://render.com/docs/disks",
    "Render. (2026). <i>Pricing</i>. https://render.com/pricing",
    "SQLite. (s. f.). <i>SQLite documentation</i>. https://www.sqlite.org/docs.html",
    "UNICEF. (2021). <i>The State of the World's Children 2021: On my mind — Promoting, protecting and caring for children's mental health</i>. https://www.unicef.org/reports/state-worlds-children-2021",
]:
    p(ref, "referencia")
p("Nota: las fuentes sobre los referentes Yana y Psonríe y la ubicación exacta del dato regional de UNICEF deben confirmarse antes de la entrega oficial.", "pendiente")

# ===========================================================================
# 24. Anexos
# ===========================================================================
salto()
h1("22. Anexos")
h2("Anexo A. Capturas de la plataforma")
figura("portada_banner.jpg", "Banner del programa psicopedagógico en la portada.")
figura("mural.jpg", "Mural de psicología: «Respira conmigo» y «¿Cómo te sientes hoy?».")
figura("herramientas.jpg", "Página de herramientas con los ejercicios por emoción.")
figura("libros.jpg", "Estante de libros de apoyo.")
figura("elegir_asistente.jpg", "Selección de asistente: Sami, Leo, Nia o «Sorpréndeme».")
figura("modo_voz.jpg", "Modo voz con el asistente.", 11)
figura("tigre_portada.jpg", "Sección del Tigre LMH en la portada.")
h2("Anexo B. Documentos pendientes de incorporar")
ul(["Manual de uso para la psicóloga.", "Video de demostración (plan de contingencia para la defensa).",
    "Fotografías de la práctica profesional en SULA, Bodega 6, si se cuenta con autorización de la empresa.",
    "Actas o constancias de aprobación institucional, si existen."])
p("Por privacidad, no se incluyen capturas del panel de la psicóloga ni del muro anónimo, ya que contienen mensajes de estudiantes.")

# ===========================================================================
# Lista final de datos pendientes
# ===========================================================================
salto()
h1("Datos pendientes de validación")
ol(["Nombre completo de la autora tal como figura en los registros del liceo.",
    "Asignatura, docente y asesor o asesora del proyecto.",
    "Fecha oficial de presentación del informe.",
    "Fechas de la fase de análisis y planificación.",
    "Datos institucionales del programa psicopedagógico (horario, población atendida, protocolos).",
    "Fechas de la práctica profesional y descripción institucional de SULA.",
    "Fuentes formales de los referentes Yana y Psonríe, y página exacta del dato de UNICEF.",
    "Validación del contenido y del filtro de riesgo por parte de la psicóloga.",
    "Precios vigentes de los equipos y del alojamiento al momento de la compra.",
    "Textos de la dedicatoria y los agradecimientos."])

# ---------------------------------------------------------------------------
ESTILO = """
@page Section1 { size: 8.5in 11.0in; margin: 1.0in 1.0in 1.0in 1.0in; mso-header-margin: .5in; mso-footer-margin: .5in; }
div.Section1 { page: Section1; }
body { font-family: Calibri, sans-serif; font-size: 11pt; }
p { margin: 0 0 8pt 0; text-align: justify; line-height: 115%; }
h1 { font-family: Calibri, sans-serif; font-size: 14pt; font-weight: bold; color: #1F4B2C; margin: 18pt 0 8pt 0; page-break-after: avoid; }
h2 { font-family: Calibri, sans-serif; font-size: 12pt; font-weight: bold; color: #354735; margin: 12pt 0 6pt 0; page-break-after: avoid; }
p.portada { text-align: center; font-size: 16pt; margin: 0 0 6pt 0; }
p.portada-izq { text-align: left; font-size: 16pt; margin: 0; }
p.portada-fecha { text-align: right; font-size: 16pt; margin: 0; }
p.titulo-indice { font-size: 14pt; font-weight: bold; color: #1F4B2C; text-align: center; }
p.titulo-tabla { text-align: center; font-size: 10pt; font-weight: bold; margin: 10pt 0 4pt 0; page-break-after: avoid; }
p.fuente { font-size: 9pt; color: #555555; margin: 2pt 0 10pt 0; text-align: left; }
p.figura { text-align: center; margin: 10pt 0 2pt 0; page-break-after: avoid; }
p.pie-figura { text-align: center; font-size: 10pt; font-style: italic; margin: 2pt 0 12pt 0; }
p.referencia { text-align: left; margin-left: .5in; text-indent: -.5in; }
p.pendiente { color: #7A5C00; font-style: italic; }
table.datos { border-collapse: collapse; width: 100%; margin: 0 0 4pt 0; }
table.datos th { background: #D9DFC7; border: 1px solid #A5B394; font-size: 10.5pt; padding: 4pt; text-align: left; }
table.datos td { border: 1px solid #A5B394; font-size: 10.5pt; padding: 4pt; vertical-align: top; text-align: left; }
ul, ol { margin-top: 0; margin-bottom: 8pt; }
li { margin-bottom: 4pt; text-align: justify; }
"""
documento = f"""<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">
<head><meta charset="utf-8"><title>Informe del proyecto No estamos solos LMH</title><style>{ESTILO}</style></head>
<body><div class="Section1">
{chr(10).join(partes)}
</div></body></html>"""
open(os.path.join(AQUI, "informe.html"), "w", encoding="utf-8").write(documento)
print(f"informe.html: {n_tabla[0]} tablas, {n_figura[0]} figuras")
