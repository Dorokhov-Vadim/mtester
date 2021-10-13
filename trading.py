from typing import List, Dict
from .instruments import Instrument


class CandleEvent:
    def __init__(self):
        self.candle_num = 0
        self.open_price = 0
        self.max_price = 0
        self.min_price = 0
        self.close_price = 0
        self.volume = 0
        self.date = None
        self.time = None


class Position:
    instrument: Instrument = None
    count = 0
    margin = 0
    mean_price = 0
    # price => count
    stop_loses: Dict[float, int] = {}
    # price => count
    take_profits: Dict[float, int] = {}

    def set_stop_loss(self, price, count):
        self.stop_loses[price] = count

    def set_take_profit(self, price, count):
        self.take_profits[price] = count


class Trade:
    def __init__(self):
        self.balance = 0
        self.positions: List[Position] = []

    def pos_by_ticker(self, ticker: str) -> Position:
        for pos in self.positions:
            if pos.instrument.ticker == ticker:
                return pos

    def pos_by_instrument(self, instrument: Instrument) -> Position:
        ticker = instrument.ticker
        return self.pos_by_ticker(ticker)

    def set_stop_loss(self, instrument: Instrument, price: float, count: int):
        self.pos_by_instrument(instrument).set_stop_loss(price, count)

    def set_take_profit(self, instrument: Instrument, price: float, count: int):
        self.pos_by_instrument(instrument).set_take_profit(price, count)

    def buy(self, instrument: Instrument, price: float, count: int):
        pos = self.pos_by_instrument(instrument)
        pos.

