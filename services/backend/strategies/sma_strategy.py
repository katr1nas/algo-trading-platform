from .base import BaseStrategy
import numpy as np
from typing import List, Dict

class SMACrossoverStrategy(BaseStrategy):
    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        super().__init__("SMA Crossover Strategy")

        if fast_period >= slow_period:
            raise ValueError("Fast period must be less then slow period")
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signals(self, data: List[Dict]) -> Dict:
        if len(data) < self.slow_period:
            return {
                'error': f'Not enough data. Need at least {self.slow_period} candles',
                'signals': []
            }
        
        closes = [candle['close'] for candle in data]

        fast_sma = self.calculate_sma(self.fast_period)
        slow_sma = self.calculate_sma(self.slow_period)

        signals = []
        position_open = False

        for i in range(len(data)):
            if np.isnan(fast_sma[i]) or np.isnan(slow_sma[i]):
                continue
            if i == 0 or np.isnan[fast_sma[i-1]] or np.isnan(slow_sma[i-1]):
                continue

            prev_fast = fast_sma[i - 1]
            prev_slow = slow_sma[i - 1]
            curr_fast = fast_sma[i]
            curr_slow = slow_sma[i]

            candle = data[i]

            if prev_fast <= prev_slow and curr_fast > curr_slow and not position_open:
                signal = {
                    'index': i,
                    'timestamp': candle['timestamp'],
                    'type': 'BUY',
                    'price': candle['close'],
                    'fast_sma': round(curr_fast, 2),
                    'slow_sma': round(curr_slow, 2),
                    'reason': f'Golden Cross: Fast SMA({self.fast_period}) crossed above Slow SMA({self.slow_period})'
                }
                signals.append(signal)
                position_open = True
            elif prev_fast >= prev_slow and curr_fast < curr_slow and position_open:
                signal = {
                    'index': i,
                    'timestamp': candle['timestamp'],
                    'type': 'SELL',
                    'price': candle['close'],
                    'fast_sma': round(curr_fast, 2),
                    'slow_sma': round(curr_slow, 2),
                    'reason': f'Death Cross: Fast SMA({self.fast_period}) crossed below Slow SMA({self.slow_period})'
                }
                signals.append(signal)
                position_open = False
                
        return {
            "strategy": self.name,
            "parameters": {
                "fast_period": self.fast_period,
                "slow_period": self.slow_period
            },
            "total_candles": len(data),
            "signals": signals,
            "buy_signals": sum(1 for s in signals if s['type'] == 'BUY'),
            "sell_signals": sum(1 for s in signals if s['type'] == 'SELL'),
            "indicators": {
                "fast_sma": [round(x, 2) if not np.isnan(x) else None for x in fast_sma],
                "slow_sma": [round(x, 2) if not np.isnan(x) else None for x in slow_sma]
            }
        }
