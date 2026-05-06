from fastapi import APIRouter, Depends

from app.core.settings import Settings, get_settings
from app.schemas.market import FundamentalsResponse
from app.services.market.data_service import MarketDataService

router = APIRouter()


@router.get("/kline")
async def kline(
    symbol: str,
    period: str = "daily",
    start_date: str | None = None,
    end_date: str | None = None,
    adjust: str = "",
    settings: Settings = Depends(get_settings),
) -> dict:
    service = MarketDataService(enable_mocks=settings.enable_mocks)
    return {
        "symbol": symbol,
        "period": period,
        "items": service.get_kline(symbol, period, start_date, end_date, adjust),
    }


@router.get("/fundamentals", response_model=FundamentalsResponse)
async def fundamentals(symbol: str, settings: Settings = Depends(get_settings)) -> FundamentalsResponse:
    service = MarketDataService(enable_mocks=settings.enable_mocks)
    data = service.get_fundamentals(symbol)
    return FundamentalsResponse(symbol=symbol, metrics=data)

