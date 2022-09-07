from typing import List, Dict
from .instruments import Instrument
from .trade_stat import TradeStat
from .providers import LimitOrder


class Position:
    def __init__(self, instrument: Instrument):
        self.instrument: Instrument = instrument
        self.count = 0
        self.mean_price = 0


class Trade:
    def __init__(self):
        self.balance = 0
        self.positions: List[Position] = []
        self.trans_count = 0
        self.stat = TradeStat()
        self.buys_limit: Dict[Instrument, List[LimitOrder]] = {}
        self.sells_limit: Dict[Instrument, List[LimitOrder]] = {}


    def pos_by_ticker(self, ticker: str) -> Position:
        for pos in self.positions:
            if pos.instrument.ticker.lower() == ticker.lower():
                return pos

    def pos_by_instrument(self, instrument: Instrument) -> Position:
        ticker = instrument.ticker
        return self.pos_by_ticker(ticker)

    def buy(self, instrument: Instrument, price: float, count: int, order_type, date, time):
        # print('buy  : '+instrument.ticker+' '+ date + ' / ' + time + ' / price = '+str(price) + ' / count = '+str(count))
        self.stat.add_buy(instrument, date, time, price, count)
        self.stat.inc_trans()
        if order_type == 'M':
            slip = instrument.slip
        else:
            slip = 0
        pos = self.pos_by_instrument(instrument)
        if pos is None:
            pos = Position(instrument)
            self.positions.append(pos)
        # add long position
        if pos.count >= 0:
            pos.mean_price = (pos.mean_price * pos.count + (price + slip) * count)/(pos.count + count)
            pos.count = pos.count + count
        # closing short position
        else:
            # if not (short -> long)
            if abs(pos.count) >= count:
                margin = (pos.mean_price - (price + slip)) * count
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
                margin = abs(pos.mean_price * pos.count) - (price + slip) * abs(pos.count)
                self.balance = self.balance + (margin//instrument.step)*instrument.step_price
                # self.stat.balance_history.append(self.balance)
                pos.count = count - abs(pos.count)
                pos.mean_price = price + slip
        if self.stat.max_load.get(instrument) is None:
            self.stat.max_load[instrument] = 0
        self.stat.max_load[instrument] = max(abs(pos.count), self.stat.max_load[instrument])
        print('Balance = ' + str(self.balance))

    def sell(self, instrument: Instrument, price: float, count: int, order_type, date, time):
        # print('sell : '+instrument.ticker+' ' + date + ' / ' + time + ' / price = '+str(price) + ' / count = '+str(count))
        self.stat.add_sell(instrument, date, time, price, count)
        self.stat.inc_trans()
        if order_type == 'M':
            slip = instrument.slip
        else:
            slip = 0
        pos = self.pos_by_instrument(instrument)
        if pos is None:
            pos = Position(instrument)
            self.positions.append(pos)
            # add short position
        if pos.count <= 0:
            pos.mean_price = (pos.mean_price * abs(pos.count) + (price - slip) * count) / abs(pos.count - count)
            pos.count = pos.count - count
        # closing long position
        else:
            # if not (long -> short)
            if abs(pos.count) >= count:
                margin = ((price - slip) - pos.mean_price) * count
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
                margin = (price - slip) * abs(pos.count) - abs(pos.mean_price * pos.count)
                self.balance = self.balance + (margin // instrument.step) * instrument.step_price
                # self.stat.balance_history.append(self.balance)
                pos.count = abs(pos.count) - count
                pos.mean_price = price - slip
        if self.stat.max_load.get(instrument) is None:
            self.stat.max_load[instrument] = 0
        self.stat.max_load[instrument] = max(abs(pos.count), self.stat.max_load[instrument])
        print('Balance = ' + str(self.balance))
