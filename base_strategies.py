from .trading import Trade, CandleEvent


class BaseCandleStrategy:
    def __init__(self):
        self.trade = Trade()

    def on_candle_close(self, event: CandleEvent):
        raise Exception('CandleStrategy class must implement on_candle_close method')
