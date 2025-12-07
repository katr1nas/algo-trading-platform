from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from services.backtest_service import BacktestEngine
import sys
sys.path.append('..')

from strategies.rsi_strategy import RSIStrategy
from endpoints.ohlcv import load_data

router = APIRouter()

class BacktestRequest(BaseModel):
    ticker: str = Field(..., description='Ticker symbol')
    period: str = Field('1mo', description='Data period')
    interval: str = Field('1h', description='Data interval')
    strategy_type: str = Field(..., description="Strategy type (rsi, ema, sma, etc)")

    rsi_period: Optional[int] = Field(14, description="RSI period")
    oversold: Optional[float] = Field(30, description="Oversold threshold")
    overbought: Optional[float] = Field(70, description="Overbought Threshold")

    initial_capital: float = Field(10000, ge=100, description="Initial capital")
    comission: float = Field(0.001, ge=0, le=0.1, description = 'Comission rate')
    position_size: float = Field(1.0, ge=0.1, le=1.0, description="Position size")

class StrategyRequest(BaseModel):
    ticker: str = Field(..., description="Ticker symbol (QQQ, GC=F, EURUSD=X, GBPUSD=X)")
    period: str = Field("1mo", description="Data period")
    interval: str = Field("1h", description="Data interval")

class RSIStrategyRequest(StrategyRequest):
    rsi_period: int = Field(14, ge=2, le=50, description="RSI period")
    oversold: float = Field(30, ge=0, le=100, description="Oversold threshold")
    overbought: float = Field(70, ge=0, le=100, description="Overbought threshold")

class StrategyListResponse(BaseModel):
    strategies: List[Dict]

@router.get("/list", response_model=StrategyListResponse)
def get_strategies():
    return {
        "strategies": [
            {
                'name': 'RSI Strategy',
                'description': "Buy when RSI < 30, Sell when RSI > 70",
                'type': 'indicator_based',
                'parameters': ['period', 'oversold', 'overbought']
            },
            {
                'name': 'EMA Crossover',
                'description': 'Buy when fast EMA crosses above slow EMA',
                'type': 'indicator_based',
                'parameters': ['fast_period', 'slow_period'],
                'status': 'coming_soon'
            },
            {
                'name': 'Breakout Strategy',
                'description': 'Buy when price breaks resistance',
                'type': 'price_action',
                'parameters': ['lookback_period', 'threshold'],
                'status': 'coming_soon'
            },
            {
                'name': "ORB (Opening Range Breakout)",
                'description': 'Trade breakouts from opening range',
                'type': 'price_action',
                'parameters': ['range_minutes'],
                'status': 'coming_soon'
            },
            {
                'name': 'ML Linear Regression',
                'description': 'Predict price using linear regression',
                'type': 'machine_learning',
                'parameters': ['feature', 'lookback'],
                'status': 'coming_soon'
            }
        ]
    }

@router.post("/rsi-strategy")
def run_rsi_strategy(request: RSIStrategyRequest):
    try:
        market_data = load_data(request.ticker, request.period, request.interval)

        if not market_data.data:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for {request.ticker}"
            )
        
        data_list = [
            {
                'timestamp': candle.timestamp,
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume
            }
            for candle in market_data.data
        ]

        strategy = RSIStrategy(
            period=request.rsi_period,
            oversold=request.oversold,
            overbought=request.overbought
        )

        signals = strategy.generate_signals(data_list)

        signals['ticker'] = request.ticker
        signals['data_period'] = request.period
        signals['data_interval'] = request.interval

        return signals
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Error running RSI strategy: {str(e)}'
        )
    
@router.get("/status")
def strategy_service_status():
    return {
        "status": 'healthy',
        'service': 'strategies',
        'available_strategies': 1,
        'coming_soon': 4
    }

@router.post("/backtest")
def run_backtest(request: BacktestRequest):
    try: 
        market_data = load_data(request.ticker, request.period, request.interval)

        if not market_data.data:
            raise HTTPException(
                status_code = 404,
                detail=f"No data available for {request.ticker}"
            )

        data_list = [
            {
                'timestamp': candle.timestamp,
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume
            }
            for candle in market_data.data
        ]

        if request.strategy_type.lower() == 'rsi':
            strategy = RSIStrategy(
                period=request.rsi_period,
                oversold=request.oversold,
                overbought=request.overbought
            )
            signal_result = strategy.generate_signals(data_list)
            signals = signal_result['signals']
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Strategy type '{request.strategy_type}' not supported yet"
            )
    
        backtest_engine = BacktestEngine(
            initital_capital=request.initial_capital,
            commision=request.comission,
            position_size=request.position_size
        )

        results = backtest_engine.run_backtest(signals, data_list)

        results['ticker'] = request.ticker
        results['period'] = request.period
        results['interval'] = request.interval
        results['strategy'] = request.strategy_type
        results['strategy_parameters'] = {
            'rsi_period': request.rsi_period,
            'oversold': request.oversold,
            'overbought': request.overbought
        }

        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error running backtest: {str(e)}"
        )