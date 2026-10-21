"""Versión 3 de la presentación "No estamos solos LMH": diseño editorial.

Dirección: minimalismo editorial, geometría orgánica (grandes círculos que salen
del encuadre, anillos y patrones de puntos), verde salvia y crema, y el avatar de
la estudiante acompañando la historia:
  - avatar_practica.png: diapositivas de la práctica profesional.
  - avatar_liceo.png: el resto.
Títulos en Sora y textos en Manrope. Una idea por diapositiva.

Cada forma lleva un nombre ("fx-...") que animar_v3.ps1 usa para darle su
animación en PowerPoint.

Uso:  python crear_presentacion_v3.py  ->  No_estamos_solos_LMH_v3.pptx
"""
import os

from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt
from lxml import etree

AQUI = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(AQUI, "recursos")
SALIDA = os.path.join(AQUI, "No_estamos_solos_LMH_v3.pptx")

OLIVA, BOSQUE, PROFUNDO, SALVIA, PALIDO = "596A4D", "354735", "263729", "A5B394", "D9DFC7"
CREMA, BLANCO, BEIGE, ARENA, GRIS = "F8F5E8", "FFFDF6", "E8DCC0", "D1B99B", "73796A"
TITULO, CUERPO = "Sora", "Manrope"
W, H = 13.333, 7.5

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
VACIA = prs.slide_layouts[6]
n_diapo = [0]


def rgb(h):
    return RGBColor.from_string(h)


def rec(nombre):
    return os.path.join(REC, nombre)


def alfa(forma, valor):
    clr = forma.fill._xPr.find(qn("a:solidFill"))[0]
    etree.SubElement(clr, qn("a:alpha")).set("val", str(int(valor * 1000)))


def sombra_suave(forma, blur=18, dist=6, opacidad=22):
    spPr = forma._element.spPr
    ef = etree.SubElement(spPr, qn("a:effectLst"))
    s = etree.SubElement(ef, qn("a:outerShdw"), blurRad=str(Pt(blur)), dist=str(Pt(dist)), dir="5400000", algn="t", rotWithShape="0")
    c = etree.SubElement(s, qn("a:srgbClr"), val="263729")
    etree.SubElement(c, qn("a:alpha"), val=str(opacidad * 1000))


# ---------------------------------------------------------------------------
# Piezas del sistema
# ---------------------------------------------------------------------------
def nueva(fondo=CREMA):
    s = prs.slides.add_slide(VACIA)
    n_diapo[0] += 1
    f = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    f.fill.solid()
    f.fill.fore_color.rgb = rgb(fondo)
    f.line.fill.background()
    f.name = "fondo"
    s._oscuro = fondo in (OLIVA, BOSQUE, PROFUNDO)
    return s


def circulo(s, x, y, d, color, transp=100, nombre="fx-circulo"):
    """Círculo relleno; x, y es la esquina superior izquierda (puede salir del encuadre)."""
    c = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    c.fill.solid()
    c.fill.fore_color.rgb = rgb(color)
    if transp < 100:
        alfa(c, transp)
    c.line.fill.background()
    c.name = nombre
    return c


def anillo(s, x, y, d, color, ancho=1.25, nombre="fx-deco"):
    c = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    c.fill.background()
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(ancho)
    c.name = nombre
    return c


def puntos(s, x, y, cols, filas, color, paso=0.24, tam=0.065):
    for i in range(filas):
        for j in range(cols):
            p = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + j * paso), Inches(y + i * paso), Inches(tam), Inches(tam))
            p.fill.solid()
            p.fill.fore_color.rgb = rgb(color)
            p.line.fill.background()
            p.name = "fx-deco"


def linea(s, x1, y1, x2, y2, color, ancho=1.0, nombre="fx-linea"):
    l = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    l.line.color.rgb = rgb(color)
    l.line.width = Pt(ancho)
    l.name = nombre
    return l


def bloque(s, x, y, w, h, color, radio=0.06, nombre="fx-circulo"):
    b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    b.adjustments[0] = radio
    b.fill.solid()
    b.fill.fore_color.rgb = rgb(color)
    b.line.fill.background()
    b.name = nombre
    return b


def texto(s, x, y, w, h, contenido, tam=18, color=BOSQUE, fuente=CUERPO, negrita=False, alinear=PP_ALIGN.LEFT,
          interlineado=1.18, anclar=MSO_ANCHOR.TOP, nombre="fx-texto", cursiva=False, despues=0):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = nombre
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = anclar
    parrafos = contenido if isinstance(contenido, list) else [contenido]
    for i, p in enumerate(parrafos):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.alignment = alinear
        par.line_spacing = interlineado
        if despues:
            par.space_after = Pt(despues)
        trozos = p if isinstance(p, list) else [(p, {})]
        for t, op in trozos:
            r = par.add_run()
            r.text = t
            f = r.font
            f.name = op.get("fuente", fuente)
            f.size = Pt(op.get("tam", tam))
            f.bold = op.get("negrita", negrita)
            f.italic = op.get("cursiva", cursiva)
            f.color.rgb = rgb(op.get("color", color))
    return tb


def titulo(s, x, y, w, h, t, tam=36, color=None):
    return texto(s, x, y, w, h, t, tam=tam, color=color or (CREMA if s._oscuro else PROFUNDO), fuente=TITULO,
                 negrita=True, interlineado=1.02, nombre="fx-titulo")


def etiqueta(s, x, y, t, color=None):
    """Etiqueta corta en minúsculas con una raya delante: dice en qué parte estamos."""
    color = color or (SALVIA if s._oscuro else OLIVA)
    linea(s, x, y + 0.17, x + 0.38, y + 0.17, color, 1.5, nombre="fx-deco")
    texto(s, x + 0.5, y, 6, 0.36, t, tam=14, color=color, negrita=True, nombre="fx-deco")


def imagen(s, archivo, x, y, w=None, h=None, nombre="fx-foto"):
    p = s.shapes.add_picture(rec(archivo), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    p.name = nombre
    return p


def avatar(s, archivo, x, alto, lado="der", y=None, nombre=None):
    """El avatar sube desde el borde inferior (su corte del pecho queda en el borde)."""
    ancho_px, alto_px = Image.open(rec(archivo)).size
    w = alto * ancho_px / alto_px
    y = H - alto if y is None else y
    return imagen(s, archivo, x, y, w=w, h=alto, nombre=nombre or f"fx-avatar-{lado}")


def pie(s, t="", x=0.9):
    color = SALVIA if s._oscuro else GRIS
    base = f"No estamos solos LMH  ·  {n_diapo[0]:02d}"
    texto(s, x, 7.0, 12.4 - x, 0.3, (t + "  ·  " + base) if t else base, tam=10, color=color, nombre="fondo-pie")


def notas(s, t):
    s.notes_slide.notes_text_frame.text = t


def foto_circular(origen, destino, modo="contener", fondo=(255, 253, 246)):
    """Guarda la foto de un producto recortada en círculo (con transparencia afuera)."""
    lado = 700
    im = Image.open(rec(origen)).convert("RGBA")
    base = Image.new("RGBA", (lado, lado), fondo + (255,))
    if modo == "cubrir":
        esc = max(lado / im.width, lado / im.height)
        im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
        base.paste(im, ((lado - im.width) // 2, (lado - im.height) // 2), im)
    else:
        esc = min(lado * 0.72 / im.width, lado * 0.72 / im.height)
        im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
        base.paste(im, ((lado - im.width) // 2, (lado - im.height) // 2), im)
    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).ellipse((0, 0, lado - 1, lado - 1), fill=255)
    base.putalpha(mascara)
    base.save(rec(destino))


foto_circular("cot_tab_a11_elektra.png", "c_tablet.png")
foto_circular("cot_samsung_a17.png", "c_celular.png")
foto_circular("cot_dell_5420.png", "c_laptop.png", modo="cubrir")

AV_LICEO, AV_PRACTICA = "avatar_liceo.png", "avatar_practica.png"

# ===========================================================================
# 1. Portada
# ===========================================================================
s = nueva(CREMA)
circulo(s, 7.55, -1.35, 7.6, OLIVA)
circulo(s, 6.55, 5.55, 1.5, BEIGE, nombre="fx-deco")
anillo(s, 11.75, 5.35, 2.2, SALVIA)
puntos(s, 0.9, 6.35, 9, 2, SALVIA)
avatar(s, AV_LICEO, 7.95, 5.7)
imagen(s, "escudo_liceo.png", 0.9, 0.7, h=0.62, nombre="fx-deco")
texto(s, 1.65, 0.78, 6, 0.5, "Liceo Militar de Honduras · Proyecto tecnológico 2026", tam=13, color=OLIVA, negrita=True, nombre="fx-deco")
titulo(s, 0.9, 1.75, 6.9, 2.6, ["No estamos", "solos LMH"], tam=66)
texto(s, 0.92, 4.35, 5.9, 1.0, "Plataforma web anónima de apoyo emocional para los estudiantes del liceo.", tam=20)
texto(s, 0.92, 5.5, 6, 0.4, "Presenta: Padilla Garay  ·  Asesor(a): [nombre]", tam=13, color=GRIS)
notas(s, "Saludo al tribunal y presentación del proyecto.")

# ===========================================================================
# 2. Dedicatoria
# ===========================================================================
s = nueva(PROFUNDO)
anillo(s, -1.6, 4.0, 5.2, SALVIA, 1.0)
circulo(s, 11.0, -1.1, 3.1, OLIVA)
etiqueta(s, 0.9, 1.0, "Dedicatoria")
texto(s, 0.9, 2.0, 9.6, 3.2, "[Escribe aquí tu dedicatoria, con tus palabras, en dos o tres oraciones.]",
      tam=30, color=CREMA, fuente=TITULO, interlineado=1.15, nombre="fx-titulo")
pie(s)
notas(s, "Dedicatoria: la escribe la estudiante.")

# ===========================================================================
# 3. Agradecimientos
# ===========================================================================
s = nueva(CREMA)
circulo(s, 0.35, 2.85, 4.6, PALIDO)
avatar(s, AV_LICEO, 0.55, 4.3, lado="izq")
etiqueta(s, 5.6, 0.95, "Agradecimientos")
titulo(s, 5.6, 1.45, 7.0, 1.2, "Gracias a quienes me acompañaron", tam=32)
items = ["[Al Liceo Militar de Honduras y al área de Informática]", "[A la psicóloga del liceo]", "[A mi asesor(a)]",
         "[A SULA, Bodega 6]", "[A mi familia]"]
for i, t in enumerate(items):
    y = 3.05 + i * 0.62
    circulo(s, 5.62, y + 0.12, 0.13, ARENA, nombre="fx-deco")
    texto(s, 5.95, y, 6.5, 0.45, t, tam=17)
pie(s, x=5.6)
notas(s, "Agradecimientos: la estudiante ajusta los nombres.")

# ===========================================================================
# 4. Introducción
# ===========================================================================
s = nueva(CREMA)
circulo(s, 8.15, 1.25, 8.2, SALVIA, transp=45)
avatar(s, AV_LICEO, 8.7, 4.7)
puntos(s, 0.9, 6.45, 6, 2, ARENA)
etiqueta(s, 0.9, 0.95, "Introducción")
titulo(s, 0.9, 1.45, 7.0, 1.8, "Pedir ayuda no debería dar miedo", tam=40)
texto(s, 0.92, 3.5, 6.6, 2.4, "Muchos estudiantes cargan estrés, ansiedad o bullying en silencio. No estamos solos LMH es un espacio anónimo para hablar, aprender y cuidarse, conectado con la psicóloga del liceo.",
      tam=19, interlineado=1.3)
notas(s, "Presentar el tema en un minuto: el problema y la respuesta.")

# ===========================================================================
# 5. Objetivo general
# ===========================================================================
s = nueva(BOSQUE)
circulo(s, -2.6, 3.6, 6.2, OLIVA)
anillo(s, 11.55, 0.6, 1.3, BEIGE)
etiqueta(s, 0.9, 1.0, "Objetivo general")
texto(s, 0.9, 1.75, 10.6, 3.6, "Desarrollar una plataforma web anónima que permita a los estudiantes del liceo pedir apoyo emocional a cualquier hora, y que avise a la psicóloga cuando haya riesgo.",
      tam=32, color=CREMA, fuente=TITULO, negrita=True, interlineado=1.12, nombre="fx-titulo")
pie(s)
notas(s, "El objetivo general en una oración.")

# ===========================================================================
# 6. Objetivos específicos
# ===========================================================================
s = nueva(CREMA)
circulo(s, 9.35, 1.55, 4.6, PALIDO)
texto(s, 9.35, 2.55, 4.6, 2.4, "05", tam=120, color=OLIVA, fuente=TITULO, negrita=True, alinear=PP_ALIGN.CENTER, nombre="fx-deco")
etiqueta(s, 0.9, 0.85, "Objetivos específicos")
titulo(s, 0.9, 1.3, 8, 0.8, "Lo que se propuso lograr", tam=32)
objetivos = ["Crear un chat anónimo y en tiempo real con la psicóloga.", "Ofrecer asistentes con IA, por chat y por voz.",
             "Detectar señales de riesgo y alertar al instante.", "Reunir artículos, ejercicios y autoevaluaciones.",
             "Dar a la psicóloga un panel para actualizar el contenido."]
for i, t in enumerate(objetivos):
    y = 2.45 + i * 0.86
    texto(s, 0.9, y, 0.8, 0.6, f"{i + 1}", tam=22, color=OLIVA, fuente=TITULO, negrita=True)
    texto(s, 1.55, y + 0.04, 7.2, 0.6, t, tam=18)
    if i < 4:
        linea(s, 0.9, y + 0.73, 8.6, y + 0.73, PALIDO, 0.75)
pie(s)
notas(s, "Cinco objetivos específicos; cada uno se cumple con una parte de la plataforma.")

# ===========================================================================
# 7. Justificación
# ===========================================================================
s = nueva(CREMA)
puntos(s, 0.9, 6.3, 7, 2, SALVIA)
etiqueta(s, 0.9, 0.85, "Justificación")
texto(s, 0.85, 1.35, 6.5, 2.4, "15 %", tam=130, color=OLIVA, fuente=TITULO, negrita=True, nombre="fx-titulo")
texto(s, 0.92, 3.95, 6.0, 1.6, "de los adolescentes de 10 a 19 años de América Latina y el Caribe vive con un trastorno mental diagnosticado.",
      tam=19, interlineado=1.28)
texto(s, 0.92, 5.55, 5, 0.4, "Fuente: UNICEF", tam=12, color=GRIS)
bloque(s, 7.9, 0.9, 4.55, 5.75, BOSQUE, radio=0.05)
circulo(s, 10.95, 4.9, 2.2, OLIVA, nombre="fx-deco")
texto(s, 8.35, 1.45, 3.7, 0.4, "Por eso", tam=14, color=SALVIA, negrita=True)
texto(s, 8.35, 1.95, 3.75, 3.2, "Un canal anónimo y siempre disponible acerca la ayuda antes de que sea tarde.",
      tam=24, color=CREMA, fuente=TITULO, negrita=True, interlineado=1.12)
pie(s)
notas(s, "El dato de UNICEF da el contexto regional; el anonimato y la disponibilidad son la respuesta.")

# ===========================================================================
# 8. Práctica profesional 1: Mi práctica profesional
# ===========================================================================
s = nueva(OLIVA)
circulo(s, 6.4, -1.6, 9.3, CREMA, transp=12)
anillo(s, 5.2, 5.45, 0.9, BEIGE)
avatar(s, AV_PRACTICA, 7.15, 5.9, nombre="fx-avatar-der")
etiqueta(s, 0.9, 0.95, "Práctica profesional", color=BEIGE)
titulo(s, 0.9, 1.5, 6.4, 1.8, "Mi práctica profesional", tam=46, color=CREMA)
texto(s, 0.92, 3.45, 6.0, 2.3, "Realicé mi práctica en SULA, Bodega 6, como analista. Puse en práctica mis conocimientos, aprendí nuevos procedimientos y gané experiencia en el área laboral.",
      tam=19, color=CREMA, interlineado=1.3)
pie(s)
notas(s, "Contexto y diagnóstico. Presentar el lugar de la práctica: SULA, Bodega 6, como analista.")

# ===========================================================================
# 9. Práctica profesional 2: Actividades realizadas
# ===========================================================================
s = nueva(CREMA)
circulo(s, 9.55, 3.35, 4.2, PALIDO)
avatar(s, AV_PRACTICA, 9.6, 3.9)
etiqueta(s, 0.9, 0.85, "Práctica profesional")
titulo(s, 0.9, 1.3, 8, 0.8, "Actividades realizadas", tam=34)
actividades = ["Trazabilidad de productos y lotes de LEYDE", "Asignación de furgones y creación de reservas", "Control y traspaso de MIGOS",
               "Manejo de formatos y programación de LEYDE", "Cambios INLACSA y rótulos de exportación", "Realización de inventario"]
for k, t in enumerate(actividades):
    col, fila = divmod(k, 3)
    x, y = 0.9 + col * 4.25, 2.6 + fila * 1.05
    circulo(s, x, y + 0.11, 0.16, OLIVA, nombre="fx-deco")
    texto(s, x + 0.35, y, 3.75, 0.85, t, tam=17, interlineado=1.15)
linea(s, 0.9, 5.85, 8.9, 5.85, PALIDO, 0.75)
texto(s, 0.9, 6.0, 8.2, 0.5, "Fortalecí mis habilidades, mi responsabilidad y el trabajo en equipo.", tam=16, color=OLIVA, negrita=True)
pie(s)
notas(s, "Las actividades de la práctica en SULA, Bodega 6.")

# ===========================================================================
# 10. Práctica profesional 3: Una oportunidad para mi futuro
# ===========================================================================
s = nueva(PROFUNDO)
circulo(s, -0.9, 1.75, 6.4, OLIVA)
puntos(s, 11.2, 0.8, 5, 3, SALVIA)
avatar(s, AV_PRACTICA, 0.25, 5.5, lado="izq")
etiqueta(s, 6.4, 1.05, "Una oportunidad para mi futuro")
texto(s, 6.4, 1.6, 6.3, 2.4, "La gerente Julissa García me ofreció una oportunidad laboral: fui contratada para empezar a trabajar próximamente.",
      tam=26, color=CREMA, fuente=TITULO, negrita=True, interlineado=1.12, nombre="fx-titulo")
texto(s, 6.42, 4.25, 6.0, 1.8, "Inicio esta etapa con entusiasmo, responsabilidad y ganas de seguir aprendiendo. Con la ayuda de Dios, seguiré creciendo.",
      tam=18, color=PALIDO, interlineado=1.3)
pie(s, x=6.4)
notas(s, "Cierre de la práctica: el resultado fue una oportunidad laboral en SULA.")

# ===========================================================================
# 11. El problema
# ===========================================================================
s = nueva(CREMA)
circulo(s, 9.7, 3.9, 4.0, BEIGE)
avatar(s, AV_LICEO, 9.9, 3.5)
etiqueta(s, 0.9, 0.85, "El problema")
titulo(s, 0.9, 1.3, 9.0, 1.4, "Muchos estudiantes no piden ayuda a tiempo", tam=34)
linea(s, 0.9, 3.45, 9.2, 3.45, SALVIA, 1.25)
causas = [("Miedo a ser identificados", "Temen que se sepa en el liceo o en casa."),
          ("Una psicóloga, horario limitado", "Fuera de horario no hay a quién acudir."),
          ("Señales que llegan tarde", "Una crisis puede no llegar a quien ayuda.")]
for i, (t, c) in enumerate(causas):
    x = 0.9 + i * 2.95
    circulo(s, x, 3.3, 0.3, OLIVA, nombre="fx-deco")
    texto(s, x, 3.85, 2.7, 0.9, t, tam=17, color=PROFUNDO, fuente=TITULO, negrita=True, interlineado=1.05)
    texto(s, x, 4.8, 2.7, 1.0, c, tam=15, color=BOSQUE, interlineado=1.2)
pie(s)
notas(s, "Tres causas del problema, con ejemplos del liceo.")

# ===========================================================================
# 12. La necesidad
# ===========================================================================
s = nueva(OLIVA)
circulo(s, 9.4, 4.4, 6.2, PROFUNDO, transp=55)
anillo(s, 0.6, 0.55, 1.0, BEIGE)
etiqueta(s, 0.9, 1.6, "Necesidad tecnológica", color=BEIGE)
texto(s, 0.9, 2.15, 10.5, 2.8, "Un canal anónimo, disponible las 24 horas, que avise a la psicóloga a tiempo.",
      tam=40, color=CREMA, fuente=TITULO, negrita=True, interlineado=1.08, nombre="fx-titulo")
texto(s, 0.92, 5.0, 9, 0.5, "Anónimo  ·  Siempre disponible  ·  Alertas al instante", tam=17, color=PALIDO, negrita=True)
pie(s)
notas(s, "La necesidad en una frase. Los tres requisitos guían todo el diseño.")

# ===========================================================================
# 13. Referentes
# ===========================================================================
s = nueva(CREMA)
etiqueta(s, 0.9, 0.85, "Referentes")
titulo(s, 0.9, 1.3, 10, 0.8, "Aprendimos de Yana y Psonríe", tam=34)
columnas = [("Yana", "México, 2017", ["Chatbot las 24 horas", "Diario de ánimo", "Gratis, con suscripción"]),
            ("Psonríe", "España, 2016", ["Psicólogos por chat o video", "Atención sin cita", "Pago por sesión"]),
            ("No estamos solos LMH", "Liceo Militar de Honduras", ["Psicóloga del liceo e IA", "Alertas de riesgo", "Gratis para el estudiante"])]
for i, (t, sub, lineas_) in enumerate(columnas):
    x = 0.9 + i * 3.95
    if i == 2:
        bloque(s, x - 0.3, 2.35, 3.9, 4.25, BOSQUE, radio=0.05)
    clr_t, clr_c = (CREMA, PALIDO) if i == 2 else (PROFUNDO, BOSQUE)
    texto(s, x, 2.65, 3.4, 0.9, t, tam=22, color=clr_t, fuente=TITULO, negrita=True, interlineado=1.0)
    texto(s, x, 3.5, 3.4, 0.4, sub, tam=13, color=SALVIA if i == 2 else GRIS)
    texto(s, x, 4.15, 3.3, 2.3, lineas_, tam=16, color=clr_c, interlineado=1.25, despues=8)
    if i == 1:
        linea(s, x - 0.35, 2.6, x - 0.35, 6.3, PALIDO, 0.75, nombre="fx-deco")
pie(s, "Fuentes: prensa sobre Yana y ficha de Psonríe")
notas(s, "Tomamos lo mejor de cada referente y lo adaptamos al liceo.")

# ===========================================================================
# 14. La propuesta
# ===========================================================================
s = nueva(CREMA)
etiqueta(s, 0.9, 0.85, "La propuesta")
titulo(s, 0.9, 1.3, 5.6, 2.0, "Un lugar para hablar, aprender y cuidarse", tam=34)
texto(s, 0.92, 3.6, 5.2, 2.4, "Chat con la psicóloga y los asistentes, 66 artículos, 24 ejercicios con pasos, diario de ánimo y autoevaluaciones.",
      tam=18, interlineado=1.3)
for nombre_, color_, x, y in [("Hablar", OLIVA, 6.9, 1.0), ("Aprender", SALVIA, 9.3, 1.0), ("Cuidarse", ARENA, 8.1, 3.15)]:
    circulo(s, x, y, 3.3, color_, transp=88)
    texto(s, x, y + 1.3, 3.3, 0.7, nombre_, tam=24, color=CREMA if color_ == OLIVA else PROFUNDO, fuente=TITULO, negrita=True,
          alinear=PP_ALIGN.CENTER, nombre="fx-diagrama")
pie(s)
notas(s, "La propuesta en tres verbos: hablar, aprender y cuidarse.")

# ===========================================================================
# 15. Funcionalidades
# ===========================================================================
s = nueva(BOSQUE)
circulo(s, 9.9, -1.9, 5.6, OLIVA)
etiqueta(s, 0.9, 0.85, "Funcionalidades")
titulo(s, 0.9, 1.3, 8, 0.8, "Lo que hace la plataforma", tam=34)
funciones = ["Chat anónimo con la psicóloga", "Sami, Leo, Nia y el Tigre, con IA", "Detección de riesgo en 8 categorías",
             "Líneas 150 y 911 a un toque", "Herramientas, artículos y tests", "Panel de contenido para la psicóloga"]
for k, t in enumerate(funciones):
    col, fila = divmod(k, 3)
    x, y = 0.9 + col * 5.4, 2.75 + fila * 1.2
    circulo(s, x, y + 0.1, 0.2, SALVIA, nombre="fx-deco")
    texto(s, x + 0.45, y, 4.7, 0.6, t, tam=19, color=CREMA)
pie(s)
notas(s, "Seis funciones. Si un mensaje tiene riesgo, no lo responde la IA: llega a la psicóloga.")

# ===========================================================================
# 16. El Tigre que habla
# ===========================================================================
s = nueva(CREMA)
circulo(s, 0.6, 0.85, 5.9, SALVIA, transp=55)
imagen(s, "tigrito_psicologo.png", 1.55, 1.25, h=5.75)
puntos(s, 11.3, 6.1, 6, 2, ARENA)
etiqueta(s, 7.3, 1.1, "Lo nuevo · Tigrito")
titulo(s, 7.3, 1.6, 5.4, 1.6, "Habla con el Tigre", tam=40)
texto(s, 7.32, 3.15, 5.2, 2.6, "Le hablas y te responde con su voz. Sus ojos te siguen y reaccionan al escuchar, pensar y hablar. Si hay riesgo, avisa a la psicóloga.",
      tam=19, interlineado=1.3)
pie(s)
notas(s, "El Tigre LMH está en la portada y en /tigre. Lo dicho por voz pasa por el mismo filtro de riesgo.")

# ===========================================================================
# 17. IA en cadena
# ===========================================================================
s = nueva(CREMA)
etiqueta(s, 0.9, 0.85, "Lo nuevo · Inteligencia artificial")
titulo(s, 0.9, 1.3, 11, 1.4, "Ocho IAs en cadena: si una falla, responde la siguiente", tam=32)
servicios = ["Claude", "Groq", "Gemini", "Mistral", "OpenRouter", "NVIDIA", "Hugging Face", "B.AI"]
linea(s, 1.45, 3.95, 11.45, 3.95, SALVIA, 1.5)
for k, n in enumerate(servicios):
    x = 0.9 + k * 1.43
    circulo(s, x, 3.4, 1.1, OLIVA if k < 3 else (SALVIA if k < 6 else ARENA), nombre="fx-diagrama")
    texto(s, x, 3.68, 1.1, 0.5, str(k + 1), tam=18, color=CREMA if k < 3 else PROFUNDO, fuente=TITULO, negrita=True,
          alinear=PP_ALIGN.CENTER, nombre="fx-diagrama")
    texto(s, x - 0.2, 4.65, 1.5, 0.5, n, tam=13, color=BOSQUE, negrita=True, alinear=PP_ALIGN.CENTER, nombre="fx-diagrama")
bloque(s, 0.9, 5.6, 11.55, 0.85, BOSQUE, radio=0.2, nombre="fx-texto")
texto(s, 1.25, 5.68, 11, 0.7, "Ninguna crisis llega a la IA: el filtro de riesgo la envía antes a la psicóloga.", tam=17, color=CREMA,
      negrita=True, anclar=MSO_ANCHOR.MIDDLE)
pie(s, "Las claves se guardan en el servidor, nunca en el código")
notas(s, "Orden en que se prueban los servicios. Si ninguno responde, el asistente usa respuestas preparadas.")

# ===========================================================================
# 18. Voz y rediseño
# ===========================================================================
s = nueva(OLIVA)
circulo(s, -1.5, -1.8, 4.6, CREMA, transp=10)
anillo(s, 11.6, 5.5, 1.5, BEIGE)
etiqueta(s, 0.9, 0.85, "Lo nuevo", color=BEIGE)
titulo(s, 0.9, 1.3, 10, 0.8, "Más cómoda y más clara", tam=34, color=CREMA)
for i, (t, items_) in enumerate([("Voz", ["Dictar en vez de escribir", "Respuestas leídas en voz alta", "Modo voz en pantalla completa"]),
                                 ("Diseño", ["Portada por capítulos", "\"Necesito ayuda ahora\" siempre visible", "Bullying y acoso, temas nuevos"])]):
    x = 0.9 + i * 6.0
    texto(s, x, 2.6, 5, 0.6, t, tam=24, color=BEIGE, fuente=TITULO, negrita=True)
    texto(s, x, 3.35, 5.2, 2.6, items_, tam=18, color=CREMA, interlineado=1.25, despues=10)
linea(s, 6.55, 2.7, 6.55, 5.6, SALVIA, 0.75, nombre="fx-deco")
pie(s)
notas(s, "La voz usa Whisper (Groq) y el audio no se guarda. El rediseño busca que la ayuda se encuentre rápido.")

# ===========================================================================
# 19. Arquitectura
# ===========================================================================
s = nueva(CREMA)
etiqueta(s, 0.9, 0.85, "Arquitectura de la propuesta")
titulo(s, 0.9, 1.3, 10, 0.8, "Cliente, servidor y datos", tam=34)
nodos = [("Cliente", "Navegador y app instalable", OLIVA), ("Servidor", "Python, Flask y Socket.IO", BOSQUE), ("Datos", "SQLite, IA en cadena y voz", SALVIA)]
for i, (t, c, color_) in enumerate(nodos):
    x = 1.1 + i * 4.0
    circulo(s, x, 2.45, 2.6, color_, nombre="fx-diagrama")
    texto(s, x, 3.4, 2.6, 0.7, t, tam=22, color=CREMA if color_ != SALVIA else PROFUNDO, fuente=TITULO, negrita=True,
          alinear=PP_ALIGN.CENTER, nombre="fx-diagrama")
    texto(s, x - 0.3, 5.3, 3.2, 0.8, c, tam=16, alinear=PP_ALIGN.CENTER, nombre="fx-diagrama")
    if i < 2:
        linea(s, x + 2.7, 3.75, x + 3.9, 3.75, OLIVA, 1.75)
        texto(s, x + 2.6, 3.15, 1.4, 0.4, "HTTPS · WebSocket" if i == 0 else "Consultas", tam=10, color=GRIS, alinear=PP_ALIGN.CENTER,
              nombre="fx-diagrama")
pie(s, "Arquitectura cliente-servidor con tiempo real")
notas(s, "El navegador se conecta por HTTPS y WebSocket al servidor en Flask, que guarda en SQLite y consulta la IA en cadena.")

# ===========================================================================
# 20. Privacidad y base de datos
# ===========================================================================
s = nueva(PROFUNDO)
anillo(s, 8.7, 0.9, 5.4, SALVIA, 1.0)
circulo(s, 10.6, 2.8, 1.6, OLIVA)
etiqueta(s, 0.9, 0.95, "Base de datos")
texto(s, 0.9, 1.5, 8.0, 2.0, "Ningún nombre de estudiante se guarda.", tam=38, color=CREMA, fuente=TITULO, negrita=True,
      interlineado=1.05, nombre="fx-titulo")
texto(s, 0.92, 3.7, 7.5, 2.4, ["Cada conversación es un código anónimo.", "Las cuentas usan apodo y contraseña cifrada.",
                              "La base de datos nunca se sube a internet."], tam=19, color=PALIDO, interlineado=1.25, despues=12)
pie(s, "SQLite: sesiones, mensajes, ánimo, tests, muro y contenido")
notas(s, "Privacidad desde el diseño: ninguna tabla guarda nombres ni correos.")

# ===========================================================================
# 21. Flujo de un mensaje
# ===========================================================================
s = nueva(CREMA)
etiqueta(s, 0.9, 0.85, "Flujo de datos")
titulo(s, 0.9, 1.3, 10, 0.8, "Qué pasa con un mensaje", tam=34)
pasos = ["Escribe", "Se guarda anónimo", "Filtro de riesgo", "Respuesta al instante"]
linea(s, 1.35, 3.0, 10.4, 3.0, SALVIA, 1.5)
for i, t in enumerate(pasos):
    x = 0.9 + i * 3.0
    circulo(s, x, 2.55, 0.9, OLIVA, nombre="fx-diagrama")
    texto(s, x, 2.72, 0.9, 0.55, str(i + 1), tam=20, color=CREMA, fuente=TITULO, negrita=True, alinear=PP_ALIGN.CENTER, nombre="fx-diagrama")
    texto(s, x - 0.6, 3.6, 2.1, 0.6, t, tam=16, color=PROFUNDO, negrita=True, alinear=PP_ALIGN.CENTER, nombre="fx-diagrama")
bloque(s, 0.9, 4.65, 5.55, 1.55, PALIDO, radio=0.08, nombre="fx-diagrama")
texto(s, 1.2, 4.8, 5.0, 1.3, [[("Riesgo bajo", {"negrita": True, "color": OLIVA, "fuente": TITULO})], "Responde el asistente y sugiere un ejercicio."],
      tam=16, nombre="fx-diagrama", interlineado=1.25)
bloque(s, 6.85, 4.65, 5.6, 1.55, BOSQUE, radio=0.08, nombre="fx-diagrama")
texto(s, 7.15, 4.8, 5.1, 1.3, [[("Riesgo medio o alto", {"negrita": True, "color": BEIGE, "fuente": TITULO})], "Alerta a la psicóloga y botones del 150 y el 911."],
      tam=16, color=CREMA, nombre="fx-diagrama", interlineado=1.25)
pie(s, "Una crisis nunca la responde el asistente")
notas(s, "El recorrido de un mensaje y la bifurcación clave según el riesgo.")

# ===========================================================================
# 22. Stack tecnológico
# ===========================================================================
s = nueva(CREMA)
circulo(s, 0.3, 3.05, 4.4, BEIGE)
avatar(s, AV_LICEO, 0.45, 4.2, lado="izq")
etiqueta(s, 5.4, 0.85, "Stack tecnológico")
titulo(s, 5.4, 1.3, 7.2, 0.8, "Con qué está hecha", tam=34)
stack = [("Lenguajes", "Python, HTML, CSS y JavaScript"), ("Web y tiempo real", "Flask y Socket.IO"), ("Datos", "SQLite"),
         ("IA y voz", "8 servicios en cadena y Whisper"), ("Publicación", "Git, GitHub y Render")]
for i, (k, v) in enumerate(stack):
    y = 2.45 + i * 0.82
    texto(s, 5.4, y, 2.6, 0.5, k, tam=15, color=OLIVA, negrita=True)
    texto(s, 8.0, y, 4.5, 0.5, v, tam=17)
    if i < 4:
        linea(s, 5.4, y + 0.66, 12.4, y + 0.66, PALIDO, 0.75)
pie(s, "Software libre o gratuito; la IA usa planes gratis", x=5.4)
notas(s, "Las herramientas del proyecto, por capa.")

# ===========================================================================
# 23. Demostración
# ===========================================================================
s = nueva(OLIVA)
circulo(s, 10.4, -2.2, 5.0, PROFUNDO, transp=45)
etiqueta(s, 0.9, 0.85, "Demostración funcional", color=BEIGE)
titulo(s, 0.9, 1.3, 10, 0.8, "En vivo: 7 minutos", tam=34, color=CREMA)
demo = [("Portada y el Tigre", "1 min"), ("Herramientas", "1 min"), ("Chat y modo voz", "2 min"), ("Prueba de riesgo", "2 min"), ("Panel y app", "1 min")]
linea(s, 1.2, 3.55, 11.9, 3.55, BEIGE, 1.25)
for i, (t, m) in enumerate(demo):
    x = 0.9 + i * 2.35
    circulo(s, x + 0.12, 3.3, 0.5, CREMA, nombre="fx-diagrama")
    texto(s, x, 4.05, 2.2, 0.9, t, tam=17, color=CREMA, fuente=TITULO, negrita=True, interlineado=1.05, nombre="fx-diagrama")
    texto(s, x, 4.95, 2.0, 0.4, m, tam=14, color=BEIGE, nombre="fx-diagrama")
pie(s, "La prueba de riesgo se hace en un entorno de prueba")
notas(s, "Guion de la demostración. Tener abiertas dos ventanas: el panel de la psicóloga y el chat del estudiante.")

# ===========================================================================
# 24. Equipos recomendados
# ===========================================================================
s = nueva(CREMA)
etiqueta(s, 0.9, 0.85, "Presupuesto · Equipos")
titulo(s, 0.9, 1.3, 10, 0.8, "Tres equipos para el liceo", tam=34)
equipos = [("c_tablet.png", "Tablet Galaxy Tab A11", "Elektra", "L 4,499", "Estación para hablar con el Tigre."),
           ("c_celular.png", "Celular Samsung A17", "La Curacao", "L 5,997", "Alertas y WhatsApp de la psicóloga."),
           ("c_laptop.png", "Laptop Dell Latitude 5420", "Geek Store", "L 9,200", "Panel y servidor de respaldo.")]
for i, (foto, nombre_, tienda, precio, uso) in enumerate(equipos):
    x = 0.9 + i * 4.0
    circulo(s, x + 0.35, 2.3, 2.6, BEIGE, nombre="fx-deco")
    f = imagen(s, foto, x + 0.5, 2.45, w=2.3, h=2.3)
    sombra_suave(f)
    texto(s, x, 5.0, 3.6, 0.45, nombre_, tam=17, color=PROFUNDO, fuente=TITULO, negrita=True)
    texto(s, x, 5.45, 3.6, 0.45, [[(precio, {"negrita": True, "color": OLIVA, "tam": 20}), (f"   {tienda}", {"color": GRIS, "tam": 13})]])
    texto(s, x, 5.95, 3.5, 0.6, uso, tam=15)
pie(s, "Total en equipos: L 19,696 · precios de octubre 2026")
notas(s, "Los tres equipos recomendados de las cotizaciones. La lista completa está en la siguiente diapositiva.")

# ===========================================================================
# 25. Todas las cotizaciones
# ===========================================================================
s = nueva(CREMA)
etiqueta(s, 0.9, 0.85, "Cotizaciones")
titulo(s, 0.9, 1.3, 10, 0.8, "Lo que comparamos en cuatro tiendas", tam=30)
filas = [("Tablet", "Elektra", "Galaxy Tab A11 · 64 GB", "L 4,499", True), ("Tablet", "Jetstereo", "Galaxy Tab A11 · 64 GB", "L 4,795", False),
         ("Tablet", "Jetstereo", "Galaxy Tab S10 Lite · 128 GB", "L 9,495", False), ("Celular", "La Curacao", "Samsung Galaxy A17", "L 5,997", True),
         ("Celular", "La Curacao", "Xiaomi Redmi 17", "L 6,599", False), ("Celular", "Elektra", "Infinix Smart 20", "L 4,599", False),
         ("Laptop", "Geek Store", "Dell Latitude 5420 · i5", "L 9,200", True), ("Laptop", "Geek Store", "Galaxy Book Pro 2 360 · i5", "L 13,200", False),
         ("Laptop", "Geek Store", "Galaxy Book Pro 2 360 · i7", "L 16,400", False)]
xs = [0.9, 2.6, 4.7, 9.4]
for j, encabezado_ in enumerate(["Equipo", "Tienda", "Modelo", "Precio"]):
    texto(s, xs[j], 2.3, 3, 0.35, encabezado_, tam=13, color=OLIVA, negrita=True, nombre="fx-diagrama")
linea(s, 0.9, 2.68, 11.0, 2.68, OLIVA, 1.0)
for i, (tipo, tienda, modelo, precio, rec_) in enumerate(filas):
    y = 2.8 + i * 0.43
    color_ = PROFUNDO if rec_ else BOSQUE
    for j, v in enumerate([tipo, tienda, modelo, precio]):
        texto(s, xs[j], y, 4.5 if j == 2 else 2.0, 0.38, v, tam=14, color=color_, negrita=rec_ and j in (2, 3), nombre="fx-diagrama")
    if rec_:
        circulo(s, 10.75, y + 0.1, 0.18, OLIVA, nombre="fx-diagrama")
texto(s, 11.05, 2.3, 1.8, 0.35, "Elegido", tam=13, color=OLIVA, negrita=True, nombre="fx-diagrama")
pie(s, "Precios de las tiendas, octubre 2026; verificar antes de comprar")
notas(s, "Las nueve cotizaciones. En negrita, los equipos elegidos por precio y uso.")

# ===========================================================================
# 26. Hosting
# ===========================================================================
s = nueva(BOSQUE)
circulo(s, -1.8, 3.9, 5.2, OLIVA)
anillo(s, 11.5, 0.5, 1.4, BEIGE)
etiqueta(s, 0.9, 0.85, "Hosting · Render Starter")
texto(s, 0.85, 1.35, 7, 1.9, "US$7.25", tam=96, color=CREMA, fuente=TITULO, negrita=True, nombre="fx-titulo")
texto(s, 0.92, 3.2, 6, 0.5, "al mes, con disco de 1 GB para los datos", tam=19, color=PALIDO)
texto(s, 0.92, 3.85, 6, 0.5, "Primer año, con dominio: ≈ L 2,626", tam=17, color=BEIGE, negrita=True)
texto(s, 7.6, 1.6, 4.9, 0.45, "Incluye", tam=15, color=SALVIA, negrita=True)
texto(s, 7.6, 2.05, 4.9, 1.9, ["Siempre encendido", "Chat en vivo y HTTPS", "Copia de los datos cada día"], tam=17, color=CREMA, interlineado=1.25, despues=6)
texto(s, 7.6, 4.0, 4.9, 0.45, "Pago", tam=15, color=SALVIA, negrita=True)
texto(s, 7.6, 4.45, 4.9, 1.3, "Tarjeta en dólares, habilitada para compras internacionales. Cobro cada mes.", tam=17, color=CREMA, interlineado=1.25)
pie(s, "render.com, octubre 2026 · L 26.80 por dólar")
notas(s, "Render Starter: US$7 de servidor más US$0.25 de disco. El plan gratis se duerme y borra los datos.")

# ===========================================================================
# 27. Proceso de compra
# ===========================================================================
s = nueva(CREMA)
etiqueta(s, 0.9, 0.85, "Proceso de compra")
titulo(s, 0.9, 1.3, 10, 0.8, "De la tarjeta a la página lista", tam=34)
pasos = ["Cuentas del liceo", "Tarjeta en Render", "Crear el servicio", "Poner las claves", "Conectar el dominio", "Probar y abrir"]
linea(s, 1.25, 3.05, 11.55, 3.05, SALVIA, 1.5)
for i, t in enumerate(pasos):
    x = 0.9 + i * 2.0
    circulo(s, x, 2.7, 0.7, OLIVA if i < 5 else BOSQUE, nombre="fx-diagrama")
    texto(s, x, 2.82, 0.7, 0.45, str(i + 1), tam=17, color=CREMA, fuente=TITULO, negrita=True, alinear=PP_ALIGN.CENTER, nombre="fx-diagrama")
    texto(s, x - 0.58, 3.6, 1.86, 0.9, t, tam=15, color=PROFUNDO, negrita=True, interlineado=1.1, alinear=PP_ALIGN.CENTER, nombre="fx-diagrama")
linea(s, 0.9, 5.15, 12.4, 5.15, PALIDO, 0.75, nombre="fx-deco")
texto(s, 0.9, 5.35, 11.5, 0.9, [[("Un año en el liceo: ", {"negrita": True, "color": OLIVA}), ("12 pagos de US$7.25, dos administradores, respaldo semanal y revisión mensual de la factura.", {})]],
      tam=17, interlineado=1.25)
pie(s, "Las claves van en el servidor, nunca en el código")
notas(s, "Seis pasos para dejarla lista un año. Dos administradores evitan que dependa de una sola persona.")

# ===========================================================================
# 28. Tiendas de apps
# ===========================================================================
s = nueva(CREMA)
etiqueta(s, 0.9, 0.85, "La app en las tiendas")
titulo(s, 0.9, 1.3, 10, 0.8, "¿Play Store, App Store o ninguna?", tam=32)
opciones = [("App instalable", "L 0", "Ya funciona: \"Agregar a inicio\" en Android y iPhone.", True),
            ("Google Play", "US$25 una vez", "≈ L 670. Si la cuenta es personal, prueba con 12 personas por 14 días.", False),
            ("App Store", "US$99 al año", "≈ L 2,653. Necesita una Mac y la revisión de Apple.", False)]
for i, (t, precio, det, dest) in enumerate(opciones):
    x = 0.9 + i * 3.95
    if dest:
        bloque(s, x - 0.3, 2.3, 3.85, 3.95, BOSQUE, radio=0.05)
    texto(s, x, 2.6, 3.4, 0.5, t, tam=20, color=CREMA if dest else PROFUNDO, fuente=TITULO, negrita=True)
    texto(s, x, 3.2, 3.4, 0.7, precio, tam=28, color=BEIGE if dest else OLIVA, fuente=TITULO, negrita=True)
    texto(s, x, 4.1, 3.25, 1.9, det, tam=15, color=PALIDO if dest else BOSQUE, interlineado=1.25)
    if i == 1:
        linea(s, x - 0.35, 2.55, x - 0.35, 6.0, PALIDO, 0.75, nombre="fx-deco")
pie(s, "Precios oficiales de Google y Apple, octubre 2026")
notas(s, "Lo más rápido y gratis es la app instalable. Google Play es el segundo paso; Apple es opcional.")

# ===========================================================================
# 29. Inversión
# ===========================================================================
s = nueva(PROFUNDO)
circulo(s, 8.6, 1.6, 6.6, OLIVA)
puntos(s, 0.9, 6.3, 8, 2, OLIVA)
etiqueta(s, 0.9, 0.95, "Inversión del primer año")
texto(s, 0.85, 1.45, 8, 1.9, "L 22,992", tam=96, color=CREMA, fuente=TITULO, negrita=True, nombre="fx-titulo")
texto(s, 0.92, 3.3, 7.2, 1.0, "Equipos L 19,696  ·  hosting y dominio L 2,626  ·  Google Play L 670", tam=17, color=PALIDO, interlineado=1.25)
texto(s, 9.2, 2.9, 5.4, 0.5, "Con App Store", tam=15, color=BEIGE, negrita=True)
texto(s, 9.2, 3.35, 5.4, 0.9, "L 25,645", tam=40, color=CREMA, fuente=TITULO, negrita=True)
texto(s, 9.2, 4.45, 3.6, 1.2, "Desde el segundo año: ≈ L 2,800 al año.", tam=16, color=PALIDO, interlineado=1.25)
pie(s, "L 26.80 por dólar · precios de octubre 2026")
notas(s, "La inversión grande es una sola vez: los equipos. Cada año se repite solo el hosting y el dominio.")

# ===========================================================================
# 30. Cronograma
# ===========================================================================
s = nueva(CREMA)
etiqueta(s, 0.9, 0.85, "Tiempo de ejecución")
titulo(s, 0.9, 1.3, 10, 0.8, "6 de 7 fases cumplidas", tam=34)
fases = [("Antes", "Análisis y planificación"), ("2–5 oct", "Chat, asistente y riesgo"), ("7–8 oct", "Funciones y diseño"),
         ("12–15 oct", "IA, mural y app"), ("17–19 oct", "Varias IAs y voz"), ("20 oct", "Tigre, bullying y acoso"), ("Próximo", "Publicar y entregar")]
linea(s, 1.15, 3.6, 12.0, 3.6, SALVIA, 1.5)
for i, (fecha, t) in enumerate(fases):
    x = 0.9 + i * 1.8
    if i < 6:
        circulo(s, x, 3.35, 0.5, OLIVA, nombre="fx-diagrama")
    else:
        anillo(s, x, 3.35, 0.5, OLIVA, 2.0, nombre="fx-diagrama")
    texto(s, x - 0.62, 2.75, 1.75, 0.4, fecha, tam=14, color=OLIVA, negrita=True, alinear=PP_ALIGN.CENTER, nombre="fx-diagrama")
    texto(s, x - 0.62, 4.05, 1.75, 0.9, t, tam=13, color=BOSQUE, interlineado=1.1, alinear=PP_ALIGN.CENTER, nombre="fx-diagrama")
texto(s, 0.9, 5.45, 11, 0.8, "Fechas reales del historial de Git. Falta publicar en Render y entregar al liceo.", tam=16, color=GRIS)
pie(s, "99 cambios guardados en Git")
notas(s, "Cronograma ejecutado y cumplimiento de fases.")

# ===========================================================================
# 31. Conclusión
# ===========================================================================
s = nueva(BOSQUE)
circulo(s, 8.25, 1.5, 6.4, OLIVA)
avatar(s, AV_LICEO, 8.6, 5.2)
etiqueta(s, 0.9, 0.95, "Conclusión")
texto(s, 0.9, 1.5, 7.2, 3.2, "La tecnología no reemplaza a la psicóloga: la acerca a los estudiantes y le avisa a tiempo.",
      tam=34, color=CREMA, fuente=TITULO, negrita=True, interlineado=1.1, nombre="fx-titulo")
texto(s, 0.92, 4.95, 7, 0.9, "66 artículos  ·  24 herramientas  ·  8 IAs en cadena", tam=16, color=BEIGE, negrita=True)
pie(s)
notas(s, "La idea principal del proyecto y sus logros en números.")

# ===========================================================================
# 32. Recomendaciones y aprendizajes
# ===========================================================================
s = nueva(CREMA)
etiqueta(s, 0.9, 0.85, "Recomendaciones y aprendizajes")
titulo(s, 0.9, 1.3, 10, 0.8, "Lo que sigue y lo que aprendí", tam=34)
for i, (t, items_) in enumerate([("Para el liceo", ["Publicar en Render Starter", "Revisar las frases de riesgo", "Respaldar la base cada semana", "Definir un protocolo de crisis"]),
                                 ("Aprendizajes", ["Chat en tiempo real", "Privacidad desde el diseño", "IA con límites y respaldo", "Control de versiones con Git"])]):
    x = 0.9 + i * 6.0
    texto(s, x, 2.5, 5, 0.5, t, tam=20, color=OLIVA, fuente=TITULO, negrita=True)
    for k, it in enumerate(items_):
        y = 3.2 + k * 0.72
        circulo(s, x, y + 0.12, 0.14, ARENA if i else OLIVA, nombre="fx-deco")
        texto(s, x + 0.35, y, 5.2, 0.5, it, tam=17)
linea(s, 6.5, 2.55, 6.5, 6.0, PALIDO, 0.75, nombre="fx-deco")
pie(s)
notas(s, "Recomendaciones para el liceo y aprendizajes técnicos.")

# ===========================================================================
# 33. Anexos
# ===========================================================================
s = nueva(CREMA)
circulo(s, 10.2, 3.9, 4.6, PALIDO)
puntos(s, 10.9, 0.8, 5, 3, SALVIA)
etiqueta(s, 0.9, 0.85, "Anexos")
titulo(s, 0.9, 1.3, 10, 0.8, "Material de apoyo", tam=34)
anexos = ["A. Capturas de la página", "B. Diagramas del sistema", "C. Cotizaciones de tiendas y hosting",
          "D. Repositorio en GitHub", "E. Manual de la psicóloga", "F. Video de la demostración (plan B)"]
for i, t in enumerate(anexos):
    y = 2.45 + i * 0.68
    texto(s, 0.9, y, 8, 0.5, t, tam=18, nombre="fx-diagrama")
    if i < 5:
        linea(s, 0.9, y + 0.56, 8.4, y + 0.56, PALIDO, 0.75)
pie(s)
notas(s, "Anexos que acompañan el informe escrito.")

# ===========================================================================
# 34. Gracias
# ===========================================================================
s = nueva(OLIVA)
circulo(s, 6.9, 0.7, 7.8, CREMA, transp=14)
anillo(s, 0.55, 0.4, 0.75, BEIGE)
avatar(s, AV_LICEO, 7.6, 6.0)
texto(s, 0.9, 1.3, 6.5, 1.8, "Gracias", tam=88, color=CREMA, fuente=TITULO, negrita=True, nombre="fx-titulo")
texto(s, 0.95, 3.1, 6, 0.6, "¿Preguntas?", tam=26, color=BEIGE, fuente=TITULO)
texto(s, 0.95, 4.0, 6.2, 1.0, ["noestamossoloslmh@gmail.com", "3174-6810  ·  San Pedro Sula, Honduras"], tam=16, color=CREMA, interlineado=1.3)
bloque(s, 0.9, 5.35, 5.7, 0.75, CREMA, radio=0.5, nombre="fx-texto")
texto(s, 1.15, 5.42, 5.3, 0.6, "Si necesitas hablar con alguien: llama gratis al 150", tam=15, color=PROFUNDO, negrita=True, anclar=MSO_ANCHOR.MIDDLE)
notas(s, "Agradecer y abrir el espacio de preguntas. Cerrar con la línea gratuita 150.")

# Pide a PowerPoint que guarde las letras dentro del archivo (solo los caracteres usados).
prs.part._element.set("embedTrueTypeFonts", "1")
prs.part._element.set("saveSubsetFonts", "1")
prs.save(SALIDA)
print("Diapositivas:", len(prs.slides), "->", SALIDA)
