# CLAUDE.md

## Sobre el proyecto
App personal de organización diaria. El centro es una **API REST** que:
- Recibe tareas y datos desde **Atajos de iPhone** (Siri, automatizaciones por hora/ubicación/modos de concentración).
- Alimenta un **panel web**, que es la interfaz principal para ver, organizar y revisar todo.

Uso personal: la usaré cada día, así que prima que funcione y sea simple antes que añadir funcionalidades.

## Sobre mí y cómo quiero trabajar
- Soy estudiante de 2º de DAM y es mi primera vez usando Claude Code.
- **El objetivo principal es aprender**, no solo tener la app hecha.
- Antes de escribir código, **propón un plan** y espera a que lo apruebe.
- **Explica cada decisión**: por qué se hace así y qué alternativas había.
- Avanza en **pasos pequeños**. Un cambio a la vez, que pueda entender y probar.
- Cuando sea un buen ejercicio, **déjame escribir el código a mí** y luego revísalo.
- Si uso un concepto que no conozco (decoradores, async, ORM, CORS...), explícalo brevemente.
- Responde en español.

## Stack
- **Backend:** Python + FastAPI
- **Base de datos:** SQLite en desarrollo (PostgreSQL al desplegar)
- **Frontend:** HTML, CSS y JavaScript sin frameworks (por ahora)
- **Clientes:** panel web + Atajos de iPhone (acción "Obtener contenido de URL")
- **Control de versiones:** git

## Arquitectura
```
iPhone (Atajos) ──┐
                  ├──► API REST (FastAPI) ──► Base de datos
Panel web ────────┘
```
- La API es la única que accede a la base de datos.
- Los endpoints que modifican datos requieren una **clave API** en una cabecera.
- Los secretos (clave API, credenciales) van en un archivo `.env` que **nunca** se sube a git.

## Convenciones
- Código y nombres en inglés; comentarios y documentación en español.
- Endpoints REST en plural: `/tasks`, `/tasks/{id}`, `/tasks/today`.
- Commits pequeños con mensajes descriptivos.
- Cada cambio o decisión relevante se apunta en `DECISIONES.md` (con fecha, qué, por qué y alternativas).

## Fases
1. **[ACTUAL]** API mínima: modelo de tarea + crear y listar tareas. Primer atajo "añadir tarea", probado en local.
2. Desplegar la API para usarla desde fuera de casa.
3. Panel web.
4. Más automatizaciones: resumen matinal, revisión nocturna, registro de tiempo.
5. Estadísticas semanales.

## Comandos
Desde la carpeta del proyecto, en PowerShell:
- Activar el entorno virtual: `.\.venv\Scripts\Activate.ps1`
- Instalar dependencias: `pip install -r requirements.txt`
- Actualizar `requirements.txt`: `pip freeze | Out-File -Encoding ascii requirements.txt` (no usar `>`: guarda en UTF-16)
- Arrancar el servidor en desarrollo: `fastapi dev main.py` → http://localhost:8000/docs
- Tests: _(pendiente)_