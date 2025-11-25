from fastapi import APIRouter
import numpy as np


router = APIRouter()

@router.post("/ema")
def ema(values: list[float], period: int):
    ema_values = []
    k = 2 / (period + 1)
    for i, val in enumerate(values):
        if i == 0:
            ema_values.append(val)
        else:
            ema_values.append(val * k+ ema_values[i-1] * (1-k))
    return {"values": ema_values}
