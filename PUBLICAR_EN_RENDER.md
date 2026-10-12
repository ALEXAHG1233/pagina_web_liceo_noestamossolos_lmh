# Cómo publicar "No estamos solos LMH" en internet (Render)

Con esto la página queda en una dirección pública, por ejemplo
`https://no-estamos-solos-lmh.onrender.com`, que funciona desde cualquier
celular o computadora, aunque tu computadora esté apagada.

## Lo que necesitas

- Tu cuenta de GitHub con el repositorio `pagina_web_liceo_noestamossolos_lmh`.
- Una cuenta en https://render.com (puedes entrar con tu cuenta de GitHub).
- Una tarjeta para pagar el plan Starter (unos US$7 al mes) y el disco (1 GB,
  unos centavos al mes). Render te muestra el total antes de confirmar.
- Decidir el usuario y la contraseña de la psicóloga (que no sean los de ejemplo).

## Pasos

1. Entra a https://dashboard.render.com y toca **New → Blueprint**.
2. Conecta tu cuenta de GitHub y elige el repositorio
   `pagina_web_liceo_noestamossolos_lmh`. Render encuentra el archivo
   `render.yaml` solo.
3. Render te pide los valores secretos. Escríbelos ahí (nunca en el código):
   - `PSICOLOGA_USUARIO`: el usuario con el que entrará la psicóloga.
   - `PSICOLOGA_CLAVE`: una contraseña larga y difícil de adivinar.
   - `ANTHROPIC_API_KEY`: la clave de la IA (de console.anthropic.com).
     Es opcional: si la dejas vacía, el asistente responde con las reglas.
   - `SECRET_KEY` la genera Render automáticamente.
4. Toca **Apply**. Render instala todo y publica la página. Tarda unos minutos.
5. Cuando diga **Live**, abre la dirección que aparece arriba
   (termina en `.onrender.com`). Esa es la página pública.
6. Prueba: entra al chat del estudiante, y en otra ventana entra al panel de
   la psicóloga con el usuario y la contraseña que pusiste.

## Después

- **Cada vez que se suba un cambio a GitHub**, Render actualiza la página sola.
- **La base de datos y las fotos** se guardan en el disco `/var/data`, así que
  no se pierden con las actualizaciones. Render permite hacer copias del disco
  desde la pestaña **Disks**; conviene hacerlo cada semana.
- **Dominio propio (opcional):** si compras uno (por ejemplo `noestamossoloslmh.com`),
  agrégalo en la pestaña **Settings → Custom Domains** del servicio.
- **Nunca** subas a GitHub el archivo `apoyo_emocional.db` ni ninguna clave.
