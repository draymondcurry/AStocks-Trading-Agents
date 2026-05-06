from fastapi import APIRouter, Depends

from app.core.settings import Settings, get_settings
from app.schemas.search import SearchQuery, SearchResponse
from app.services.search.factory import SearchFactory

router = APIRouter()


@router.post("/query", response_model=SearchResponse)
async def query_search(payload: SearchQuery, settings: Settings = Depends(get_settings)) -> SearchResponse:
    provider = SearchFactory(settings).create(payload.provider)
    items = await provider.search(payload.query, payload.max_results)
    return SearchResponse(provider=provider.provider, items=items)

