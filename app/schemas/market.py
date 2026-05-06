from typing import Any

from pydantic import BaseModel, Field


class KlineQuery(BaseModel):
    symbol: str
    period: str = "daily"
    start_date: str | None = None
    end_date: str | None = None
    adjust: str = ""


class FundamentalsResponse(BaseModel):
    symbol: str
    metrics: dict[str, Any] = Field(default_factory=dict)

