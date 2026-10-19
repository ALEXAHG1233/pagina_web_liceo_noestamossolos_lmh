"""
Varios servicios de IA en cadena: si uno se queda sin saldo, sin cuota, falla o
tarda demasiado, la conversación pasa sola al siguiente. Si ninguno responde,
app.py usa las respuestas preparadas (respuestas_bot.py): el chat nunca se queda
sin contestar.

Reglas que no cambian:
  - Solo se llega aquí con mensajes de riesgo "bajo". Las crisis las atiende la
    psicóloga (app.py) y nunca pasan por ninguna IA.
  - A los servicios solo se envía el texto anónimo de la conversación; el código
    del estudiante (token) nunca sale del servidor.
  - Las claves se leen del archivo .env (o del panel de Render) y nunca se
    escriben en el código ni se muestran en pantalla ni en los registros.

Orden: el de PROVEEDORES, o el que se ponga en .env con IA_ORDEN (por ejemplo
IA_ORDEN=groq,google,anthropic). El modelo de cada uno se puede cambiar con
<ID>_MODELO (por ejemplo GROQ_MODELO=llama-3.1-8b-instant).

Voz: transcribir() convierte audio en texto con Whisper en Groq (y, si falla,
con Whisper en Hugging Face).
"""

import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
import uuid

log = logging.getLogger(__name__)

try:
    import anthropic
except ImportError:  # sin la librería, Claude se salta y se usan los demás
    anthropic = None

TIEMPO_POR_SERVICIO = 25   # segundos máximos esperando a un servicio
TIEMPO_TOTAL = 50          # segundos máximos sumando todos los intentos


def cargar_env(ruta=None):
    """Lee el archivo .env (NOMBRE=valor por línea) sin pisar variables ya definidas."""
    ruta = ruta or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8-sig") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            nombre, valor = linea.split("=", 1)
            os.environ.setdefault(nombre.strip(), valor.strip().strip('"').strip("'"))


def _bearer(clave):
    return {"Authorization": f"Bearer {clave}"}


def _espacio_anthropic():
    """Las claves de Claude que no son de un "workspace" necesitan su ID (ANTHROPIC_WORKSPACE_ID)."""
    espacio = os.environ.get("ANTHROPIC_WORKSPACE_ID", "").strip()
    return {"anthropic-workspace-id": espacio} if espacio else {}


# Cada servicio: id, nombre, variable de la clave, modelos (del preferido al de respaldo), URL del chat
# (formato compatible con OpenAI) y cómo revisar la clave gratis.
PROVEEDORES = [
    {
        "id": "anthropic", "nombre": "Claude", "clave": "ANTHROPIC_API_KEY", "modelo": ["claude-opus-5-5", "claude-haiku-5-5"],
        "tipo": "anthropic",
        "verificar": lambda c: ("https://api.anthropic.com/v1/models", {"x-api-key": c, "anthropic-version": "2023-06-01", **_espacio_anthropic()}),
    },
    {
        "id": "groq", "nombre": "Groq", "clave": "GROQ_KEY", "modelo": ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"],
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "verificar": lambda c: ("https://api.groq.com/openai/v1/models", _bearer(c)),
    },
    {
        "id": "google", "nombre": "Gemini", "clave": "GOOGLE_KEY", "modelo": ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"],
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "verificar": lambda c: ("https://generativelanguage.googleapis.com/v1beta/models", {"x-goog-api-key": c}),
    },
    {
        "id": "mistral", "nombre": "Mistral", "clave": "MISTRAL_KEY", "modelo": ["mistral-small-latest", "mistral-medium-latest", "ministral-8b-latest"],
        "url": "https://api.mistral.ai/v1/chat/completions",
        "verificar": lambda c: ("https://api.mistral.ai/v1/models", _bearer(c)),
    },
    {
        "id": "openrouter", "nombre": "OpenRouter", "clave": "OPENROUTER_KEY", "modelo": ["google/gemma-4-31b-it:free", "google/gemma-4-26b-a4b-it:free"],
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "verificar": lambda c: ("https://openrouter.ai/api/v1/key", _bearer(c)),
    },
    {
        "id": "nvidia", "nombre": "NVIDIA", "clave": "NVIDIA_KEY", "modelo": ["openai/gpt-oss-20b", "deepseek-ai/deepseek-v4.1-flash"],
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "verificar": lambda c: ("https://integrate.api.nvidia.com/v1/models", _bearer(c)),
    },
    {
        "id": "huggingface", "nombre": "Hugging Face", "clave": "HUGGINGFACE_KEY", "modelo": ["Qwen/Qwen3-235B-A22B-Instruct-2507", "Qwen/Qwen3-32B"],
        "url": "https://router.huggingface.co/v1/chat/completions",
        "verificar": lambda c: ("https://huggingface.co/api/whoami-v2", _bearer(c)),
    },
    {
        # B.AI (docs.b.ai): una sola clave da acceso a modelos de Claude, GPT, Gemini,
        # Qwen y otros. Necesita saldo en la cuenta de B.AI; sin saldo se salta sola.
        "id": "bai", "nombre": "B.AI", "clave": "BAI_KEY",
        "modelo": ["claude-haiku-5.5", "gemini-3.5-flash", "gpt-5.4-mini", "qwen3.8-flash"],
        "url": "https://api.b.ai/v1/chat/completions",
        "verificar": lambda c: ("https://api.b.ai/v1/models", _bearer(c)),
    },
]
POR_ID = {p["id"]: p for p in PROVEEDORES}

# Servicios en pausa: id -> hasta cuándo (time.time()). Se llenan solos cuando un
# servicio se queda sin saldo, sin cuota o falla, y se vacían cuando pasa el tiempo.
_pausados = {}
ultimo_usado = {"id": None, "cuando": 0}


def _modelos(p):
    """Modelos de un servicio, del preferido al de respaldo. Se pueden cambiar en .env
    con <ID>_MODELO, separados por comas (por ejemplo GROQ_MODELO=a,b)."""
    propio = os.environ.get(f"{p['id'].upper()}_MODELO", "").strip()
    if propio:
        return [m.strip() for m in propio.split(",") if m.strip()]
    base = p.get("modelo")
    return list(base) if isinstance(base, (list, tuple)) else ([base] if base else [])


def _modelo(p):
    lista = _modelos(p)
    return lista[0] if lista else None


def _url(p):
    return os.environ.get(f"{p['id'].upper()}_URL") or p.get("url")


def _clave(p):
    return os.environ.get(p["clave"], "").strip()


def configurado(p):
    if not _clave(p):
        return False
    if p.get("tipo") == "anthropic":
        return anthropic is not None
    return bool(_url(p) and _modelos(p))


def en_orden():
    orden = [i.strip() for i in os.environ.get("IA_ORDEN", "").split(",") if i.strip() in POR_ID]
    lista = [POR_ID[i] for i in orden] + [p for p in PROVEEDORES if p["id"] not in orden]
    return [p for p in lista if configurado(p)]


def alguno_disponible():
    return bool(en_orden())


def _pausar(p, segundos, motivo):
    _pausados[p["id"]] = time.time() + segundos
    log.warning("IA %s en pausa %s min: %s", p["nombre"], round(segundos / 60), motivo)


def _clasificar(estado, texto):
    """Cuánto tiempo dejar en pausa un servicio que falló."""
    t = (texto or "").lower()
    if any(p in t for p in ("credit", "saldo", "balance", "insufficient", "billing", "payment")) or estado == 402:
        return 6 * 3600, "sin saldo"  # se acabó el saldo de la cuenta: se salta todo el servicio
    if any(p in t for p in ("quota", "exceeded your")):
        return 3600, "sin cuota en este modelo por ahora"  # a veces otro modelo del mismo servicio sí tiene
    if "workspace" in t:
        return 3600, "a la clave le falta el workspace (ANTHROPIC_WORKSPACE_ID)"
    if "deposit" in t or "access restricted" in t:
        return 6 * 3600, "sin saldo (hace falta un depósito en la cuenta)"
    if estado in (401, 403):
        return 3600, "clave rechazada"
    if estado == 429:
        return 90, "demasiadas peticiones por ahora"
    if estado == 404:
        return 3600, "modelo no encontrado"
    return 120, f"error {estado}"


def _quitar_pensamiento(texto):
    """Algunos modelos escriben su razonamiento entre <think></think>: no se muestra."""
    texto = re.sub(r"<think>.*?</think>", "", texto or "", flags=re.S | re.I)
    return texto.strip()


def _chat_compatible(p, modelo, sistema, mensajes, tiempo):
    cuerpo = {
        "model": modelo,
        "messages": [{"role": "system", "content": sistema}] + mensajes,
        "max_tokens": 400,
        "temperature": 0.7,
    }
    cabeceras = {"Content-Type": "application/json", "User-Agent": "no-estamos-solos-lmh", **_bearer(_clave(p))}
    if p["id"] == "openrouter":
        cabeceras["X-Title"] = "No estamos solos LMH"
    if "gpt-oss" in cuerpo["model"] or p["id"] == "google":
        # Modelos que razonan antes de responder: poco razonamiento (chat rápido) y
        # espacio suficiente para que no se corte la respuesta.
        cuerpo["reasoning_effort"] = "low"
        cuerpo["max_tokens"] = 1500
    req = urllib.request.Request(_url(p), data=json.dumps(cuerpo).encode("utf-8"), headers=cabeceras, method="POST")
    with urllib.request.urlopen(req, timeout=tiempo) as r:
        datos = json.loads(r.read().decode("utf-8"))
    opciones = datos.get("choices") or []
    if not opciones:
        return None
    return _quitar_pensamiento((opciones[0].get("message") or {}).get("content") or "")


_cliente_anthropic = None


def _chat_anthropic(p, modelo, sistema, mensajes, tiempo):
    global _cliente_anthropic
    if _cliente_anthropic is None:
        _cliente_anthropic = anthropic.Anthropic(api_key=_clave(p), timeout=float(tiempo), max_retries=0,
                                                 default_headers=_espacio_anthropic() or None)
    respuesta = _cliente_anthropic.beta.messages.create(
        model=modelo,
        max_tokens=4000,
        system=sistema,
        messages=mensajes,
        output_config={"effort": "low"},  # chat: respuestas rápidas
        # Si el modelo se negara a responder, la API reintenta con otro modelo en la misma llamada.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if respuesta.stop_reason == "refusal":
        return None
    return "".join(b.text for b in respuesta.content if b.type == "text").strip()


PROBLEMAS_DE_CUENTA = ("sin saldo", "clave rechazada", "workspace")


def _error(e):
    """(estado, detalle) de un error de cualquier servicio."""
    if isinstance(e, urllib.error.HTTPError):
        try:
            return e.code, e.read().decode("utf-8", "replace")[:400]
        except Exception:
            return e.code, ""
    return getattr(e, "status_code", None), (getattr(e, "message", "") or type(e).__name__)


def conversar(sistema, mensajes):
    """Prueba cada servicio en orden y, dentro de cada uno, sus modelos.
    Devuelve (texto, "servicio/modelo"), o (None, None) si nadie pudo responder."""
    inicio = time.time()
    for p in en_orden():
        if _pausados.get(p["id"], 0) > time.time():
            continue
        for modelo in _modelos(p):
            clave_modelo = f"{p['id']}:{modelo}"
            if _pausados.get(clave_modelo, 0) > time.time():
                continue
            quedan = TIEMPO_TOTAL - (time.time() - inicio)
            if quedan < 5:
                return None, None
            tiempo = min(TIEMPO_POR_SERVICIO, quedan)
            try:
                if p.get("tipo") == "anthropic":
                    texto = _chat_anthropic(p, modelo, sistema, mensajes, tiempo)
                else:
                    texto = _chat_compatible(p, modelo, sistema, mensajes, tiempo)
                if texto:
                    ultimo_usado.update(id=f"{p['id']}/{modelo}", cuando=time.time())
                    return texto, f"{p['id']}/{modelo}"
                _pausados[clave_modelo] = time.time() + 120
                continue
            except Exception as e:  # HTTP, conexión, tiempo de espera, librería de Claude
                estado, detalle = _error(e)
                segundos, motivo = _clasificar(estado, detalle) if estado else (120, type(e).__name__)
            if any(m in motivo for m in PROBLEMAS_DE_CUENTA):
                _pausar(p, segundos, motivo)  # la cuenta no sirve ahora: todo el servicio en pausa
                break
            _pausados[clave_modelo] = time.time() + segundos
            log.warning("IA %s, modelo %s en pausa %s min: %s", p["nombre"], modelo, round(segundos / 60), motivo)
    return None, None


# ---------------------------------------------------------------------------
# Voz a texto (Whisper)
# ---------------------------------------------------------------------------
TRANSCRIPTORES = [
    ("groq", "GROQ_KEY", "https://api.groq.com/openai/v1/audio/transcriptions", "whisper-large-v3-turbo"),
]


def _multipart(campos, archivo_nombre, archivo_bytes, archivo_tipo):
    limite = uuid.uuid4().hex
    partes = []
    for nombre, valor in campos.items():
        partes.append(f'--{limite}\r\nContent-Disposition: form-data; name="{nombre}"\r\n\r\n{valor}\r\n'.encode("utf-8"))
    partes.append(
        f'--{limite}\r\nContent-Disposition: form-data; name="file"; filename="{archivo_nombre}"\r\n'
        f"Content-Type: {archivo_tipo}\r\n\r\n".encode("utf-8") + archivo_bytes + b"\r\n"
    )
    partes.append(f"--{limite}--\r\n".encode("utf-8"))
    return b"".join(partes), f"multipart/form-data; boundary={limite}"


def transcribir(audio, tipo="audio/webm"):
    """Devuelve el texto en español de una grabación, o None si no se pudo."""
    extension = {"audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "m4a", "audio/mpeg": "mp3", "audio/wav": "wav"}
    nombre = "grabacion." + extension.get(tipo.split(";")[0], "webm")
    for id_, variable, url, modelo in TRANSCRIPTORES:
        clave = os.environ.get(variable, "").strip()
        if not clave or _pausados.get("voz-" + id_, 0) > time.time():
            continue
        cuerpo, tipo_cuerpo = _multipart(
            {"model": os.environ.get("VOZ_MODELO", modelo), "language": "es", "response_format": "json", "temperature": "0"},
            nombre, audio, tipo.split(";")[0],
        )
        req = urllib.request.Request(url, data=cuerpo, method="POST",
                                     headers={"Content-Type": tipo_cuerpo, "User-Agent": "no-estamos-solos-lmh", **_bearer(clave)})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                texto = (json.loads(r.read().decode("utf-8")).get("text") or "").strip()
            return texto or None
        except urllib.error.HTTPError as e:
            segundos, motivo = _clasificar(e.code, e.read().decode("utf-8", "replace")[:300])
            _pausados["voz-" + id_] = time.time() + segundos
            log.warning("Voz (%s) en pausa: %s", id_, motivo)
        except Exception as e:
            log.warning("Voz (%s) falló: %s", id_, type(e).__name__)
    return None


def voz_disponible():
    return any(os.environ.get(v, "").strip() for _, v, _, _ in TRANSCRIPTORES)
