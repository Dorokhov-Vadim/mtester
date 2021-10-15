from .trading import Trade
from .providers import Candle


class BaseCandleStrategy:
    def __init__(self):
        self.trade = Trade()

    def on_candle_close(self, event: Candle):
        raise Exception('CandleStrategy class must implement on_candle_close method')
