from fastapi import APIRouter
import numpy as np

router = APIRouter()

@router.post("/sma")
def sma(values: list[float], period: int):
    values = np.array(values)
    if len(values) < period:
        return {"values": []}
    sma = np.convolve(values, np.ones(period)/period, mode='valid')
    return {"values": sma.tolist()}