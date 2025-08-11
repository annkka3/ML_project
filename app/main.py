
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, translate, wallet, history
from database.init_db import init as init_db

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
INIT_DB_ON_START = os.getenv("INIT_DB_ON_START", "False").lower() == "true"

app = FastAPI(title=os.getenv("APP_NAME", "ML_API"))

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup() -> None:
    """
    ⚠️ init_db чистит БД и создаёт демо‑пользователей.
    Запускаем только в DEV и если явно разрешено.
    """
    if DEBUG and INIT_DB_ON_START:
        await init_db()

app.include_router(auth.router)
app.include_router(translate.router)
app.include_router(wallet.router)
app.include_router(history.router)

@app.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}

@app.get("/")
async def root() -> dict:
    return {
        "app": os.getenv("APP_NAME", "ML_API"),
        "version": os.getenv("API_VERSION", "v1"),
        "debug": DEBUG,
    }
