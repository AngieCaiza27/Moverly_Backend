# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import settings
from app.db.session import engine
from app.models.base import Base
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.orders import router as orders_router
from app.routes.drivers import router as drivers_router
from app.routes.chat_ratings import router as chat_router
from app.routes.admin import router as admin_router
from app.routes.ws_chat import router as ws_chat_router

# Crear la app
app = FastAPI(
    title="Moverly Backend",
    description="API proyecto Moverly 🚚⚡",
    version="1.0.0",
    # Force the OpenAPI "servers" entry to localhost for the Swagger UI so
    # the browser issues requests to a reachable URL (127.0.0.1) even when
    # Uvicorn is listening on 0.0.0.0. This prevents Swagger "Failed to fetch"
    # errors caused by an invalid 0.0.0.0 base URL.
    servers=[{"url": "http://127.0.0.1:8000"}],
)

# Configuración de CORS
origins = [
    "http://localhost:19006",  # Expo (React Native en local)
    "http://localhost:3000",   # React web en local (si aplicas)
    "*"                        # Permitir todo (cambiar en producción)
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
    return {"message": " Bienvenido a la API de Moverly"}

# Ejemplo de endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Moverly Backend"}


@app.on_event("startup")
async def on_startup() -> None:
    # MVP: crear tablas automáticamente si no existen
    async with engine.begin() as conn:  # type: ignore[attr-defined]
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(orders_router)
app.include_router(drivers_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(ws_chat_router)
