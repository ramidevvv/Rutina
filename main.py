from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel, Field


# Datos que envía el cliente al crear una tarea
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


# Tarea completa, tal y como la devuelve la API
class Task(TaskCreate):
    id: int
    done: bool
    created_at: datetime


# Instancia de la aplicación: representa toda la API
app = FastAPI(title="Rutina")

# Almacenamiento temporal: se pierde al reiniciar el servidor
tasks: list[Task] = []
next_id = 1


# Endpoint raíz: sirve para comprobar que la API está en marcha
@app.get("/")
def read_root():
    return {"message": "Hola desde Rutina"}


# Crea una tarea nueva; la API asigna id, estado y fecha de creación
@app.post("/tasks", status_code=201)
def create_task(task_in: TaskCreate) -> Task:
    global next_id
    task = Task(
        id=next_id,
        title=task_in.title,
        description=task_in.description,
        done=False,
        created_at=datetime.now(timezone.utc),
    )
    tasks.append(task)
    next_id += 1
    return task


# Lista todas las tareas
@app.get("/tasks")
def list_tasks() -> list[Task]:
    return tasks
