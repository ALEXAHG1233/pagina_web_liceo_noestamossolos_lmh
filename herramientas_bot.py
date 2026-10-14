"""
Herramientas para sentirse mejor, ordenadas por lo que la persona siente
(ansiedad, enojo, tristeza...) y escritas con palabras sencillas, para que
las entienda cualquier estudiante, también los más pequeños.

Por dentro vienen de técnicas reales de la psicología (por ejemplo, la
Terapia Cognitivo-Conductual y la Dialéctico-Conductual), pero en la página
se muestran con nombres fáciles. Son herramientas de autoayuda, no terapia:
están disponibles las 24 horas porque son contenido fijo, y cada una
recuerda que la psicóloga sigue siendo la opción real cuando algo pesa mucho.

Cada categoría tiene:
  - "corto": nombre breve para los botones de arriba de la página.
  - "sintomas": señales para reconocer lo que estás sintiendo.
  - "tecnicas": cada una con nombre, resumen, pasos y (si existe) un video.
"""

TECNICAS = {
    "ansiedad": {
        "titulo": "Cuando siento ansiedad o nervios",
        "corto": "Ansiedad",
        "descripcion": "Para cuando el miedo o la preocupación no te dejan en paz.",
        "color": "azul",
        "sintomas": [
            "El corazón late muy rápido.",
            "Te sudan o tiemblan las manos.",
            "Sientes un nudo en el estómago o en la garganta.",
            "Piensas una y otra vez que algo malo va a pasar.",
        ],
        "tecnicas": {
            "respiracion": {
                "nombre": "Respiración 4-4-4-4",
                "resumen": "Respirar dibujando un cuadrado: 4 lados de 4 segundos. Baja los nervios en un minuto.",
                "video_youtube_id": "Nvtr6Ms4bmo",
                "pasos": [
                    "Toma aire por la nariz contando despacio hasta 4 (subes por un lado del cuadrado).",
                    "Aguanta el aire contando hasta 4 (cruzas el lado de arriba).",
                    "Suelta el aire por la boca contando hasta 4 (bajas por el otro lado).",
                    "Quédate sin aire contando hasta 4 (cruzas el lado de abajo).",
                    "Da 4 o 5 vueltas al cuadrado. Si te mareas, respira normal y descansa.",
                ],
            },
            "respiracion_globo": {
                "nombre": "Respirar como un globo",
                "resumen": "Llenar la panza de aire, como un globo, para que el cuerpo se calme.",
                "video_youtube_id": "TuPaMCsnxes",
                "pasos": [
                    "Pon una mano en tu pecho y otra en tu panza.",
                    "Toma aire por la nariz e intenta que se infle la panza, no el pecho, como un globo.",
                    "Suelta el aire despacio por la boca, como si apagaras una vela sin prisa.",
                    "Hazlo 5 veces. Es la base de casi todos los ejercicios para calmarse.",
                ],
            },
            "cinco_sentidos": {
                "nombre": "El juego de los 5 sentidos (5-4-3-2-1)",
                "resumen": "Volver al presente cuando la mente se va a lo que da miedo.",
                "video_youtube_id": "hXV3Od4uz9M",
                "pasos": [
                    "Nombra 5 cosas que puedes ver a tu alrededor.",
                    "Nombra 4 cosas que puedes tocar (tu ropa, la mesa, tu cabello).",
                    "Nombra 3 sonidos que puedes escuchar.",
                    "Nombra 2 olores y 1 sabor. Al terminar, tu mente ya está aquí y no en el miedo.",
                ],
            },
            "hora_preocupacion": {
                "nombre": "La caja de las preocupaciones",
                "resumen": "Guardar las preocupaciones para más tarde, en vez de pensarlas todo el día.",
                "video_youtube_id": None,
                "pasos": [
                    "Escribe en un papel lo que te preocupa, una cosa por línea.",
                    "Dobla el papel y guárdalo en una caja, un sobre o tu cuaderno.",
                    "Elige una hora del día (15 minutos) para leerlo y pensar qué puedes hacer.",
                    "Si la preocupación vuelve antes, dile: \"ya te guardé, te veo a las 5\".",
                ],
            },
        },
    },
    "enojo": {
        "titulo": "Cuando siento mucho enojo (ira)",
        "corto": "Enojo",
        "descripcion": "Para cuando el enojo crece rápido y no quieres hacer algo de lo que te arrepientas.",
        "color": "rojo",
        "sintomas": [
            "Sientes calor en la cara o en el pecho.",
            "Aprietas los puños o los dientes.",
            "Tienes ganas de gritar, golpear o romper algo.",
            "Te cuesta escuchar a los demás.",
        ],
        "tecnicas": {
            "semaforo": {
                "nombre": "El semáforo: alto, piensa, actúa",
                "resumen": "Frenar un segundo antes de reaccionar.",
                "video_youtube_id": "XzUF0_BC7Vo",
                "pasos": [
                    "Rojo: ALTO. No digas ni hagas nada todavía, quédate quieto/a.",
                    "Amarillo: respira hondo y mira qué está pasando de verdad.",
                    "Piensa: ¿qué pasaría si reacciono ahora? ¿y si espero un poco?",
                    "Verde: ahora sí, actúa de la forma que no te va a hacer daño ni a ti ni a otros.",
                ],
            },
            "contar_alejarse": {
                "nombre": "Contar hasta 10 y alejarme",
                "resumen": "Darle tiempo al enojo para que baje antes de hablar.",
                "video_youtube_id": None,
                "pasos": [
                    "Cuando sientas que el enojo sube, cuenta despacio del 1 al 10.",
                    "Si sigues muy enojado/a, di \"necesito un momento\" y aléjate un poco.",
                    "Camina, toma agua o respira como un globo mientras te calmas.",
                    "Cuando ya estés más tranquilo/a, vuelve a hablar del problema.",
                ],
            },
            "enfriar_cuerpo": {
                "nombre": "Enfriar el cuerpo cuando todo explota",
                "resumen": "Para un enojo o una emoción muy fuerte: calmar primero el cuerpo.",
                "video_youtube_id": "y379TF6XOJc",
                "pasos": [
                    "Moja tu cara con agua fría, o sostén algo frío unos segundos.",
                    "Haz ejercicio fuerte por un minuto: salta, corre en tu lugar o sube escaleras.",
                    "Respira más lento: que soltar el aire dure más que tomarlo.",
                    "Aprieta y suelta los músculos, como en el ejercicio de la tortuga.",
                ],
            },
            "tortuga": {
                "nombre": "La tortuga: aprieto y suelto",
                "resumen": "Apretar y soltar los músculos para sacar la tensión del cuerpo.",
                "video_youtube_id": None,
                "pasos": [
                    "Siéntate o acuéstate cómodo/a.",
                    "Aprieta fuerte los puños 5 segundos, como una tortuga que se esconde, y luego suelta.",
                    "Haz lo mismo con los hombros, la cara, la panza y las piernas.",
                    "Fíjate en la diferencia entre la tensión y el descanso.",
                ],
            },
            "escribir_romper": {
                "nombre": "Escribir y romper",
                "resumen": "Sacar el enojo en un papel, sin lastimar a nadie.",
                "video_youtube_id": None,
                "pasos": [
                    "Toma una hoja y escribe todo lo que te enoja, tal como lo sientes.",
                    "No tienes que cuidar la letra ni las palabras, nadie lo va a leer.",
                    "Cuando termines, rompe el papel en pedacitos.",
                    "Después pregúntate: ¿qué necesito ahora para sentirme mejor?",
                ],
            },
        },
    },
    "tristeza": {
        "titulo": "Cuando me siento triste o sin ganas (depresión)",
        "corto": "Tristeza",
        "descripcion": "Para cuando la tristeza dura varios días y todo cuesta más.",
        "color": "morado",
        "sintomas": [
            "Lloras seguido o tienes ganas de llorar.",
            "Ya no disfrutas lo que antes te gustaba.",
            "Duermes mucho o casi no duermes.",
            "Te alejas de tus amigos o de tu familia.",
            "Si esto dura más de dos semanas, habla con la psicóloga.",
        ],
        "tecnicas": {
            "paso_pequeno": {
                "nombre": "Un paso pequeño cada día",
                "resumen": "Cuando no hay ganas de nada, hacer algo pequeño ayuda a que el ánimo suba.",
                "video_youtube_id": "aP5RHNG9q-s",
                "pasos": [
                    "Elige algo pequeño y concreto: bañarte, salir 10 minutos, escribirle a alguien.",
                    "Hazlo aunque no tengas ganas. Muchas veces las ganas llegan después de empezar.",
                    "Fíjate cómo te sientes al terminar, aunque sea un poquito mejor.",
                    "Mañana elige otro paso pequeño. Son pasos, no saltos.",
                ],
            },
            "revisar_pensamientos": {
                "nombre": "Revisar lo que me digo",
                "resumen": "Cambiar un pensamiento que te hace daño por uno más justo contigo.",
                "video_youtube_id": "hVpw2JrlQMs",
                "pasos": [
                    "Escribe lo que te estás diciendo, por ejemplo: \"soy un fracaso\".",
                    "Pregúntate: ¿qué pruebas tengo de que es verdad? ¿y de que no lo es?",
                    "Pregúntate: si un amigo pensara esto de sí mismo, ¿qué le diría yo?",
                    "Escribe una frase más justa: \"me fue mal en esto, pero eso no es todo lo que soy\".",
                ],
            },
            "tres_cosas_buenas": {
                "nombre": "Tres cosas buenas",
                "resumen": "Entrenar a la mente para notar también lo que sí salió bien.",
                "video_youtube_id": None,
                "pasos": [
                    "Antes de dormir, piensa en tu día.",
                    "Escribe 3 cosas buenas que pasaron, aunque sean pequeñas (una comida rica, una risa).",
                    "Al lado de cada una, escribe por qué pasó o quién la hizo posible.",
                    "Hazlo una semana y lee tu lista cuando te sientas mal.",
                ],
            },
            "persona_confianza": {
                "nombre": "Mi lista de personas de confianza",
                "resumen": "Saber a quién acudir antes de que lo necesites.",
                "video_youtube_id": None,
                "pasos": [
                    "Piensa en 3 personas con las que te sientas seguro/a: familia, amigos, maestros.",
                    "Escribe sus nombres y cómo contactarlas.",
                    "Agrega a la psicóloga del liceo y la línea 150 del Teléfono de la Esperanza.",
                    "Cuando te sientas mal, elige a una y escríbele: \"¿puedo hablar contigo?\".",
                ],
            },
            "moverse": {
                "nombre": "Moverme 10 minutos",
                "resumen": "El cuerpo en movimiento ayuda a que la mente se sienta mejor.",
                "video_youtube_id": None,
                "pasos": [
                    "Elige algo que puedas hacer ahora: caminar, bailar una canción, estirarte.",
                    "Hazlo por 10 minutos, sin pensar en hacerlo perfecto.",
                    "Si puedes, hazlo al aire libre o cerca de una ventana.",
                    "Nota cómo se siente tu cuerpo al terminar.",
                ],
            },
        },
    },
    "calma": {
        "titulo": "Cuando quiero calmar mi mente",
        "corto": "Calma",
        "descripcion": "Ejercicios cortos para cuando hay mucho estrés o la cabeza no para.",
        "color": "verde",
        "sintomas": [
            "Sientes que tienes demasiadas cosas que hacer.",
            "Te duele la cabeza o la espalda por la tensión.",
            "Te cuesta concentrarte.",
            "Estás de mal humor sin saber bien por qué.",
        ],
        "tecnicas": {
            "meditacion_breve": {
                "nombre": "Pausa de 3 minutos",
                "resumen": "Una meditación muy corta para darle un descanso a tu mente.",
                "video_youtube_id": "_lOpSbsm9y4",
                "pasos": [
                    "Siéntate cómodo/a y cierra los ojos, o mira un punto fijo.",
                    "Durante un minuto, nota cómo entra y sale el aire.",
                    "Si te distraes, no pasa nada: vuelve a fijarte en la respiración.",
                    "Al terminar, abre los ojos despacio y fíjate cómo te sientes.",
                ],
            },
            "recorrer_cuerpo": {
                "nombre": "Recorrer mi cuerpo",
                "resumen": "Pasar la atención por cada parte del cuerpo para soltar la tensión.",
                "video_youtube_id": "xmKKab7h4s8",
                "pasos": [
                    "Acuéstate o siéntate y cierra los ojos.",
                    "Empieza por los pies: nota cómo se sienten, sin cambiar nada.",
                    "Sube poco a poco: piernas, panza, pecho, brazos, cuello y cara.",
                    "Si encuentras una parte tensa, respira hacia ella y déjala aflojar.",
                ],
            },
            "lugar_seguro": {
                "nombre": "Mi lugar seguro",
                "resumen": "Imaginar un lugar donde te sientes tranquilo/a y a salvo.",
                "video_youtube_id": None,
                "pasos": [
                    "Cierra los ojos y piensa en un lugar real o inventado donde te sientas tranquilo/a.",
                    "Imagina qué ves ahí, qué escuchas, qué hueles y qué temperatura hace.",
                    "Quédate ahí un minuto, respirando despacio.",
                    "Recuerda que puedes volver a ese lugar en tu mente cuando lo necesites.",
                ],
            },
        },
    },
    "decir": {
        "titulo": "Cuando necesito decir lo que siento",
        "corto": "Decir lo que siento",
        "descripcion": "Para pedir lo que necesitas o decir que no, sin pelear.",
        "color": "dorado",
        "sintomas": [
            "Te quedas callado/a aunque algo te molesta.",
            "Terminas gritando cuando intentas explicar algo.",
            "Te cuesta decir que no.",
        ],
        "tecnicas": {
            "pedir_respeto": {
                "nombre": "Pedir algo o decir que no, con respeto",
                "resumen": "Una forma clara de pedir lo que necesitas o poner un límite.",
                "video_youtube_id": "eVqWl1Sfav8",
                "pasos": [
                    "Cuenta qué pasó, sin exagerar: \"ayer no me esperaste a la salida\".",
                    "Di cómo te sentiste: \"me sentí triste y solo/a\".",
                    "Pide algo concreto: \"¿me avisas la próxima vez?\".",
                    "Mantente tranquilo/a. Puedes repetirlo con calma si no te escuchan.",
                ],
            },
            "mensajes_yo": {
                "nombre": "Hablar con \"yo siento\"",
                "resumen": "Decir lo que sientes sin culpar, para que la otra persona te escuche.",
                "video_youtube_id": None,
                "pasos": [
                    "En vez de \"tú siempre...\", empieza con \"yo me siento...\".",
                    "Explica cuándo: \"...cuando me interrumpen\".",
                    "Di por qué: \"...porque siento que no importa lo que digo\".",
                    "Termina con lo que necesitas: \"me gustaría que me dejaras terminar\".",
                ],
            },
        },
    },
    "dormir": {
        "titulo": "Cuando no puedo dormir",
        "corto": "Dormir",
        "descripcion": "Para las noches en que la cabeza no se apaga.",
        "color": "azul",
        "sintomas": [
            "Das muchas vueltas en la cama.",
            "Te despiertas varias veces en la noche.",
            "Te levantas cansado/a aunque dormiste.",
        ],
        "tecnicas": {
            "rutina_noche": {
                "nombre": "Mi rutina antes de dormir",
                "resumen": "Avisarle al cuerpo que ya es hora de descansar.",
                "video_youtube_id": None,
                "pasos": [
                    "Deja el celular y las pantallas 30 minutos antes de dormir.",
                    "Haz siempre las mismas cosas: bañarte, lavarte los dientes, leer un poco.",
                    "Intenta acostarte y levantarte a la misma hora todos los días.",
                    "Si a los 20 minutos no te duermes, levántate un rato y vuelve cuando tengas sueño.",
                ],
            },
            "respiracion_478": {
                "nombre": "Respiración 4-7-8 para dormir",
                "resumen": "Una respiración lenta que ayuda al cuerpo a relajarse en la cama.",
                "video_youtube_id": None,
                "pasos": [
                    "Acostado/a, toma aire por la nariz contando hasta 4.",
                    "Aguanta el aire contando hasta 7.",
                    "Suéltalo despacio por la boca contando hasta 8.",
                    "Repite 4 veces. Si 7 y 8 se te hacen mucho, usa números más cortos.",
                ],
            },
        },
    },
    "estudiar": {
        "titulo": "Para estudiar mejor",
        "corto": "Estudiar",
        "descripcion": "Hábitos de estudio para aprender más con menos estrés.",
        "color": "verde",
        "sintomas": [
            "Estudias mucho tiempo pero se te olvida todo.",
            "Dejas las tareas para el último momento.",
            "Te distraes con el celular cada pocos minutos.",
        ],
        "tecnicas": {
            "tomate": {
                "nombre": "La técnica del tomate (25 y 5)",
                "resumen": "Estudiar en ratos cortos con descansos, para no cansarte.",
                "video_youtube_id": None,
                "pasos": [
                    "Elige una sola tarea y guarda el celular lejos.",
                    "Pon un temporizador de 25 minutos y estudia solo eso.",
                    "Cuando suene, descansa 5 minutos: estírate, toma agua.",
                    "Después de 4 rondas, descansa más tiempo (15 a 30 minutos).",
                ],
            },
            "organizar_semana": {
                "nombre": "Organizar mi semana",
                "resumen": "Ver todo lo que tienes que hacer para que no te tome por sorpresa.",
                "video_youtube_id": None,
                "pasos": [
                    "El domingo, escribe tus tareas y exámenes de la semana.",
                    "Divide lo grande en partes pequeñas (\"leer el capítulo 1\" en vez de \"estudiar todo\").",
                    "Pon cada parte en un día, dejando espacio para descansar.",
                    "Cada noche tacha lo que hiciste. Ver el avance motiva.",
                ],
            },
            "explicarlo": {
                "nombre": "Explicárselo a alguien",
                "resumen": "Si puedes explicarlo con palabras sencillas, de verdad lo entendiste.",
                "video_youtube_id": None,
                "pasos": [
                    "Elige un tema que estés estudiando.",
                    "Explícalo en voz alta como si se lo contaras a un niño más pequeño.",
                    "Si te trabas, esa es la parte que debes repasar.",
                    "Vuelve a estudiar esa parte y explícala otra vez.",
                ],
            },
        },
    },
}
