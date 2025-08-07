from fastapi import FastAPI
from routers.home import router as home_router
from routers.auth import router as auth_router
from routers.translate import router as translate_router
from routers.wallet import router as wallet_router
from routers.history import router as history_router
from database.database import engine, Base

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(home_router)
app.include_router(auth_router)
app.include_router(translate_router)
app.include_router(wallet_router)
app.include_router(history_router)
