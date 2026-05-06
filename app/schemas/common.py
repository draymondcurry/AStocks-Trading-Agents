from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    title: str
    url: str
    snippet: str
    source_type: str
    published_at: datetime | None = None
    score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class AlphaSignal(BaseModel):
    name: str
    direction: str
    score: float
    reason: str


class AgentInsight(BaseModel):
    agent: str
    summary: str
    score: float
    signals: list[AlphaSignal] = Field(default_factory=list)
    sources: list[SourceItem] = Field(default_factory=list)

