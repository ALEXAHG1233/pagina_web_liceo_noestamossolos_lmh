# Plataforma de apoyo emocional — Fase 1

## Cómo correrlo

```bash
pip install -r requirements.txt
python app.py
```

Luego abre en el navegador:

- **Vista del estudiante:** http://localhost:5000/estudiante
- **Vista de la psicóloga:** http://localhost:5000/psicologa

Abre ambas en pestañas distintas (o una en modo incógnito) para simular
la conversación entre las dos partes.

## Qué hace ya esta Fase 1

- Genera un token anónimo por estudiante (`Usuario-XXXXXX`) sin pedir datos.
- Chat en tiempo real vía WebSockets (Flask-SocketIO).
- Guarda todos los mensajes en `apoyo_emocional.db` (SQLite), asociados solo al token.
- El **filtro de riesgo** (`filtro_riesgo.py`) analiza cada mensaje del estudiante:
  - Detecta patrones de ideación suicida, autolesión, abuso/violencia, bullying y desesperanza.
  - Calcula un nivel: `bajo`, `medio`, `alto`, `critico`.
- Si el nivel es medio o superior, el chat se resalta en rojo en el panel
  de la psicóloga y sube al inicio de la lista.
- Si el nivel es crítico, el estudiante ve automáticamente un mensaje de
  apoyo inmediato (mientras se espera a la psicóloga).

## Qué falta para las siguientes fases

- **Autenticación real** de la psicóloga (por ahora `/psicologa` es de acceso libre — solo válido para la demo escolar).
- **Persistencia de conexión**: si el estudiante recarga la página, hoy conserva su token (vía `session` de Flask), pero conviene añadir reconexión automática de Socket.IO.
- **Líneas de ayuda reales**: reemplazar el texto genérico de `apoyo_emergencia` en `app.py` por los números de contención de tu país/institución.
- **Mejorar el filtro**: si más adelante quieres subir de nivel 1 (regex) a nivel 2 (NLP real), se puede integrar spaCy (`es_core_news_sm`) dentro de `filtro_riesgo.py` sin tocar el resto del sistema — la función `analizar_riesgo()` es el único punto de entrada.
