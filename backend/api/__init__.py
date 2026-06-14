from .dashboard import router as dashboard_router
from .customers import router as customers_router
from .segments import router as segments_router
from .campaigns import router as campaigns_router
from .receipts import router as receipts_router
from .ingest import router as ingest_router

__all__ = [
    "dashboard_router",
    "customers_router",
    "segments_router",
    "campaigns_router",
    "receipts_router",
    "ingest_router"
]
