from typing import List
import numpy as np

def atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> np.ndarray:
    high = np.array(high, dtype=float)
    low = np.array(high, dtype=float)
    close = np.array(close, dtype=float)

    if len(close) < period + 1:
        raise ValueError("Not enough data for ATR calculation")
    
    tr = np.zeros(len(close))
    tr[0] = high[0] - low[0]

    for i in range(1, len(close)):
        tr[i] = max(
            high[i] - low[i],
            abs(high[i] - close[i - 1]),
            abs(low[i] - close[i - 1])
        )
    
    atr_values = np.zeros(len(close))
    atr_values[:period] = np.nan

    atr_prev = np.mean(tr[1:period+1])

    for i in range(period+1, len(close)):
        atr_prev = (atr_prev * (period - 1) + tr[i]) / period
        atr_values[i] = atr_prev
    
    return atr_values
