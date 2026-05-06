import httpx
from fastapi import APIRouter, Depends, HTTPException

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
    try:
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
    except httpx.HTTPStatusError as exc:
        upstream = exc.response.text[:500] if exc.response is not None else str(exc)
        raise HTTPException(
            status_code=502,
            detail=f"外部服务返回错误: {upstream}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"外部服务请求失败: {exc}",
        ) from exc
    return StockPickResponse(**result)
