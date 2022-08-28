from .bases import BaseCandleIndicator
from typing import List
from ..providers import Candle

# Simple Moving Avarage indicator
class MovingAverage(BaseCandleIndicator):
    def __init__(self, size: int = 0):
        self.size = size

    def get_value(self, candles: List[Candle]):
        if len(candles) < self.size:
            return None
        candles = candles[-self.size:]
        cn_sum = 0
        for candle in candles:
            cn_sum = cn_sum + candle.close
        return cn_sum/self.size

