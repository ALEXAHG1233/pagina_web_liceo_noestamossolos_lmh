import os
import random
import sqlite3
import uuid
from datetime import datetime

from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_socketio import SocketIO, join_room, emit
from werkzeug.utils import secure_filename

from filtro_riesgo import analizar_riesgo
from filtro_ofensivo import contiene_lenguaje_ofensivo
from respuestas_bot import generar_respuesta, RESPUESTA_DERIVACION, PERSONAJES
from futuro_bot import generar_mensaje_futuro
from tests_bot import TESTS, obtener_test, calcular_resultado
from articulos_bot import ARTICULOS
from herramientas_bot import TECNICAS

app = Flask(__name__)
# En producción, SECRET_KEY y las credenciales de la psicóloga se deben poner
# como variables de entorno en el servicio de hosting (nunca dejarlas escritas
# aquí). Los valores de la derecha son solo para que funcione en desarrollo local.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cambia-esto-por-una-clave-secreta-real")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB, para que no se abuse de las fotos de reseñas
socketio = SocketIO(app, cors_allowed_origins="*")

DB_PATH = "apoyo_emocional.db"

PSICOLOGA_USUARIO = os.environ.get("PSICOLOGA_USUARIO", "psicologa")
PSICOLOGA_CLAVE = os.environ.get("PSICOLOGA_CLAVE", "cambia-esta-clave")

# IDs de conexión (socket.io) de la psicóloga con el panel abierto ahora mismo.
# Sirve solo para avisarle al estudiante si hay alguien del otro lado o no —
# no decide nada, solo informa.
PSICOLOGA_SIDS = set()


def psicologa_esta_conectada():
    return len(PSICOLOGA_SIDS) > 0

CARPETA_FOTOS_RESENAS = os.path.join("static", "uploads", "resenas")
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


def guardar_mensaje(token, emisor, contenido, analisis):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO mensajes (token, emisor, contenido, nivel_riesgo, categorias, fecha)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            token,
            emisor,
            contenido,
            analisis["nivel"],
            ",".join(analisis["categorias"]),
            datetime.now().isoformat(),
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
        "SELECT estrellas, comentario, fecha, foto FROM resenas ORDER BY id DESC LIMIT ?",
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
        "SELECT contenido, fecha FROM muro_posts ORDER BY id DESC LIMIT ?",
        (limite,),
    )
    filas = cur.fetchall()
    conn.close()
    return filas


def obtener_resumen_resenas():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), AVG(estrellas) FROM resenas")
    total, promedio = cur.fetchone()
    conn.close()
    return {
        "total": total or 0,
        "promedio": round(promedio, 1) if promedio else 0,
    }


# ---------------------------------------------------------------------------
# Rutas HTTP
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    registrar_visita()
    return render_template(
        "index.html",
        categorias_video=VIDEOS_CURADOS,
        video_prevencion_id=VIDEO_PREVENCION_SUICIDIO_ID,
    )


@app.route("/estudiante")
def estudiante():
    # Genera un token anónimo único si no existe ya en la sesión del navegador
    if "token" not in session:
        session["token"] = f"Usuario-{uuid.uuid4().hex[:6]}"
        registrar_sesion(session["token"])
    return render_template("estudiante.html", token=session["token"])


@app.route("/chatbot")
def chatbot():
    """Muestra la selección de con cuál asistente hablar."""
    if "token" not in session:
        session["token"] = f"Usuario-{uuid.uuid4().hex[:6]}"
        registrar_sesion(session["token"])
    return render_template("elegir_amigo.html", personajes=PERSONAJES)


@app.route("/chatbot/sorpresa")
def chatbot_sorpresa():
    return redirect(url_for("chatbot_persona", persona=random.choice(list(PERSONAJES.keys()))))


@app.route("/chatbot/<persona>")
def chatbot_persona(persona):
    if persona not in PERSONAJES:
        return redirect(url_for("chatbot"))
    if "token" not in session:
        session["token"] = f"Usuario-{uuid.uuid4().hex[:6]}"
        registrar_sesion(session["token"])
    return render_template(
        "asistente.html",
        token=session["token"],
        persona_id=persona,
        persona=PERSONAJES[persona],
    )


@app.route("/diario")
def diario():
    if "token" not in session:
        session["token"] = f"Usuario-{uuid.uuid4().hex[:6]}"
        registrar_sesion(session["token"])
    token = session["token"]
    racha = calcular_racha(token)
    historial = obtener_animos_recientes(token, dias=7)
    nuevo = request.args.get("nuevo") == "1"
    return render_template("diario.html", racha=racha, historial=historial, nuevo=nuevo)


@app.route("/diario/registrar/<estado>")
def diario_registrar(estado):
    if "token" not in session:
        session["token"] = f"Usuario-{uuid.uuid4().hex[:6]}"
        registrar_sesion(session["token"])
    if estado in ("genial", "bien", "normal", "mal", "muy_mal"):
        guardar_animo(session["token"], estado)
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
    "lgbt": {
        "titulo": "Comunidad LGBT+",
        "videos": [
            {
                "tipo": "enlace",
                "url": "https://www.youtube.com/user/itgetsbetterproject/videos",
                "titulo": "It Gets Better Project",
                "descripcion": "Canal oficial del proyecto internacional que acompaña a jóvenes LGBT+ con historias reales de que las cosas mejoran.",
            },
        ],
    },
    "hombres_adultos": {
        "titulo": "Para hombres adultos",
        "videos": [
            {
                "tipo": "embed",
                "youtube_id": "ExqTHyfHN-c",
                "titulo": "Hombres, hablemos de salud mental",
                "descripcion": "Charla TEDx sobre por qué a los hombres les cuesta más pedir ayuda, y por qué vale la pena hacerlo.",
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
    return render_template("informate.html", articulos=ARTICULOS)


@app.route("/informate/<slug>")
def informate_articulo(slug):
    articulo = ARTICULOS.get(slug)
    if not articulo:
        return redirect(url_for("informate"))
    return render_template("articulo.html", articulo=articulo)


@app.route("/herramientas")
def herramientas():
    return render_template("herramientas.html", categorias=TECNICAS)


@app.route("/herramientas/<categoria>/<tecnica>")
def herramientas_detalle(categoria, tecnica):
    cat = TECNICAS.get(categoria)
    item = cat["tecnicas"].get(tecnica) if cat else None
    if not cat or not item:
        return redirect(url_for("herramientas"))
    return render_template(
        "herramienta_detalle.html", categoria=cat, categoria_id=categoria, tecnica=item
    )


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
        if usuario == PSICOLOGA_USUARIO and clave == PSICOLOGA_CLAVE:
            session["es_psicologa"] = True
            return redirect(url_for("psicologa"))
        error = "Usuario o clave incorrectos."
    return render_template("psicologa_login.html", error=error)


@app.route("/psicologa/logout")
def psicologa_logout():
    session.pop("es_psicologa", None)
    return redirect(url_for("psicologa_login"))


@app.route("/psicologa")
def psicologa():
    if not session.get("es_psicologa"):
        return redirect(url_for("psicologa_login"))
    return render_template("psicologa.html")


@app.route("/psicologa/estadisticas")
def psicologa_estadisticas():
    if not session.get("es_psicologa"):
        return redirect(url_for("psicologa_login"))
    return render_template("psicologa_estadisticas.html", stats=obtener_estadisticas())


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
                "usa el botón de WhatsApp."
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


@socketio.on("mensaje_estudiante")
def on_mensaje_estudiante(data):
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
        },
        room="panel_psicologa",
    )

    if analisis["nivel"] in ("medio", "alto", "critico"):
        # El bot NO improvisa: siempre deriva a un humano si hay riesgo
        respuesta = RESPUESTA_DERIVACION
        emit(
            "alerta_riesgo",
            {"token": token, "nivel": analisis["nivel"], "categorias": analisis["categorias"]},
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

    analisis = analizar_riesgo(contenido)  # se registra igual, aunque no genera alerta
    guardar_mensaje(token, "psicologa", contenido, analisis)

    emit("nuevo_mensaje", {"emisor": "psicologa", "contenido": contenido}, room=token)
    emit(
        "nuevo_mensaje_panel",
        {"token": token, "emisor": "psicologa", "contenido": contenido, "nivel_riesgo": "bajo"},
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
