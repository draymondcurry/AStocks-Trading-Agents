from fastapi import APIRouter, Depends

from app.core.settings import Settings, get_settings
from app.schemas.analysis import StockPickRequest, StockPickResponse
from app.services.agents.orchestrator import AgentOrchestrator
from app.services.kg.graph_service import KnowledgeGraphService
from app.services.llm.factory import LLMFactory
from app.services.market.data_service import MarketDataService
from app.services.search.factory import SearchFactory

router = APIRouter()


@router.post("/stock-pick", response_model=StockPickResponse)
async def stock_pick(
    payload: StockPickRequest,
    settings: Settings = Depends(get_settings),
) -> StockPickResponse:
    llm = LLMFactory(settings).create(payload.llm_provider)
    search_provider = SearchFactory(settings).create(payload.search_provider)
    orchestrator = AgentOrchestrator(
        llm=llm,
        search_provider=search_provider,
        market_service=MarketDataService(enable_mocks=settings.enable_mocks),
        graph_service=KnowledgeGraphService(),
    )
    result = await orchestrator.analyze(
        symbol=payload.symbol,
        company_name=payload.company_name,
        query=payload.query,
        include_minutes=payload.include_minutes,
    )
    return StockPickResponse(**result)

