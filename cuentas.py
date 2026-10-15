"""
Cuentas opcionales de estudiantes: apodo + avatar + contraseña.

Nadie está obligado a crear una. Sirven para que el diario de ánimo diga
"Hola, <apodo>" y siga a la persona en cualquier celular o computadora.

Privacidad:
  - Se pide un APODO, no el nombre real, y un avatar de una galería
    (no se suben fotos).
  - La contraseña se guarda cifrada (hash), nunca tal cual.
  - El diario de la cuenta usa su propio código, distinto del que se usa en
    los chats: así los chats con la psicóloga siguen siendo anónimos.
  - La persona puede borrar su cuenta y su diario cuando quiera.
"""

import re
import sqlite3
import uuid
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = None

# Avatares: (clave, dibujo, color de fondo).
AVATARES = [
    ("tigre", "🐯", "#c3e956"), ("buho", "🦉", "#91eaaf"), ("panda", "🐼", "#dff7e8"),
    ("zorro", "🦊", "#f7c99b"), ("tortuga", "🐢", "#91eaaf"), ("delfin", "🐬", "#a9d8f5"),
    ("leon", "🦁", "#f5d27a"), ("koala", "🐨", "#d8dde0"), ("girasol", "🌻", "#c3e956"),
    ("estrella", "⭐", "#fff1b8"), ("cohete", "🚀", "#cfd8ff"), ("planta", "🌱", "#c4ebd2"),
]
AVATARES_POR_CLAVE = {a[0]: a for a in AVATARES}


def configurar(db_path):
    global DB_PATH
    DB_PATH = db_path


def _conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_tablas(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apodo TEXT UNIQUE COLLATE NOCASE,
            clave_hash TEXT,
            avatar TEXT,
            token_diario TEXT UNIQUE,   -- código del diario (no se usa en los chats)
            creado TEXT
        )
        """
    )


def validar_apodo(apodo):
    apodo = (apodo or "").strip()
    if not 3 <= len(apodo) <= 20:
        return None, "El apodo debe tener entre 3 y 20 letras."
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9 _.\-]+", apodo):
        return None, "Usa solo letras, números, espacios, puntos o guiones."
    return apodo, None


def crear(apodo, clave, avatar):
    apodo, error = validar_apodo(apodo)
    if error:
        return None, error
    if len(clave or "") < 6:
        return None, "La contraseña debe tener al menos 6 caracteres."
    if avatar not in AVATARES_POR_CLAVE:
        avatar = AVATARES[0][0]
    token = f"Diario-{uuid.uuid4().hex[:10]}"
    try:
        with _conectar() as conn:
            cur = conn.execute(
                "INSERT INTO usuarios (apodo, clave_hash, avatar, token_diario, creado) VALUES (?, ?, ?, ?, ?)",
                (apodo, generate_password_hash(clave), avatar, token, datetime.now().isoformat(timespec="seconds")),
            )
            return cur.lastrowid, None
    except sqlite3.IntegrityError:
        return None, "Ese apodo ya está en uso. Prueba con otro."


def entrar(apodo, clave):
    with _conectar() as conn:
        f = conn.execute("SELECT * FROM usuarios WHERE apodo = ?", ((apodo or "").strip(),)).fetchone()
    if f and check_password_hash(f["clave_hash"], clave or ""):
        return f["id"]
    return None


def obtener(usuario_id):
    if not usuario_id:
        return None
    with _conectar() as conn:
        f = conn.execute("SELECT id, apodo, avatar, token_diario FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    if not f:
        return None
    clave, dibujo, color = AVATARES_POR_CLAVE.get(f["avatar"], AVATARES[0])
    return {"id": f["id"], "apodo": f["apodo"], "avatar": clave, "avatar_dibujo": dibujo,
            "avatar_color": color, "token_diario": f["token_diario"]}


def actualizar(usuario_id, apodo, avatar):
    apodo, error = validar_apodo(apodo)
    if error:
        return error
    if avatar not in AVATARES_POR_CLAVE:
        return "Elige un avatar de la lista."
    try:
        with _conectar() as conn:
            conn.execute("UPDATE usuarios SET apodo = ?, avatar = ? WHERE id = ?", (apodo, avatar, usuario_id))
    except sqlite3.IntegrityError:
        return "Ese apodo ya está en uso. Prueba con otro."
    return None


def pasar_diario(token_anonimo, token_diario):
    """Al crear una cuenta, el diario que ya llevaba sin cuenta pasa a ella."""
    if not token_anonimo:
        return
    with _conectar() as conn:
        conn.execute("UPDATE OR IGNORE animos SET token = ? WHERE token = ?", (token_diario, token_anonimo))


def borrar(usuario_id):
    """Borra la cuenta y su diario."""
    u = obtener(usuario_id)
    if not u:
        return
    with _conectar() as conn:
        conn.execute("DELETE FROM animos WHERE token = ?", (u["token_diario"],))
        conn.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
