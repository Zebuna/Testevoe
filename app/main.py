from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine, get_db
from app.routers import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(
    title="Task Tracker API",
    description="Упрощённый сервис управления задачами",
    lifespan=lifespan,
)
app.include_router(api_router)
