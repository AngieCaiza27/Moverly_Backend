# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Crear la app
app = FastAPI(
    title="Moverly Backend",
    description="API para el proyecto Moverly 🚚⚡",
    version="1.0.0"
)

# Configuración de CORS
origins = [
    "http://localhost:19006",  # Expo (React Native en local)
    "http://localhost:3000",   # React web en local (si aplicas)
    "*"                        # ⚠️ Permitir todo (cambiar en producción)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta de prueba
@app.get("/")
def read_root():
    return {"message": "🚀 Bienvenido a la API de Moverly"}

# Ejemplo de endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Moverly Backend"}
