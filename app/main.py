from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.router import api_router
from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.services.memory.store import MemoryStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    memory_store = MemoryStore(settings.memory_db_path)
    await memory_store.initialize()
    app.state.memory_store = memory_store
    yield
    await memory_store.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix="/api/v1")
    Instrumentator().instrument(app).expose(app, include_in_schema=False)
    return app


app = create_app()

