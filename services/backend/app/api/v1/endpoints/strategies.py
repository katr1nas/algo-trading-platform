from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.services.backtest_service import BacktestEngine
from strategies.ema_strategy import EMACrossoverStrategy
from strategies.sma_strategy import SMACrossoverStrategy
from strategies.breakout_strategy import BreakoutStrategy
from strategies.orb_strategy import ORBStrategy
from strategies.ml_strategy import MLPredictionStrategy, MLDirectionStrategy
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

    # RSI strategy parameters
    rsi_period: Optional[int] = Field(14, description="RSI period")
    oversold: Optional[float] = Field(30, description="Oversold threshold")
    overbought: Optional[float] = Field(70, description="Overbought Threshold")

    # EMA/SMA strategy parameters
    fast_period: Optional[int] = Field(14, description="Fast EMA/SMA period"),
    slow_period: Optional[int] = Field(26, description="Slow EMA/SMA period")

    # Breakout stratey paraneters
    lookback_period: Optional[List] = Field(20),
    breakout_threshold: Optional[float] = Field(0.02)

    # ORB parameters
    range_minutes: Optional[int] = Field(30)
    min_range_size = Optional[float] = Field(0.005)

    # ML parameters
    ml_lookback: Optional[int] = Field(30)
    prediction_threshold: Optional[int] = Field(0.01)
    confidence_threshold: Optional[int] = Field(0.65)


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

class EMAStrategyRequest(StrategyRequest):
    fast_period: int = Field(12, ge=2, le=100, description="Fast EMA period")
    slow_period: int = Field(26, ge=2, le=200, description="Slow EMA period")

class SMAStrategyRequest(StrategyRequest):
    fast_period: int = Field(20, ge=2, le=100, description="Fast SMA period")
    slow_period: int = Field(50, ge=2, le=200, description="Slow SMA period")

class BreakoutStrategyRequest(StrategyRequest):
    lookback_period: int = Field(20, ge=5, le=100, description='Lookback period for high/low')
    breakout_threshold: float = Field(0.02, ge=0, le=0.1, description='Breakout threshold (e.g., 0.02 = 2%)')

class ORBStrategyRequest(StrategyRequest):
    range_minutes: int = Field(30, ge=5, le=120, description='Opening range duration in minutes')
    min_range_size: float = Field(0.005, ge=0, le=0.05, description="Minimum range size to avoid false signals")

class MLPredictionStrategyRequest(StrategyRequest):
    lookback: int = Field(10, ge=5, le=30, description='Feature lookback period')
    prediction_threshold: float = Field(0.01, ge=0.005, le=0.05, description='Minimum predicted % move')
    confidence_thresold: float = Field(0.6, ge=0.5, le=0.95, description='Minimum confidence')

class MLDirectionStrategyRequest(StrategyRequest):
    lookback: int = Field(10, ge=5, le=30, description='Feature lookback period')
    confidence_thresold: float = Field(0.65, ge=0.5, le=0.95, description='Minimum confidence')

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
            raise HTTPException(status_code=404, detail=f"No data for {request.ticker}")
        
        data_list = [
            {
                "timestamp": candle.timestamp,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume
            }
            for candle in market_data.data
        ]
        
        # Select and initialize strategy
        strategy_type = request.strategy_type.lower()
        
        if strategy_type == "rsi":
            strategy = RSIStrategy(request.rsi_period, request.oversold, request.overbought)
        elif strategy_type == "ema":
            strategy = EMACrossoverStrategy(request.fast_period, request.slow_period)
        elif strategy_type == "sma":
            strategy = SMACrossoverStrategy(request.fast_period, request.slow_period)
        elif strategy_type == "breakout":
            strategy = BreakoutStrategy(request.lookback_period, request.breakout_threshold)
        elif strategy_type == "orb":
            strategy = ORBStrategy(request.range_minutes, request.min_range_size)
        elif strategy_type == 'ml_prediction':
            strategy = MLPredictionStrategy(request.ml_lookback, request.prediction_threshold, request.confidence_threshold)
        elif strategy_type == 'ml_direction':
            strategy = MLDirectionStrategy(request.ml_lookback, request.confidence_threshold)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Strategy '{strategy_type}' not supported. Use: rsi, ema, sma, breakout, orb"
            )
        
        signal_result = strategy.generate_signals(data_list)
        signals = signal_result['signals']
        
        # Run backtest
        backtest_engine = BacktestEngine(
            initial_capital=request.initial_capital,
            commission=request.commission,
            position_size=request.position_size
        )
        
        results = backtest_engine.run_backtest(signals, data_list)
        results['ticker'] = request.ticker
        results['period'] = request.period
        results['interval'] = request.interval
        results['strategy'] = strategy_type
        results['strategy_parameters'] = signal_result['parameters']

        if 'model_metrics' in signal_result and signal_result['model_metrics']:
            results['ml_model_metrics'] = signal_result['model_metrics']
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {str(e)}")

@router.post('/ema-strategy')
def run_ema_strategy(request: EMACrossoverStrategy):
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

        strategy = EMACrossoverStrategy(
            fast_period=request.fast_period,
            slow_period=request.slow_period
        )

        signals = strategy.generate_signals(data_list)
        signals['ticker'] = request.ticker
        signals['data_period'] = request.fast_period
        signals['data_interval'] = request.interval

        return signals

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running EMA strategy: {str(e)}"
        )

@router.post('/sma-strategy')
def run_sma_strategy(request: SMAStrategyRequest):
    try:
        market_data = load_data(request.ticker, request.period, request.interval)
        
        if not market_data.data:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for {request.ticker}"
            )
        
        data_list = [
            {
                "timestamp": candle.timestamp,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume
            }
            for candle in market_data.data
        ]
        
        strategy = SMACrossoverStrategy(
            fast_period=request.fast_period,
            slow_period=request.slow_period
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
            detail=f"Error running SMA strategy: {str(e)}"
        )
    
@router.post("/breakout-strategy")
def run_breakout_strategy(request: BreakoutStrategyRequest):
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

        strategy = BreakoutStrategy(
            lookback_period=request.lookback_period,
            breakout_threshold=request.breakout_threshold
        )

        signals = strategy.generate_signals(data_list),
        signals['ticker'] = request.ticker,
        signals['data_period'] = request.period
        signals['data_interval'] = request.interval

        return signals
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running Breakout strategy: {str(e)}"
        )
    
@router.post("/orb-strategy")
def run_orb_strategy(request: ORBStrategyRequest):
    try: 
        market_data = load_data(request.ticker, request.period, request.interval)

        if not market_data.data:
            raise HTTPException(
                status_code=404, 
                detail=f"Not available for {request.ticker}"
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

        strategy = ORBStrategy(
            range_minutes=request.range_minutes,
            min_range_size=request.min_range_size
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
            detail = f"Error running ORB strategy: {str(e)}"
        )
    
@router.post('/ml-prediction-strategy')
def run_ml_prediction_strategy(request:MLPredictionStrategyRequest):
    try:
        market_data = load_data(request.ticker, request.period, request.interval)

        if not market_data.data:
            raise HTTPException(status_code=404, detail=f"No data for {request.ticker}")
        
        data_list = [{
            'open': candle.open,
            'high': candle.high,
            'low': candle.low,
            'close': candle.close,
            'volume': candle.volume
        } for candle in market_data.data]

        strategy = MLPredictionStrategy(
            lookback=request.lookback,
            prediction_thresold=request.prediction_threshold,
            confidence_threshold=request.confidence_thresold
        )

        signals = strategy.generate_signals(data_list)
        signals['ticker'] = request.ticker
        signals['period'] = request.period
        signals['data_interval'] = request.interval
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
@router.post('ml_direction-strategy')
def run_ml_direction_strategy(request: MLDirectionStrategy):
    try: 
        market_data = load_data(request.ticker, request.period, request.interval)

        if not market_data.data:
            raise HTTPException(status_code=404, detail=f"Not available data for {request.ticker}")
        
        data_list = [
            {
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume
            } for candle in market_data.data
        ]

        signals = request.generate_signals(request.lookback, request.confidence_threshold)
        signals['ticker'] = request.ticker
        signals['data_period'] = request.period
        signals['data_interval'] = request.interval

        return signals
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")