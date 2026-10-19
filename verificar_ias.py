"""Revisa que las claves de IA del archivo .env funcionen, sin gastar tokens.

Uso:  python verificar_ias.py
Solo hace llamadas gratuitas (ver modelos disponibles o datos de la clave) y nunca
muestra las claves: solo dice si cada servicio respondió bien.
"""
import json
import os
import urllib.error
import urllib.request

from ia_proveedores import cargar_env, PROVEEDORES


def pedir(url, cabeceras):
    req = urllib.request.Request(url, headers={"User-Agent": "no-estamos-solos-lmh", **cabeceras})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        try:
            cuerpo = json.loads(e.read().decode("utf-8") or "{}")
        except Exception:
            cuerpo = {}
        return e.code, cuerpo
    except Exception as e:  # sin internet, DNS, tiempo de espera
        return None, {"error": type(e).__name__}


def modelos_de(datos):
    lista = datos.get("data") or datos.get("models") or []
    ids = []
    for m in lista:
        if isinstance(m, dict):
            ids.append(m.get("id") or m.get("name", "").replace("models/", ""))
    return [i for i in ids if i]


def main():
    cargar_env()
    print("Servicio".ljust(14), "Clave".ljust(9), "Estado")
    for p in PROVEEDORES:
        clave = os.environ.get(p["clave"], "").strip()
        if not clave:
            print(p["nombre"].ljust(14), "falta".ljust(9), f"(agrega {p['clave']} en .env)")
            continue
        url, cab = p["verificar"](clave)
        if not url.startswith("http"):
            print(p["nombre"].ljust(14), "incompleto".ljust(9), f"falta {p['id'].upper()}_URL y {p['id'].upper()}_MODELO en .env")
            continue
        estado, datos = pedir(url, cab)
        if estado == 200:
            ids = modelos_de(datos)
            import ia_proveedores
            modelos = ia_proveedores._modelos(p)
            extra = ""
            if ids and modelos:
                marcas = [m if (m in ids or any(i.endswith(m) for i in ids)) else f"{m} (no aparece)" for m in modelos]
                extra = " · modelos: " + ", ".join(marcas)
            if p["id"] == "openrouter" and isinstance(datos.get("data"), dict):
                d = datos["data"]
                extra = f" · límite {d.get('limit')} · usado {d.get('usage')}"
            print(p["nombre"].ljust(14), "ok".ljust(9), "funciona" + extra)
        else:
            msg = datos.get("error") if isinstance(datos.get("error"), str) else (datos.get("error") or {}).get("message", "") if isinstance(datos.get("error"), dict) else datos.get("message", "")
            print(p["nombre"].ljust(14), "revisar".ljust(9), f"respondió {estado} {str(msg)[:90]}")


def probar_chat():
    """Manda un saludo corto a cada servicio (gasta muy pocos tokens)."""
    import ia_proveedores as ia
    print()
    print("Prueba de conversación (un saludo corto a cada servicio):")
    for p in ia.en_orden():
        solo = [p]
        original = ia.en_orden
        ia.en_orden = lambda: solo
        try:
            texto, quien = ia.conversar("Responde en español con una sola oración corta.", [{"role": "user", "content": "Hola, ¿cómo estás?"}])
        finally:
            ia.en_orden = original
        estado = "ok" if texto else "falló"
        print(" ", p["nombre"].ljust(13), estado.ljust(6), " ".join((texto or "").split())[:70])


if __name__ == "__main__":
    import sys
    main()
    if "--chat" in sys.argv:
        probar_chat()
