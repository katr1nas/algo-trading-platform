from .base import BaseStrategy
from typing import List, Dict
from datetime import datetime, time

class ORBStrategy(BaseStrategy):
    def __init__(
            self,
            range_minutes: int = 30,
            min_range_size: float = 0.005
):
        super().__init__("ORB Strategy")
        self.range_minutes = range_minutes,
        self.min_range_size = min_range_size
    
    def generate_signals(self, data: List[Dict]) -> Dict:
        if len(data) < self.range_minutes + 1:
            return {
                'error': f"Not enough data. Need at least {self.range_minutes + 1} candles",
                'signals': []
            }
        
        signals = []
        current_day_start = None
        opening_range_high = None
        opening_range_low = None
        position_open = False

        for i, candle in enumerate(data):
            try: 
                if isinstance(candle['timestamp'], str):
                    ts = datetime.fromisoformat(candle['timestamp'].replace('Z', '+00:00'))
                else:
                    ts = candle['timestamp']
                
                current_date = ts.date()

                if current_day_start is None or current_date != current_day_start:
                    current_day_start = current_date
                    opening_range_high = None
                    opening_range_low = None
                    position_open = False

                    if i + self.range_minutes < len(data):
                        range_data = data[i:i + self.range_minutes]
                        opening_range_high = max(c['high'] for c in range_data)
                        opening_range_low = min(c['low'] for c in range_data)

                        range_size = (opening_range_high - opening_range_low) / opening_range_low
                        if range_size < self.min_range_size:
                            opening_range_high = None
                            opening_range_low = None
                    continue

                if opening_range_high is None or opening_range_low is None:
                    continue

                current_price = candle['close']

                if current_price > opening_range_high and not position_open:
                    signal = {
                        'index': i,
                        'timestamp': candle['timestamp'],
                        'type': 'BUY',
                        'price': current_price,
                        'opening_range_high': round(opening_range_high, 2),
                        'opening_range_low': round(opening_range_low, 2),
                        'breakout_percent': round(((current_price - opening_range_high) / opening_range_high) * 100, 2),
                        'reason': f"ORB Buy: Price broke above opening eange high ({opening_range_high:.2f})"
                    }
                    signals.append(signal)
                    position_open = True

                elif current_price < opening_range_low and position_open:
                    signal = {
                        'index': i,
                        'timestamp': candle['timestamp'],
                        'type': 'SELL',
                        'price': current_price,
                        'opening_range_high': round(opening_range_high, 2),
                        'opening_range_low': round(opening_range_low, 2),
                        'breakdown_percent': round(((opening_range_low - current_price) / opening_range_low) * 100, 2),
                        'reason': f"ORB Sell: Price broke below opening range low ({opening_range_low:.2f})"
                    }
                    signals.append(signal)
                    position_open = False
            except Exception as e:
                continue

        return {
            'strategy': self.name, 
            'parameters': {
                'range_minutes': self.range_minutes,
                'min_range_size': self.min_range_size
            },
            'total_candles': len(data),
            'signals': signals,
            'buy_signals': sum(1 for s in signals if s['type'] == 'BUY'),
            'sell_signals': sum(1 for s in signals if s['type'] == 'SELL')
        }