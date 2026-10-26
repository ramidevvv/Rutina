# Registro de decisiones

Diario del proyecto: qué hemos cambiado, cuándo y **por qué**.
La idea es que dentro de unos meses pueda leer esto y entender cada decisión sin tener que recordarla.

## Cómo usar este archivo
- Las entradas más recientes van **arriba**.
- Una entrada por día de trabajo (o por decisión importante).
- Cada entrada responde a tres preguntas:
  - **Qué** se ha hecho o decidido.
  - **Por qué** se ha hecho así.
  - **Alternativas** que se consideraron y por qué se descartaron (si las hubo).

### Plantilla
```markdown
## AAAA-MM-DD — Título corto

**Qué:** ...
**Por qué:** ...
**Alternativas descartadas:** ...
**Pendiente / siguiente paso:** ...
```

---

## 2026-10-26 — Repositorio git propio y cuenta personal

**Qué:**
- `git init` dentro de `ClaudeCode` (rama `main`).
- Identidad local del repositorio: `ramidevvv <ramidevvv@gmail.com>`.
- `.gitignore` que excluye `.env`, el entorno virtual, la base de datos local, `__pycache__/` y la configuración del editor.

**Por qué:**
- `ClaudeCode` no tenía `.git` propio, así que git subía de carpeta en carpeta hasta usar el repositorio de `C:\Users\Rami`, que veía todo el perfil de usuario (incluido `.ssh/`). Con un `.git` propio, git usa siempre el más cercano.
- Este es un proyecto de autoaprendizaje y va con la cuenta personal, no con la del instituto. La configuración local de un repositorio tiene prioridad sobre la global, así que la global (del instituto) se queda intacta para lo demás.
- El `.gitignore` se crea antes del primer commit para que nunca llegue a git un secreto ni archivos generados.

**Alternativas descartadas:**
- Borrar el `.git` de `C:\Users\Rami`: tiene remoto, configuración y objetos guardados, y no hace falta tocarlo para arreglar esto.
- `includeIf` en la configuración global para aplicar la cuenta personal a toda una carpeta: en `Desktop\projects` hay proyectos personales mezclados con otros, y la configuración por repositorio es más fácil de entender.

**Pendiente / siguiente paso:**
- Paso 1: entorno virtual e instalación de FastAPI y uvicorn.

## 2026-10-26 — Definición del proyecto y creación de este registro

**Qué:**
- Se redacta `CLAUDE.md` con la idea del proyecto: una API REST (FastAPI) que recibe tareas desde Atajos de iPhone y alimenta un panel web.
- Stack inicial: Python + FastAPI, SQLite en desarrollo (PostgreSQL al desplegar), HTML/CSS/JS sin frameworks y git.
- Se crea este archivo, `DECISIONES.md`, para documentar el porqué de cada cambio.

**Por qué:**
- El objetivo principal es aprender, así que conviene dejar por escrito el razonamiento detrás de cada paso, no solo el código.
- Es una app de uso personal y diario: prima que sea simple y funcione antes que añadir funcionalidades.
- Los secretos irán en `.env` y nunca se suben a git, para no exponer la clave API.

**Alternativas descartadas:**
- Usar un `CHANGELOG.md` clásico: suele listar *qué* cambia en cada versión, pero no el *porqué*. Un registro de decisiones encaja mejor con el objetivo de aprender.

**Pendiente / siguiente paso:**
- Fase 1: proponer el plan para la API mínima (modelo de tarea + crear y listar tareas).
