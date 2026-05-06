from fastapi import APIRouter, Depends

from app.core.settings import Settings, get_settings
from app.services.llm.factory import LLMFactory
from app.services.search.factory import SearchFactory

router = APIRouter()


@router.get("/bootstrap")
async def frontend_bootstrap(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "app_name": settings.app_name,
        "default_llm_provider": LLMFactory(settings).get_default_provider_name(),
        "default_search_provider": SearchFactory(settings).get_default_provider_name(),
        "supported_timeframes": ["intraday", "swing", "position"],
        "risk_profiles": ["conservative", "balanced", "aggressive"],
        "market_periods": ["daily", "1min", "5min", "15min", "30min", "60min"],
    }
