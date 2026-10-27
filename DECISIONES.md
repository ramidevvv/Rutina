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

## 2026-10-27 — Las tareas hechas se guardan para estadísticas (panel, paso 3)

**Qué:**
- Reglas nuevas en `claude.md` (sección "Reglas de las tareas").
- Campo `completed_at` en `Task`: `PATCH` con `done: true` guarda la hora (UTC) y con `done: false` la vacía.
- `DELETE` de una tarea hecha responde `409 Conflict`. Solo se borran las pendientes.
- Panel: casilla para marcar o desmarcar (`PATCH`), botón **Borrar** solo en las pendientes (`DELETE`) y orden con las pendientes primero (`tasks.sort`).
- Columna añadida a mano con `ALTER TABLE task ADD COLUMN completed_at ...`: en Neon (SQL Editor, `TIMESTAMP`) y en el `rutina.db` local (`DATETIME`), sin perder datos.

**Por qué:**
- Las tareas hechas son el historial para las estadísticas (Fase 5). Borrar solo sirve para corregir errores, como cuando Siri entiende mal.
- La regla está en la API, no solo en el panel: así se cumple desde cualquier cliente (atajos, panel...).
- `completed_at` permite saber cuántas tareas se completan por día o semana. Las que ya estaban hechas se quedan sin fecha.
- `create_all` no modifica tablas existentes: primero se añade la columna en Neon y después se despliega. En el orden contrario, la API fallaría.

**Alternativas descartadas:**
- Prohibir borrar del todo: no habría forma de quitar tareas creadas por error.
- Ocultar las hechas en el panel: preferí verlas tachadas debajo.
- Migraciones con Alembic: para una sola columna, un `ALTER TABLE` a mano es más sencillo. Se reconsiderará si los cambios de tablas se vuelven frecuentes.

**A tener en cuenta:**
- Con `load_dotenv(override=True)`, una variable puesta al lanzar un comando (`SQL_ECHO=0 python ...`) también la sobrescribe `.env`.
- Cada dirección del panel tiene su clave: `localhost` → la local, `rutina.fastapicloud.dev` → la de producción. Si el navegador guarda una incorrecta: `localStorage.removeItem("apiKey")` en la consola (F12).

## 2026-10-27 — Panel web, paso 2: añadir tareas

**Qué:**
- Formulario con un campo de título (`required`) y un botón **Añadir**.
- Al enviarlo: `preventDefault()`, `POST /tasks` con la clave y `{"title": ...}`, vaciar el campo y recargar la lista.

**Por qué:**
- `required` evita enviar títulos vacíos sin escribir JavaScript.
- `preventDefault()`: sin él, el navegador recarga la página al enviar el formulario.
- Solo título, por ser lo mínimo. La descripción se añadirá si hace falta.

**Pendiente / siguiente paso:**
- Panel: marcar tareas como hechas y borrarlas.

## 2026-10-27 — Fase 3: panel web, paso 1 (ver la lista)

**Qué:**
- `panel.html`: una sola página con HTML, CSS y JavaScript sin frameworks. Pide la clave con `prompt`, la guarda en `localStorage` y muestra las tareas con `fetch("/tasks")`. Las hechas salen tachadas.
- `GET /panel` en `main.py` devuelve la página con `FileResponse`. No pide clave: la página no contiene datos y las tareas las pide luego ella misma con la clave.
- `load_dotenv(override=True)`.

**Por qué:**
- Servir el panel desde la propia API: no hace falta otro alojamiento y, al estar en la misma dirección, el navegador no bloquea las peticiones (CORS).
- `localStorage`: no pedir la clave cada vez. Si la API responde `401`, se borra y se vuelve a pedir.
- `override=True`: tras cambiar la clave local en `.env`, el servidor seguía con la antigua incluso al reiniciarlo. La terminal ya tenía cargada `API_KEY` (probablemente VS Code la carga al abrir la terminal) y `load_dotenv()` no sobrescribe las variables que ya existen. Con `override=True`, `.env` siempre manda. En producción no afecta, porque no hay `.env`.

**Pendiente / siguiente paso:**
- Panel: añadir tareas, marcarlas como hechas y borrarlas.

## 2026-10-27 — Atajo "Ver tareas" en el iPhone

**Qué:**
- Duplicado de "Añadir tarea", sin *Solicitar entrada*, con método `GET` y sin cuerpo. Mantiene la cabecera `X-API-Key`.
- Muestra solo los títulos: *Repetir con cada* elemento de *Contenido de la URL* → *Obtener valor de diccionario* `title` de *Elemento de repetición* → *Mostrar* *Resultados de repetir*.

**Por qué:**
- Duplicar el atajo evita volver a escribir la clave.
- *Obtener valor de diccionario* aplicado directamente a la respuesta no funcionó: Atajos no la recorría como lista. El bucle *Repetir con cada* procesa las tareas una a una y es la forma fiable.

**Pendiente:**
- Mostrar solo las tareas pendientes (`done: false`) y marcarlas como hechas desde el iPhone.

## 2026-10-27 — Modificar y borrar tareas (PATCH y DELETE)

**Qué:**
- Modelo `TaskUpdate`: `title`, `description` y `done`, todos opcionales.
- `PATCH /tasks/{task_id}`: cambia solo los campos enviados (`exclude_unset=True`). Por ejemplo, `{"done": true}` marca la tarea como hecha.
- `DELETE /tasks/{task_id}`: borra la tarea y responde `204`.
- Si la tarea no existe, los dos responden `404`. Piden la clave por estar en `tasks_router`.

**Por qué:**
- Sin poder marcar ni borrar tareas, la app no sirve para el día a día, y el panel web y los atajos lo necesitan.
- PATCH y no PUT: PUT obliga a enviar la tarea entera. Con PATCH basta con `{"done": true}`, más cómodo desde un atajo.
- La tabla no cambia, así que no hay que tocar Neon.

**Alternativas descartadas:**
- Una primera versión incluía `GET /tasks/{id}`, quitar espacios del título y rechazar `null`. Se quitó: usaba conceptos nuevos (`BeforeValidator`, `field_validator`) que hacían el código difícil de seguir. Decidí ir a lo mínimo y dejar las comprobaciones para más adelante.

**Pendiente:**
- `GET /tasks/{id}` para ver una sola tarea.
- Rechazar títulos de solo espacios (`"   "`).
- `PATCH` con `{"title": null}` o `{"done": null}` da `500`: rechazarlo con un `422`.

## 2026-10-26 — Atajo del iPhone y arreglo de conexiones caducadas (pool_pre_ping)

**Qué:**
- Atajo "Añadir tarea" en el iPhone: *Solicitar entrada* → *Obtener contenido de URL* (`POST https://rutina.fastapicloud.dev/tasks`, cabecera `X-API-Key`, cuerpo JSON `title` = Entrada proporcionada) → *Mostrar resultado*. Funciona con Siri y con datos móviles.
- `pool_pre_ping=True` en `create_engine`.

**Por qué:**
- En los registros de producción, la primera tarea tras un rato sin uso dio `500` con `psycopg.OperationalError: SSL connection has been closed unexpectedly`, y esa tarea no se guardó.
- Causa: SQLAlchemy reutiliza las conexiones abiertas (*pool*), pero Neon las cierra al suspenderse tras 5 minutos sin uso. La siguiente petición intentaba usar una conexión ya cerrada.
- `pool_pre_ping` comprueba la conexión con una consulta mínima antes de usarla y, si está cerrada, abre otra. Cuesta unos milisegundos por petición.

**Alternativas descartadas:**
- `pool_recycle` (renovar las conexiones cada X segundos): reduce el problema, pero no lo elimina si Neon cierra antes de ese tiempo.
- Reintentar la petición en el atajo: esconde el error en lugar de arreglarlo, y habría que hacerlo en cada cliente.

**Cómo comprobar que llegan las tareas:**
- El atajo muestra un JSON con `id` (tarea guardada) o un error.
- `/docs` de producción con Authorize y la clave de producción → `GET /tasks`.
- Neon: *Tables* o *SQL Editor* (`SELECT * FROM task;`).
- `fastapi cloud logs`: cada petición con su código (`201` = guardada).

**Pendiente / siguiente paso:**
- Comprobar en los registros que no vuelve a salir el `500` tras un rato sin uso.

## 2026-10-26 — API desplegada en FastAPI Cloud

**Qué:**
- App `rutina` desplegada con `fastapi deploy` en el team `ramidevvv`. URL: https://rutina.fastapicloud.dev
- `fastapi deploy` crea la carpeta `.fastapicloud/`, que vincula el proyecto a la app y no se sube a git. En los siguientes despliegues ya no hace preguntas.
- Variables de entorno en el panel, ambas como **Secret**: `API_KEY` (clave de producción, distinta de la local) y `DATABASE_URL` (Neon, con `postgresql+psycopg://`). `SQL_ECHO` no se define.
- Comprobado: `GET /` → `200`, `/tasks` sin clave → `401`, con clave → `200` (conecta con Neon), la clave local → `401`, y `http://` redirige a `https://`.

**Por qué:**
- La clave de producción es distinta de la local porque la local había aparecido en la conversación. Así, aunque se filtre la local, no da acceso a los datos reales.
- Secret: su valor queda cifrado y no se puede ver ni en el panel ni con `fastapi cloud env list`. Solo se puede elegir al crear la variable; para cambiarlo, hay que borrarla y crearla de nuevo.

**Problemas encontrados y cómo se resolvieron:**
- Primer despliegue: **Verification Failed** con `KeyError: 'API_KEY'`. Era lo esperado: aún no había variables y la API no arranca sin ellas.
- Tras añadir las variables seguía fallando: se habían guardado sin redesplegar. Con **Save Only** se aplican en el siguiente despliegue; se solucionó con `fastapi deploy`.
- La URL del panel (`dashboard.fastapicloud.com/...`) no es la de la API (`rutina.fastapicloud.dev`).
- Un `404` sin cuerpo viene de la plataforma (Cloudflare), no de la API (que respondería `{"detail":"Not Found"}`): la petición no llega a la app.
- Lección: lo que se selecciona en VS Code llega a Claude Code. Para copiar secretos sin mostrarlos se usa `Set-Clipboard`, o se copian directamente de la web del servicio.

**A tener en cuenta:**
- La contraseña de Neon apareció en la conversación. Decidí no cambiarla. Si en algún momento se quiere cambiar: en Neon, *Reset password* del rol `neondb_owner`, y actualizar el secreto `DATABASE_URL` en FastAPI Cloud con *Save and Redeploy*.

**Pendiente / siguiente paso:**
- Crear el atajo "Añadir tarea" en el iPhone contra `https://rutina.fastapicloud.dev/tasks`.

## 2026-10-26 — Mostrar el SQL solo en local (SQL_ECHO)

**Qué:**
- Nueva variable opcional `SQL_ECHO`: con `SQL_ECHO=1` el engine muestra el SQL que ejecuta. Sin definir, no lo muestra.
- En el `.env` local está a `1`. En producción no se define.

**Por qué:**
- En producción, `echo=True` escribiría en los registros cada consulta, incluidos los títulos de las tareas, que son datos personales.
- Es opcional (`os.environ.get`) y no obligatoria como `API_KEY` o `DATABASE_URL`: si falta, el resultado es el valor seguro (no mostrar nada), así que no hace falta impedir que arranque la API.

**Alternativas descartadas:**
- Activar el echo solo si la base de datos es SQLite: funciona, pero mezcla dos cosas distintas (qué base de datos se usa y si se quiere ver el SQL).
- Quitar el echo del todo: se perdería una herramienta útil para aprender qué hace el ORM.

**Pendiente / siguiente paso:**
- Desplegar con `fastapi deploy` y configurar `API_KEY` (nueva, distinta de la local) y `DATABASE_URL` como secretos en FastAPI Cloud.

## 2026-10-26 — Fase 2: elegir dónde desplegar y preparar la base de datos

**Qué:**
- Se salta el Paso 6 de la Fase 1 (atajo probado en la WiFi de casa): el objetivo es crear tareas desde el iPhone en cualquier sitio, así que se pasa directamente a desplegar.
- Despliegue elegido: **FastAPI Cloud** (plan Hobby) para la API y **Neon** (plan Free, región Frankfurt, con connection pooling) para PostgreSQL.
- `DATABASE_URL` se lee de `.env` (obligatoria, como `API_KEY`). `check_same_thread` solo se aplica si la URL es de SQLite.
- Instalado `psycopg[binary]` 3.3.6, el driver de PostgreSQL.
- Conexión con Neon probada: la tabla `task` se crea sola y `POST`/`GET /tasks` funcionan sin cambiar el código. Las tareas de prueba se borraron.
- En local se sigue usando SQLite. La URL de Neon queda comentada en `.env`.

**Por qué:**
- Desplegar en la nube frente a dejarlo en el PC con un túnel (Tailscale, Cloudflare Tunnel): la app se usa a diario y el PC no está siempre encendido.
- FastAPI Cloud: gratis y sin tarjeta, hecho para FastAPI, y el comando `fastapi deploy` ya venía con `fastapi[standard]`. Render se descartó por su arranque en frío de alrededor de 1 minuto tras 15 minutos sin uso, que es un problema para un atajo de Siri.
- Neon: PostgreSQL gratis, permanente y sin tarjeta. Se suspende sin uso, pero no borra datos.
- SQLite no sirve en producción: el disco de estos servicios se borra en cada reinicio o despliegue.
- `DATABASE_URL` obligatoria: si faltara en producción y se usara SQLite por defecto, se perderían datos sin darse cuenta.
- SQLite en local: las pruebas no ensucian las tareas reales, funciona sin internet y se puede borrar `rutina.db` al cambiar el modelo.
- `postgresql+psycopg://` en la URL: con SQLAlchemy 2.1 bastaría con `postgresql://` (ya usa psycopg por defecto, comprobado), pero así queda claro qué driver se usa.

**Alternativas descartadas:**
- Render (arranque en frío lento; su Postgres gratis caduca a los 30 días), Railway (solo crédito de prueba), Fly.io y Koyeb (piden tarjeta o pago).
- Supabase: pausa el proyecto tras 1 semana sin uso.
- Abrir un puerto en el router: expone el PC a internet y sin HTTPS.
- Neon también en local: los experimentos afectarían a los datos reales.

**A tener en cuenta:**
- FastAPI Cloud está en beta pública: las condiciones pueden cambiar. El código no depende del servicio y se puede volver a desplegar en otro.
- Las capas gratuitas cambian a menudo: revisar los límites de vez en cuando.

**Pendiente / siguiente paso:**
- Decidir `echo=True` en producción: escribiría el SQL (con los títulos de las tareas) en los registros.
- Usar en producción una `API_KEY` distinta de la local.
- Desplegar con `fastapi deploy`, configurar los secretos y crear el atajo del iPhone.

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
