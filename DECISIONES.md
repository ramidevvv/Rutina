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

## 2026-10-26 — Clave API en todos los endpoints de /tasks (Paso 5)

**Qué:**
- `.env` con `API_KEY`, una clave aleatoria de 43 caracteres generada con `secrets.token_urlsafe(32)`. No se sube a git.
- `.env.example` (sí se sube): plantilla con las variables que necesita el proyecto.
- `load_dotenv()` + `os.environ["API_KEY"]`: si falta la clave, la API no arranca.
- Dependencia `verify_api_key`: lee la cabecera `X-API-Key` (`APIKeyHeader`) y responde `401` si falta o no coincide.
- `APIRouter` con `prefix="/tasks"` y la dependencia aplicada a todo el grupo. `GET /` queda libre.
- `claude.md` actualizado: la clave se pide también en los endpoints de lectura.

**Por qué:**
- Las tareas son personales: al desplegar, cualquiera que conozca la URL podría leerlas. Por eso se protege también `GET /tasks` y no solo lo que modifica datos (cambio respecto a la idea inicial).
- El router aplica la clave en un único sitio: cualquier endpoint nuevo de `/tasks` queda protegido sin acordarse de hacerlo.
- Fallar al arrancar si no hay clave es mejor que funcionar sin protección sin darse cuenta.
- `secrets.compare_digest` en vez de `==`: tarda siempre lo mismo, así no se puede adivinar la clave midiendo tiempos.
- La clave va en una cabecera y no en la URL, porque las URL quedan en historiales y registros de servidores.
- `APIKeyHeader` añade el botón **Authorize** en `/docs`.

**Alternativas descartadas:**
- Comprobar la clave en cada endpoint por separado: es fácil olvidarla en uno nuevo.
- Usuarios y contraseñas o tokens que caducan: demasiado para una app con un único usuario.
- `pydantic-settings` para leer la configuración: más potente, pero para una sola variable basta con `python-dotenv`.

**A tener en cuenta:**
- Abrir `/tasks` en la barra del navegador da `401`, porque no se envía la cabecera. Es lo esperado: para probar, usar `/docs` (Authorize + Try it out) o `Invoke-RestMethod -Headers`.
- En los clientes, usar `/tasks` sin barra final: `/tasks/` redirige con un `307`.
- Al desplegar será obligatorio HTTPS: sin cifrado, la cabecera viaja en claro.

**Pendiente / siguiente paso:**
- Paso 6: servidor accesible desde la red local y primer atajo "Añadir tarea" en el iPhone.

## 2026-10-26 — Guardar las tareas en SQLite con SQLModel (Paso 4)

**Qué:**
- Instalado `sqlmodel` 0.0.48 (con SQLAlchemy 2.1.6).
- `TaskCreate` pasa a heredar de `SQLModel`, y `Task` es además la tabla (`table=True`). La base de datos asigna `id` (`primary_key=True`), y `done` y `created_at` tienen valores por defecto.
- Engine con `sqlite:///rutina.db`, `echo=True` para ver el SQL en la terminal y `check_same_thread=False`.
- Las tablas se crean al arrancar (`lifespan` + `SQLModel.metadata.create_all`).
- Una sesión por petición mediante la dependencia `get_session` (`SessionDep`).
- Desaparecen la lista `tasks` y el contador `next_id`.

**Por qué:**
- Con un ORM, el código no depende de la base de datos: pasar a otra (PostgreSQL, MySQL) será cambiar la URL de conexión.
- SQLModel es del autor de FastAPI y se basa en Pydantic, así que los modelos del Paso 3 casi no cambian.
- SQLite en desarrollo: un archivo, sin servidor ni contraseñas. La base de datos de producción se decide en la Fase 2.
- `echo=True` para aprender qué SQL genera el ORM.
- `check_same_thread=False`: FastAPI atiende peticiones en varios hilos y SQLite, por defecto, no lo permite.
- La dependencia (`Depends`) abre y cierra la sesión en un solo sitio, aunque haya errores. La misma idea servirá para la clave API.

**Alternativas descartadas:**
- `sqlite3` con SQL a mano: se aprende más SQL, pero hay que convertir las filas a mano y cambiar más código al pasar a otra base de datos.
- MySQL en local (ya instalado): requiere servidor en marcha, usuario y contraseña. No aporta nada en esta fase.
- Tercer modelo `TaskPublic` para las respuestas (lo recomienda la documentación de SQLModel): solo mejora cómo sale el `id` en `/docs`. Se añadirá si hace falta.

**A tener en cuenta:**
- `create_all` solo crea tablas que no existen. Si se cambia un campo de `Task`, en desarrollo hay que borrar `rutina.db`. En producción harán falta migraciones (Alembic).
- SQLite no guarda la zona horaria: por convención, todas las fechas de la base de datos están en UTC.

**Pendiente / siguiente paso:**
- Paso 5: exigir una clave API (cabecera `X-API-Key`, leída de `.env`) en los endpoints que modifican datos.

## 2026-10-26 — Modelo de tarea y endpoints en memoria (Paso 3)

**Qué:**
- Modelos Pydantic: `TaskCreate` (`title`, `description`), con lo que envía el cliente, y `Task`, que hereda de `TaskCreate` y añade `id`, `done` y `created_at`, con lo que devuelve la API.
- `title` obligatorio, de 1 a 200 caracteres. `description` opcional (`str | None`).
- `POST /tasks` crea una tarea y responde con `201 Created`. `GET /tasks` lista todas.
- Almacenamiento en una lista de Python, con un contador `next_id` para los ids.
- Probado en `/docs`, con `Invoke-RestMethod` y con `TestClient`, incluidos los casos de error (`422`).

**Por qué:**
- Dos modelos para que el cliente no pueda fijar `id`, `done` ni `created_at`: si los envía, se ignoran (comprobado).
- `description` se añade a petición mía, para apuntar notas extra. Es opcional para poder crear tareas solo con el título desde Siri.
- `min_length=1` rechaza títulos vacíos, por ejemplo si Siri no entiende bien.
- `created_at` en UTC: al desplegar, el servidor estará en otra zona horaria. El panel convertirá la hora a la local al mostrarla.
- Contador en vez de `len(tasks) + 1`: cuando se puedan borrar tareas, el tamaño de la lista bajará y se repetirían ids.
- Memoria antes que base de datos: así se entiende la API sin mezclar dos conceptos nuevos a la vez.

**Alternativas descartadas:**
- Un único modelo con `id` y `created_at` opcionales: más corto, pero mezcla lo que entra con lo que sale.
- Hora local en `created_at`: depende de dónde esté el servidor.

**Pendiente / siguiente paso:**
- Mejora apuntada: un título de solo espacios (`"   "`) se acepta. Quitar los espacios antes de validar.
- Paso 4: guardar las tareas en SQLite para que no se pierdan al reiniciar.

## 2026-10-26 — Primer endpoint: "hola mundo" (Paso 2)

**Qué:**
- `main.py` con la instancia `app = FastAPI(title="Rutina")` y el endpoint `GET /`, que devuelve `{"message": "Hola desde Rutina"}`.
- Probado con `fastapi dev main.py` en el navegador (`/` y `/docs`) y con `TestClient`.

**Por qué:**
- Antes de añadir lógica conviene comprobar que la base funciona: servidor, recarga automática y documentación en `/docs`.
- `GET /` sirve de comprobación rápida de que la API está en marcha. Será útil cuando esté desplegada.
- Funciones con `def` normal en vez de `async def`: es más fácil y suficiente para una app personal.

**Alternativas descartadas:**
- `async def`: solo aporta algo cuando hay esperas largas (red, archivos) y muchas peticiones a la vez.
- Estructura con carpeta `app/` desde el principio: con un solo archivo no aporta nada. Se reorganizará cuando haya varios.

**Pendiente / siguiente paso:**
- Paso 3: modelo `Task` con Pydantic y endpoints `POST /tasks` y `GET /tasks`, guardando en memoria.

## 2026-10-26 — Entorno virtual e instalación de FastAPI (Paso 1)

**Qué:**
- Entorno virtual en `.venv` con Python 3.14.2.
- Instalado `fastapi[standard]` (FastAPI 0.162.0, uvicorn 0.54.0, pydantic 2.14.1).
- `requirements.txt` generado con `pip freeze`, con versiones exactas y codificado en ASCII.

**Por qué:**
- El entorno virtual aísla las librerías de este proyecto de las de otros y del Python del sistema.
- `[standard]` incluye uvicorn y el comando `fastapi dev`, que reinicia el servidor al guardar cambios.
- `pip freeze` fija las versiones exactas, para que al desplegar se instale lo mismo que en local.
- En PowerShell 5.1, `>` guarda en UTF-16, que GitHub y Linux leen mal. Por eso se genera con `pip freeze | Out-File -Encoding ascii requirements.txt`. `-Encoding utf8` también se descartó porque añade una BOM.

**Alternativas descartadas:**
- `pip install fastapi uvicorn`: más ligero, pero sin `fastapi dev`.
- Llamar al entorno `venv` sin punto: funciona igual, pero `.venv` es lo más habitual y VS Code lo detecta solo.

**Pendiente / siguiente paso:**
- Paso 2: `main.py` con un endpoint `GET /` y probar la documentación automática en `/docs`.

## 2026-10-26 — Repositorio git propio y cuenta personal

**Qué:**
- `git init` dentro de `ClaudeCode` (rama `main`).
- Identidad local del repositorio: `ramidevvv <ramidevvv@gmail.com>`.
- `.gitignore` que excluye `.env`, el entorno virtual, la base de datos local, `__pycache__/` y la configuración del editor.
- Remoto `origin` en GitHub: `https://github.com/ramidevvv/Rutina.git`, creado vacío desde la web.

**Por qué:**
- `ClaudeCode` no tenía `.git` propio, así que git subía de carpeta en carpeta hasta usar el repositorio de `C:\Users\Rami`, que veía todo el perfil de usuario (incluido `.ssh/`). Con un `.git` propio, git usa siempre el más cercano.
- Este es un proyecto de autoaprendizaje y va con la cuenta personal, no con la del instituto. La configuración local de un repositorio tiene prioridad sobre la global, así que la global (del instituto) se queda intacta para lo demás.
- El `.gitignore` se crea antes del primer commit para que nunca llegue a git un secreto ni archivos generados.
- El remoto sirve de copia de seguridad. Se creó sin README ni `.gitignore` para que su historial no chocara con el local en el primer `push`.

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
