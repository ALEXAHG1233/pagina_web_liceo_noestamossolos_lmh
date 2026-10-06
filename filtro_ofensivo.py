"""
Filtro simple de lenguaje ofensivo para contenido público (como el Muro
Interactivo). No reemplaza la moderación humana: solo evita que insultos
obvios se publiquen directo, igual que el filtro de riesgo evita que una
crisis real se publique en un muro público. La psicóloga también puede
bloquear cualquier publicación manualmente si algo se les escapa a estos
patrones.
"""

import re

PALABRAS_OFENSIVAS = [
    r"\bidiota(s)?\b",
    r"\bestupid[oa](s)?\b",
    r"\bimb[eé]cil(es)?\b",
    r"\bpendej[oa](s)?\b",
    r"\bmaldit[oa](s)?\b",
    r"\bbasura\b",
    r"\bmierda(s)?\b",
    r"\bput[oa](s)?\b",
    r"\bperra(s)?\b",
    r"\bcabr[oó]n(es)?\b",
    r"\bzorra(s)?\b",
    r"\bretrasad[oa](s)?\b",
    r"\bin[uú]til(es)?\b",
]


def contiene_lenguaje_ofensivo(texto: str) -> bool:
    texto_normalizado = texto.lower().strip()
    return any(re.search(patron, texto_normalizado) for patron in PALABRAS_OFENSIVAS)
