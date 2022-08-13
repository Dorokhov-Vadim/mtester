from .bases import BaseCandleIndicator
from typing import List
from ..providers import Candle

# Simple Moving Avarage indicator
class MovingAverage(BaseCandleIndicator):
    def __init__(self, data: List[Candle], size: int = 0):
        if len(data) < size:
            raise Exception("data size can't be less then size param")
        if size <= 0:
            self.candles = data
            self.size = len(data)
        else:
            self.candles = data[-size:]
            self.size = size

    def get_value(self):
        cn_sum = 0
        for candle in self.candles:
            cn_sum = cn_sum + candle.close
        return cn_sum/self.size

