from fastapi import APIRouter

from app.api.routes import analysis, frontend, health, market, memory, providers, search

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(frontend.router, prefix="/frontend", tags=["frontend"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
