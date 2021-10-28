from typing import List, Dict
from .trading import Trade, Position
from .providers import Candle
from .instruments import Instrument


class BaseCandleStrategy:
    def __init__(self, window_size: int):
        self.trade = Trade()
        self.window_size = window_size
        self.candles_dict: Dict[Instrument, List] = {}

    def pos_by_ticker(self, ticker: str) -> Position:
        return self.trade.pos_by_ticker(ticker)

    def pos_by_instrument(self, instrument: Instrument) -> Position:
        return self.trade.pos_by_instrument(instrument)

    def set_defer_order(self, instrument: Instrument, oper, order_type, price: float, count: int):
        self.trade.set_defer_order(instrument, oper, order_type, price, count)

    def buy(self, instrument: Instrument, price: float, count: int, order_type):
        self.trade.buy(instrument, price, count, order_type)

    def sell(self, instrument: Instrument, price: float, count: int, order_type):
        self.trade.sell(instrument, price, count, order_type)

    def receive_data(self, candles: List[Candle]):
        for candle in candles:
            if self.trade.pos_by_instrument(candle.instrument) is None:
                self.trade.positions.append(Position(candle.instrument))
            if self.candles_dict.get(candle.instrument) is None:
                self.candles_dict[candle.instrument] = []
            if len(self.candles_dict[candle.instrument]) >= self.window_size:
                self.candles_dict[candle.instrument].pop(0)
            self.candles_dict[candle.instrument].append(candle)
        self.on_candle_close(candles)

    def on_candle_close(self, candles: List[Candle]):
        raise Exception('CandleStrategy class must implement on_candle_close method')
