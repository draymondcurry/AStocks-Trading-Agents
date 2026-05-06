from pydantic import BaseModel, Field

from app.schemas.common import SourceItem


class SearchQuery(BaseModel):
    query: str
    max_results: int = Field(default=8, ge=1, le=20)
    provider: str | None = None


class SearchResponse(BaseModel):
    provider: str
    items: list[SourceItem]

