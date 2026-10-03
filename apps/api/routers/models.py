from fastapi import APIRouter, Depends
from services.ai_core.registry import get_provider_registry, ProviderRegistry
from services.ai_core.router import get_intelligence_router, IntelligenceRouter, RouteRequest, RouteResult
from services.ai_core.provider_base import ModelCapability

router = APIRouter(prefix="/models", tags=["Model Providers & Intelligence Router"])

@router.get("/providers")
async def list_providers(registry: ProviderRegistry = Depends(get_provider_registry)):
    return registry.list_providers()

@router.get("/capabilities")
async def list_capabilities():
    return [c.value for c in ModelCapability]

@router.post("/route", response_model=RouteResult)
async def route_request(
    request: RouteRequest,
    router: IntelligenceRouter = Depends(get_intelligence_router)
):
    return router.route(request)
