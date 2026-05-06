from fastapi import APIRouter

from app.core.settings import get_settings
from app.services.llm.factory import LLMFactory
from app.services.search.factory import SearchFactory

router = APIRouter()


@router.get("/status")
async def provider_status() -> dict:
    settings = get_settings()
    llm_factory = LLMFactory(settings)
    search_factory = SearchFactory(settings)
    return {
        "llm": llm_factory.status(),
        "search": search_factory.status(),
        "market_data_provider": settings.market_data_provider,
        "mock_enabled": settings.enable_mocks,
    }

