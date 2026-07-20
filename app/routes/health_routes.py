from fastapi import APIRouter, Depends

from app.dependencies import get_health_service
from app.schemas.health_schema import HealthSummarySchema
from app.services.health_service import HealthService

router = APIRouter(
    prefix="/api/health",
    tags=["Health"],
)


@router.get("/scrapers", response_model=HealthSummarySchema)
def get_scraper_health(
    service: HealthService = Depends(get_health_service),
):
    sources = service.get_health_summary()

    return {
        "total_sources": len(sources),
        "healthy": sum(1 for s in sources if s["status"] == "healthy"),
        "degraded": sum(1 for s in sources if s["status"] == "degraded"),
        "down": sum(1 for s in sources if s["status"] == "down"),
        "sources": sources,
    }
