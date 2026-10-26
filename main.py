from fastapi import FastAPI

# Instancia de la aplicación: representa toda la API
app = FastAPI(title="Rutina")


# Endpoint raíz: sirve para comprobar que la API está en marcha
@app.get("/")
def read_root():
    return {"message": "Hola desde Rutina"}
