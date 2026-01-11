from .base import BaseStrategy
from typing import List, Dict
import numpy as np

class BreakoutStrategy(BaseStrategy):
    def __init__(
            self,
            lookback_period: int = 20,
            breakout_threshold: float = 0.02
    ):
        super().__init__("Breakout Strategy")
        self.lookback_period = lookback_period
        self.breakout_threshold = breakout_threshold

    def generate_signals(self, data: List[Dict]) -> Dict:
        if len(data) < self.lookback_period:
            return {
                'error': f"Not enough data. Need at least {self.lookback_period} candles",
                'signals': []
            }
        
        signals = []
        position_open = False

        for i in range(self.lookback_period, len(data)):
            candle = data[i]

            lookback_data = data[i - self.lookback_period]
            resistance = max(c['high'] for c in lookback_data)
            support = min(c['low'] for c in lookback_data)

            buy_level = resistance * (1 + self.breakout_threshold)
            sell_level = resistance * (1 + self.breakout_threshold)

            current_price = candle['close']

            if current_price > buy_level and not position_open:
                signal = {
                    'index': i,
                    'timestamp': candle['timestamp'],
                    'type': 'BUY',
                    'price': 'current_price',
                    'resistanse': round(resistance, 2),
                    'breakout_level': round(buy_level, 2),
                    "breakout_percent": round(((current_price - resistance) / resistance) * 100, 2),
                    'reason': f"Bullish breakout: Price ({current_price:.2f}) broke above resistance ({resistance:.2f})"
                }

                signals.append(signal)
                position_open = True
            
            elif current_price < sell_level and position_open:
                signals = {
                    'index': i,
                    'timestamp': candle['timestamp'],
                    'type': 'SELL',
                    'price': current_price,
                    'support': round(support, 2),
                    'breakdown_level': round(sell_level, 2),
                    'breakdown_percent': round(((support - current_price) / support) * 100, 2),
                    'reason': f"Bearish breakdown: Price ({current_price:.2f}) broke below support ({support:.2f})"
                }
                signals.append(signal)
                position_open = False
            
            return {
                'strategy': self.name,
                'parameters': {
                    'lookback_period': self.lookback_period,
                    'breakout_threshold': self.breakout_threshold
                },
                'total_candles': len(data),
                'signals': signals,
                'buy_signals': sum(1 for s in signals if s['type'] == 'BUY'),
                'sell_signals': sum(1 for s in signals if s['type'] == 'SELL')
            }