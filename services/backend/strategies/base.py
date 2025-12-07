from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np

class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name
        self.signals = []
    
    @abstractmethod
    def generate_signals(self, data: List[Dict]) -> List[Dict]:
        pass
    
    def calculate_rsi(self, closes: List[float], period: int = 14) -> List[float]:
        closes = np.array(closes, dtype=float)
        deltas = np.diff(closes)

        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gain[:period])
        avg_loss = np.mean(loss[:period])

        rsi_values = [np.nan] * period

        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gain[i]) / period
            avg_loss = (avg_loss * (period - 1) + loss[i]) / period

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)

        if avg_loss == 0:
            rsi_values.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi_values.append(100 - (100 / (1 + rs)))

        return rsi_values
    
    def calculate_ema(self, values: List[float], period: int) -> List[float]:
        ema_values = []
        k = 2 / (period + 1)

        for i, val in enumerate(values):
            if i == 0:
                ema_values.append(val)
            else: 
                ema_values.append(val * k + ema_values[i - 1] * (1 - k))
        
        return ema_values
    
    def calculate_sma(self, values: List[float], period: int) -> List[float]:
        sma_values = []
        for i in range(len(values)):
            if i < period - 1:
                sma_values.append(np.nan)
            else: 
                sma_values.append(np.mean(values[i - period + 1:i + 1]))
        
        return sma_values
    
