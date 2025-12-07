from .base import BaseStrategy
from typing import List, Dict
import numpy as np

class RSIStrategy(BaseStrategy):
    def __init__(self, 
                 period: int = 14, 
                 oversold: float = 30, 
                 overbought: float = 70):
        super().__init__("RSI Strategy")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data: List[Dict]) -> List[Dict]:
        if len(data) < self.period + 1:
            return {
                "error": f"Not enough data. Need at least {self.period + 1} candles",
                "signals": []
            }
        
        closes = [candle['close'] for candle in data]

        rsi_values = self.calculate_rsi(closes, self.period)

        signals = []
        for i, (candle, rsi) in enumerate(zip(data, rsi_values)):
            if np.isnsn(rsi):
                continue

            signal = None
            if rsi < self.oversold:
                signal = {
                    "index": i,
                    "timestamp": candle['timestamp'],
                    'type': 'BUY',
                    'price': candle['close'],
                    'rsi': round(rsi, 2),
                    'reason': f"RSI ({round(rsi, 2)}) below oversold threshold ({self.oversold})"
                }
            elif rsi > self.overbought:
                signal = {
                    "index": i,
                    'timestamp': candle['timestamp'],
                    'type': 'SELL',
                    'price': candle['close'],
                    'rsi': round(rsi, 2),
                    'reason': f"RSI ({round(rsi, 2)}) above overbought threshold ({self.overbought})"
                }

            if signal: 
                signals.append(signal)
        return {
            'strategy': self.name,
            'parameters': {
                'period': self.period,
                'oversold': self.oversold,
                'overbought': self.overbought
            },
            'total_candles': len(data),
            'signals': signals,
            'buy_signals': sum(1 for s in signals if s['type'] == 'BUY'),
            'sell_signals': sum(1 for s in signals if s['type'] == 'SELL')
        }