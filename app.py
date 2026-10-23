import hmac
import os
import random
import re
import time
import sqlite3
import uuid
from datetime import datetime


def cargar_archivo_env(ruta=".env"):
    """Lee claves del archivo .env (una por línea: NOMBRE=valor) si existe.
    Sirve en la computadora de desarrollo; en Render las claves se ponen en
    su panel. Nunca reemplaza una variable que ya esté definida, y el
    archivo .env no se sube a GitHub (está en .gitignore)."""
    if not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8-sig") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            nombre, valor = linea.split("=", 1)
            os.environ.setdefault(nombre.strip(), valor.strip().strip('"').strip("'"))


cargar_archivo_env()

from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify, send_from_directory
from flask_socketio import SocketIO, join_room, emit
from werkzeug.utils import secure_filename

from filtro_riesgo import analizar_riesgo
from filtro_ofensivo import contiene_lenguaje_ofensivo
import ia_asistente
import ia_proveedores
from respuestas_bot import generar_respuesta, RESPUESTA_DERIVACION, PERSONAJES
import conversacion_bot
from futuro_bot import generar_mensaje_futuro
from tests_bot import TESTS, obtener_test, calcular_resultado
from articulos_bot import ARTICULOS, CATEGORIAS_INFORMATE, GLOSARIO
from herramientas_bot import TECNICAS
from libros_bot import LIBROS
import contenido
import cuentas

app = Flask(__name__)
# En producción, SECRET_KEY y las credenciales de la psicóloga se deben poner
# como variables de entorno en el servicio de hosting (nunca dejarlas escritas
# aquí). Los valores de la derecha son solo para que funcione en desarrollo local.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cambia-esto-por-una-clave-secreta-real")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB, para que no se abuse de las fotos de reseñas
socketio = SocketIO(app, cors_allowed_origins="*")


def csrf_token():
    """Código secreto por sesión que llevan los formularios de cuentas y del
    panel, para que otra página no pueda enviarlos en nombre de alguien."""
    if "csrf" not in session:
        session["csrf"] = uuid.uuid4().hex
    return session["csrf"]


def csrf_valido():
    return request.form.get("csrf") == session.get("csrf")


def usuario_actual():
    return cuentas.obtener(session.get("usuario_id"))


@app.url_defaults
def version_estaticos(endpoint, valores):
    """Agrega ?v=<fecha del archivo> a los archivos de static/. Así, cuando cambia un
    estilo o un script, el navegador (y la app instalada) bajan la versión nueva."""
    if endpoint == "static" and "filename" in valores and "v" not in valores:
        try:
            valores["v"] = int(os.stat(os.path.join(app.static_folder, valores["filename"])).st_mtime)
        except OSError:
            pass


@app.context_processor
def datos_globales():
    # Las páginas solo dicen que el asistente es IA cuando de verdad lo es.
    ajustes = contenido.ajustes()
    return {
        "ia_activa": ia_asistente.ia_disponible(),
        "voz_activa": ia_proveedores.voz_disponible(),
        "whatsapp_numero": ajustes["whatsapp_numero"],
        "whatsapp_nombre": ajustes["whatsapp_nombre"],
        "usuario": usuario_actual(),
        "csrf_token": csrf_token,
    }

# DATA_DIR: carpeta para los datos que deben sobrevivir a cada actualización
# (en Render, el disco persistente montado en /var/data). Sin ella, todo se
# guarda junto al código, como en la computadora de desarrollo.
DATA_DIR = os.environ.get("DATA_DIR")
DB_PATH = os.path.join(DATA_DIR, "apoyo_emocional.db") if DATA_DIR else "apoyo_emocional.db"
contenido.configurar(DB_PATH)
cuentas.configurar(DB_PATH)

PSICOLOGA_USUARIO = os.environ.get("PSICOLOGA_USUARIO", "psicologa")
PSICOLOGA_CLAVE = os.environ.get("PSICOLOGA_CLAVE", "cambia-esta-clave")

# Cuentas del panel: usuario -> nombre que se muestra. La clave de cada una
# va en el .env (o en el panel de Render) como CLAVE_<USUARIO>, por ejemplo
# CLAVE_MAYRA_RODRIGUEZ. Una cuenta sin clave configurada no puede entrar.
CUENTAS_PANEL = {
    "mayra.rodriguez": "Mayra Rodríguez",
    "subteniente.aleman": "Subteniente Alemán",
    "lesly.ruiz": "Lesly Ruiz",
    "lic.gemmi": "Lic. Gemmi",
}


def cuenta_panel(usuario, clave):
    """Devuelve el nombre de quien entra al panel, o None si no coincide."""
    usuario = ".".join(usuario.strip().lower().split())
    if usuario in CUENTAS_PANEL:
        guardada = os.environ.get("CLAVE_" + usuario.upper().replace(".", "_"))
        if guardada and hmac.compare_digest(clave, guardada):
            return CUENTAS_PANEL[usuario]
        return None
    if usuario == PSICOLOGA_USUARIO and hmac.compare_digest(clave, PSICOLOGA_CLAVE):
        return "Psicóloga"
    return None

# Dominios de correo del liceo con los que se puede entrar a los chats
# (separados por coma). Se cambian con la variable DOMINIOS_CORREO del .env.
DOMINIOS_CORREO = [
    d.strip().lower().lstrip("@")
    for d in os.environ.get("DOMINIOS_CORREO", "lmh.edu,lmh.edu.hn,gmail.com").split(",")
    if d.strip()
]

# IDs de conexión (socket.io) de la psicóloga con el panel abierto ahora mismo.
# Sirve solo para avisarle al estudiante si hay alguien del otro lado o no —
# no decide nada, solo informa.
PSICOLOGA_SIDS = set()


def psicologa_esta_conectada():
    return len(PSICOLOGA_SIDS) > 0

CARPETA_FOTOS_RESENAS = (
    os.path.join(DATA_DIR, "uploads", "resenas") if DATA_DIR
    else os.path.join("static", "uploads", "resenas")
)
EXTENSIONES_FOTO_PERMITIDAS = {"png", "jpg", "jpeg", "gif", "webp"}
os.makedirs(CARPETA_FOTOS_RESENAS, exist_ok=True)


def guardar_foto_resena(archivo):
    """Guarda una foto opcional de una reseña. Devuelve la ruta relativa (para static/) o None."""
    if not archivo or not archivo.filename:
        return None
    extension = archivo.filename.rsplit(".", 1)[-1].lower() if "." in archivo.filename else ""
    if extension not in EXTENSIONES_FOTO_PERMITIDAS:
        return None
    nombre = secure_filename(f"{uuid.uuid4().hex}.{extension}")
    archivo.save(os.path.join(CARPETA_FOTOS_RESENAS, nombre))
    return f"uploads/resenas/{nombre}"


# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sesiones (
            token TEXT PRIMARY KEY,
            creado_en TEXT,
            nivel_riesgo_max TEXT DEFAULT 'bajo'
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT,
            emisor TEXT,          -- 'estudiante' o 'psicologa'
            contenido TEXT,
            nivel_riesgo TEXT,
            categorias TEXT,
            fecha TEXT,
            FOREIGN KEY (token) REFERENCES sesiones (token)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS animos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT,
            fecha TEXT,          -- formato YYYY-MM-DD, un registro por día
            estado TEXT,         -- 'genial' | 'bien' | 'normal' | 'mal' | 'muy_mal'
            UNIQUE(token, fecha)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resenas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estrellas INTEGER,
            comentario TEXT,
            fecha TEXT,
            foto TEXT
        )
        """
    )
    try:
        cur.execute("ALTER TABLE resenas ADD COLUMN foto TEXT")
    except sqlite3.OperationalError:
        pass  # ya existe (base de datos creada antes de agregar esta columna)
    try:
        cur.execute("ALTER TABLE sesiones ADD COLUMN correo TEXT")
    except sqlite3.OperationalError:
        pass  # ya existe
    try:
        # Quién del panel respondió (Mayra Rodríguez, Lesly Ruiz...), para que
        # todas las cuentas vean la misma conversación y sepan quién contestó.
        cur.execute("ALTER TABLE mensajes ADD COLUMN autor TEXT")
    except sqlite3.OperationalError:
        pass  # ya existe
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contactos_emergencia (
            token TEXT PRIMARY KEY,
            telefono TEXT,
            plataforma TEXT,      -- 'whatsapp' o 'telegram'
            fecha TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resultados_test (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id TEXT,
            nivel TEXT,           -- 'bien' | 'medio' | 'alerta' (nunca las respuestas individuales)
            fecha TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS visitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS muro_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contenido TEXT,
            fecha TEXT
        )
        """
    )
    contenido.init_tablas(conn)
    cuentas.init_tablas(conn)
    conn.commit()
    conn.close()


def registrar_visita():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO visitas (fecha) VALUES (?)", (datetime.now().isoformat(),))
    conn.commit()
    conn.close()


def guardar_resultado_test(test_id, nivel):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO resultados_test (test_id, nivel, fecha) VALUES (?, ?, ?)",
        (test_id, nivel, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def obtener_estadisticas():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM visitas")
    visitas = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT token) FROM mensajes WHERE emisor = 'asistente'")
    teleorientaciones = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT token) FROM mensajes WHERE emisor = 'psicologa'")
    teleconsultas = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM resultados_test")
    tests_realizados = cur.fetchone()[0]
    conn.close()
    return {
        "visitas": visitas,
        "teleorientaciones": teleorientaciones,
        "teleconsultas": teleconsultas,
        "tests_realizados": tests_realizados,
    }


def obtener_contadores_portada():
    """Números reales para los contadores animados de la portada. Solo se
    cuentan registros anónimos: nunca se muestra quién hizo qué."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    def contar(sql):
        cur.execute(sql)
        return cur.fetchone()[0] or 0
    datos = {
        "visitas": contar("SELECT COUNT(*) FROM visitas"),
        "conversaciones": contar("SELECT COUNT(DISTINCT token) FROM mensajes WHERE emisor = 'estudiante'"),
        "autoevaluaciones": contar("SELECT COUNT(*) FROM resultados_test"),
        "participaciones": contar("SELECT COUNT(*) FROM animos")
        + contar("SELECT COUNT(*) FROM muro_posts")
        + contar("SELECT COUNT(*) FROM resenas"),
    }
    conn.close()
    return datos


def obtener_historial(token, limite=20):
    """Últimos mensajes de una conversación, del más viejo al más nuevo,
    como lista de (emisor, contenido). Se usa para que la IA recuerde el chat."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT emisor, contenido FROM mensajes WHERE token = ? ORDER BY id DESC LIMIT ?",
        (token, limite),
    )
    filas = cur.fetchall()
    conn.close()
    return list(reversed(filas))


def guardar_mensaje(token, emisor, contenido, analisis, autor=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO mensajes (token, emisor, contenido, nivel_riesgo, categorias, fecha, autor)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            token,
            emisor,
            contenido,
            analisis["nivel"],
            ",".join(analisis["categorias"]),
            datetime.now().isoformat(),
            autor,
        ),
    )
    # Actualiza el nivel máximo de riesgo visto en esa sesión
    orden = {"bajo": 0, "medio": 1, "alto": 2, "critico": 3}
    cur.execute("SELECT nivel_riesgo_max FROM sesiones WHERE token = ?", (token,))
    fila = cur.fetchone()
    if fila and orden[analisis["nivel"]] > orden[fila[0]]:
        cur.execute(
            "UPDATE sesiones SET nivel_riesgo_max = ? WHERE token = ?",
            (analisis["nivel"], token),
        )
    conn.commit()
    conn.close()


def registrar_sesion(token):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO sesiones (token, creado_en) VALUES (?, ?)",
        (token, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def correo_valido(correo):
    usuario, arroba, dominio = correo.partition("@")
    return bool(arroba) and bool(re.fullmatch(r"[a-z0-9._%+-]+", usuario)) and dominio in DOMINIOS_CORREO


def token_de_correo(correo, token_actual=None):
    """Cada correo tiene una sola conversación: si ya habló antes (aunque sea
    desde otro dispositivo) sigue la misma. Si no, se le pone el correo a la
    conversación de este navegador, o se crea una nueva si esa ya es de otro correo."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT token FROM sesiones WHERE correo = ? ORDER BY creado_en DESC LIMIT 1", (correo,))
    fila = cur.fetchone()
    if fila:
        conn.close()
        return fila[0]
    if token_actual:
        cur.execute("SELECT correo FROM sesiones WHERE token = ?", (token_actual,))
        fila = cur.fetchone()
        if fila and fila[0]:
            token_actual = None
    token = token_actual or f"Usuario-{uuid.uuid4().hex[:6]}"
    cur.execute(
        "INSERT OR IGNORE INTO sesiones (token, creado_en) VALUES (?, ?)",
        (token, datetime.now().isoformat()),
    )
    cur.execute("UPDATE sesiones SET correo = ? WHERE token = ?", (correo, token))
    conn.commit()
    conn.close()
    return token


def correo_de(token):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT correo FROM sesiones WHERE token = ?", (token,))
    fila = cur.fetchone()
    conn.close()
    return fila[0] if fila else None


def pide_correo():
    """Los chats (psicóloga, asistentes y Tigre) piden el correo cada vez que
    alguien entra: primero la página del correo y después el chat. El permiso
    sirve para una sola entrada a ese chat. Devuelve la redirección si falta."""
    permiso = session.pop("entrada_chat", None)
    if permiso == request.path and session.get("correo") and session.get("token"):
        return None
    return redirect(url_for("entrar_correo", siguiente=request.path))


def guardar_animo(token, estado):
    hoy = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO animos (token, fecha, estado) VALUES (?, ?, ?)",
        (token, hoy, estado),
    )
    conn.commit()
    conn.close()


def calcular_racha(token):
    """Cuenta días consecutivos (hasta hoy o ayer) en que el estudiante registró su ánimo."""
    from datetime import timedelta

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT fecha FROM animos WHERE token = ? ORDER BY fecha DESC", (token,))
    fechas = {row[0] for row in cur.fetchall()}
    conn.close()

    racha = 0
    cursor_fecha = datetime.now().date()
    # Si hoy no ha registrado, la racha se cuenta desde ayer (para no romperla antes de tiempo)
    if cursor_fecha.strftime("%Y-%m-%d") not in fechas:
        cursor_fecha -= timedelta(days=1)

    while cursor_fecha.strftime("%Y-%m-%d") in fechas:
        racha += 1
        cursor_fecha -= timedelta(days=1)

    return racha


def obtener_animos_recientes(token, dias=7):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT fecha, estado FROM animos WHERE token = ? ORDER BY fecha DESC LIMIT ?",
        (token, dias),
    )
    filas = cur.fetchall()
    conn.close()
    return list(reversed(filas))


def guardar_resena(estrellas, comentario, foto=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO resenas (estrellas, comentario, fecha, foto) VALUES (?, ?, ?, ?)",
        (estrellas, comentario, datetime.now().isoformat(), foto),
    )
    conn.commit()
    conn.close()


def obtener_resenas(limite=30):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT estrellas, comentario, fecha, foto FROM resenas WHERE COALESCE(oculto, 0) = 0 ORDER BY id DESC LIMIT ?",
        (limite,),
    )
    filas = cur.fetchall()
    conn.close()
    return filas


def guardar_contacto_emergencia(token, telefono, plataforma):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO contactos_emergencia (token, telefono, plataforma, fecha) VALUES (?, ?, ?, ?)",
        (token, telefono, plataforma, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def guardar_muro_post(contenido):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO muro_posts (contenido, fecha) VALUES (?, ?)",
        (contenido, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def obtener_muro_posts(limite=50):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT contenido, fecha FROM muro_posts WHERE COALESCE(oculto, 0) = 0 ORDER BY id DESC LIMIT ?",
        (limite,),
    )
    filas = cur.fetchall()
    conn.close()
    return filas


def obtener_resumen_resenas():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), AVG(estrellas) FROM resenas WHERE COALESCE(oculto, 0) = 0")
    total, promedio = cur.fetchone()
    conn.close()
    return {
        "total": total or 0,
        "promedio": round(promedio, 1) if promedio else 0,
    }


# ---------------------------------------------------------------------------
# Rutas HTTP
# ---------------------------------------------------------------------------
# Temas destacados en la sección "Recursos de psicología" de la portada
# (slugs de artículos). El título y la descripción salen del propio
# artículo, así nunca se desincronizan.
RECURSOS_PORTADA = [
    "bullying",
    "acoso-ciberacoso",
    "controlar-emociones",
    "apego-evitativo",
    "dopamina",
    "cortisol",
    "amigdala-emociones",
    "neuronas-espejo",
    "sesgo-confirmacion",
    "efecto-placebo",
    "autosabotaje",
    "superar-perdida",
    "psicologia-deseo",
    "sueños-neurociencia",
    "madurar-temprano",
    "pensamiento-estrategico",
    "nueva-oportunidad",
]


# Secciones fijas que aparecen en el buscador de la portada (Ctrl+K).
# "palabras" son términos extra con los que alguien podría buscarlas.
PAGINAS_BUSCADOR = [
    ("estudiante", None, "Hablar con la psicóloga", "Chat anónimo con una persona real", "ayuda triste ansiedad miedo hablar chat"),
    ("chatbot", None, "Hablar con el asistente", "Disponible a cualquier hora", "bot sami nia conversar"),
    ("tigre_voz", None, "Habla con el Tigre por voz", "Le hablas y te responde con su voz", "tigre tigrito voz hablar escuchar microfono"),
    ("diario", None, "Mi diario de ánimo", "Registra cómo te sientes cada día", "emociones registro animo"),
    ("herramientas", None, "Herramientas para sentirme mejor", "Ansiedad, enojo, tristeza, dormir y estudiar", "calma tecnicas relajacion respiracion ira depresion estres"),
    ("informate", None, "Infórmate", "Artículos sobre salud mental", "leer articulos temas"),
    ("tests", None, "Autoevaluaciones", "Preguntas para reflexionar sobre ti", "test cuestionario"),
    ("video", None, "Videos", "Videos sobre salud mental", "youtube ver"),
    ("musica", None, "Música", "Música relajante para calmarte", "canciones spotify relajar"),
    ("fe", None, "Fe y esperanza", "Mensajes de fe y esperanza", "dios oracion biblia"),
    ("muro", None, "Muro interactivo", "Comparte tu experiencia de forma anónima", "historias escribir"),
    ("futuro", None, "Mi futuro", "Metas y planes para lo que viene", "metas suenos carrera"),
    ("resenas", None, "Reseñas", "Opiniones sobre la página", "opinion comentarios"),
    ("terminos", None, "Términos y condiciones", "Cómo funciona y cómo cuidamos tu privacidad", "privacidad reglas"),
    ("index", "titulo-emergencia", "¿Estás en peligro ahora mismo?", "Emergencias: 911 y Teléfono de la Esperanza 150", "emergencia urgente peligro suicidio 911 150 esperanza linea crisis"),
    ("index", "contacto", "Contáctenos", "Correo, teléfono y redes sociales", "contacto correo telefono whatsapp"),
]


def construir_indice_busqueda():
    """Todo lo que se puede encontrar desde el buscador de la portada."""
    indice = [
        {"nombre": nombre, "meta": meta, "tipo": "Sección", "palabras": palabras,
         "url": url_for(ruta, _anchor=ancla) if ancla else url_for(ruta)}
        for ruta, ancla, nombre, meta, palabras in PAGINAS_BUSCADOR
    ]
    for cat_id, cat in contenido.tecnicas().items():
        for tec_id, tec in cat["tecnicas"].items():
            indice.append({
                "nombre": tec["nombre"], "meta": tec["resumen"], "tipo": "Técnica",
                "palabras": cat["titulo"],
                "url": url_for("herramientas", _anchor=f"{cat_id}-{tec_id}"),
            })
    for test_id, test in TESTS.items():
        indice.append({
            "nombre": test["titulo"], "meta": test["descripcion"], "tipo": "Autoevaluación",
            "palabras": "test", "url": url_for("test_detalle", test_id=test_id),
        })
    for slug, art in contenido.articulos().items():
        indice.append({
            "nombre": art["titulo"], "meta": art["resumen"], "tipo": "Artículo",
            "palabras": art.get("categoria", ""),
            "url": url_for("informate", _anchor=slug),
        })
    return indice


@app.template_global()
def imagen_recurso(slug, solo_foto=False):
    """Ilustración de un tema de psicología (static/images/recursos): primero la
    imagen elegida por el equipo (.webp) y, si no hay, el dibujo (.svg)."""
    for ext in ("webp",) if solo_foto else ("webp", "svg"):
        ruta = f"images/recursos/{slug}.{ext}"
        if os.path.exists(os.path.join(app.static_folder, ruta)):
            return ruta
    return None


@app.template_global()
def portada_libro(libro_id):
    """Foto de la portada de un libro (static/images/libros/<id>.webp, .jpg o .png).
    Si no hay foto, el estante dibuja la portada con los colores del libro."""
    for ext in ("webp", "jpg", "jpeg", "png"):
        ruta = f"images/libros/{libro_id}.{ext}"
        if os.path.exists(os.path.join(app.static_folder, ruta)):
            return ruta
    return None


@app.route("/")
def index():
    registrar_visita()
    articulos = contenido.articulos()
    recursos = [
        {"slug": slug, **articulos[slug]}
        for slug in RECURSOS_PORTADA
        if slug in articulos
    ]
    return render_template(
        "index.html",
        categorias_video=VIDEOS_CURADOS,
        video_prevencion_id=VIDEO_PREVENCION_SUICIDIO_ID,
        recursos_psicologia=recursos,
        tests=TESTS,
        libros=LIBROS,
        glosario=[g for g in GLOSARIO if g[2] in articulos],
        textos=contenido.textos(),
        contadores=obtener_contadores_portada(),
        indice_busqueda=construir_indice_busqueda(),
        temas_informate=[
            {
                "nombre": nombre,
                "descripcion": descripcion,
                "total": sum(1 for a in articulos.values() if a["categoria"] == nombre),
                "ejemplos": [
                    (slug, a["titulo"]) for slug, a in articulos.items() if a["categoria"] == nombre
                ][:3],
            }
            for nombre, descripcion in CATEGORIAS_INFORMATE
        ],
        videos_informate=[
            (slug, a["titulo"], a["video_youtube_id"])
            for slug, a in articulos.items() if a.get("video_youtube_id")
        ],
        # El visor 3D de Tigrito solo aparece cuando ya existe el modelo.
        modelo_tigre=os.path.exists(os.path.join(app.static_folder, "models", "tigre.glb")),
    )


# ---------------------------------------------------------------------------
# Aplicación instalable (PWA): manifiesto, service worker y página sin conexión
# ---------------------------------------------------------------------------
@app.route("/manifest.webmanifest")
def manifiesto():
    datos = {
        "name": "No estamos solos LMH",
        "short_name": "No estamos solos",
        "description": "Apoyo emocional anónimo para los estudiantes del Liceo Militar de Honduras.",
        "lang": "es",
        "start_url": "/?app=1",
        "scope": "/",
        "display": "standalone",
        "background_color": "#1f4b2c",
        "theme_color": "#1f4b2c",
        "icons": [
            {"src": url_for("static", filename="iconos/icono-192.png"), "sizes": "192x192", "type": "image/png"},
            {"src": url_for("static", filename="iconos/icono-512.png"), "sizes": "512x512", "type": "image/png"},
            {"src": url_for("static", filename="iconos/icono-maskable-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "shortcuts": [
            {"name": "Hablar con la psicóloga", "url": "/estudiante"},
            {"name": "Mi diario de ánimo", "url": "/diario"},
            {"name": "Herramientas", "url": "/herramientas"},
        ],
    }
    resp = jsonify(datos)
    resp.mimetype = "application/manifest+json"
    return resp


@app.route("/sw.js")
def service_worker():
    # Se sirve desde la raíz para que pueda funcionar en todas las páginas.
    resp = send_from_directory(os.path.join(app.static_folder, "js"), "sw.js", mimetype="application/javascript")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["Service-Worker-Allowed"] = "/"
    return resp


@app.route("/sin-conexion")
def sin_conexion():
    return render_template("sin_conexion.html")


@app.route("/api/estado-psicologa")
def estado_psicologa():
    """Solo dice si la psicóloga tiene el panel abierto (para el puntito
    verde de la barra inferior). No expone nada más."""
    return jsonify({"conectada": psicologa_esta_conectada()})


@app.route("/api/voz/transcribir", methods=["POST"])
def voz_transcribir():
    """Convierte en texto lo que el estudiante dijo por voz (Whisper en Groq).
    El audio no se guarda: se transcribe y se descarta. El texto que vuelve se
    envía al chat como cualquier mensaje, así que pasa por el filtro de riesgo."""
    if not request.headers.get("X-CSRF") or request.headers.get("X-CSRF") != session.get("csrf"):
        return jsonify({"error": "sesion"}), 403
    ahora = time.time()
    recientes = [t for t in session.get("voz_usos", []) if ahora - t < 60]
    if len(recientes) >= 20:  # máximo 20 grabaciones por minuto
        return jsonify({"error": "espera"}), 429
    session["voz_usos"] = recientes + [ahora]
    audio = request.files.get("audio")
    if not audio:
        return jsonify({"error": "sin_audio"}), 400
    datos = audio.read()
    if len(datos) < 800:  # grabación vacía o de menos de medio segundo
        return jsonify({"texto": ""})
    texto = ia_proveedores.transcribir(datos, audio.mimetype or "audio/webm")
    if texto is None:
        return jsonify({"error": "sin_servicio"}), 503
    return jsonify({"texto": texto})


@app.route("/fotos-resenas/<nombre>")
def foto_resena(nombre):
    """Sirve las fotos de las reseñas desde donde estén guardadas (static/ o el disco)."""
    return send_from_directory(CARPETA_FOTOS_RESENAS, secure_filename(nombre))


@app.route("/entrar", methods=["GET", "POST"])
def entrar_correo():
    """Antes de hablar con la psicóloga o con un asistente se pone el correo del liceo."""
    siguiente = request.values.get("siguiente") or url_for("chatbot")
    if not siguiente.startswith("/") or siguiente.startswith("//"):
        siguiente = url_for("chatbot")
    error = None
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        if not csrf_valido():
            error = "La página se venció. Vuelve a escribir tu correo."
        elif not correo_valido(correo):
            error = "Usa un correo que termine en @" + ", @".join(DOMINIOS_CORREO) + "."
        else:
            session["token"] = token_de_correo(correo, session.get("token"))
            session["correo"] = correo
            session["entrada_chat"] = siguiente  # deja pasar una vez a ese chat
            return redirect(siguiente)
    return render_template("entrar_correo.html", error=error, siguiente=siguiente, dominios=DOMINIOS_CORREO)


@app.route("/entrar/cambiar")
def cambiar_correo():
    session.pop("correo", None)
    session.pop("token", None)
    return redirect(url_for("entrar_correo", siguiente=request.args.get("siguiente") or url_for("chatbot")))


@app.route("/estudiante")
def estudiante():
    falta = pide_correo()
    if falta:
        return falta
    return render_template("estudiante.html", token=session["token"], correo=session["correo"])


@app.route("/chatbot")
def chatbot():
    """Muestra la selección de con cuál asistente hablar."""
    if "token" not in session:
        session["token"] = f"Usuario-{uuid.uuid4().hex[:6]}"
        registrar_sesion(session["token"])
    return render_template("elegir_amigo.html", personajes=PERSONAJES_DEL_CHAT)


# El Tigre LMH no sale en el chat: tiene su propia página para hablar por voz.
PERSONAJES_DEL_CHAT = {k: p for k, p in PERSONAJES.items() if not p.get("solo_voz")}


@app.route("/chatbot/sorpresa")
def chatbot_sorpresa():
    return redirect(url_for("chatbot_persona", persona=random.choice(list(PERSONAJES_DEL_CHAT.keys()))))


@app.route("/tigre")
def tigre_voz():
    """Hablar con el Tigre LMH por voz: su cara, sus ojos y su voz, sin chat.
    Usa el mismo camino que el chat (filtro de riesgo, aviso a la psicóloga, IA)."""
    falta = pide_correo()
    if falta:
        return falta
    return render_template("tigre_voz.html", token=session["token"], persona=PERSONAJES["tigre"])


@app.route("/api/tigre/sesion", methods=["POST"])
def tigre_sesion():
    """Crea la conversación anónima del Tigre la primera vez que alguien le habla
    desde la portada (así no se registra a quien solo mira la página)."""
    if not request.headers.get("X-CSRF") or request.headers.get("X-CSRF") != session.get("csrf"):
        return jsonify({"error": "sesion"}), 403
    if not session.get("correo") or not session.get("token"):
        return jsonify({"error": "correo", "ir": url_for("entrar_correo", siguiente=url_for("tigre_voz"))}), 401
    return jsonify({"token": session["token"]})


@app.route("/chatbot/<persona>")
def chatbot_persona(persona):
    if persona == "tigre":
        return redirect(url_for("tigre_voz"))
    if persona not in PERSONAJES:
        return redirect(url_for("chatbot"))
    falta = pide_correo()
    if falta:
        return falta
    return render_template(
        "asistente.html",
        token=session["token"],
        correo=session["correo"],
        persona_id=persona,
        persona=PERSONAJES[persona],
    )


def token_diario():
    """El diario de quien tiene cuenta usa el código de su cuenta (lo sigue
    en cualquier dispositivo); sin cuenta, el código anónimo de la sesión."""
    u = usuario_actual()
    if u:
        return u["token_diario"]
    if "token" not in session:
        session["token"] = f"Usuario-{uuid.uuid4().hex[:6]}"
        registrar_sesion(session["token"])
    return session["token"]


@app.route("/diario")
def diario():
    token = token_diario()
    racha = calcular_racha(token)
    historial = obtener_animos_recientes(token, dias=7)
    nuevo = request.args.get("nuevo") == "1"
    return render_template("diario.html", racha=racha, historial=historial, nuevo=nuevo)


@app.route("/diario/registrar/<estado>")
def diario_registrar(estado):
    token = token_diario()
    if estado in ("genial", "bien", "normal", "mal", "muy_mal"):
        guardar_animo(token, estado)
    return redirect(url_for("diario", nuevo=1))


@app.route("/fe")
def fe():
    return render_template("fe.html")


@app.route("/terminos")
def terminos():
    return render_template("terminos.html")


# Listas oficiales de Spotify (editoriales, con licencia de Spotify) — se
# incrustan con el reproductor oficial, nunca se descarga ni se aloja audio.
PLAYLISTS_MUSICA = [
    {
        "id": "37i9dQZF1DX3rxVfibe1L0",
        "nombre": "Mood Booster",
        "descripcion": "Éxitos conocidos para subir el ánimo.",
    },
    {
        "id": "37i9dQZF1DX10zKzsJ2jva",
        "nombre": "Viva Latino",
        "descripcion": "Los hits latinos más sonados del momento.",
    },
    {
        "id": "37i9dQZF1DX9XIFQuFvzM4",
        "nombre": "Feelin' Good",
        "descripcion": "Canciones conocidas con buena energía, más tranquilas.",
    },
]


PODCASTS_MOTIVACION = [
    {
        "id": "3HplUkBr4kobLs90f8nr3u",
        "nombre": "Motivación diaria",
        "descripcion": "Episodios cortos para arrancar el día con otra energía.",
    },
    {
        "id": "15etuVh6AvZHA3as2OhVst",
        "nombre": "El Poder de UNO — Motivación",
        "descripcion": "Historias y reflexiones sobre superación personal.",
    },
]


@app.route("/musica")
def musica():
    return render_template("musica.html", playlists=PLAYLISTS_MUSICA, podcasts=PODCASTS_MOTIVACION)


CARPETA_VIDEOS = os.path.join("static", "videos")
EXTENSIONES_VIDEO_PERMITIDAS = (".mp4", ".webm", ".ogg")
os.makedirs(CARPETA_VIDEOS, exist_ok=True)

# Video opcional para la sección "10 de septiembre" de la portada.
VIDEO_PREVENCION_SUICIDIO_ID = "YSGnQeEWJMs"

# Videos curados, embebidos directo desde YouTube (oficial, con licencia de
# YouTube — nunca se descarga ni se aloja el video). Organizados por a quién
# van dirigidos, cada uno en su propio recuadro.
VIDEOS_CURADOS = {
    "adolescentes": {
        "titulo": "Para adolescentes",
        "videos": [
            {
                "tipo": "embed",
                "youtube_id": "QVZdMXK4kvk",
                "titulo": "La salud mental juvenil no es tan complicada como creemos",
                "descripcion": "Charla TEDx sobre salud mental en adolescentes, de forma cercana y sin tecnicismos.",
            },
        ],
    },
}


@app.route("/video")
def video():
    """
    Videos curados por categoría (embebidos desde YouTube), más un espacio
    para un video propio (institucional) que el administrador coloca
    directamente en static/videos/ — no es un formulario público de subida,
    para evitar que cualquier visitante suba contenido sin control.
    """
    archivos = sorted(
        f for f in os.listdir(CARPETA_VIDEOS) if f.lower().endswith(EXTENSIONES_VIDEO_PERMITIDAS)
    )
    video_archivo = archivos[0] if archivos else None
    return render_template("video.html", video_archivo=video_archivo, categorias=VIDEOS_CURADOS)


@app.route("/tests")
def tests():
    return render_template("tests.html", tests=TESTS)


@app.route("/test/<test_id>", methods=["GET", "POST"])
def test_detalle(test_id):
    test = obtener_test(test_id)
    if not test:
        return redirect(url_for("tests"))

    resultado = None
    if request.method == "POST":
        respuestas = []
        for i in range(len(test["preguntas"])):
            valor = request.form.get(f"pregunta_{i}", type=int)
            if valor is None:
                return redirect(url_for("test_detalle", test_id=test_id))
            respuestas.append(valor)

        mensaje, nivel = calcular_resultado(test_id, respuestas)
        guardar_resultado_test(test_id, nivel)
        resultado = {"mensaje": mensaje, "nivel": nivel}

    return render_template("test_detalle.html", test=test, test_id=test_id, resultado=resultado)


@app.route("/informate")
def informate():
    return render_template(
        "informate.html", articulos=contenido.articulos(), categorias=CATEGORIAS_INFORMATE, glosario=GLOSARIO
    )


@app.route("/informate/<slug>")
def informate_articulo(slug):
    # Los artículos ya se leen completos en Infórmate: los enlaces viejos
    # llevan a ese artículo dentro de la página.
    if slug not in contenido.articulos():
        return redirect(url_for("informate"))
    return redirect(url_for("informate", _anchor=slug))


@app.route("/herramientas")
def herramientas():
    return render_template("herramientas.html", categorias=contenido.tecnicas())


@app.route("/herramientas/<categoria>/<tecnica>")
def herramientas_detalle(categoria, tecnica):
    # Cada herramienta ya se ve completa en Herramientas: los enlaces viejos
    # llevan a esa herramienta dentro de la página.
    cat = contenido.tecnicas().get(categoria)
    if not cat or tecnica not in cat["tecnicas"]:
        return redirect(url_for("herramientas"))
    return redirect(url_for("herramientas", _anchor=f"{categoria}-{tecnica}"))


@app.route("/futuro", methods=["GET", "POST"])
def futuro():
    resultado = None

    if request.method == "POST":
        if "token" not in session:
            session["token"] = f"Usuario-{uuid.uuid4().hex[:6]}"
            registrar_sesion(session["token"])

        texto_usuario = (request.form.get("respuesta") or "").strip()[:120]

        if texto_usuario:
            analisis = analizar_riesgo(texto_usuario)

            if analisis["nivel"] in ("medio", "alto", "critico"):
                guardar_mensaje(session["token"], "estudiante", texto_usuario, analisis)
                socketio.emit(
                    "alerta_riesgo",
                    {
                        "token": session["token"],
                        "nivel": analisis["nivel"],
                        "categorias": analisis["categorias"],
                    },
                    room="panel_psicologa",
                )
                resultado = {
                    "riesgo": True,
                    "nombre": texto_usuario,
                    "mensaje": (
                        "Lo que escribiste suena importante y merece más que esto. Ya se lo avisamos "
                        "a la psicóloga; también puedes escribirle directamente ahora mismo."
                    ),
                }
            else:
                nombre, mensaje = generar_mensaje_futuro(texto_usuario)
                resultado = {"riesgo": False, "nombre": nombre, "mensaje": mensaje}

    return render_template("futuro.html", resultado=resultado)


@app.route("/resenas", methods=["GET", "POST"])
def resenas():
    if "token" not in session:
        session["token"] = f"Usuario-{uuid.uuid4().hex[:6]}"
        registrar_sesion(session["token"])

    if request.method == "POST":
        estrellas = request.form.get("estrellas", type=int)
        comentario = (request.form.get("comentario") or "").strip()[:280]

        if estrellas and 1 <= estrellas <= 5:
            analisis = analizar_riesgo(comentario) if comentario else {"nivel": "bajo", "categorias": []}

            if analisis["nivel"] in ("medio", "alto", "critico"):
                # No publicamos algo que suene a una crisis real en un muro público:
                # se guarda solo la calificación y se avisa a la psicóloga, igual
                # que en el resto de la plataforma.
                guardar_resena(estrellas, "")
                guardar_mensaje(session["token"], "estudiante", comentario, analisis)
                socketio.emit(
                    "alerta_riesgo",
                    {
                        "token": session["token"],
                        "nivel": analisis["nivel"],
                        "categorias": analisis["categorias"],
                    },
                    room="panel_psicologa",
                )
                flash(
                    "Lo que escribiste suena importante y merece más que una reseña. "
                    "Ya se lo avisamos a la psicóloga; también puedes escribirle directamente.",
                    "aviso",
                )
            else:
                foto = guardar_foto_resena(request.files.get("foto"))
                guardar_resena(estrellas, comentario, foto)
                flash("¡Gracias por tu reseña! Ayuda a que otros estudiantes se animen a hablar.", "exito")

        return redirect(url_for("resenas"))

    resumen = obtener_resumen_resenas()
    lista = obtener_resenas()
    return render_template("resenas.html", resenas=lista, resumen=resumen)


@app.route("/muro", methods=["GET", "POST"])
def muro():
    if "token" not in session:
        session["token"] = f"Usuario-{uuid.uuid4().hex[:6]}"
        registrar_sesion(session["token"])

    if request.method == "POST":
        contenido = (request.form.get("contenido") or "").strip()[:300]

        if contenido:
            analisis = analizar_riesgo(contenido)

            if analisis["nivel"] in ("medio", "alto", "critico"):
                # No se publica en un muro público algo que suene a una crisis
                # real: se guarda en el historial de la sesión y se avisa a la
                # psicóloga, igual que en el resto de la plataforma.
                guardar_mensaje(session["token"], "estudiante", contenido, analisis)
                socketio.emit(
                    "alerta_riesgo",
                    {
                        "token": session["token"],
                        "nivel": analisis["nivel"],
                        "categorias": analisis["categorias"],
                    },
                    room="panel_psicologa",
                )
                flash(
                    "Lo que escribiste suena importante y merece más que una publicación. "
                    "Ya se lo avisamos a la psicóloga; también puedes escribirle directamente.",
                    "aviso",
                )
            else:
                guardar_muro_post(contenido)
                flash("Tu experiencia ya está en el muro. Gracias por compartirla.", "exito")

        return redirect(url_for("muro"))

    posts = obtener_muro_posts()
    return render_template("muro.html", posts=posts)


@app.route("/psicologa/login", methods=["GET", "POST"])
def psicologa_login():
    error = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        clave = request.form.get("clave", "")
        nombre = cuenta_panel(usuario, clave)
        if nombre:
            session["es_psicologa"] = True
            session["nombre_panel"] = nombre
            return redirect(url_for("psicologa"))
        error = "Usuario o clave incorrectos."
    return render_template("psicologa_login.html", error=error)


@app.route("/psicologa/logout")
def psicologa_logout():
    session.pop("es_psicologa", None)
    session.pop("nombre_panel", None)
    return redirect(url_for("psicologa_login"))


@app.route("/psicologa")
def psicologa():
    if not session.get("es_psicologa"):
        return redirect(url_for("psicologa_login"))
    return render_template("psicologa.html", nombre_panel=session.get("nombre_panel", "Psicóloga"))


@app.route("/psicologa/api/conversaciones")
def psicologa_conversaciones():
    """Todas las conversaciones con su correo y el nivel de riesgo más alto que tuvieron."""
    if not session.get("es_psicologa"):
        return jsonify({"error": "sesion"}), 403
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """SELECT s.token, s.correo, s.nivel_riesgo_max, COUNT(m.id), MAX(m.fecha)
           FROM sesiones s JOIN mensajes m ON m.token = s.token
           GROUP BY s.token ORDER BY MAX(m.fecha) DESC LIMIT 500"""
    )
    filas = cur.fetchall()
    conn.close()
    return jsonify([
        {"token": t, "correo": c, "nivel": n or "bajo", "mensajes": total, "ultimo": ultimo}
        for t, c, n, total, ultimo in filas
    ])


@app.route("/psicologa/api/conversacion/<token>")
def psicologa_conversacion(token):
    """Los mensajes de una conversación, cada uno con el riesgo que le dio el filtro."""
    if not session.get("es_psicologa"):
        return jsonify({"error": "sesion"}), 403
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """SELECT emisor, contenido, nivel_riesgo, categorias, fecha, autor FROM mensajes
           WHERE token = ? ORDER BY id DESC LIMIT 500""",
        (token,),
    )
    filas = cur.fetchall()
    conn.close()
    return jsonify([
        {"emisor": e, "contenido": c, "nivel": n or "bajo",
         "categorias": [x for x in (cat or "").split(",") if x], "fecha": f, "autor": a}
        for e, c, n, cat, f, a in reversed(filas)
    ])


@app.route("/psicologa/estadisticas")
def psicologa_estadisticas():
    if not session.get("es_psicologa"):
        return redirect(url_for("psicologa_login"))
    return render_template("psicologa_estadisticas.html", stats=obtener_estadisticas())


# ---------------------------------------------------------------------------
# Cuentas opcionales de estudiantes (apodo + avatar)
# ---------------------------------------------------------------------------
@app.route("/cuenta/crear", methods=["GET", "POST"])
def cuenta_crear():
    if usuario_actual():
        return redirect(url_for("cuenta"))
    error = None
    datos = {"apodo": "", "avatar": cuentas.AVATARES[0][0]}
    if request.method == "POST":
        datos = {"apodo": request.form.get("apodo", ""), "avatar": request.form.get("avatar", "")}
        if not csrf_valido():
            error = "La página expiró. Vuelve a intentarlo."
        elif request.form.get("clave") != request.form.get("clave2"):
            error = "Las dos contraseñas no son iguales."
        else:
            usuario_id, error = cuentas.crear(datos["apodo"], request.form.get("clave"), datos["avatar"])
            if usuario_id:
                session["usuario_id"] = usuario_id
                # El diario que ya llevaba sin cuenta pasa a su cuenta.
                cuentas.pasar_diario(session.get("token"), cuentas.obtener(usuario_id)["token_diario"])
                flash("¡Listo! Tu cuenta está creada. Tu diario ahora te sigue en cualquier dispositivo.", "exito")
                return redirect(url_for("diario"))
    return render_template("cuenta.html", modo="crear", error=error, datos=datos, avatares=cuentas.AVATARES)


@app.route("/cuenta/entrar", methods=["GET", "POST"])
def cuenta_entrar():
    if usuario_actual():
        return redirect(url_for("cuenta"))
    error = None
    if request.method == "POST":
        if not csrf_valido():
            error = "La página expiró. Vuelve a intentarlo."
        else:
            usuario_id = cuentas.entrar(request.form.get("apodo"), request.form.get("clave"))
            if usuario_id:
                session["usuario_id"] = usuario_id
                return redirect(url_for("diario"))
            error = "Apodo o contraseña incorrectos."
    return render_template("cuenta.html", modo="entrar", error=error, datos={"apodo": request.form.get("apodo", "")}, avatares=cuentas.AVATARES)


@app.route("/cuenta", methods=["GET", "POST"])
def cuenta():
    u = usuario_actual()
    if not u:
        return redirect(url_for("cuenta_entrar"))
    error = None
    if request.method == "POST":
        if not csrf_valido():
            error = "La página expiró. Vuelve a intentarlo."
        else:
            error = cuentas.actualizar(u["id"], request.form.get("apodo"), request.form.get("avatar"))
            if not error:
                flash("Guardamos tus cambios.", "exito")
                return redirect(url_for("cuenta"))
    return render_template("cuenta.html", modo="perfil", error=error, datos=u, avatares=cuentas.AVATARES)


@app.route("/cuenta/salir", methods=["POST"])
def cuenta_salir():
    if csrf_valido():
        session.pop("usuario_id", None)
    return redirect(url_for("index"))


@app.route("/cuenta/borrar", methods=["POST"])
def cuenta_borrar():
    u = usuario_actual()
    if u and csrf_valido():
        cuentas.borrar(u["id"])
        session.pop("usuario_id", None)
        flash("Tu cuenta y tu diario se borraron.", "exito")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Panel de contenido de la psicóloga (cambiar la página sin tocar el código)
# ---------------------------------------------------------------------------
def solo_psicologa():
    return bool(session.get("es_psicologa"))


@app.route("/psicologa/contenido")
def psicologa_contenido():
    if not solo_psicologa():
        return redirect(url_for("psicologa_login"))
    t = contenido.textos()
    return render_template(
        "psicologa_contenido.html",
        articulos=contenido.articulos(incluir_ocultos=True),
        categorias=CATEGORIAS_INFORMATE,
        tecnicas=contenido.tecnicas(incluir_ocultos=True),
        frases="\n".join(t["frases"]),
        mitos=contenido.mitos_a_texto(t["mitos"]),
        historias=contenido.historias_a_texto(t["historias"]),
        muro=contenido.publicaciones_muro(),
        resenas=contenido.resenas_todas(),
        ajustes=contenido.ajustes(),
    )


@app.route("/psicologa/contenido/articulo/<slug>", methods=["GET", "POST"])
def psicologa_articulo(slug):
    if not solo_psicologa():
        return redirect(url_for("psicologa_login"))
    articulos = contenido.articulos(incluir_ocultos=True)
    nuevo = slug == "nuevo"
    if not nuevo and slug not in articulos:
        return redirect(url_for("psicologa_contenido", _anchor="articulos"))
    if request.method == "POST" and csrf_valido():
        titulo = (request.form.get("titulo") or "").strip()[:140]
        texto = (request.form.get("contenido") or "").strip()
        if titulo and texto:
            guardado = contenido.guardar_articulo(
                None if nuevo else slug, titulo,
                request.form.get("categoria") or CATEGORIAS_INFORMATE[0][0],
                (request.form.get("resumen") or "").strip()[:300], texto,
                request.form.get("video") or "",
            )
            flash("Artículo guardado. Ya se ve en Infórmate.", "exito")
            return redirect(url_for("psicologa_contenido", _anchor="articulos"))
        flash("Falta el título o el texto del artículo.", "aviso")
    a = {} if nuevo else articulos[slug]
    return render_template("psicologa_editar.html", tipo="articulo", nuevo=nuevo, clave=slug, item=a,
                           texto="\n\n".join(a.get("contenido", [])), categorias=CATEGORIAS_INFORMATE)


@app.route("/psicologa/contenido/herramienta/<path:clave>", methods=["GET", "POST"])
def psicologa_herramienta(clave):
    if not solo_psicologa():
        return redirect(url_for("psicologa_login"))
    tecnicas = contenido.tecnicas(incluir_ocultos=True)
    nuevo = clave == "nuevo"
    t, cat_id = {}, None
    if not nuevo:
        cat_id, _, tec_id = clave.partition("/")
        t = tecnicas.get(cat_id, {}).get("tecnicas", {}).get(tec_id)
        if t is None:
            return redirect(url_for("psicologa_contenido", _anchor="herramientas"))
    if request.method == "POST" and csrf_valido():
        nombre = (request.form.get("nombre") or "").strip()[:120]
        pasos = (request.form.get("pasos") or "").strip()
        categoria = cat_id or request.form.get("categoria")
        if nombre and pasos and categoria in tecnicas:
            contenido.guardar_herramienta(None if nuevo else clave, categoria, nombre,
                                          (request.form.get("resumen") or "").strip()[:300], pasos,
                                          request.form.get("video") or "")
            flash("Herramienta guardada. Ya se ve en Herramientas.", "exito")
            return redirect(url_for("psicologa_contenido", _anchor="herramientas"))
        flash("Falta el nombre, la categoría o los pasos.", "aviso")
    return render_template("psicologa_editar.html", tipo="herramienta", nuevo=nuevo, clave=clave, item=t,
                           texto="\n".join(t.get("pasos", [])), categoria_actual=cat_id,
                           categorias=[(c, cat["titulo"]) for c, cat in tecnicas.items()])


@app.route("/psicologa/contenido/accion", methods=["POST"])
def psicologa_accion():
    """Esconder, mostrar o restaurar artículos y herramientas; moderar el muro y las reseñas."""
    if not solo_psicologa() or not csrf_valido():
        return redirect(url_for("psicologa_login"))
    tipo, clave, accion = request.form.get("tipo"), request.form.get("clave", ""), request.form.get("accion")
    ancla = "articulos"
    if tipo == "articulo":
        if accion in ("ocultar", "mostrar"):
            contenido.poner_oculto_articulo(clave, accion == "ocultar")
        elif accion == "restaurar":
            contenido.restaurar_articulo(clave)
    elif tipo == "herramienta":
        ancla = "herramientas"
        if accion in ("ocultar", "mostrar"):
            contenido.poner_oculto_herramienta(clave, accion == "ocultar")
        elif accion == "restaurar":
            contenido.restaurar_herramienta(clave)
    elif tipo in ("muro_posts", "resenas") and clave.isdigit():
        ancla = "moderar"
        contenido.moderar(tipo, int(clave), accion)
    return redirect(url_for("psicologa_contenido", _anchor=ancla))


@app.route("/psicologa/contenido/textos", methods=["POST"])
def psicologa_textos():
    if not solo_psicologa() or not csrf_valido():
        return redirect(url_for("psicologa_login"))
    if request.form.get("restaurar"):
        contenido.restaurar_texto(request.form["restaurar"])
    else:
        contenido.guardar_texto("frases", contenido.separar_lineas(request.form.get("frases")))
        contenido.guardar_texto("mitos", contenido.texto_a_mitos(request.form.get("mitos")))
        contenido.guardar_texto("historias", contenido.texto_a_historias(request.form.get("historias")))
    flash("Textos de la portada guardados.", "exito")
    return redirect(url_for("psicologa_contenido", _anchor="textos"))


@app.route("/psicologa/contenido/ajustes", methods=["POST"])
def psicologa_ajustes():
    if not solo_psicologa() or not csrf_valido():
        return redirect(url_for("psicologa_login"))
    numero = contenido.numero_whatsapp(request.form.get("whatsapp_numero"))
    if len(numero) >= 10:
        contenido.guardar_ajuste("whatsapp_numero", numero)
        contenido.guardar_ajuste("whatsapp_nombre", (request.form.get("whatsapp_nombre") or "").strip()[:40])
        flash("WhatsApp guardado. El botón verde ya escribe a ese número.", "exito")
    else:
        flash("Ese número no parece correcto. Escribe los 8 dígitos (ej. 9999-9999).", "aviso")
    return redirect(url_for("psicologa_contenido", _anchor="ajustes"))


# ---------------------------------------------------------------------------
# Eventos WebSocket (Socket.IO)
# ---------------------------------------------------------------------------
@socketio.on("unirse")
def on_unirse(data):
    """El estudiante o la psicóloga se unen a una 'sala' identificada por el token."""
    token = data["token"]
    join_room(token)

    if data.get("quien") == "estudiante":
        conectada = psicologa_esta_conectada()
        if conectada:
            mensaje = (
                "La psicóloga está conectada ahora mismo. Puede tardar unos minutos "
                "en responder — tu mensaje no se pierde, ella lo va a leer."
            )
        else:
            mensaje = (
                "En este momento la psicóloga no está conectada. Tu mensaje queda "
                "guardado y te va a responder en cuanto pueda. Si es una emergencia, "
                "llama gratis al 150 (Teléfono de la Esperanza) o usa el botón de WhatsApp."
            )
        emit("estado_psicologa", {"conectada": conectada, "mensaje": mensaje})


@socketio.on("unirse_panel")
def on_unirse_panel():
    """La psicóloga se une a la sala general de notificaciones (requiere sesión iniciada)."""
    if not session.get("es_psicologa"):
        return
    join_room("panel_psicologa")
    PSICOLOGA_SIDS.add(request.sid)


@socketio.on("disconnect")
def on_disconnect():
    PSICOLOGA_SIDS.discard(request.sid)


@socketio.on("escribiendo")
def on_escribiendo(data):
    """Avisa en tiempo real que alguien está escribiendo en esa sala (indicador visual)."""
    token = data.get("token")
    if not token:
        return
    emit(
        "alguien_escribiendo",
        {"token": token, "quien": data.get("quien")},
        room=token,
        include_self=False,
    )


@socketio.on("dejo_de_escribir")
def on_dejo_de_escribir(data):
    token = data.get("token")
    if not token:
        return
    emit(
        "alguien_dejo_de_escribir",
        {"token": token, "quien": data.get("quien")},
        room=token,
        include_self=False,
    )


@socketio.on("guardar_contacto_emergencia")
def on_guardar_contacto_emergencia(data):
    """
    El estudiante, de forma totalmente voluntaria y solo cuando ya se mostró el
    aviso de apoyo de emergencia, puede dejar un número para que la psicóloga
    lo contacte por WhatsApp o Telegram. Nunca se pide un nombre.
    """
    token = data.get("token")
    telefono = (data.get("telefono") or "").strip()[:20]
    plataforma = data.get("plataforma") if data.get("plataforma") in ("whatsapp", "telegram") else "whatsapp"

    if not token or not telefono:
        return

    guardar_contacto_emergencia(token, telefono, plataforma)
    emit(
        "contacto_emergencia_panel",
        {"token": token, "telefono": telefono, "plataforma": plataforma},
        room="panel_psicologa",
    )
    emit(
        "contacto_emergencia_confirmado",
        {"mensaje": "Gracias por confiar en nosotros. La psicóloga ya tiene tu número para contactarte."},
        room=token,
    )


def sin_correo(data):
    """Nadie escribe en un chat sin haber puesto su correo: si falta, se le
    manda a la página del correo y el mensaje no se guarda."""
    if session.get("correo") and data.get("token") == session.get("token"):
        return False
    emit("pide_correo", {"ir": url_for("entrar_correo")})
    return True


@socketio.on("mensaje_estudiante")
def on_mensaje_estudiante(data):
    if sin_correo(data):
        return
    token = data["token"]
    contenido = data["contenido"]

    analisis = analizar_riesgo(contenido)
    guardar_mensaje(token, "estudiante", contenido, analisis)

    # El estudiante ve su propio mensaje reflejado en su chat
    emit("nuevo_mensaje", {"emisor": "estudiante", "contenido": contenido}, room=token)

    # La psicóloga recibe el mensaje en su vista de ese chat específico
    emit(
        "nuevo_mensaje_panel",
        {
            "token": token,
            "emisor": "estudiante",
            "contenido": contenido,
            "nivel_riesgo": analisis["nivel"],
            "categorias": analisis["categorias"],
            "correo": correo_de(token),
        },
        room="panel_psicologa",
    )

    # Si el riesgo es medio o superior, se dispara una alerta específica
    if analisis["nivel"] in ("medio", "alto", "critico"):
        emit(
            "alerta_riesgo",
            {
                "token": token,
                "nivel": analisis["nivel"],
                "categorias": analisis["categorias"],
                "correo": correo_de(token),
            },
            room="panel_psicologa",
        )

    # Si el riesgo es crítico, se muestra apoyo inmediato al estudiante
    if analisis["nivel"] == "critico":
        emit(
            "apoyo_emergencia",
            {
                "mensaje": (
                    "No estás solo/a. Mientras te conectamos con la psicóloga, "
                    "aquí tienes líneas de ayuda disponibles ahora mismo."
                )
            },
            room=token,
        )


@socketio.on("mensaje_chatbot")
def on_mensaje_chatbot(data):
    if sin_correo(data):
        return
    token = data["token"]
    contenido = data["contenido"]
    persona = data.get("persona")

    analisis = analizar_riesgo(contenido)
    guardar_mensaje(token, "estudiante", contenido, analisis)

    # El estudiante ve su propio mensaje
    emit("nuevo_mensaje", {"emisor": "estudiante", "contenido": contenido}, room=token)

    # La psicóloga siempre puede ver estas conversaciones también (transparencia total)
    emit(
        "nuevo_mensaje_panel",
        {
            "token": token,
            "emisor": "estudiante",
            "contenido": contenido,
            "nivel_riesgo": analisis["nivel"],
            "categorias": analisis["categorias"],
            "correo": correo_de(token),
        },
        room="panel_psicologa",
    )

    if analisis["nivel"] in ("medio", "alto", "critico"):
        # El bot NO improvisa: siempre deriva a un humano si hay riesgo
        respuesta = RESPUESTA_DERIVACION
        conversacion_bot.olvidar(token)  # después no sigue con el tema anterior como si nada
        emit(
            "alerta_riesgo",
            {"token": token, "nivel": analisis["nivel"], "categorias": analisis["categorias"],
             "correo": correo_de(token)},
            room="panel_psicologa",
        )
        if analisis["nivel"] == "critico":
            emit(
                "apoyo_emergencia",
                {
                    "mensaje": (
                        "No estás solo/a. Mientras te conectamos con la psicóloga, "
                        "aquí tienes líneas de ayuda disponibles ahora mismo."
                    )
                },
                room=token,
            )
    else:
        # Riesgo bajo: responde la IA si está configurada; si no está o falla,
        # responden las reglas de respuestas_bot.py.
        historial = obtener_historial(token)[:-1]  # sin el mensaje que acaba de llegar
        nombre = PERSONAJES.get(persona, {}).get("nombre", "el asistente")
        respuesta = ia_asistente.responder(historial, contenido, persona=persona, nombre=nombre)
        if not respuesta:
            respuesta = generar_respuesta(contenido, token, personaje=persona)

    guardar_mensaje(token, "asistente", respuesta, {"nivel": "bajo", "categorias": []})
    emit("nuevo_mensaje", {"emisor": "asistente", "contenido": respuesta}, room=token)
    emit(
        "nuevo_mensaje_panel",
        {"token": token, "emisor": "asistente", "contenido": respuesta, "nivel_riesgo": "bajo"},
        room="panel_psicologa",
    )


@socketio.on("mensaje_psicologa")
def on_mensaje_psicologa(data):
    if not session.get("es_psicologa"):
        return
    token = data["token"]
    contenido = data["contenido"]

    autor = session.get("nombre_panel", "Psicóloga")

    analisis = analizar_riesgo(contenido)  # se registra igual, aunque no genera alerta
    guardar_mensaje(token, "psicologa", contenido, analisis, autor=autor)

    emit("nuevo_mensaje", {"emisor": "psicologa", "contenido": contenido}, room=token)
    # Les llega a todas las cuentas del panel, con el nombre de quien respondió
    emit(
        "nuevo_mensaje_panel",
        {"token": token, "emisor": "psicologa", "contenido": contenido, "nivel_riesgo": "bajo",
         "autor": autor},
        room="panel_psicologa",
    )


# Se ejecuta siempre (también bajo gunicorn en producción), no solo al correr
# "python app.py" directamente — si no, en el servidor real nunca se crearían
# las tablas de la base de datos.
init_db()

if __name__ == "__main__":
    # Este bloque solo se ejecuta con "python app.py" (desarrollo local).
    # En producción, gunicorn importa "app" directamente y nunca pasa por aquí.
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
