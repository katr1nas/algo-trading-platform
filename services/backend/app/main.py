from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import router as api_router

from app.api.v1.endpoints import indicators as indicators_router
from app.api.v1.endpoints import ohlcv as ohlcv_router


app = FastAPI(title="Algorithmic Trading Research Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins
    allow_credentials=True,
    allow_methods=["*"],   # allow all HTTP methods
    allow_headers=["*"],   # allow all headers
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(indicators_router.router, prefix="/api/v1/indicators")
app.include_router(ohlcv_router.router, prefix="/api/v1")

