"""
Técnicas prácticas de TCC (Terapia Cognitivo-Conductual) y TDC (Terapia
Dialéctico-Conductual), en formato de pasos simples para autoaplicar.

Son herramientas de autoayuda, no terapia en sí — están disponibles en
cualquier momento (24/7) porque son contenido estático, no dependen de que
haya alguien conectado del otro lado. Para algo que necesite más que estas
técnicas, cada una recuerda que la psicóloga sigue siendo la opción real.
"""

TECNICAS = {
    "tcc": {
        "titulo": "TCC — Terapia Cognitivo-Conductual",
        "descripcion": "Técnicas para identificar y cuestionar pensamientos que te hacen sentir peor de lo necesario.",
        "color": "azul",
        "tecnicas": {
            "reestructuracion": {
                "nombre": "Reestructuración cognitiva",
                "resumen": "Cuestionar un pensamiento que te está pesando, paso a paso.",
                "video_youtube_id": "hVpw2JrlQMs",
                "pasos": [
                    "Identifica el pensamiento exacto que te está afectando (ej: \"soy un fracaso\").",
                    "Pregúntate: ¿qué evidencia tengo de que esto es cierto? ¿Qué evidencia tengo de que NO lo es?",
                    "Pregúntate: si un amigo pensara esto de sí mismo, ¿qué le dirías?",
                    "Escribe un pensamiento alternativo, más balanceado (no necesariamente positivo, solo más justo). Ej: \"Me fue mal en esto, pero eso no define todo lo que soy\".",
                ],
            },
            "activacion": {
                "nombre": "Activación conductual",
                "resumen": "Cuando el ánimo está bajo, hacer algo (aunque no den ganas) ayuda a que el ánimo suba, y no al revés.",
                "video_youtube_id": "aP5RHNG9q-s",
                "pasos": [
                    "Elige una actividad pequeña y concreta (no \"sentirme mejor\", sino algo específico: salir a caminar 10 minutos, bañarte, escribirle a alguien).",
                    "Hazla aunque no tengas ganas — la motivación muchas veces llega DESPUÉS de empezar, no antes.",
                    "Nota cómo te sientes al terminar, aunque sea un cambio pequeño.",
                    "Repite con otra actividad pequeña mañana. Son pasos, no saltos.",
                ],
            },
            "respiracion": {
                "nombre": "Respiración 4-4-4",
                "resumen": "Para bajar la ansiedad en el momento, en menos de un minuto.",
                "video_youtube_id": "Nvtr6Ms4bmo",
                "pasos": [
                    "Inhala contando lentamente hasta 4.",
                    "Sostén el aire contando hasta 4.",
                    "Exhala lentamente contando hasta 4.",
                    "Repite 4 o 5 veces. Si te mareas, vuelve a respirar normal un momento.",
                ],
            },
            "relajacion_muscular": {
                "nombre": "Relajación muscular progresiva",
                "resumen": "Para soltar la tensión física acumulada, grupo de músculos por grupo de músculos.",
                "video_youtube_id": None,
                "pasos": [
                    "Siéntate o acuéstate cómodamente.",
                    "Tensa los músculos de los pies con fuerza por 5 segundos, luego suelta de golpe.",
                    "Sube por el cuerpo: pantorrillas, piernas, abdomen, brazos, hombros, cara — tensando y soltando cada grupo.",
                    "Al terminar, nota la diferencia entre cómo se sentía tenso y cómo se siente ahora.",
                ],
            },
        },
    },
    "tdc": {
        "titulo": "TDC — Terapia Dialéctico-Conductual",
        "descripcion": "Técnicas para momentos de mucha intensidad emocional, y para manejar mejor tus relaciones con otros.",
        "color": "dorado",
        "tecnicas": {
            "tipp": {
                "nombre": "TIPP (para crisis emocional intensa)",
                "resumen": "Para cuando la emoción es tan fuerte que sientes que vas a explotar o colapsar.",
                "video_youtube_id": "y379TF6XOJc",
                "pasos": [
                    "Temperatura: moja tu cara con agua fría, o sostén un hielo un momento — esto baja la intensidad física de la emoción rápido.",
                    "Ejercicio intenso: si puedes, haz algo físico breve e intenso (saltar, correr en el lugar) por un minuto.",
                    "Respiración pausada: exhala más lento de lo que inhalas (ej. inhala en 4, exhala en 6).",
                    "Relajación muscular: tensa y suelta los músculos, como en la técnica de TCC de arriba.",
                ],
            },
            "autocalma_sentidos": {
                "nombre": "Autocalma con los 5 sentidos",
                "resumen": "Para regresar al presente cuando todo se siente abrumador.",
                "video_youtube_id": "hXV3Od4uz9M",
                "pasos": [
                    "Vista: busca 3 cosas que puedas ver y nómbralas en voz baja.",
                    "Oído: identifica 2 sonidos que puedas escuchar ahora mismo.",
                    "Tacto: siente la textura de algo cerca de ti (tu ropa, una mesa, tu cabello).",
                    "Olfato/gusto: si puedes, huele algo agradable o toma un sorbo de agua, notando la sensación.",
                ],
            },
            "stop": {
                "nombre": "La habilidad STOP",
                "resumen": "Para no reaccionar de forma impulsiva en un momento difícil.",
                "video_youtube_id": "XzUF0_BC7Vo",
                "pasos": [
                    "S — Para (Stop): detente, no hagas nada todavía.",
                    "T — Toma distancia: da un paso atrás, mental o físicamente.",
                    "O — Observa: ¿qué está pasando, dentro y fuera de ti, ahora mismo?",
                    "P — Procede con conciencia: decide tu siguiente paso con calma, no desde el impulso.",
                ],
            },
            "dear_man": {
                "nombre": "DEAR MAN (para pedir algo o poner un límite)",
                "resumen": "Una forma de comunicarte de manera clara y respetuosa en una conversación difícil.",
                "video_youtube_id": "eVqWl1Sfav8",
                "pasos": [
                    "Describe la situación con hechos, sin juzgar (\"Cuando pasó X...\").",
                    "Expresa cómo te sientes al respecto (\"...me sentí Y\").",
                    "Afirma lo que necesitas o pides, de forma directa (\"Lo que necesito es Z\").",
                    "Refuerza por qué eso ayuda a ambos, mantente firme (Mantén tu postura) y Atento/Negociable si hace falta ceder un poco.",
                ],
            },
        },
    },
    "respiracion_meditacion": {
        "titulo": "Respiración y meditación",
        "descripcion": "Ejercicios cortos para calmar el cuerpo y aquietar la mente, cuando quieras — no toman más de unos minutos.",
        "color": "verde",
        "tecnicas": {
            "respiracion_diafragmatica": {
                "nombre": "Respiración diafragmática (desde el estómago)",
                "resumen": "La base de casi todas las técnicas de calma: respirar profundo de verdad, no superficial.",
                "video_youtube_id": "TuPaMCsnxes",
                "pasos": [
                    "Pon una mano en el pecho y otra en el estómago.",
                    "Inhala por la nariz dejando que se infle el estómago (la mano del pecho se mueve poco).",
                    "Exhala lento por la boca, sintiendo cómo baja el estómago.",
                    "Repite durante 1-2 minutos, sin forzar el ritmo.",
                ],
            },
            "respiracion_caja": {
                "nombre": "Respiración en caja (box breathing)",
                "resumen": "Usada incluso por equipos de rescate para mantener la calma bajo presión.",
                "video_youtube_id": "tEmt1Znux58",
                "pasos": [
                    "Inhala contando hasta 4.",
                    "Sostén el aire contando hasta 4.",
                    "Exhala contando hasta 4.",
                    "Mantén los pulmones vacíos contando hasta 4. Repite el ciclo 4-6 veces.",
                ],
            },
            "meditacion_breve": {
                "nombre": "Meditación breve guiada (3 minutos)",
                "resumen": "Una meditación simple de atención plena, sin necesidad de experiencia previa.",
                "video_youtube_id": "_lOpSbsm9y4",
                "pasos": [
                    "Siéntate cómodo/a, cierra los ojos o baja la mirada.",
                    "Lleva la atención a tu respiración, sin cambiarla, solo notándola entrar y salir.",
                    "Cuando notes que tu mente se fue a otro pensamiento (va a pasar, es normal), solo regresa la atención a la respiración, sin juzgarte.",
                    "Haz esto durante 2-3 minutos. Al terminar, abre los ojos despacio y nota cómo te sientes.",
                ],
            },
            "escaneo_corporal": {
                "nombre": "Escaneo corporal",
                "resumen": "Para reconectar con tu cuerpo y bajar la tensión que no habías notado que tenías.",
                "video_youtube_id": "xmKKab7h4s8",
                "pasos": [
                    "Acuéstate o siéntate cómodamente y cierra los ojos.",
                    "Lleva la atención a tus pies: ¿qué sientes ahí? Sin cambiar nada, solo nota.",
                    "Sube lentamente la atención: piernas, abdomen, pecho, brazos, manos, cuello, cara — notando cada zona unos segundos.",
                    "Al terminar, respira profundo una vez y abre los ojos.",
                ],
            },
        },
    },
}
