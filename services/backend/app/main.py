# ==================== File: app/api/v1/routes.py ====================
from fastapi import APIRouter
from app.api.v1.endpoints import indicators, strategies, data

router = APIRouter()

# Include all endpoint routers
router.include_router(
    indicators.router,
    prefix="/indicators",
    tags=["Technical Indicators"]
)

router.include_router(
    strategies.router,
    prefix="/strategies",
    tags=["Trading Strategies"]
)

router.include_router(
    data.router,
    prefix="/data",
    tags=["Market Data"]
)