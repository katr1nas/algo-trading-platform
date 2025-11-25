from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import router as api_router
from indicators import ema, sma
from strategies import rsi_strategy

app = FastAPI(title="Algorithmic Trading Research Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(ema.router, prefix="/api/v1/indicators")
app.include_router(sma.router, prefix="/api/v1/indicators")
app.include_router(rsi_strategy.router, prefix="/api/v1/strategies")
