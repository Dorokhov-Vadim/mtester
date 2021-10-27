from typing import List
from .trading import Trade
from .providers import Candle


class BaseCandleStrategy:
    def __init__(self):
        self.trade = Trade()

    def on_candle_close(self, candles: List[Candle]):
        raise Exception('CandleStrategy class must implement on_candle_close method')
