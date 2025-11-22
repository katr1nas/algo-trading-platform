from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd

router = APIRouter()

class PriceData(BaseModel):
    close: list
    period: int

def compute_rsi(close, period):
    df = pd.DataFrame(close, columns=["close"])
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0).tolist()

@router.post("/indicators/rsi")
def rsi_endpoint(data: PriceData):
    result = compute_rsi(data.close, data.period)
    return {"rsi": result}

@router.get("/status")
def status():
    return {"status": "ok"}

@router.get("/strategies/list")
def get_strategies():
    return [
        {"name": "mean_reversion", "description": "Simple MR strategy"},
        {"name": "breakout", "description": "Basic breakout logic"}
    ]

