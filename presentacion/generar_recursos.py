"""Genera los fondos y los elementos 3D de la presentación (paleta Green Screen).
Paleta: F4FFFC, 91EAAF, C3E956, 4D7111, 1F4B2C."""
import math
import os
import random
import shutil
import sys

from PIL import Image, ImageDraw, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(AQUI, "recursos")
os.makedirs(REC, exist_ok=True)
W, H = 1920, 1080
random.seed(7)

def hexa(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)

BLANCO, MENTA, LIMA, OLIVA, OSCURO = "#F4FFFC", "#91EAAF", "#C3E956", "#4D7111", "#1F4B2C"


def mancha(lienzo, cx, cy, r, color, alfa, desenfoque):
    capa = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=hexa(color, alfa))
    capa = capa.filter(ImageFilter.GaussianBlur(desenfoque))
    lienzo.alpha_composite(capa)


def cuadricula(lienzo, alfa=18, paso=90):
    """Rombos finos como en la imagen de la paleta."""
    capa = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for k in range(-H, W + H, paso):
        d.line((k, 0, k + H, H), fill=hexa(BLANCO, alfa), width=1)
        d.line((k, H, k + H, 0), fill=hexa(BLANCO, alfa), width=1)
    lienzo.alpha_composite(capa)


def vineta(lienzo, fuerza=150):
    capa = Image.new("L", lienzo.size, 0)
    d = ImageDraw.Draw(capa)
    for i in range(40):
        t = i / 40
        d.rectangle((int(W * t * 0.18), int(H * t * 0.18), W - int(W * t * 0.18), H - int(H * t * 0.18)),
                    fill=int(fuerza * (1 - t)))
    capa = capa.filter(ImageFilter.GaussianBlur(120))
    negro = Image.new("RGBA", lienzo.size, (8, 24, 14, 255))
    negro.putalpha(capa)
    lienzo.alpha_composite(negro)


def bokeh(lienzo, n, colores, rmin, rmax, alfa, desenfoque):
    for _ in range(n):
        mancha(lienzo, random.randint(0, W), random.randint(0, H), random.randint(rmin, rmax),
               random.choice(colores), alfa, desenfoque)


def fondo_principal(nombre, variante=0):
    lienzo = Image.new("RGBA", (W, H), hexa(OSCURO))
    # Luces grandes, como la imagen de la paleta.
    mancha(lienzo, 260 + variante * 120, 520, 520, "#5f9a2e", 200, 220)
    mancha(lienzo, 1700 - variante * 90, 300, 480, "#7cc36a", 150, 240)
    mancha(lienzo, 980, 1150, 600, OLIVA, 210, 200)
    mancha(lienzo, 120, 80, 280, MENTA, 70, 160)
    mancha(lienzo, 1820, 980, 300, LIMA, 60, 170)
    bokeh(lienzo, 26, [LIMA, MENTA, BLANCO], 6, 26, 90, 4)
    bokeh(lienzo, 10, [LIMA, MENTA], 40, 90, 40, 18)
    cuadricula(lienzo)
    vineta(lienzo, 120)
    lienzo.convert("RGB").save(os.path.join(REC, nombre), quality=92)


def fondo_brillante(nombre):
    """Para diapositivas de una sola idea: verde lima luminoso."""
    lienzo = Image.new("RGBA", (W, H), hexa("#d4ef7a"))
    mancha(lienzo, 420, 360, 760, BLANCO, 200, 280)
    mancha(lienzo, 1500, 260, 520, LIMA, 230, 240)
    mancha(lienzo, 1650, 950, 520, MENTA, 200, 240)
    mancha(lienzo, 250, 1000, 420, "#b5e36b", 200, 220)
    bokeh(lienzo, 22, [BLANCO, MENTA], 6, 22, 130, 4)
    cuadricula(lienzo, 18)
    vineta(lienzo, 35)
    lienzo.convert("RGB").save(os.path.join(REC, nombre), quality=92)


def fondo_foto(nombre, foto, lado="izquierda"):
    """Foto del liceo con un velo verde para que el texto se lea."""
    im = Image.open(foto).convert("RGB")
    proporcion = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * proporcion), int(im.height * proporcion)), Image.LANCZOS)
    x = (im.width - W) // 2
    y = (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H)).convert("RGBA")
    velo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(velo)
    for i in range(W):
        t = i / W if lado == "derecha" else 1 - i / W
        a = int(40 + 215 * (t ** 1.4))
        d.line((i, 0, i, H), fill=hexa(OSCURO, min(a, 245)))
    im.alpha_composite(velo)
    abajo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(abajo)
    for j in range(H):
        a = int(170 * max(0, (j - H * 0.55) / (H * 0.45)) ** 1.5)
        d.line((0, j, W, j), fill=hexa(OSCURO, a))
    im.alpha_composite(abajo)
    bokeh(im, 14, [LIMA, MENTA], 6, 20, 80, 4)
    im.convert("RGB").save(os.path.join(REC, nombre), quality=92)


def esfera(nombre, color, tam=520):
    """Esfera brillante 3D: degradado radial, brillo y sombra de contacto."""
    s = tam * 2
    lienzo = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    base = hexa(color)
    cx, cy, r = s // 2, int(s * 0.46), int(s * 0.36)
    # Sombra en el piso.
    sombra = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse((cx - r * 0.9, cy + r * 0.92, cx + r * 0.9, cy + r * 1.18), fill=(5, 20, 10, 140))
    lienzo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(s * 0.03)))
    # Cuerpo: muchas capas de círculos, de oscuro (borde) a claro (centro-arriba).
    cuerpo = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(cuerpo)
    pasos = 90
    for i in range(pasos):
        t = i / (pasos - 1)
        rr = r * (1 - t * 0.92)
        ox, oy = cx - r * 0.28 * t, cy - r * 0.32 * t
        luz = 0.55 + 0.75 * t
        c = tuple(min(255, int(base[k] * luz + 255 * max(0, t - 0.75) * 1.2)) for k in range(3)) + (255,)
        d.ellipse((ox - rr, oy - rr, ox + rr, oy + rr), fill=c)
    cuerpo = cuerpo.filter(ImageFilter.GaussianBlur(s * 0.006))
    mascara = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mascara).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    cuerpo.putalpha(Image.composite(cuerpo.getchannel("A"), Image.new("L", (s, s), 0), mascara))
    lienzo.alpha_composite(cuerpo)
    # Borde de luz (rebote) abajo a la derecha.
    rebote = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(rebote).arc((cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6), 10, 100, fill=hexa(BLANCO, 120), width=int(s * 0.012))
    lienzo.alpha_composite(rebote.filter(ImageFilter.GaussianBlur(s * 0.006)))
    # Brillo especular.
    brillo = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(brillo).ellipse((cx - r * 0.55, cy - r * 0.72, cx - r * 0.12, cy - r * 0.42), fill=(255, 255, 255, 210))
    lienzo.alpha_composite(brillo.filter(ImageFilter.GaussianBlur(s * 0.018)))
    lienzo = lienzo.resize((tam, tam), Image.LANCZOS)
    lienzo.save(os.path.join(REC, nombre))


def capsula(nombre, c1, c2, tam=520):
    """Cápsula 3D de dos colores (como una píldora de bienestar)."""
    s = tam * 2
    lienzo = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    largo, ancho = s * 0.7, s * 0.26
    cuerpo = Image.new("RGBA", (int(largo), int(ancho)), (0, 0, 0, 0))
    d = ImageDraw.Draw(cuerpo)
    for i in range(60):
        t = i / 59
        inset = ancho * 0.5 * t * 0.85
        for mitad, col in ((0, c1), (1, c2)):
            base = hexa(col)
            luz = 0.6 + 0.6 * t
            c = tuple(min(255, int(base[k] * luz + 255 * max(0, t - 0.8) * 1.5)) for k in range(3)) + (255,)
            x0 = inset if mitad == 0 else largo / 2
            x1 = largo / 2 if mitad == 0 else largo - inset
            d.rounded_rectangle((x0, inset * 0.9, x1, ancho - inset * 1.1), radius=max(1, (ancho - 2 * inset) / 2), fill=c)
    # Unión de las dos mitades y brillo.
    d.line((largo / 2, ancho * 0.12, largo / 2, ancho * 0.88), fill=hexa(OSCURO, 45), width=3)
    d.rounded_rectangle((ancho * 0.35, ancho * 0.16, largo - ancho * 0.35, ancho * 0.3), radius=ancho * 0.08, fill=(255, 255, 255, 170))
    cuerpo = cuerpo.filter(ImageFilter.GaussianBlur(2))
    m = Image.new("L", cuerpo.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, largo - 1, ancho - 1), radius=ancho / 2, fill=255)
    cuerpo.putalpha(m)
    cuerpo = cuerpo.rotate(28, expand=True, resample=Image.BICUBIC)
    sombra = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse((s * 0.22, s * 0.72, s * 0.8, s * 0.82), fill=(5, 20, 10, 130))
    lienzo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(s * 0.03)))
    lienzo.alpha_composite(cuerpo, ((s - cuerpo.width) // 2, (s - cuerpo.height) // 2 - int(s * 0.04)))
    lienzo.resize((tam, tam), Image.LANCZOS).save(os.path.join(REC, nombre))


def anillo(nombre, color, tam=520):
    """Aro 3D (dona) con brillo, para decorar."""
    s = tam * 2
    lienzo = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    cx, cy = s // 2, s // 2
    R, grosor = s * 0.34, s * 0.11
    base = hexa(color)
    for i in range(50):
        t = i / 49
        g = grosor * (1 - t * 0.8)
        luz = 0.55 + 0.7 * t
        c = tuple(min(255, int(base[k] * luz + 255 * max(0, t - 0.8) * 1.4)) for k in range(3)) + (255,)
        capa = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        ImageDraw.Draw(capa).ellipse((cx - R - g / 2 - t * 6, cy - R * 0.42 - g / 2 - t * 10, cx + R + g / 2 - t * 6, cy + R * 0.42 + g / 2 - t * 10),
                                     outline=c, width=int(max(2, g)))
        lienzo.alpha_composite(capa)
    lienzo = lienzo.filter(ImageFilter.GaussianBlur(3)).rotate(-18, resample=Image.BICUBIC)
    lienzo.resize((tam, tam), Image.LANCZOS).save(os.path.join(REC, nombre))


if __name__ == "__main__":
    fotos = sys.argv[1]
    fondo_principal("fondo_1.jpg", 0)
    fondo_principal("fondo_2.jpg", 1)
    fondo_principal("fondo_3.jpg", 2)
    fondo_brillante("fondo_brillante.jpg")
    fondo_foto("fondo_liceo.jpg", os.path.join(fotos, "36.jpg"), "izquierda")
    fondo_foto("fondo_liceo_der.jpg", os.path.join(fotos, "36.jpg"), "derecha")
    esfera("esfera_lima.png", LIMA)
    esfera("esfera_menta.png", MENTA)
    esfera("esfera_blanca.png", "#E6F7EE")
    esfera("esfera_oliva.png", "#6f9a1f")
    capsula("capsula.png", LIMA, BLANCO)
    anillo("anillo_menta.png", MENTA)
    anillo("anillo_lima.png", LIMA)
    # Imágenes del liceo que mandó la usuaria.
    copias = {"30.png": "tigrito_psicologo.png", "31.png": "escudo_liceo.png", "33.png": "tigres_bravios.png",
              "34.jpg": "tigrito_uniforme.jpg", "36.jpg": "liceo.jpg", "37.png": "informatica.png"}
    for o, dst in copias.items():
        shutil.copy(os.path.join(fotos, o), os.path.join(REC, dst))
    print("listo")
