from .base import BaseStrategy
from typing import List, Dict
import numpy as np

class EMACrossoverStrategy(BaseStrategy):
    def __init__(self, fast_period: int = 12, slow_period: int = 26):
        super().__init__("Ema Crossover Strategy")
        if fast_period >= slow_period:
            raise ValueError("Fast period must be less than slow period")
        
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signals(self, data: List[Dict]) -> Dict:
        if len(data) < self.slow_period:
            return {
                'error': f"Not enough data. Need at least {self.slow_period} candles",
                "signals": []
            }

        closes = [candle['close'] for candle in data]

        fast_ema = self.calculate_ema(closes, self.fast_period)
        slow_ema = self.calculate_ema(closes, self.slow_period)

        signals = []
        position_open = False

        for i in range(1, len(data)):
            if i < self.slow_period:
                continue
            
            prev_fast = fast_ema[i - 1]
            prev_slow = slow_ema[i - 1]
            curr_fast = fast_ema[i]
            curr_slow = slow_ema[i]

            candle = data[i]

            if prev_fast <= prev_slow and curr_fast > curr_slow and not position_open:
                signal = {
                    'index': i,
                    'timestamp': candle['timestamp'],
                    'type': 'BUY',
                    'price': candle['close'],
                    'fast_ema': round(curr_fast, 2),
                    'slow_ema': round(curr_slow, 2),
                    'reason': f"Golden Cross: Fast EMA({self.fast_period}) crosses above Slow EMA({self.slow_period})"
                }
                signals.append(signal)
                position_open = True
            
            elif prev_fast >= prev_slow and curr_fast < curr_slow and position_open:
                signal = {
                    'index': i,
                    'timestamp': candle['timestamp'],
                    'type': 'SELL',
                    'price': candle['close'],
                    'fast_ema': round(curr_fast, 2),
                    'slow_ema': round(curr_slow, 2),
                    'reason': f"Death Cross: Fast EMA({self.fast_period}) crosses below Slow EMA({self.slow_period})"
                }
                signals.append(signal)
                position_open = False
            
            return {
                'strategy': self.name,
                'parameters': {
                    'fast_period': self.fast_period,
                    'slow_period': self.slow_period
                },
                'total_candles': len(data),
                'signals': signals,
                'buy_signals': sum(1 for s in signals if s['type'] == 'BUY'),
                'sell_signals': sum(1 for s in signals if s['type'] == 'SELL'),
                'indicators': {
                    'fast_ema': [round(x, 2) for x in fast_ema],
                    'slow_ema': [round(x, 2) for x in slow_ema]
                }
            }
        