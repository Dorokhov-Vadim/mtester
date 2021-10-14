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
    def __init__(self, instrument: Instrument):
        self.instrument: Instrument = instrument
        self.count = 0
        # margin = 0
        self.mean_price = 0
        # price => count
        self.stop_loses: Dict[float, int] = {}
        # price => count
        self.take_profits: Dict[float, int] = {}

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

    # def add_position(self, ):

    def buy(self, instrument: Instrument, price: float, count: int):
        pos = self.pos_by_instrument(instrument)
        if pos is None:
            pos = Position(instrument)
            self.positions.append(pos)
        # add long position
        if pos.count >= 0:
            pos.mean_price = (pos.mean_price * pos.count + (price + pos.instrument.slip) * count)/(pos.count + count)
            pos.count = pos.count + count
        # closing short position
        else:
            # if not (short -> long)
            if abs(pos.count) >= count:
                margin = (pos.mean_price - (price + pos.instrument.slip)) * count
                self.balance = self.balance + (margin//instrument.step)*instrument.step_price
                # mean pos price is not changed
                if count == abs(pos.count):
                    # all pos is closed
                    pos.mean_price = 0
                    pos.count = 0
                else:
                    pos.count = pos.count + count
            else:
                # if (short -> long)
                margin = abs(pos.mean_price * pos.count) - (price + pos.instrument.slip) * abs(pos.count)
                self.balance = self.balance + (margin//instrument.step)*instrument.step_price
                pos.count = count - abs(pos.count)
                pos.mean_price = price + pos.instrument.slip

    def sell(self, instrument: Instrument, price: float, count: int):
        pos = self.pos_by_instrument(instrument)
        if pos is None:
            pos = Position(instrument)
            self.positions.append(pos)
            # add short position
        if pos.count <= 0:
            pos.mean_price = (pos.mean_price * abs(pos.count) + (price - pos.instrument.slip) * count) / abs(pos.count - count)
            pos.count = pos.count - count
        # closing long position
        else:
            # if not (long -> short)
            if abs(pos.count) >= count:
                margin = ((price - pos.instrument.slip) - pos.mean_price) * count
                self.balance = self.balance + (margin // instrument.step) * instrument.step_price
                # mean pos price is not changed
                if count == abs(pos.count):
                    # all pos is closed
                    pos.mean_price = 0
                    pos.count = 0
                else:
                    pos.count = pos.count - count
            else:
                # if (long -> short)
                margin = (price - pos.instrument.slip) * abs(pos.count) - abs(pos.mean_price * pos.count)
                self.balance = self.balance + (margin // instrument.step) * instrument.step_price
                pos.count = abs(pos.count) - count
                pos.mean_price = price - pos.instrument.slip
