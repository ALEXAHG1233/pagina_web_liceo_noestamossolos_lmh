"""
Filtro de detección de riesgo emocional.

Funciona en dos niveles:
  1. Palabras/frases clave (regex) -> detección rápida e inmediata.
  2. Puntuación acumulada -> si varias señales "medias" aparecen juntas,
     el riesgo sube aunque ninguna sola sea crítica.

Este módulo NO decide nada por sí solo: solo clasifica el mensaje.
La psicóloga siempre es quien atiende; el filtro solo prioriza y alerta.
"""

import re

# Cada categoría tiene patrones con su propio peso (0-10).
# Los patrones son deliberadamente generales: cubren la intención,
# no una lista exhaustiva de frases exactas.
PATRONES = {
    "ideacion_suicida": {
        "peso": 10,
        "patrones": [
            r"\bno quiero (vivir|seguir viviendo|existir)\b",
            r"\bquiero (morir|desaparecer)\b",
            r"\bganas de (morir|no despertar)\b",
            r"\bya no aguanto (más|mas)\b",
            r"\bmejor (si|estarían mejor) sin m[ií]\b",
        ],
    },
    "autolesion": {
        "peso": 9,
        "patrones": [
            r"\bme (quiero|voy a) hacer daño\b",
            r"\blastimarme\b",
            r"\bcortarme\b",
        ],
    },
    "abuso_violencia": {
        "peso": 8,
        "patrones": [
            r"\bme (pega|pegan|golpea|golpean)\b",
            r"\babuso\b",
            r"\bme toca(n)? sin (permiso|querer)\b",
            r"\bmiedo de (ir a|llegar a) (mi )?casa\b",
        ],
    },
    "bullying": {
        "peso": 6,
        "patrones": [
            r"\bme molestan (todos los d[ií]as|siempre)\b",
            r"\bbullying\b",
            r"\bacoso escolar\b",
            r"\bse burlan de m[ií]\b",
        ],
    },
    "desesperanza": {
        "peso": 4,
        "patrones": [
            r"\bnada tiene sentido\b",
            r"\bestoy solo\b|\bestoy sola\b",
            r"\bnadie me entiende\b",
            r"\bno le importo a nadie\b",
        ],
    },
}

# Umbrales para clasificar el nivel final de riesgo
UMBRAL_CRITICO = 9
UMBRAL_ALTO = 6
UMBRAL_MEDIO = 3


def analizar_riesgo(texto: str) -> dict:
    """
    Analiza un mensaje y devuelve:
      {
        "nivel": "bajo" | "medio" | "alto" | "critico",
        "puntuacion": int,
        "categorias": ["ideacion_suicida", ...]
      }
    """
    texto_normalizado = texto.lower().strip()
    puntuacion = 0
    categorias_detectadas = []

    for categoria, datos in PATRONES.items():
        for patron in datos["patrones"]:
            if re.search(patron, texto_normalizado):
                puntuacion += datos["peso"]
                if categoria not in categorias_detectadas:
                    categorias_detectadas.append(categoria)
                break  # no sumar dos veces la misma categoría

    if puntuacion >= UMBRAL_CRITICO:
        nivel = "critico"
    elif puntuacion >= UMBRAL_ALTO:
        nivel = "alto"
    elif puntuacion >= UMBRAL_MEDIO:
        nivel = "medio"
    else:
        nivel = "bajo"

    return {
        "nivel": nivel,
        "puntuacion": puntuacion,
        "categorias": categorias_detectadas,
    }


if __name__ == "__main__":
    # Pruebas rápidas manuales
    ejemplos = [
        "hola, ¿cómo estás?",
        "en mi casa se burlan de mí todos los días",
        "no quiero seguir viviendo, ya no aguanto más",
    ]
    for e in ejemplos:
        print(e, "->", analizar_riesgo(e))
