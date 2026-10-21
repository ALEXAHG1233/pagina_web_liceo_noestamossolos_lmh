"""Versión 2 de la presentación "No estamos solos LMH".

Toma el diseño y las 27 diapositivas de crear_presentacion.py, las actualiza con
todo lo que se agregó a la página y añade lo que pide la estructura de defensa
del liceo: dedicatoria, agradecimientos, introducción, objetivos, justificación,
práctica profesional (3 diapositivas para editar), lo nuevo de la plataforma,
cotizaciones de equipos, hosting, compra, tiendas de apps y anexos.

Uso:  python crear_presentacion_v2.py   ->  No_estamos_solos_LMH_v2.pptx
La versión 1 (No_estamos_solos_LMH.pptx) no se toca.
"""
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
original = open(os.path.join(AQUI, "crear_presentacion.py"), encoding="utf-8").read()

MARCA = re.compile(r"# -{75}\n# (\d+)\. [^\n]*\n# -{75}\n")
trozos = MARCA.split(original)
cabeza = trozos[0]
bloques = {int(trozos[i]): trozos[i + 1] for i in range(1, len(trozos), 2)}
final_27 = bloques[27]
guardar = final_27[final_27.index("prs.save(SALIDA)"):]
bloques[27] = final_27[:final_27.index("prs.save(SALIDA)")]

cabeza = cabeza.replace('SALIDA = os.path.join(AQUI, "No_estamos_solos_LMH.pptx")',
                        'SALIDA = os.path.join(AQUI, "No_estamos_solos_LMH_v2.pptx")')


def cambiar(n, pares):
    for a, b in pares:
        if a not in bloques[n]:
            raise SystemExit(f"Diapositiva {n}: no encontré {a[:60]!r}")
        bloques[n] = bloques[n].replace(a, b)


# ---------------------------------------------------------------------------
# Piezas nuevas que usan varias diapositivas
# ---------------------------------------------------------------------------
cabeza += '''

from PIL import Image as _Imagen


def producto(s, archivo, x, y, wmax, hmax):
    """Foto de un producto centrada en su espacio, sin deformarla."""
    ancho, alto = _Imagen.open(rec(archivo)).size
    escala = min(wmax / ancho, hmax / alto)
    w, h = ancho * escala, alto * escala
    foto = s.shapes.add_picture(rec(archivo), Inches(x + (wmax - w) / 2), Inches(y + (hmax - h) / 2), Inches(w), Inches(h))
    sombra(foto, blur=20, dist=8, opacidad=40)
    return foto


def cotizacion(s, i, tienda, archivo, nombre, precio, antes, uso, recomendado=False):
    """Una columna de cotización: foto, tienda, producto, precio y para qué sirve."""
    x = 0.85 + i * 3.95
    producto(s, archivo, x + 0.25, 2.2, 3.15, 1.95)
    pastilla(s, x, 4.3, 1.9, tienda, tam=12, h=0.4)
    if recomendado:
        pastilla(s, x + 2.0, 4.3, 1.6, "Recomendado", color=OSCURO, color_texto=LIMA, tam=11, h=0.4)
    texto(s, x, 4.78, 3.65, 0.55, nombre, tam=14, fuente=TITULO, negrita=True, color=LIMA, interlineado=1.0)
    linea = [(precio, {"tam": 24, "fuente": TITULO, "negrita": True, "color": BLANCO})]
    if antes:
        linea.append(("   antes " + antes, {"tam": 11, "color": TEXTO_SUAVE}))
    texto(s, x, 5.3, 3.65, 0.5, [linea])
    texto(s, x, 5.82, 3.6, 1.05, uso, tam=12, color=TEXTO_SUAVE, interlineado=1.18)


def para_editar(s, x, y, w, h, guia, tam=15):
    """Recuadro punteado con una guía de lo que va ahí: lo edita la estudiante."""
    f = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    f.adjustments[0] = 0.06
    f.fill.solid()
    f.fill.fore_color.rgb = rgb(BLANCO)
    alfa(f, 7)
    f.line.color.rgb = rgb(LIMA)
    f.line.width = Pt(1.25)
    f.line.dash_style = 4
    tf = f.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.2)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    lineas = guia if isinstance(guia, list) else [guia]
    for k, t in enumerate(lineas):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.line_spacing = 1.3
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = t
        r.font.name, r.font.size = CUERPO, Pt(tam)
        r.font.color.rgb = rgb(TEXTO_SUAVE)
    return f
'''

# ---------------------------------------------------------------------------
# Diapositivas nuevas
# ---------------------------------------------------------------------------
nuevas = {}

nuevas["dedicatoria"] = '''
s = nueva("fondo_brillante.jpg", icono="corazon")
deco(s, [("esfera_lima.png", 0.4, 6.0, 0.8), ("anillo_menta.png", 10.9, 5.4, 1.5)])
texto(s, 0.95, 0.85, 10, 0.4, "Dedicatoria", tam=14, color=OSCURO, negrita=True, espaciado=3, mayus=True)
texto(s, 0.95, 1.3, 10, 1.0, "A quienes me acompañaron", tam=36, fuente=TITULO, negrita=True, color=OSCURO)
f = para_editar(s, 0.95, 2.6, 10.3, 3.6, ["[Escribe aquí tu dedicatoria: a tu familia, a Dios, a un profesor o a quien tú quieras.]",
                                         "", "Tip: dos o tres oraciones, con tus propias palabras."], tam=17)
f.text_frame.paragraphs[0].runs[0].font.color.rgb = rgb(OSCURO)
for p in f.text_frame.paragraphs[1:]:
    for r in p.runs:
        r.font.color.rgb = rgb(OLIVA)
pie(s)
notas(s, "Dedicatoria personal: la escribe la estudiante.")
'''

nuevas["agradecimientos"] = '''
s = nueva("fondo_1.jpg", icono="estrella")
encabezado(s, "Agradecimientos", "Gracias a quienes hicieron posible este proyecto")
para_editar(s, 0.85, 2.4, 11.6, 3.9, ["[Escribe aquí tus agradecimientos. Por ejemplo:]",
                                      "•  Al Liceo Militar de Honduras y al área de Informática.",
                                      "•  A la psicóloga del liceo, por sus ideas y su revisión.",
                                      "•  A mi asesor(a) [nombre], por su guía.",
                                      "•  A la empresa o institución de mi práctica profesional.",
                                      "•  A mi familia y a mis compañeros que probaron la página."], tam=16)
pie(s)
notas(s, "Agradecimientos: la estudiante los ajusta con los nombres reales.")
'''

nuevas["introduccion"] = '''
s = nueva("fondo_2.jpg", icono="burbuja")
encabezado(s, "Introducción", "De qué trata este proyecto")
texto(s, 0.85, 2.35, 7.3, 4.3, [
    "En el liceo, muchos estudiantes viven estrés, ansiedad, bullying o problemas en casa, y no siempre se animan a pedir ayuda: temen que se sepa quiénes son o no encuentran a la psicóloga a tiempo.",
    "",
    "\\"No estamos solos LMH\\" es una plataforma web anónima que acerca esa ayuda: los estudiantes pueden hablar con la psicóloga o con un asistente, aprender sobre lo que sienten y usar ejercicios para calmarse, desde el celular o la computadora.",
    "",
    "Si un mensaje muestra señales de riesgo, la plataforma avisa a la psicóloga al instante y muestra las líneas de ayuda 150 y 911.",
], tam=16, color=TEXTO_SUAVE, interlineado=1.28)
imagen(s, "tigrito_psicologo.png", 8.6, 1.9, h=4.9)
pie(s)
notas(s, "Presentar el tema en un minuto: el problema, la solución y por qué importa.")
'''

nuevas["objetivo_general"] = '''
s = nueva("fondo_brillante.jpg", icono="estrella")
deco(s, [("esfera_blanca.png", 8.4, 0.5, 1.2), ("esfera_lima.png", 0.4, 6.05, 0.8)])
texto(s, 0.95, 0.85, 10, 0.4, "Objetivo general", tam=14, color=OSCURO, negrita=True, espaciado=3, mayus=True)
texto(s, 0.95, 1.5, 11.3, 3.8, "Desarrollar una plataforma web anónima de apoyo emocional para los estudiantes del Liceo Militar de Honduras, que les permita pedir ayuda en cualquier momento y que avise a la psicóloga a tiempo cuando un mensaje muestre señales de riesgo.",
      tam=31, fuente=TITULO, negrita=True, color=OSCURO, interlineado=1.08)
for i, t in enumerate(["Anónima", "Disponible 24/7", "Alertas a tiempo"]):
    pastilla(s, 0.95 + i * 2.6, 5.55, 2.4, t, color=OSCURO, color_texto=LIMA, tam=13, h=0.6)
pie(s)
notas(s, "El objetivo general en una oración: qué se hace, para quién y para qué.")
'''

nuevas["objetivos_especificos"] = '''
s = nueva("fondo_3.jpg", icono="engranaje")
encabezado(s, "Objetivos específicos", "Lo que se propuso lograr el proyecto")
for k, (t, c) in enumerate([
    ("Escuchar sin exponer", "Crear un chat anónimo en tiempo real con la psicóloga del liceo."),
    ("Acompañar a toda hora", "Ofrecer asistentes con IA (Sami, Leo, Nia y el Tigre LMH) por chat y por voz."),
    ("Detectar el riesgo", "Revisar cada mensaje con 8 categorías y alertar a la psicóloga al instante."),
    ("Enseñar y cuidar", "Publicar 66 artículos, 24 herramientas con pasos, tests y un diario de ánimo."),
    ("Dejarla en manos del liceo", "Un panel para que la psicóloga actualice el contenido sin programar."),
    ("Que funcione siempre", "Publicarla en internet con varias IAs en cadena y respuestas de respaldo."),
]):
    fila, col = divmod(k, 3)
    tarjeta(s, 0.85 + col * 3.95, 2.35 + fila * 2.2, 3.65, 2.0, t, c, numero_tarjeta=f"0{k + 1}", tam_titulo=17, tam_cuerpo=13.5)
pie(s)
notas(s, "Seis objetivos específicos; cada uno se cumple con una parte de la plataforma.")
'''

nuevas["justificacion"] = '''
s = nueva("fondo_1.jpg", icono="corazon")
encabezado(s, "Justificación", "Por qué este proyecto es necesario")
for i, (t, c) in enumerate([
    ("Pedir ayuda da miedo", "El anonimato quita la barrera más grande: que se sepa quién es."),
    ("La ayuda llega tarde", "Una sola psicóloga no puede estar siempre; la plataforma sí, y le avisa a tiempo."),
    ("Bajo costo, alto impacto", "Software libre e IA con planes gratis: el liceo paga solo el hosting y los equipos."),
]):
    tarjeta(s, 0.85 + i * 3.95, 2.35, 3.65, 2.55, t, c, numero_tarjeta=f"0{i + 1}")
caja(s, 0.85, 5.25, 11.55, 1.25, color=LIMA, transp=100, borde=None)
texto(s, 1.2, 5.35, 11, 1.05, "Cuidar la salud mental de los estudiantes también es cuidar su disciplina, su estudio y su futuro en el liceo.",
      tam=19, fuente=TITULO, negrita=True, color=OSCURO, anclar=MSO_ANCHOR.MIDDLE)
pie(s)
notas(s, "Por qué vale la pena: el anonimato, la rapidez de la ayuda y el bajo costo.")
'''

for n, (titulo, subtitulo, guia) in enumerate([
    ("Lugar de práctica", "Generalidades de la empresa o institución", [
        "[Nombre de la empresa o institución donde hiciste tu práctica]",
        "[Ubicación y a qué se dedica]",
        "[Misión o propósito, en una oración]",
        "[Área o departamento donde trabajaste y quién fue tu jefe inmediato]",
        "[Fechas y horario de la práctica]"]),
    ("Tareas realizadas", "Lo que hice durante la práctica", [
        "[Tarea 1: por ejemplo, soporte técnico a equipos]",
        "[Tarea 2: por ejemplo, instalación de redes o programas]",
        "[Tarea 3]",
        "[Tarea 4]",
        "[Lo que más aprendí]"]),
    ("Problema identificado", "La necesidad tecnológica que encontré", [
        "[¿Qué problema viste en la práctica o en el liceo?]",
        "[¿A quién afecta y cómo lo supiste?]",
        "[¿Por qué una solución tecnológica ayuda?]",
        "[Cómo se conecta con No estamos solos LMH]"]),
], start=1):
    nuevas[f"practica_{n}"] = f'''
s = nueva("fondo_{1 + n % 3}.jpg", icono="{["escudo", "engranaje", "rayo"][n - 1]}")
encabezado(s, "Práctica profesional · {n} de 3", "{titulo}")
texto(s, 0.85, 2.2, 11, 0.45, "{subtitulo}", tam=17, color=TEXTO_SUAVE)
para_editar(s, 0.85, 2.85, 11.6, 3.75, {guia!r}, tam=16)
pie(s, "Diapositiva para editar")
notas(s, "Contexto y diagnóstico (4 a 5 minutos entre las 3 diapositivas). Esta la completa la estudiante con su práctica profesional.")
'''

nuevas["nuevo_ia"] = '''
s = nueva("fondo_2.jpg", icono="rayo")
encabezado(s, "Lo nuevo · Inteligencia artificial", "Ocho servicios de IA en cadena")
texto(s, 0.85, 2.2, 11.5, 0.8, "Si un servicio se queda sin saldo, sin cuota o falla, el asistente pasa solo al siguiente. Si ninguno responde, usa las respuestas preparadas por el equipo: el chat nunca se queda callado.",
      tam=15, color=TEXTO_SUAVE, interlineado=1.25)
servicios = ["Claude", "Groq", "Google Gemini", "Mistral", "OpenRouter", "NVIDIA", "Hugging Face", "B.AI"]
for k, nombre in enumerate(servicios):
    fila, col = divmod(k, 4)
    x, y = 0.85 + col * 2.95, 3.2 + fila * 0.85
    pastilla(s, x, y, 2.45, f"{k + 1}. {nombre}", color=LIMA if k < 3 else MENTA, tam=14, h=0.55)
    if col < 3:
        flecha(s, x + 2.5, y + 0.15, 0.36, 0.26)
for i, (t, c) in enumerate([
    ("Sin cortes", "Cada servicio prueba varios modelos antes de pasar al siguiente."),
    ("Gratis o casi gratis", "La mayoría usa planes gratuitos; Claude es opcional."),
    ("Nunca atiende una crisis", "Si hay riesgo, el mensaje va a la psicóloga, no a la IA."),
]):
    tarjeta(s, 0.85 + i * 3.95, 5.0, 3.65, 1.75, t, c, acento=(i == 2), tam_titulo=16, tam_cuerpo=12.5)
pie(s, "Las claves de la IA se guardan en el servidor, nunca en el código")
notas(s, "Orden en que se prueban los servicios de IA. Si uno se queda sin saldo, se pausa y se prueba el siguiente. Ninguna crisis llega a la IA: el filtro de riesgo la deriva antes a la psicóloga.")
'''

nuevas["nuevo_voz"] = '''
s = nueva("fondo_3.jpg", icono="burbuja")
encabezado(s, "Lo nuevo · Voz", "Hablar en vez de escribir, y el Tigre que responde")
items = [
    ("Dictar en el chat", "El micrófono convierte la voz en texto con Whisper (Groq). El audio no se guarda."),
    ("Respuestas en voz", "Quien responde lee su mensaje en voz alta, si la persona lo prefiere."),
    ("Modo voz", "Pantalla completa: hablas, te contesta con voz y subtítulos, y vuelve a escucharte."),
    ("Habla con el Tigre", "En la portada y en /tigre: sus ojos te siguen y reaccionan al escuchar, pensar y hablar."),
]
for k, (t, c) in enumerate(items):
    fila, col = divmod(k, 2)
    tarjeta(s, 0.85 + col * 3.75, 2.35 + fila * 2.2, 3.5, 2.0, t, c, acento=(k == 3), tam_titulo=17, tam_cuerpo=13)
imagen(s, "tigrito_psicologo.png", 8.75, 1.95, h=4.85)
pie(s, "Lo dicho por voz pasa por el mismo filtro de riesgo que lo escrito")
notas(s, "La voz hace la plataforma más cómoda para quien no quiere escribir. El Tigre LMH es la mascota que habla: se le toca, se le habla y responde con su voz.")
'''

nuevas["nuevo_diseno"] = '''
s = nueva("fondo_1.jpg", icono="estrella")
encabezado(s, "Lo nuevo · Diseño y contenidos", "Una página más clara, cálida y completa")
items = [
    ("Portada por capítulos", "Hablar, Si es urgente, Cuídate hoy, Entiende y Comunidad."),
    ("Ayuda siempre a mano", "Botón \\"Necesito ayuda ahora\\" fijo, también en el celular."),
    ("Bullying y acoso", "Artículos nuevos: qué es, qué hacer si te pasa o si lo ves."),
    ("17 temas con imagen", "Recursos de psicología con ilustraciones y libros con portada."),
    ("Letras más legibles", "Fraunces en títulos y Atkinson Hyperlegible en textos."),
    ("Animaciones con toque", "Efectos que responden al dedo en el celular y caritas nuevas."),
]
for k, (t, c) in enumerate(items):
    fila, col = divmod(k, 3)
    tarjeta(s, 0.85 + col * 3.95, 2.35 + fila * 2.2, 3.65, 2.0, t, c, acento=(k == 2), tam_titulo=17, tam_cuerpo=13.5)
pie(s)
notas(s, "Los cambios de diseño buscan que la ayuda se encuentre rápido y que la página sea cómoda de leer.")
'''

nuevas["cot_tablets"] = '''
s = nueva("fondo_2.jpg", icono="moneda")
encabezado(s, "Cotización de equipos · Tablets", "Para el Tigre por voz y las charlas")
cotizacion(s, 0, "Jetstereo", "cot_tab_a11_jetstereo.png", "Samsung Galaxy Tab A11 · 8\\" · 64 GB", "L 4,795", "L 5,495",
           "Estación de autoayuda en orientación: el Tigre por voz, la respiración y los tests.")
cotizacion(s, 1, "Jetstereo", "cot_tab_s10_lite.png", "Samsung Galaxy Tab S10 Lite · 10.9\\" · 128 GB", "L 9,495", "L 10,995",
           "Para la psicóloga en charlas y talleres: pantalla grande y lápiz para anotar.")
cotizacion(s, 2, "Elektra", "cot_tab_a11_elektra.png", "Samsung Galaxy Tab A11 · 4 GB / 64 GB", "L 4,499", "L 5,499",
           "El mismo uso que la primera, L 296 más barata: la mejor opción.", recomendado=True)
pie(s, "Precios de las tiendas, octubre 2026; verificar antes de comprar")
notas(s, "Las tablets llevan la app instalada. La de 8 pulgadas sirve como estación donde los estudiantes hablan con el Tigre o hacen un ejercicio; la de 10.9 es para presentaciones de la psicóloga.")
'''

nuevas["cot_celulares"] = '''
s = nueva("fondo_3.jpg", icono="telefono")
encabezado(s, "Cotización de equipos · Celulares", "El teléfono de la psicóloga")
cotizacion(s, 0, "La Curacao", "cot_samsung_a17.png", "Samsung Galaxy A17 · 4 GB + 128 GB", "L 5,997", "L 7,999",
           "Recibe las alertas de riesgo y el WhatsApp de emergencias, con la app instalada.", recomendado=True)
cotizacion(s, 1, "La Curacao", "cot_redmi_17.png", "Xiaomi Redmi 17 · 4 GB + 128 GB", "L 6,599", "",
           "El mismo uso; incluye cargador, cable y estuche.")
cotizacion(s, 2, "Elektra", "cot_infinix_smart20.png", "Infinix Smart 20 · 4 GB + 128 GB", "L 4,599", "L 5,999",
           "La opción más económica para las alertas y el WhatsApp.")
pie(s, "Precios de las tiendas, octubre 2026; verificar antes de comprar")
notas(s, "Un teléfono del liceo para la psicóloga: así no usa su número personal y las alertas no se pierden. Recomendamos el Samsung A17 por precio y actualizaciones.")
'''

nuevas["cot_laptops"] = '''
s = nueva("fondo_1.jpg", icono="engranaje")
encabezado(s, "Cotización de equipos · Laptops", "Para el panel de la psicóloga y la demostración")
cotizacion(s, 0, "Geek Store", "cot_dell_5420.png", "Dell Latitude 5420 · i5 11.ª · 8 GB · 256 GB", "L 9,200", "",
           "Panel de la psicóloga y servidor local de respaldo (plan B) para la defensa.", recomendado=True)
cotizacion(s, 1, "Geek Store", "cot_book_pro_i5.png", "Galaxy Book Pro 2 360 · i5 · 8 GB · 13.4\\"", "L 13,200", "",
           "Pantalla táctil que gira como tablet: para charlas y para el Tigre.")
cotizacion(s, 2, "Geek Store", "cot_book_pro_i7.png", "Galaxy Book Pro 2 360 · i7 · 16 GB · 13.4\\"", "L 16,400", "",
           "La más potente: si también se usará para clases o edición de video.")
pie(s, "Precios de la tienda, octubre 2026; preguntar si es nueva o reacondicionada y la garantía")
notas(s, "Con la Dell Latitude basta para el panel y para tener la página funcionando sin internet durante la defensa (servidor local listo, como pide la lista de verificación).")
'''

nuevas["hosting"] = '''
s = nueva("fondo_2.jpg", icono="nube")
encabezado(s, "Cotización de hosting", "Render: plan Starter con disco para los datos")
tabla(s, 0.85, 2.3, 6.6, [
    ["Concepto", "Precio"],
    ["Espacio de trabajo Hobby", "US$0"],
    ["Servidor Starter (512 MB, 0.5 CPU)", "US$7.00 al mes"],
    ["Disco de 1 GB para los datos", "US$0.25 al mes"],
    ["Tráfico: 5 GB al mes incluidos", "US$0 (extra US$0.15/GB)"],
    ["Dominio .com, primer año", "≈ US$11"],
    ["Total al mes", "US$7.25 ≈ L 194"],
    ["Total del primer año", "≈ US$98 ≈ L 2,626"],
], [4.1, 2.5], tam=12.5, alto_fila=0.5, resaltar=7)
barra(s, 7.85, 2.35, 2.35, LIMA)
texto(s, 8.1, 2.3, 4.4, 0.5, "Qué ofrece", tam=19, fuente=TITULO, negrita=True, color=LIMA)
texto(s, 8.1, 2.8, 4.5, 1.9, ["•  Siempre encendido, sin dormirse", "•  Chat en vivo (WebSockets)", "•  HTTPS gratis, también con dominio propio",
                              "•  Copia del disco cada 24 horas", "•  Se actualiza sola desde GitHub"], tam=13, color=TEXTO_SUAVE, interlineado=1.3)
barra(s, 7.85, 4.95, 1.75, MENTA)
texto(s, 8.1, 4.9, 4.4, 0.5, "Cómo se paga", tam=19, fuente=TITULO, negrita=True, color=LIMA)
texto(s, 8.1, 5.4, 4.5, 1.3, ["•  Tarjeta de crédito o débito en dólares", "•  Habilitada para compras internacionales", "•  Cobro automático cada mes"],
      tam=13, color=TEXTO_SUAVE, interlineado=1.3)
pie(s, "render.com, octubre 2026 · L 26.80 por dólar (BCH)")
notas(s, "Recomendamos Render Starter porque la página ya está preparada para Render. El plan gratis no sirve para uso real: se duerme y borra los datos al reiniciarse. Render cobra solo con tarjeta, en dólares; la tarjeta del liceo debe permitir compras internacionales.")
'''

nuevas["proceso"] = '''
s = nueva("fondo_3.jpg", icono="reloj")
encabezado(s, "Proceso de compra", "Del pago a la página lista para el liceo")
pasos = [
    ("Cuentas del liceo", "Crear GitHub y Render con un correo institucional."),
    ("Agregar la tarjeta", "En Billing de Render, con la tarjeta del liceo."),
    ("Crear el servicio", "Desde el repositorio: plan Starter y disco de 1 GB."),
    ("Poner las claves", "IA, psicóloga y clave secreta en Environment."),
    ("Comprar el dominio", "Conectarlo en Render: el HTTPS se activa solo."),
    ("Probar y abrir", "Pruebas con la psicóloga; luego, a los estudiantes."),
]
for k, (t, c) in enumerate(pasos):
    fila, col = divmod(k, 3)
    tarjeta(s, 0.85 + col * 3.95, 2.3 + fila * 1.75, 3.65, 1.6, t, c, numero_tarjeta=f"{k + 1}", tam_titulo=16, tam_cuerpo=12.5)
caja(s, 0.85, 5.85, 11.55, 0.95, color=LIMA, transp=100, borde=None)
texto(s, 1.15, 5.9, 11.1, 0.85, [[("Un año en el liceo: ", {"negrita": True}), ("12 pagos de US$7.25 más el dominio (≈ L 2,626), dos administradores, respaldo semanal de la base de datos y revisión mensual de la factura.", {})]],
      tam=14.5, color=OSCURO, anclar=MSO_ANCHOR.MIDDLE, interlineado=1.15)
pie(s)
notas(s, "Pasos para dejarla funcionando un año. Las claves nunca se escriben en el código ni se suben a GitHub. Tener dos administradores evita que la página dependa de una sola persona.")
'''

nuevas["tiendas"] = '''
s = nueva("fondo_1.jpg", icono="telefono")
encabezado(s, "La app en las tiendas", "Play Store y App Store")
tabla(s, 0.85, 2.3, 11.6, [
    ["Opción", "Costo", "Qué pide", "Recomendación"],
    ["App instalable (PWA)", "L 0", "Ya funciona: \\"Agregar a inicio\\" en Android y iPhone", "Usarla desde ya"],
    ["Google Play Store", "US$25 una vez ≈ L 670", "Cuenta de desarrollador; si es personal, prueba con 12 personas por 14 días", "Segundo paso"],
    ["Apple App Store", "US$99 al año ≈ L 2,653", "Una Mac para preparar la app y la revisión de Apple", "Opcional"],
], [2.6, 2.6, 4.4, 2.0], tam=12.5, alto_fila=0.78, resaltar=1)
texto(s, 0.85, 5.6, 11.6, 1.2, "La página ya se instala como app con el ícono del liceo. Para subirla a Google Play se puede empaquetar con PWABuilder (gratis); como organización, Google pide un número D-U-N-S en lugar de la prueba con 12 personas. Apple puede rechazar una app que solo muestra una página web.",
      tam=13.5, color=TEXTO_SUAVE, interlineado=1.25)
pie(s, "Precios oficiales de Google y Apple, octubre 2026 · L 26.80 por dólar")
notas(s, "Lo más rápido y gratis es la app instalable que ya tiene la página. Google Play cuesta US$25 una sola vez; Apple cobra US$99 cada año y necesita una Mac.")
'''

nuevas["anexos"] = '''
s = nueva("fondo_2.jpg", icono="candado")
encabezado(s, "Anexos", "Material de apoyo")
for k, (t, c) in enumerate([
    ("A. Capturas", "Portada, chat, Tigre por voz, panel de la psicóloga y celular."),
    ("B. Diagramas", "Arquitectura, base de datos, flujo de datos y procesos."),
    ("C. Cotizaciones", "Jetstereo, La Curacao, Elektra, Geek Store, Render y tiendas de apps."),
    ("D. Código", "Repositorio en GitHub con el historial de cambios."),
    ("E. Manual", "Guía para la psicóloga: panel, alertas y contenido."),
    ("F. Plan B", "Video de la demostración por si falla la red o la energía."),
]):
    fila, col = divmod(k, 3)
    tarjeta(s, 0.85 + col * 3.95, 2.35 + fila * 2.2, 3.65, 2.0, t, c, tam_titulo=17, tam_cuerpo=13.5)
pie(s, "Agrega aquí tus capturas y documentos")
notas(s, "Lista de anexos que acompañan el informe escrito.")
'''

# ---------------------------------------------------------------------------
# Las diapositivas de la versión 1, actualizadas
# ---------------------------------------------------------------------------
cambiar(5, [("Chat anónimo con la psicóloga del liceo y con el asistente Sami, Leo o Nia, que hace preguntas de seguimiento.",
             "Chat anónimo con la psicóloga del liceo y con Sami, Leo, Nia o el Tigre LMH, también por voz."),
            ("64 artículos", "66 artículos")])
cambiar(6, [('("Asistente Sami, Leo o Nia", "Pregunta, recuerda el tema y sugiere herramientas.")',
             '("Asistentes con IA", "Sami, Leo, Nia y el Tigre: por chat o por voz.")'),
            ('("Infórmate", "64 artículos, 4 secciones y glosario.")', '("Infórmate", "66 artículos, bullying y acoso incluidos.")')])
cambiar(8, [('("Libros de apoyo", "Un estante con 7 libros reales y para qué ayuda cada uno.")',
             '("Libros de apoyo", "Un estante con 7 libros reales, con foto de portada.")'),
            ('("Recursos ilustrados", "15 temas de psicología, cada uno con su dibujo.")',
             '("Recursos con imagen", "17 temas de psicología, cada uno con su imagen.")')])
cambiar(10, [('["Base de datos SQLite", "API de Claude (IA)", "YouTube y Spotify"]',
              '["Base de datos SQLite", "8 servicios de IA en cadena", "Voz: Whisper (Groq)", "YouTube y Spotify"]')])
cambiar(11, [('["SQLite", "API de Claude (IA)", "YouTube y Spotify"]', '["SQLite", "IA: 8 servicios en cadena", "Voz: Whisper (Groq)", "YouTube y Spotify"]'),
             ('"Asistente y respaldo por reglas"', '"Asistentes, voz y respaldo por reglas"'),
             ("consulta la IA por la API de Claude.", "consulta la IA en cadena: si un servicio falla, responde el siguiente.")])
cambiar(15, [('["Inteligencia artificial", "API de Claude (librería anthropic)", "Asistente que conversa"]',
              '["Inteligencia artificial", "8 servicios en cadena (Claude, Groq, Gemini…)", "Asistentes que conversan"]'),
             ('["Animaciones y app", "Canvas, WebGL, SVG y PWA", "Mural, efectos y app instalable"]',
              '["Voz, animaciones y app", "Whisper, voz del navegador, Canvas, SVG y PWA", "Hablar, efectos y app instalable"]'),
             ('pie(s, "Todo el software es libre o gratuito, salvo la API de IA")', 'pie(s, "Todo el software es libre o gratuito; la IA usa planes gratis")'),
             ("la API de Claude para la IA", "ocho servicios de IA en cadena, Whisper para la voz")])
cambiar(17, [('("Portada: logo, carrusel, mural de psicología y línea 150", "1 min")',
              '("Portada: capítulos, \\"Necesito ayuda ahora\\" y el Tigre que habla", "1 min")'),
             ('("Chat con Sami: pregunta, recuerda el tema y sugiere una herramienta", "2 min")',
              '("Chat con Sami y modo voz: recuerda el tema y sugiere una herramienta", "2 min")')])
cambiar(18, [("cada mejora es un cambio guardado en Git (76 hasta hoy).", "cada mejora es un cambio guardado en Git (99 hasta hoy).")])
bloques[19] = '''
s = nueva("fondo_1.jpg", icono="moneda")
encabezado(s, "Presupuesto", "Hardware, licencias y servicios")
tabla(s, 0.85, 2.3, 11.6, [
    ["Concepto", "Detalle", "Costo"],
    ["Software", "Python, Flask, SQLite y Git: licencias libres", "L 0"],
    ["IA y voz", "Planes gratuitos en cadena (Claude es opcional)", "L 0"],
    ["Celular de la psicóloga", "Samsung Galaxy A17, La Curacao", "L 5,997"],
    ["Tablet para el Tigre por voz", "Samsung Galaxy Tab A11, Elektra", "L 4,499"],
    ["Laptop del panel y plan B", "Dell Latitude 5420, Geek Store", "L 9,200"],
    ["Internet", "Red del liceo", "L 0"],
    ["Hosting, dominio y tiendas", "Ver las cotizaciones siguientes", "≈ L 3,296"],
], [3.6, 6.2, 1.8], tam=13, alto_fila=0.52)
pie(s, "Equipos recomendados de cada cotización · octubre 2026; verificar antes de comprar")
notas(s, "El software es libre y la IA usa planes gratis. La inversión está en los equipos: el celular de la psicóloga, una tablet para el Tigre por voz y una laptop para el panel y el servidor de respaldo.")
'''
bloques[21] = '''
s = nueva("fondo_brillante.jpg", icono="moneda")
deco(s, [("esfera_lima.png", 12.1, 5.2, 0.7)])
texto(s, 0.95, 0.75, 10, 0.4, "Inversión del proyecto", tam=14, color=OSCURO, negrita=True, espaciado=3, mayus=True)
texto(s, 0.95, 1.2, 10.5, 1.0, "Costo estimado del primer año", tam=36, fuente=TITULO, negrita=True, color=OSCURO)
for i, (t, cifra, det) in enumerate([
    ("Recomendado (con Google Play)", "L 22,992", "Equipos L 19,696 + hosting y dominio L 2,626 + Google Play L 670"),
    ("Con Play Store y App Store", "L 25,645", "Lo anterior + Apple US$99 al año (≈ L 2,653)"),
]):
    x = 0.95 + i * 5.85
    barra(s, x, 2.75, 3.3, OSCURO if i == 0 else OLIVA)
    texto(s, x + 0.4, 2.85, 5.0, 0.5, t, tam=17, negrita=True, color=OLIVA)
    texto(s, x + 0.4, 3.35, 5.0, 1.3, cifra, tam=66, fuente=TITULO, negrita=True, color=OSCURO)
    texto(s, x + 0.4, 4.85, 4.9, 1.2, det, tam=15, color=OSCURO, interlineado=1.25)
texto(s, 0.95, 6.15, 11.3, 0.6, "Desde el segundo año: solo hosting y dominio, unos L 2,800 al año (más Apple, si se publica ahí). La IA sigue en US$0 con los planes gratis.",
      tam=13.5, color=OSCURO)
pie(s, "L 26.80 por dólar (BCH) · precios de octubre 2026")
notas(s, "La inversión grande es una sola vez: los equipos. Lo que se repite cada año es poco: el hosting y el dominio.")
'''
cambiar(22, [('columnas = ["Antes", "2–3 oct", "4–5 oct", "7–8 oct", "12 oct", "13–15 oct", "Próximo"]',
              'columnas = ["Antes", "2–5 oct", "7–8 oct", "12–15 oct", "17–19 oct", "20 oct", "Próximo"]'),
             ('fases = ["Análisis y planificación", "Base: chat, asistente y riesgo", "Funciones: diario, tests, Infórmate",\n         "Diseño e identidad del liceo", "IA, herramientas y línea 150", "Interactividad, paleta y contenidos", "Pruebas, publicación y entrega"]',
              'fases = ["Análisis y planificación", "Base: chat, asistente y riesgo", "Funciones, diseño e identidad",\n         "IA, herramientas, mural y app", "Varias IAs, voz y rediseño", "Tigre por voz, bullying y acoso", "Pruebas, publicación y entrega"]')])
cambiar(23, [('["Funciones", "Cumplida", "Diario, tests, Infórmate y herramientas"]', '["Funciones y diseño", "Cumplida", "Diario, tests, Infórmate y colores del liceo"]'),
             ('["Diseño institucional", "Cumplida", "Colores del liceo, escudo y uso en celular"]', '["IA y herramientas", "Cumplida", "Asistente, línea 150, mural y app, 12 a 15 oct"]'),
             ('["IA y contenidos", "Cumplida", "Asistente y línea 150, 12 de octubre"]', '["Varias IAs, voz y rediseño", "Cumplida", "8 servicios de IA, voz y capítulos, 17 a 19 oct"]'),
             ('["Interactividad y paleta", "Cumplida", "Mural, recursos ilustrados, panel y app, 13 a 15 de octubre"]', '["Tigre por voz y contenidos", "Cumplida", "Tigre en la portada, bullying y acoso, 20 oct"]'),
             ('["Pruebas y publicación", "En curso", "Falta publicar en Render y activar la clave de IA"]', '["Pruebas y publicación", "En curso", "Código en GitHub; falta Render Starter y las claves en el servidor"]'),
             ('pie(s, "76 cambios guardados en Git")', 'pie(s, "99 cambios guardados en Git")')])
cambiar(25, [('("64", "artículos en Infórmate")', '("66", "artículos en Infórmate")'), ('("26", "conceptos en el glosario")', '("8", "servicios de IA en cadena")')])
cambiar(26, [('"Usar historias reales, anónimas y con permiso"', '"Pagar Render Starter y poner las claves allí"')])

# ---------------------------------------------------------------------------
# Orden final, siguiendo la estructura de defensa del liceo
# ---------------------------------------------------------------------------
orden = [
    1, "dedicatoria", "agradecimientos", "introduccion", "objetivo_general", "objetivos_especificos", "justificacion",
    # Bloque 1: contexto y diagnóstico
    "practica_1", "practica_2", "practica_3", 2, 3, 4,
    # Propuesta de solución
    5, 6, 7, 8, 9, "nuevo_ia", "nuevo_voz", "nuevo_diseno",
    # Bloque núcleo: arquitectura de la propuesta
    10, 11, 12, 13, 14, 15, 16, 17,
    # Bloque final: gestión, cronograma y cierre
    18, 19, "cot_tablets", "cot_celulares", "cot_laptops", "hosting", "proceso", "tiendas", 21, 22, 23,
    24, 25, 26, "anexos", 27,
]
usadas = {o for o in orden if isinstance(o, int)}
assert usadas == set(range(1, 28)) - {20}, "Faltan o sobran diapositivas de la versión 1"
codigo = cabeza
for n, clave in enumerate(orden, start=1):
    cuerpo = bloques[clave] if isinstance(clave, int) else nuevas[clave]
    codigo += f"\n# {'-' * 75}\n# {n}.\n# {'-' * 75}\n" + cuerpo
codigo += "\n" + guardar
exec(compile(codigo, "crear_presentacion_v2", "exec"), {"__name__": "__main__", "__file__": os.path.join(AQUI, "crear_presentacion.py")})
