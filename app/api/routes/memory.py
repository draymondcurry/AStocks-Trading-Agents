from fastapi import APIRouter, Depends, Request

from app.core.settings import Settings, get_settings
from app.schemas.memory import RecallRequest, RememberRequest
from app.services.llm.factory import LLMFactory
from app.services.memory.manager import MemoryManager

router = APIRouter()


def get_memory_manager(request: Request, settings: Settings) -> MemoryManager:
    llm = LLMFactory(settings).create()
    return MemoryManager(request.app.state.memory_store, llm, settings)


@router.post("/remember")
async def remember(
    payload: RememberRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> dict:
    manager = get_memory_manager(request, settings)
    await manager.remember(
        payload.session_id,
        payload.namespace,
        payload.content,
        payload.importance,
    )
    return {"status": "stored"}


@router.post("/recall")
async def recall(
    payload: RecallRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> dict:
    manager = get_memory_manager(request, settings)
    return await manager.recall(
        payload.session_id,
        payload.namespace,
        payload.query,
        payload.limit,
    )

