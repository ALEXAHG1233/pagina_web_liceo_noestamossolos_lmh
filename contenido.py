"""
Contenido que la psicóloga puede cambiar desde su panel, sin tocar el código.

El contenido "de fábrica" sigue en articulos_bot.py y herramientas_bot.py.
Lo que la psicóloga edita se guarda en la base de datos y se aplica encima:

  - Si edita un artículo o herramienta que ya existía, su versión reemplaza
    a la original (y puede "restaurar" para volver a la de fábrica).
  - Si crea uno nuevo, se agrega.
  - Si lo esconde, deja de aparecer en la página (sin borrarse).

También guarda textos de la portada (frases, mitos, historias), los ajustes
(como el WhatsApp del botón flotante) y si una publicación del muro o una
reseña está escondida.
"""

import copy
import json
import re
import sqlite3
from datetime import datetime

from articulos_bot import ARTICULOS
from herramientas_bot import TECNICAS

DB_PATH = None  # lo pone app.py al iniciar


def configurar(db_path):
    global DB_PATH
    DB_PATH = db_path


def _conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_tablas(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contenido_articulos (
            slug TEXT PRIMARY KEY,
            titulo TEXT,
            categoria TEXT,
            resumen TEXT,
            contenido TEXT,       -- párrafos separados por una línea en blanco
            video TEXT,           -- ID de YouTube (opcional)
            oculto INTEGER DEFAULT 0,
            actualizado TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contenido_herramientas (
            clave TEXT PRIMARY KEY,   -- "categoria/id"
            categoria TEXT,
            nombre TEXT,
            resumen TEXT,
            pasos TEXT,               -- un paso por línea
            video TEXT,
            oculto INTEGER DEFAULT 0,
            actualizado TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contenido_textos (
            clave TEXT PRIMARY KEY,   -- frases | mitos | historias
            valor TEXT,               -- JSON
            actualizado TEXT
        )
        """
    )
    cur.execute("CREATE TABLE IF NOT EXISTS ajustes (clave TEXT PRIMARY KEY, valor TEXT)")
    for tabla in ("muro_posts", "resenas"):
        try:
            cur.execute(f"ALTER TABLE {tabla} ADD COLUMN oculto INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # ya existe


def _ahora():
    return datetime.now().isoformat(timespec="seconds")


def crear_slug(texto):
    texto = texto.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ü", "u"), ("ñ", "n")):
        texto = texto.replace(a, b)
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    return texto[:60] or "sin-titulo"


def separar_parrafos(texto):
    return [p.strip() for p in re.split(r"\n\s*\n", texto or "") if p.strip()]


def separar_lineas(texto):
    return [l.strip(" -•\t") for l in (texto or "").splitlines() if l.strip(" -•\t")]


def id_youtube(texto):
    """Acepta un ID o un enlace de YouTube y devuelve solo el ID (o '')."""
    texto = (texto or "").strip()
    m = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})", texto)
    if m:
        return m.group(1)
    return texto if re.fullmatch(r"[A-Za-z0-9_-]{11}", texto) else ""


# ---------------------------------------------------------------------------
# Artículos
# ---------------------------------------------------------------------------
def _filas_articulos():
    with _conectar() as conn:
        return {f["slug"]: dict(f) for f in conn.execute("SELECT * FROM contenido_articulos")}


def articulos(incluir_ocultos=False):
    """Los artículos que se muestran: los de fábrica con los cambios de la
    psicóloga aplicados, más los que ella creó. Cada uno lleva "origen"
    (fabrica | editado | nuevo) y "oculto"."""
    base = copy.deepcopy(ARTICULOS)
    for a in base.values():
        a["origen"] = "fabrica"
        a["oculto"] = False
    for slug, f in _filas_articulos().items():
        a = base.get(slug)
        if a is None:
            a = {"origen": "nuevo"}
            base[slug] = a
        else:
            a["origen"] = "editado"
        a["titulo"] = f["titulo"]
        a["categoria"] = f["categoria"]
        a["resumen"] = f["resumen"]
        a["contenido"] = separar_parrafos(f["contenido"])
        if f["video"]:
            a["video_youtube_id"] = f["video"]
        else:
            a.pop("video_youtube_id", None)
        a["oculto"] = bool(f["oculto"])
    if incluir_ocultos:
        return base
    return {s: a for s, a in base.items() if not a["oculto"]}


def guardar_articulo(slug, titulo, categoria, resumen, contenido, video):
    if not slug:
        slug = crear_slug(titulo)
        existentes = set(ARTICULOS) | set(_filas_articulos())
        base, n = slug, 2
        while slug in existentes:
            slug, n = f"{base}-{n}", n + 1
    oculto = _filas_articulos().get(slug, {}).get("oculto", 0)
    with _conectar() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO contenido_articulos VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (slug, titulo, categoria, resumen, contenido, id_youtube(video), oculto, _ahora()),
        )
    return slug


def poner_oculto_articulo(slug, oculto):
    filas = _filas_articulos()
    if slug not in filas:
        a = ARTICULOS.get(slug)
        if not a:
            return
        guardar_articulo(slug, a["titulo"], a["categoria"], a["resumen"],
                         "\n\n".join(a["contenido"]), a.get("video_youtube_id", ""))
    with _conectar() as conn:
        conn.execute("UPDATE contenido_articulos SET oculto = ? WHERE slug = ?", (1 if oculto else 0, slug))


def restaurar_articulo(slug):
    """Quita los cambios de la psicóloga (si era uno nuevo, lo borra)."""
    with _conectar() as conn:
        conn.execute("DELETE FROM contenido_articulos WHERE slug = ?", (slug,))


# ---------------------------------------------------------------------------
# Herramientas
# ---------------------------------------------------------------------------
def _filas_herramientas():
    with _conectar() as conn:
        return {f["clave"]: dict(f) for f in conn.execute("SELECT * FROM contenido_herramientas")}


def tecnicas(incluir_ocultos=False):
    base = copy.deepcopy(TECNICAS)
    for cat in base.values():
        for t in cat["tecnicas"].values():
            t["origen"] = "fabrica"
            t["oculto"] = False
    for clave, f in _filas_herramientas().items():
        cat_id, tec_id = clave.split("/", 1)
        cat = base.get(f["categoria"]) or base.get(cat_id)
        if cat is None:
            continue
        # Si la cambiaron de categoría, se quita de la anterior.
        if f["categoria"] != cat_id and cat_id in base:
            base[cat_id]["tecnicas"].pop(tec_id, None)
        t = cat["tecnicas"].get(tec_id)
        if t is None:
            t = {"origen": "nuevo"}
            cat["tecnicas"][tec_id] = t
        elif t.get("origen") == "fabrica":
            t["origen"] = "editado"
        t["nombre"] = f["nombre"]
        t["resumen"] = f["resumen"]
        t["pasos"] = separar_lineas(f["pasos"])
        t["video_youtube_id"] = f["video"] or None
        t["oculto"] = bool(f["oculto"])
    if not incluir_ocultos:
        for cat in base.values():
            cat["tecnicas"] = {k: t for k, t in cat["tecnicas"].items() if not t["oculto"]}
    return base


def guardar_herramienta(clave, categoria, nombre, resumen, pasos, video):
    if not clave:
        tec_id = crear_slug(nombre)
        existentes = {f"{c}/{t}" for c, cat in TECNICAS.items() for t in cat["tecnicas"]} | set(_filas_herramientas())
        base, n = tec_id, 2
        while f"{categoria}/{tec_id}" in existentes:
            tec_id, n = f"{base}-{n}", n + 1
        clave = f"{categoria}/{tec_id}"
    oculto = _filas_herramientas().get(clave, {}).get("oculto", 0)
    with _conectar() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO contenido_herramientas VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (clave, categoria, nombre, resumen, pasos, id_youtube(video), oculto, _ahora()),
        )
    return clave


def poner_oculto_herramienta(clave, oculto):
    if clave not in _filas_herramientas():
        cat_id, tec_id = clave.split("/", 1)
        t = TECNICAS.get(cat_id, {}).get("tecnicas", {}).get(tec_id)
        if not t:
            return
        guardar_herramienta(clave, cat_id, t["nombre"], t["resumen"], "\n".join(t["pasos"]), t.get("video_youtube_id") or "")
    with _conectar() as conn:
        conn.execute("UPDATE contenido_herramientas SET oculto = ? WHERE clave = ?", (1 if oculto else 0, clave))


def restaurar_herramienta(clave):
    with _conectar() as conn:
        conn.execute("DELETE FROM contenido_herramientas WHERE clave = ?", (clave,))


# ---------------------------------------------------------------------------
# Textos de la portada
# ---------------------------------------------------------------------------
TEXTOS_POR_DEFECTO = {
    "frases": [
        "Lo que sientes es válido, aunque nadie más lo vea.",
        "Pedir ayuda también es ser valiente.",
        "No tienes que resolverlo todo hoy: un paso a la vez.",
        "Un mal día no es una mala vida.",
        "Tu valor no depende de una nota.",
        "Está bien descansar. Descansar no es rendirse.",
    ],
    "mitos": [
        ["Ir al psicólogo es solo para personas \"locas\".", "mito", "Cualquier persona puede ir: igual que vas al médico para cuidar tu cuerpo, el psicólogo ayuda a cuidar tu mente."],
        ["Llorar es señal de debilidad.", "mito", "Llorar es una forma natural de soltar emociones. Lo hacen personas de todas las edades y es sano."],
        ["En la adolescencia el cerebro cambia mucho con lo que practicas.", "realidad", "Se llama neuroplasticidad: en esta etapa es muy fuerte, por eso los hábitos que entrenas hoy cuentan."],
        ["Preguntarle a alguien si piensa en suicidarse le da la idea.", "mito", "Preguntar con cariño no da la idea; al contrario, abre la puerta para que la persona pida ayuda."],
        ["Moverte un rato puede ayudar a bajar el estrés.", "realidad", "La actividad física ayuda al cuerpo a gastar la energía del estrés y mejora el ánimo."],
        ["Si alguien está triste, solo necesita \"echarle ganas\".", "mito", "La tristeza profunda no se quita con fuerza de voluntad; necesita apoyo, comprensión y a veces ayuda profesional."],
    ],
    "historias": [
        ["Antes de los exámenes me bloqueaba y pensaba que era el único al que le pasaba. Probé la respiración 4-4-4-4 y le escribí a la psicóloga sin dar mi nombre. Todavía me pongo nervioso, pero ahora sé qué hacer cuando me pasa.", "2"],
        ["Tenía miedo de que se enteraran en mi casa o en el liceo. Cuando supe que era anónimo, me animé a escribir por primera vez. Ahora hablo seguido, y me siento más tranquilo/a.", "4"],
    ],
}


def textos():
    datos = copy.deepcopy(TEXTOS_POR_DEFECTO)
    with _conectar() as conn:
        for f in conn.execute("SELECT clave, valor FROM contenido_textos"):
            try:
                datos[f["clave"]] = json.loads(f["valor"])
            except ValueError:
                pass
    return datos


def guardar_texto(clave, valor):
    with _conectar() as conn:
        conn.execute("INSERT OR REPLACE INTO contenido_textos VALUES (?, ?, ?)",
                     (clave, json.dumps(valor, ensure_ascii=False), _ahora()))


def restaurar_texto(clave):
    with _conectar() as conn:
        conn.execute("DELETE FROM contenido_textos WHERE clave = ?", (clave,))


# Formato de los cuadros de texto del panel (una línea por elemento).
def mitos_a_texto(mitos):
    return "\n".join(f"{'Mito' if t == 'mito' else 'Realidad'} | {f} | {e}" for f, t, e in mitos)


def texto_a_mitos(texto):
    mitos = []
    for linea in separar_lineas(texto):
        partes = [p.strip() for p in linea.split("|")]
        if len(partes) < 3:
            continue
        tipo = "realidad" if partes[0].lower().startswith("real") else "mito"
        mitos.append([partes[1], tipo, " | ".join(partes[2:])])
    return mitos


def historias_a_texto(historias):
    return "\n".join(f"{anio} | {t}" for t, anio in historias)


def texto_a_historias(texto):
    historias = []
    for linea in separar_lineas(texto):
        if "|" in linea:
            anio, t = [p.strip() for p in linea.split("|", 1)]
        else:
            anio, t = "", linea.strip()
        anio = re.sub(r"[^0-9]", "", anio)[:2]
        if t:
            historias.append([t.strip('"“”'), anio])
    return historias


# ---------------------------------------------------------------------------
# Ajustes
# ---------------------------------------------------------------------------
AJUSTES_POR_DEFECTO = {
    "whatsapp_numero": "50431746810",
    "whatsapp_nombre": "",
}


def ajustes():
    datos = dict(AJUSTES_POR_DEFECTO)
    with _conectar() as conn:
        for f in conn.execute("SELECT clave, valor FROM ajustes"):
            datos[f["clave"]] = f["valor"]
    return datos


def guardar_ajuste(clave, valor):
    with _conectar() as conn:
        conn.execute("INSERT OR REPLACE INTO ajustes VALUES (?, ?)", (clave, valor))


def numero_whatsapp(texto):
    """Deja solo los dígitos; agrega 504 (Honduras) si escribieron 8 dígitos."""
    digitos = re.sub(r"\D", "", texto or "")
    if len(digitos) == 8:
        digitos = "504" + digitos
    return digitos


# ---------------------------------------------------------------------------
# Muro y reseñas (moderación)
# ---------------------------------------------------------------------------
def publicaciones_muro(limite=200):
    with _conectar() as conn:
        return [dict(f) for f in conn.execute(
            "SELECT id, contenido, fecha, COALESCE(oculto, 0) AS oculto FROM muro_posts ORDER BY id DESC LIMIT ?", (limite,))]


def resenas_todas(limite=200):
    with _conectar() as conn:
        return [dict(f) for f in conn.execute(
            "SELECT id, estrellas, comentario, fecha, foto, COALESCE(oculto, 0) AS oculto FROM resenas ORDER BY id DESC LIMIT ?", (limite,))]


def moderar(tabla, id_, accion):
    if tabla not in ("muro_posts", "resenas"):
        return
    with _conectar() as conn:
        if accion == "borrar":
            conn.execute(f"DELETE FROM {tabla} WHERE id = ?", (id_,))
        elif accion in ("ocultar", "mostrar"):
            conn.execute(f"UPDATE {tabla} SET oculto = ? WHERE id = ?", (1 if accion == "ocultar" else 0, id_))
