from fastapi import APIRouter, HTTPException
import numpy as np
from typing import List
from pydantic import BaseModel, Field, validator

router = APIRouter()


# Pudantic schemas

class RSIStrategyRequest(BaseModel):
    rsi: List[float] = Field(..., min_items=1, description="RSI values")
    oversold: float = Field(30, ge=0, le=100, description="Oversold threshold")
    overbought: float = Field(70, ge=0, le=100, description="Overbought threshold")

    @validator('rsi')
    def validate_rsi_values(cls, v):
        if any(val < 0 or val > 100 for val in v):
            raise ValueError("RSI values nust be between 0 and 100")
        return v
    
class Signal(BaseModel):
    index: int
    type: str
    values: float

class RSIStrategyResponse(BaseModel):
    signals: List[Signal]
    total_buy_signals: int
    total_sell_signals: int

class EMARequest(BaseModel):
    values: List[float] = Field(..., min_items=1, description="Price values")
    period: int = Field(..., ge=2, le=200, description="EMA period")

class SMARequest(BaseModel):
    values: List[float] = Field(..., min_items=1, description="Price values")
    period: int = Field(..., ge=2, le=100, description="SMA period")

class RSIRequest(BaseModel):
    values: List[float] = Field(..., min_items=14, description="Price values (close)")
    period: int = Field(14, ge=2, le=50, description="RSI period")

class ATRRequest(BaseModel):
    high: List[float] = Field(..., min_items=2, description="High prices")
    low: List[float] = Field(..., min_items=2, description="Low prices")
    close: List[float] = Field(..., min_items=2, description="Close prices")
    period: int = Field(14, ge=2, le=50, description="ATR period")

    @validator('high', 'low', 'close')
    def validate_equal_lengths(cls, v, values):
        if 'high' in values and len(v) != len(values['high']):
            raise ValueError("high, low, and close must have the same length")
        
        if 'low' in values and len(v) != len(values['low']):
            raise ValueError('high, low, and close must have the same length')
        return v

class IndicatorResponse(BaseModel):
    values: List[float]
    period: int
    count: int

@router.post("/rsi-strategy", response_model=RSIStrategyResponse)
def rsi_strategy(request: RSIStrategyRequest):
    signals = []

    for i, value in enumerate(request.rsi):
        if value < request.oversold:
            signals.append(Signal(index=i, type='buy', value=value))
        elif value > request.overbought:
            signals.append(Signal(index=i, type="sell", value=value))

    buy_signals = sum(1 for s in signals if s.type == 'buy')
    sell_signals = sum(1 for s in signals if s.type == 'sell')
    
    return RSIStrategyResponse(
        signals=signals,
        total_buy_signals=buy_signals,
        total_sell_signals=sell_signals
    )

@router.post("/rsi", response_model=IndicatorResponse)
def calculate_rsi(request: RSIRequest):
    if len(request.values) < request.period + 1:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least {request.period + 1} values for RSI calculations"
        )

    values = np.array(request.values, dtype=float)
    deltas = np.diff(values)

    gain = np.where(deltas > 0, deltas, 0)
    loss = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gain[:request.period])
    avg_loss = np.mean(loss[:request.period])

    rsi_values = [np.nan] * request.period

    for i in range(request.period, len(deltas)):
        avg_gain = (avg_gain * (request.period - 1) + gain[i] / request.period)
        avg_loss = (avg_loss * (request.period - 1) + loss[i] / request.period)

        if avg_loss == 0:
            rsi = 100
        else: 
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        rsi_values.append(rsi)
    
    # Handle the first values
    if avg_loss == 0:
        rsi_values.append(100)
    else:
        rs = avg_gain / avg_loss
        rsi_values.append(100 - (100 / (1 + rs)))

    return IndicatorResponse(
        values=rsi_values,
        period=request.period,
        count=len(rsi_values)
    )

@router.post("/ema", response_model=IndicatorResponse)
def calculate_ema(request: EMARequest):

    if not request.values:
        raise HTTPException(status_code=400, detail="Values list cannot be empty")
    ema_values = []
    k = 2 / (request.period + 1)
    for i, val in enumerate(request.values):
        if i == 0:
            ema_values.append(val)
        else:
            ema_values.append(val * k+ ema_values[i-1] * (1-k))
    return IndicatorResponse(
        values=ema_values,
        period=request.period,
        count=len(ema_values)
    )

@router.post("/sma", response_model=IndicatorResponse)
def calculte_sma(request: SMARequest):

    if len(request.values) < request.period:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least {request.period} values for SMA calculation"
        )
    values = np.array(request.values, dtype=float)

    # Pad with NaN for the first (period - 1) values
    sma_values = [np.nan] * (request.period - 1)

    #Calculate SMA using convolution
    sma = np.convolve(values, np.ones(request.period)/request.period, mode='valid')
    sma_values.extend(sma.tolist())

    return IndicatorResponse(
        values=sma_values,
        period=request.period,
        count=len(sma_values)
    )

@router.post("/atr", response_model=IndicatorResponse)
def calculate_atr(request: ATRRequest):

    if len(request.close) < request.period + 1:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least {request.period + 1} values for ATR calculation"
        )
    
    high = np.array(request.high, dtype=float)
    low = np.array(request.low, dtype=float)
    close = np.array(request.close, dtype=float)

    
    tr = np.zeros(len(close))
    tr[0] = high[0] - low[0]

    for i in range(1, len(close)):
        tr[i] = max(
            high[i] - low[i],
            abs(high[i] - close[i - 1]),
            abs(low[i] - close[i - 1])
        )
    
    atr_values = [np.nan] * request.period

    atr_prev = np.mean(tr[1:request.period+1])

    for i in range(request.period+1, len(close)):
        atr_prev = (atr_prev * (request.period - 1) + tr[i]) / request.period
        atr_values[i] = atr_prev
    
    return IndicatorResponse(
        values=atr_values,
        period=request.period,
        count=len(atr_values)
    )

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "indicators",
        "available_endpoints": [
            "/rsi",
            "/ema",
            "/sma",
            "/atr",
            "/rsi-strategy"
        ]
    }