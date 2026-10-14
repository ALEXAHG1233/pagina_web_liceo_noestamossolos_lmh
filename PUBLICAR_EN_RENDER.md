# Cómo publicar "No estamos solos LMH" en internet (Render, gratis)

Con esto la página queda en una dirección pública, por ejemplo
`https://no-estamos-solos-lmh.onrender.com`, que funciona desde cualquier
celular o computadora, aunque tu computadora esté apagada.

## Lo que necesitas

- Tu cuenta de GitHub con el repositorio `pagina_web_liceo_noestamossolos_lmh`.
- Una cuenta en https://render.com (puedes entrar con tu cuenta de GitHub).
  El plan gratis no pide tarjeta.
- Decidir el usuario y la contraseña de la psicóloga (que no sean los de ejemplo).

## Pasos

1. Entra a https://dashboard.render.com y toca **New → Blueprint**.
2. Conecta tu cuenta de GitHub y elige el repositorio
   `pagina_web_liceo_noestamossolos_lmh`. Render encuentra el archivo
   `render.yaml` solo.
3. Render te pide los valores secretos. Escríbelos ahí (nunca en el código):
   - `PSICOLOGA_USUARIO`: el usuario con el que entrará la psicóloga.
   - `PSICOLOGA_CLAVE`: una contraseña larga y difícil de adivinar.
   - `ANTHROPIC_API_KEY`: déjala vacía si no tienes saldo. El asistente
     responde con las reglas automáticas.
   - `SECRET_KEY` la genera Render automáticamente.
4. Toca **Apply**. Render instala todo y publica la página. Tarda unos minutos.
5. Cuando diga **Live**, abre la dirección que aparece arriba
   (termina en `.onrender.com`). Esa es la página pública.
6. Prueba: entra al chat del estudiante, y en otra ventana entra al panel de
   la psicóloga con el usuario y la contraseña que pusiste.

## Lo que hay que saber del plan gratis

- **Se duerme:** si nadie entra en 15 minutos, la página se apaga. La próxima
  persona que entre espera más o menos un minuto mientras despierta.
  Antes de la exposición, ábrela unos minutos antes para que ya esté despierta.
- **Los datos no se guardan para siempre:** mensajes, diario, reseñas y
  contadores se borran cada vez que la página se reinicia o se actualiza.
  Sirve para mostrarla, no para atender estudiantes de verdad.
- Para uso real, cambia al plan Starter (instrucciones dentro de `render.yaml`).

## Después

- **Cada vez que se suba un cambio a GitHub**, Render actualiza la página sola.
- **Nunca** subas a GitHub el archivo `apoyo_emocional.db` ni ninguna clave.
