"""Objetos 3D "inflados" (estilo íconos 3D de Canva) con la paleta Green Screen.
Solo usa PIL: el volumen sale de una máscara desenfocada iluminada desde arriba a la izquierda."""
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(AQUI, "recursos")
os.makedirs(REC, exist_ok=True)
S = 1040  # se dibuja al doble y se reduce a 520 para suavizar bordes

BLANCO, MENTA, LIMA, OLIVA, OSCURO = "#F4FFFC", "#91EAAF", "#C3E956", "#4D7111", "#1F4B2C"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lienzo_l():
    return Image.new("L", (S, S), 0)


def sombrear(mascara, color, inflado=60):
    """Convierte una máscara en un objeto con volumen, brillo y sombra."""
    h = mascara.filter(ImageFilter.GaussianBlur(inflado))
    k = 14
    adelante = ImageChops.offset(h, -k, -k)
    luz = ImageChops.subtract(adelante, h, scale=0.55)
    sombra = ImageChops.subtract(h, adelante, scale=0.45)
    base = Image.new("RGBA", (S, S), rgb(color) + (255,))
    oscuro = tuple(int(c * 0.45) for c in rgb(color))
    base.alpha_composite(Image.merge("RGBA", [Image.new("L", (S, S), v) for v in oscuro] + [sombra]))
    base.alpha_composite(Image.merge("RGBA", [Image.new("L", (S, S), 255)] * 3 + [luz]))
    # El centro un poco más claro: se ve "inflado".
    centro = h.point(lambda v: int(max(0, v - 150) * 0.5))
    base.alpha_composite(Image.merge("RGBA", [Image.new("L", (S, S), 255)] * 3 + [centro]))
    # Brillo especular: la máscara corrida hacia el centro, recortada y desenfocada.
    nucleo = mascara.filter(ImageFilter.GaussianBlur(inflado * 0.9)).point(lambda v: 255 if v > 235 else 0)
    brillo = ImageChops.offset(nucleo, -int(S * 0.04), -int(S * 0.05)).filter(ImageFilter.GaussianBlur(22))
    brillo = ImageChops.multiply(brillo, mascara).point(lambda v: int(v * 0.5))
    base.alpha_composite(Image.merge("RGBA", [Image.new("L", (S, S), 255)] * 3 + [brillo]))
    base.putalpha(mascara)
    return base


def componer(objeto, nombre, extras=None, sombra_piso=True):
    final = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    a = objeto.getchannel("A")
    caja = a.getbbox()
    if sombra_piso and caja:
        piso = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        x0, y0, x1, y1 = caja
        ancho = (x1 - x0) * 0.42
        cx = (x0 + x1) / 2
        ImageDraw.Draw(piso).ellipse((cx - ancho, y1 - 18, cx + ancho, y1 + 34), fill=(5, 20, 10, 120))
        final.alpha_composite(piso.filter(ImageFilter.GaussianBlur(26)))
    # Sombra suave proyectada.
    proy = Image.new("RGBA", (S, S), (6, 23, 13, 0))
    proy.putalpha(ImageChops.offset(a, 16, 26).filter(ImageFilter.GaussianBlur(24)).point(lambda v: int(v * 0.35)))
    final.alpha_composite(proy)
    final.alpha_composite(objeto)
    if extras:
        extras(final)
    final.resize((S // 2, S // 2), Image.LANCZOS).save(os.path.join(REC, nombre))


def detalle(final, dibujar, color=BLANCO, alto=6):
    """Detalles en relieve (puntos, palomita, letras) sobre el objeto."""
    m = lienzo_l()
    dibujar(ImageDraw.Draw(m))
    sombra = Image.new("RGBA", (S, S), (6, 23, 13, 0))
    sombra.putalpha(ImageChops.offset(m, alto, alto + 2).filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.45)))
    final.alpha_composite(sombra)
    final.alpha_composite(sombrear(m, color, inflado=14))


def poligono(puntos):
    m = lienzo_l()
    ImageDraw.Draw(m).polygon(puntos, fill=255)
    return m


# ---------------------------------------------------------------------------
def corazon():
    pts = []
    for i in range(400):
        t = i / 400 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((S / 2 + x * 22, S * 0.46 - y * 22))
    componer(sombrear(poligono(pts), LIMA), "obj_corazon.png")


def burbuja():
    m = lienzo_l()
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((S * 0.14, S * 0.2, S * 0.86, S * 0.68), radius=S * 0.16, fill=255)
    d.polygon([(S * 0.3, S * 0.6), (S * 0.24, S * 0.84), (S * 0.48, S * 0.64)], fill=255)

    def puntos(dd):
        for k in range(3):
            cx = S * (0.34 + 0.16 * k)
            dd.ellipse((cx - 38, S * 0.44 - 38, cx + 38, S * 0.44 + 38), fill=255)
    componer(sombrear(m, MENTA), "obj_burbuja.png", extras=lambda f: detalle(f, puntos, BLANCO))


def hoja(nombre, color, giro):
    m = lienzo_l()
    d = ImageDraw.Draw(m)
    # Hoja: intersección de dos círculos (forma de lente) con punta.
    a = lienzo_l()
    ImageDraw.Draw(a).ellipse((S * 0.02, S * 0.18, S * 0.98, S * 1.14), fill=255)
    b = lienzo_l()
    ImageDraw.Draw(b).ellipse((S * 0.02, S * -0.14, S * 0.98, S * 0.82), fill=255)
    m = ImageChops.multiply(a, b)
    obj = sombrear(m, color, inflado=70)

    def venas(dd):
        dd.line((S * 0.06, S * 0.5, S * 0.94, S * 0.5), fill=255, width=16)
        for k in range(1, 6):
            x = S * (0.1 + k * 0.14)
            largo = S * (0.12 + 0.04 * math.sin(k / 6 * math.pi))
            dd.line((x, S * 0.5, x + S * 0.09, S * 0.5 - largo), fill=255, width=11)
            dd.line((x, S * 0.5, x + S * 0.09, S * 0.5 + largo), fill=255, width=11)
    final = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    final.alpha_composite(obj)
    vena = rgb(OLIVA) if color != OLIVA else rgb(LIMA)
    mv = lienzo_l()
    venas(ImageDraw.Draw(mv))
    mv = ImageChops.multiply(mv, m.filter(ImageFilter.MinFilter(41)))
    capa = Image.new("RGBA", (S, S), vena + (0,))
    capa.putalpha(mv.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.55)))
    final.alpha_composite(capa)
    final = final.rotate(giro, resample=Image.BICUBIC)
    componer(final, nombre, sombra_piso=False)


def escudo():
    pts = [(S * 0.5, S * 0.12), (S * 0.84, S * 0.24), (S * 0.8, S * 0.56), (S * 0.5, S * 0.88),
           (S * 0.2, S * 0.56), (S * 0.16, S * 0.24)]
    m = poligono(pts).filter(ImageFilter.GaussianBlur(18)).point(lambda v: 255 if v > 128 else 0)

    def palomita(dd):
        dd.line((S * 0.34, S * 0.48, S * 0.46, S * 0.6, S * 0.67, S * 0.36), fill=255, width=64, joint="curve")
    componer(sombrear(m, MENTA), "obj_escudo.png", extras=lambda f: detalle(f, palomita, BLANCO))


def estrella():
    pts = []
    for i in range(10):
        r = S * (0.4 if i % 2 == 0 else 0.18)
        t = -math.pi / 2 + i * math.pi / 5
        pts.append((S / 2 + r * math.cos(t), S * 0.5 + r * math.sin(t)))
    m = poligono(pts).filter(ImageFilter.GaussianBlur(12)).point(lambda v: 255 if v > 128 else 0)
    componer(sombrear(m, LIMA), "obj_estrella.png")


def engranaje():
    m = lienzo_l()
    d = ImageDraw.Draw(m)
    d.ellipse((S * 0.22, S * 0.22, S * 0.78, S * 0.78), fill=255)
    for k in range(8):
        t = k * math.pi / 4
        cx, cy = S / 2 + math.cos(t) * S * 0.31, S / 2 + math.sin(t) * S * 0.31
        diente = Image.new("L", (S, S), 0)
        ImageDraw.Draw(diente).rounded_rectangle((cx - 62, cy - 62, cx + 62, cy + 62), radius=22, fill=255)
        m = ImageChops.lighter(m, diente.rotate(-math.degrees(t), center=(cx, cy)))
    hueco = lienzo_l()
    ImageDraw.Draw(hueco).ellipse((S * 0.39, S * 0.39, S * 0.61, S * 0.61), fill=255)
    m = ImageChops.subtract(m, hueco)
    componer(sombrear(m, MENTA, inflado=40), "obj_engranaje.png")


def candado():
    m = lienzo_l()
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((S * 0.22, S * 0.42, S * 0.78, S * 0.86), radius=S * 0.08, fill=255)
    d.arc((S * 0.32, S * 0.14, S * 0.68, S * 0.62), 180, 360, fill=255, width=int(S * 0.075))
    d.rectangle((S * 0.32, S * 0.37, S * 0.395, S * 0.46), fill=255)
    d.rectangle((S * 0.605, S * 0.37, S * 0.68, S * 0.46), fill=255)

    def cerradura(dd):
        dd.ellipse((S * 0.455, S * 0.55, S * 0.545, S * 0.64), fill=255)
        dd.rounded_rectangle((S * 0.478, S * 0.6, S * 0.522, S * 0.74), radius=10, fill=255)
    componer(sombrear(m, LIMA), "obj_candado.png", extras=lambda f: detalle(f, cerradura, OSCURO, alto=-4))


def rayo():
    pts = [(S * 0.58, S * 0.08), (S * 0.24, S * 0.56), (S * 0.47, S * 0.56), (S * 0.38, S * 0.92),
           (S * 0.78, S * 0.4), (S * 0.54, S * 0.4)]
    m = poligono(pts).filter(ImageFilter.GaussianBlur(10)).point(lambda v: 255 if v > 128 else 0)
    componer(sombrear(m, LIMA, inflado=45), "obj_rayo.png")


def nube():
    m = lienzo_l()
    d = ImageDraw.Draw(m)
    for x0, y0, x1, y1 in [(0.12, 0.42, 0.42, 0.72), (0.28, 0.24, 0.62, 0.58), (0.5, 0.32, 0.84, 0.66), (0.66, 0.46, 0.9, 0.72)]:
        d.ellipse((S * x0, S * y0, S * x1, S * y1), fill=255)
    d.rounded_rectangle((S * 0.26, S * 0.5, S * 0.8, S * 0.72), radius=S * 0.1, fill=255)
    componer(sombrear(m, BLANCO, inflado=70), "obj_nube.png")


def moneda():
    m = lienzo_l()
    ImageDraw.Draw(m).ellipse((S * 0.14, S * 0.14, S * 0.86, S * 0.86), fill=255)
    obj = sombrear(m, LIMA, inflado=50)

    def letra(dd):
        dd.ellipse((S * 0.24, S * 0.24, S * 0.76, S * 0.76), outline=255, width=22)
        try:
            fuente = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", int(S * 0.34))
        except OSError:
            fuente = ImageFont.load_default()
        dd.text((S * 0.5, S * 0.51), "L", font=fuente, fill=255, anchor="mm")
    componer(obj, "obj_moneda.png", extras=lambda f: detalle(f, letra, OLIVA, alto=-3))


def reloj():
    m = lienzo_l()
    ImageDraw.Draw(m).ellipse((S * 0.14, S * 0.14, S * 0.86, S * 0.86), fill=255)
    obj = sombrear(m, MENTA, inflado=50)

    def cara(dd):
        dd.ellipse((S * 0.24, S * 0.24, S * 0.76, S * 0.76), fill=255)

    def agujas(dd):
        dd.line((S * 0.5, S * 0.5, S * 0.5, S * 0.3), fill=255, width=34)
        dd.line((S * 0.5, S * 0.5, S * 0.64, S * 0.58), fill=255, width=34)
        dd.ellipse((S * 0.47, S * 0.47, S * 0.53, S * 0.53), fill=255)

    def extras(f):
        detalle(f, cara, BLANCO, alto=-4)
        detalle(f, agujas, OSCURO, alto=4)
    componer(obj, "obj_reloj.png", extras=extras)


def luna():
    a = lienzo_l()
    ImageDraw.Draw(a).ellipse((S * 0.14, S * 0.14, S * 0.86, S * 0.86), fill=255)
    b = lienzo_l()
    ImageDraw.Draw(b).ellipse((S * 0.36, S * 0.04, S * 1.02, S * 0.7), fill=255)
    m = ImageChops.subtract(a, b)
    componer(sombrear(m, "#E9F7A8", inflado=55), "obj_luna.png")


def libro():
    m = lienzo_l()
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((S * 0.16, S * 0.2, S * 0.84, S * 0.8), radius=S * 0.06, fill=255)
    obj = sombrear(m, MENTA, inflado=40)

    def paginas(dd):
        dd.rounded_rectangle((S * 0.22, S * 0.25, S * 0.48, S * 0.74), radius=18, fill=255)
        dd.rounded_rectangle((S * 0.52, S * 0.25, S * 0.78, S * 0.74), radius=18, fill=255)

    def renglones(dd):
        for k in range(4):
            y = S * (0.35 + k * 0.09)
            dd.line((S * 0.27, y, S * 0.43, y), fill=255, width=12)
            dd.line((S * 0.57, y, S * 0.73, y), fill=255, width=12)

    def extras(f):
        detalle(f, paginas, BLANCO, alto=4)
        detalle(f, renglones, MENTA, alto=-2)
    componer(obj, "obj_libro.png", extras=extras)


def telefono():
    m = lienzo_l()
    ImageDraw.Draw(m).rounded_rectangle((S * 0.3, S * 0.1, S * 0.7, S * 0.9), radius=S * 0.08, fill=255)
    obj = sombrear(m, "#2f6a3a", inflado=35)

    def pantalla(dd):
        dd.rounded_rectangle((S * 0.34, S * 0.17, S * 0.66, S * 0.8), radius=24, fill=255)

    def burbujas(dd):
        dd.rounded_rectangle((S * 0.38, S * 0.26, S * 0.58, S * 0.34), radius=20, fill=255)
        dd.rounded_rectangle((S * 0.44, S * 0.4, S * 0.62, S * 0.48), radius=20, fill=255)
        dd.rounded_rectangle((S * 0.38, S * 0.54, S * 0.56, S * 0.62), radius=20, fill=255)

    def extras(f):
        detalle(f, pantalla, MENTA, alto=-3)
        detalle(f, burbujas, BLANCO, alto=3)
    componer(obj, "obj_telefono.png", extras=extras)


def taza():
    m = lienzo_l()
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((S * 0.2, S * 0.34, S * 0.66, S * 0.82), radius=S * 0.1, fill=255)
    d.arc((S * 0.54, S * 0.42, S * 0.84, S * 0.7), -90, 90, fill=255, width=int(S * 0.06))
    obj = sombrear(m, BLANCO, inflado=45)

    def cafe(dd):
        dd.ellipse((S * 0.24, S * 0.32, S * 0.62, S * 0.42), fill=255)

    def vapor(dd):
        for k in range(3):
            x = S * (0.3 + k * 0.08)
            dd.arc((x - 30, S * 0.12, x + 30, S * 0.22), 90, 270, fill=255, width=14)
            dd.arc((x - 30, S * 0.2, x + 30, S * 0.3), -90, 90, fill=255, width=14)

    def extras(f):
        detalle(f, cafe, "#8a5a34", alto=-2)
        detalle(f, vapor, BLANCO, alto=2)
    componer(obj, "obj_taza.png", extras=extras)


def bombillo():
    m = lienzo_l()
    d = ImageDraw.Draw(m)
    d.ellipse((S * 0.22, S * 0.08, S * 0.78, S * 0.64), fill=255)
    d.polygon([(S * 0.34, S * 0.56), (S * 0.66, S * 0.56), (S * 0.6, S * 0.72), (S * 0.4, S * 0.72)], fill=255)
    obj = sombrear(m, "#F2FBB0", inflado=55)

    def base(dd):
        for k in range(3):
            y = S * (0.73 + k * 0.055)
            dd.rounded_rectangle((S * 0.39, y, S * 0.61, y + S * 0.045), radius=14, fill=255)

    def filamento(dd):
        dd.line((S * 0.42, S * 0.56, S * 0.46, S * 0.38, S * 0.5, S * 0.46, S * 0.54, S * 0.38, S * 0.58, S * 0.56), fill=255, width=12, joint="curve")

    def extras(f):
        detalle(f, base, "#7d8f86", alto=3)
        detalle(f, filamento, OLIVA, alto=-2)
    componer(obj, "obj_bombillo.png", extras=extras)


def manzana():
    m = lienzo_l()
    d = ImageDraw.Draw(m)
    d.ellipse((S * 0.14, S * 0.26, S * 0.56, S * 0.86), fill=255)
    d.ellipse((S * 0.44, S * 0.26, S * 0.86, S * 0.86), fill=255)
    hueco = lienzo_l()
    ImageDraw.Draw(hueco).ellipse((S * 0.43, S * 0.2, S * 0.57, S * 0.34), fill=255)
    m = ImageChops.subtract(m, hueco)
    obj = sombrear(m, "#9fd94a", inflado=60)

    def tallo(dd):
        dd.line((S * 0.5, S * 0.32, S * 0.53, S * 0.14), fill=255, width=26)

    def extras(f):
        detalle(f, tallo, "#7a4e2a", alto=3)
        h = Image.open(os.path.join(REC, "obj_hoja_menta.png")).resize((S // 4, S // 4))
        f.alpha_composite(h.rotate(-30, expand=False), (int(S * 0.52), int(S * 0.06)))
    componer(obj, "obj_manzana.png", extras=extras)


def gota(nombre="obj_gota.png", color="#9fd8f5"):
    pts = []
    for i in range(300):
        t = i / 300 * 2 * math.pi
        x = math.sin(t) * (1 - math.cos(t)) * 0.5
        y = -math.cos(t)
        pts.append((S / 2 + x * S * 0.36, S * 0.5 + y * S * 0.38))
    componer(sombrear(poligono(pts), color, inflado=45), nombre)


def equis():
    m = lienzo_l()
    d = ImageDraw.Draw(m)
    d.line((S * 0.26, S * 0.26, S * 0.74, S * 0.74), fill=255, width=int(S * 0.17))
    d.line((S * 0.74, S * 0.26, S * 0.26, S * 0.74), fill=255, width=int(S * 0.17))
    m = m.filter(ImageFilter.GaussianBlur(16)).point(lambda v: 255 if v > 128 else 0)
    componer(sombrear(m, "#F2A08C", inflado=40), "obj_equis.png")


def cara(nombre, color, rasgos):
    """Carita 3D: círculo inflado y rasgos en relieve oscuro."""
    m = lienzo_l()
    ImageDraw.Draw(m).ellipse((S * 0.12, S * 0.12, S * 0.88, S * 0.88), fill=255)
    obj = sombrear(m, color, inflado=60)

    def extras(f):
        rasgos(f)
    componer(obj, nombre, extras=extras)


def ojos_abiertos(dd, y=0.42):
    dd.ellipse((S * 0.33, S * (y - 0.06), S * 0.43, S * (y + 0.07)), fill=255)
    dd.ellipse((S * 0.57, S * (y - 0.06), S * 0.67, S * (y + 0.07)), fill=255)


def caras():
    def bien(f):
        detalle(f, ojos_abiertos, OSCURO, alto=-3)
        detalle(f, lambda dd: dd.arc((S * 0.3, S * 0.36, S * 0.7, S * 0.7), 20, 160, fill=255, width=30), OSCURO, alto=-3)
        detalle(f, lambda dd: [dd.ellipse((S * 0.2, S * 0.52, S * 0.3, S * 0.6), fill=255), dd.ellipse((S * 0.7, S * 0.52, S * 0.8, S * 0.6), fill=255)], "#F5B6A0", alto=0)
    cara("cara_bien.png", LIMA, bien)

    def nervioso(f):
        detalle(f, ojos_abiertos, OSCURO, alto=-3)
        detalle(f, lambda dd: dd.line([(S * (0.34 + k * 0.04), S * (0.64 + (0.03 if k % 2 else -0.03))) for k in range(9)], fill=255, width=22, joint="curve"), OSCURO, alto=-3)
        gota_mask = lambda dd: dd.polygon([(S * 0.78, S * 0.18), (S * 0.72, S * 0.32), (S * 0.84, S * 0.32)], fill=255) or dd.ellipse((S * 0.715, S * 0.27, S * 0.845, S * 0.38), fill=255)
        detalle(f, gota_mask, "#9fd8f5", alto=3)
    cara("cara_nervioso.png", MENTA, nervioso)

    def enojado(f):
        detalle(f, lambda dd: ojos_abiertos(dd, 0.46), OSCURO, alto=-3)
        detalle(f, lambda dd: [dd.line((S * 0.3, S * 0.3, S * 0.45, S * 0.37), fill=255, width=26), dd.line((S * 0.7, S * 0.3, S * 0.55, S * 0.37), fill=255, width=26)], OSCURO, alto=-3)
        detalle(f, lambda dd: dd.arc((S * 0.34, S * 0.62, S * 0.66, S * 0.86), 200, 340, fill=255, width=28), OSCURO, alto=-3)
    cara("cara_enojado.png", "#F4A88E", enojado)

    def triste(f):
        detalle(f, ojos_abiertos, OSCURO, alto=-3)
        detalle(f, lambda dd: dd.arc((S * 0.33, S * 0.6, S * 0.67, S * 0.86), 205, 335, fill=255, width=28), OSCURO, alto=-3)
        detalle(f, lambda dd: dd.ellipse((S * 0.62, S * 0.5, S * 0.7, S * 0.62), fill=255), "#9fd8f5", alto=2)
    cara("cara_triste.png", "#A9D8F2", triste)

    def cansado(f):
        detalle(f, lambda dd: [dd.arc((S * 0.31, S * 0.36, S * 0.45, S * 0.5), 10, 170, fill=255, width=20), dd.arc((S * 0.55, S * 0.36, S * 0.69, S * 0.5), 10, 170, fill=255, width=20)], OSCURO, alto=-3)
        detalle(f, lambda dd: dd.ellipse((S * 0.45, S * 0.6, S * 0.55, S * 0.72), fill=255), OSCURO, alto=-3)
        try:
            fuente = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", int(S * 0.14))
        except OSError:
            fuente = ImageFont.load_default()
        detalle(f, lambda dd: dd.text((S * 0.72, S * 0.2), "z", font=fuente, fill=255, anchor="mm"), BLANCO, alto=3)
    cara("cara_cansado.png", "#CDBDF2", cansado)


def exportar_web():
    """Copia los objetos a la página web en tamaño liviano (WebP)."""
    destino = os.path.join(os.path.dirname(AQUI), "static", "img", "3d")
    os.makedirs(destino, exist_ok=True)
    for f in sorted(os.listdir(REC)):
        if f.startswith(("obj_", "cara_", "esfera_")) and f.endswith(".png"):
            im = Image.open(os.path.join(REC, f)).resize((240, 240), Image.LANCZOS)
            im.save(os.path.join(destino, f[:-4] + ".webp"), "WEBP", quality=88, method=6)


if __name__ == "__main__":
    import sys
    if "--solo-nuevos" in sys.argv:
        luna(); libro(); telefono(); taza(); bombillo(); manzana(); gota(); equis(); caras()
        exportar_web()
        print("nuevos listos")
        raise SystemExit
    corazon()
    burbuja()
    hoja("obj_hoja_menta.png", MENTA, 35)
    hoja("obj_hoja_lima.png", LIMA, -25)
    hoja("obj_hoja_oscura.png", "#3f8a3a", 60)
    escudo()
    estrella()
    engranaje()
    candado()
    rayo()
    nube()
    moneda()
    reloj()
    print("objetos listos")
