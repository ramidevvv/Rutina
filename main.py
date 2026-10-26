from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select


# Datos que envía el cliente al crear una tarea
class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


# Tarea completa: es a la vez la tabla de la base de datos y lo que devuelve la API
class Task(TaskCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    done: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Conexión a la base de datos (un archivo SQLite en la carpeta del proyecto).
# echo=True muestra en la terminal el SQL que se ejecuta.
# check_same_thread=False: FastAPI atiende peticiones en varios hilos y SQLite,
# por defecto, solo deja usar una conexión desde el hilo que la creó.
engine = create_engine(
    "sqlite:///rutina.db",
    echo=True,
    connect_args={"check_same_thread": False},
)


# Abre una sesión por petición y la cierra al terminar, aunque haya un error
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


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


# Crea una tarea nueva; la base de datos asigna el id
@app.post("/tasks", status_code=201)
def create_task(task_in: TaskCreate, session: SessionDep) -> Task:
    task = Task.model_validate(task_in)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# Lista todas las tareas
@app.get("/tasks")
def list_tasks(session: SessionDep) -> list[Task]:
    return session.exec(select(Task)).all()
