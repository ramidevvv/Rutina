import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Carga las variables del archivo .env. Si falta alguna, la API no arranca:
# mejor fallar al inicio que funcionar sin protección o con la base de datos equivocada.
load_dotenv()
API_KEY = os.environ["API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]


# Datos que envía el cliente al crear una tarea
class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


# Tarea completa: es a la vez la tabla de la base de datos y lo que devuelve la API
class Task(TaskCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    done: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# check_same_thread=False solo aplica a SQLite: FastAPI atiende peticiones en
# varios hilos y SQLite, por defecto, solo deja usar una conexión desde el hilo
# que la creó. Otras bases de datos (PostgreSQL) no aceptan esta opción.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Conexión a la base de datos. echo=True muestra en la terminal el SQL que se ejecuta.
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


# Abre una sesión por petición y la cierra al terminar, aunque haya un error
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# Lee la cabecera X-API-Key. auto_error=False para devolver nuestro propio 401
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# Rechaza la petición si la clave falta o no coincide con la de .env.
# compare_digest compara en tiempo constante para no dar pistas sobre la clave.
def verify_api_key(api_key: Annotated[str | None, Security(api_key_header)]):
    if api_key is None or not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(status_code=401, detail="Clave API no válida o ausente")


# Se ejecuta al arrancar la API: crea las tablas que aún no existan
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


# Instancia de la aplicación: representa toda la API
app = FastAPI(title="Rutina", lifespan=lifespan)


# Endpoint raíz: sirve para comprobar que la API está en marcha
@app.get("/")
def read_root():
    return {"message": "Hola desde Rutina"}


# Todos los endpoints de /tasks exigen la clave API
tasks_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(verify_api_key)],
)


# Crea una tarea nueva; la base de datos asigna el id
@tasks_router.post("", status_code=201)
def create_task(task_in: TaskCreate, session: SessionDep) -> Task:
    task = Task.model_validate(task_in)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# Lista todas las tareas
@tasks_router.get("")
def list_tasks(session: SessionDep) -> list[Task]:
    return session.exec(select(Task)).all()


app.include_router(tasks_router)
