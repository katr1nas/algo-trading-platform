import yfinance as yf
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import pandas as pd

router = APIRouter()

class OHLCVData(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class MarketDataResponse(BaseModel):
    ticker: str
    period: str
    interval: str
    data: List[OHLCVData]
    count: int

def load_data(
        ticker: str,
        period: str = "1mo",
        interval: str = "1h"
) -> MarketDataResponse:
    try:
        data = yf.download(
            ticker, 
            period=period,
            interval=interval,
            progress=False
        )

        if data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for ticker {ticker} with period={period} and interval={interval}"
            )
        
        data = data.reset_index()
        datetime_col = 'Datetime' if 'Datetime' in data.columns else 'Date'

        result = []
        for _, row in data.iterrows():
            try:
                result.append(OHLCVData(
                    timestamp=row[datetime_col].isoformat(),
                    open = float(row["Open"]),
                    low = float(row['Low']),
                    close = float(row['Close']),
                    high = float(row['High']),
                    volume = float(row['Volume']),   
                ))
            except (KeyError, ValueError) as e:
                continue
        if not result:
            raise HTTPException(
                status_code=500,
                detail=f"Failse to parse data for ticker {ticker}"
            )
        return MarketDataResponse(
            ticker=ticker,
            period=period,
            interval=interval,
            data=result, count=len(result)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching data for {ticker}: {str(e)}"
        )
    
@router.get("/nasdaq", response_model=MarketDataResponse)
def get_nasdaq(
    period: str = Query("1mo", description="Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"),
    interval: str = Query("1h", description="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)")
):
    return load_data("QQQ", period, interval)

@router.get("/gold", response_model=MarketDataResponse)
def get_gold(
    period: str = Query("1mo", description="Data period"),
    interval: str = Query("1h", description="Data interval")
):
    return load_data("GC=F", period, interval)

@router.get('/eurusd', response_model=MarketDataResponse)
def get_eurusd(
    period: str = Query("1mo", description="Data period"),
    interval: str = Query("1h", description="Data interval")
):
    return load_data("EURUSD=X", period, interval)

@router.get("/gbpusd", response_model=MarketDataResponse)
def gbpusd(
        period: str = Query("1mo", description="Data period"),
        interval: str = Query("1h", description="Data interval")
):
    return load_data("GBPUSD=X", period, interval)

@router.get("/custom/{ticker}", response_model=MarketDataResponse)
def get_custom_ticker(
    ticker:str,
    period: str = Query("1mo", description="Data period"),
    interval: str = Query("1h", description="Data interval")
):
    if not ticker or len(ticker) > 20:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticker symbol"
        )
    
    return load_data(ticker.upper(), period, interval)

@router.get("/status")
def data_service_status():
    try:
        test_data = yf.download('QQQ', period='1d', interval='1h', progress=False)

        return {
            "status": "healthy",
            "service": "market_data",
            "yfinance_connection": "ok" if not test_data.empty else 'degraded',
            "supported_tickers": ["QQQ (NASDAQ)", "GC=F (Gold)", "EURUSD=X", "GBPUSD=X"],
            "supported_periods": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
            "supported_intervals": ["1m", "2m", "5m", "15m", "30m", "60m", "1h", "1d", "5d", "1wk", "1mo"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "market_data",
            "error": str(e)
        }

@router.get("/latest_{ticker}")
def get_latest_price(ticker: str):
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info

        hist = ticker_obj.history(period="1d")
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data available for {ticker}")
        
        latest = hist.iloc[-1]

        return {
            "ticker": ticker,
            "price": float(latest['Close']),
            "open": float(latest['Open']),
            "high": float(latest['High']),
            "low": float(latest['Low']),
            "volume": float(latest['Volume']),
            "timestamp": latest.name.isoformat(),
            "currency": info.get('currency', 'USD')
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching latest price for {ticker}: {str(e)}"
        )