from typing import List
from .instruments import Instrument
from .trade_stat import TradeStat


class DeferredOrder:
    order_id = 0

    def __init__(self, oper, order_type, price, count):
        self.order_id = self.order_id + 1
        if oper not in ('B', 'S'):
            raise Exception('oper param must be str "B" or "S"')
        # B-buy, S-sell
        self.oper: str = oper
        if order_type not in ('L', 'M'):
            raise Exception('oper param must be str "L"(limit order) or "M"(market order)')
        # L-limit, M-market (market order use instrument.slip)
        self.order_type: str = order_type
        self.price: float = price
        self.count: int = count


class Position:
    def __init__(self, instrument: Instrument):
        self.instrument: Instrument = instrument
        self.count = 0
        # margin = 0
        self.mean_price = 0
        # price => count
        self.deferred_orders: List[DeferredOrder] = []

    def set_defer_order(self, oper, order_type, price, count) -> int:
        self.deferred_orders.append(DeferredOrder(oper, order_type, price, count))
        return self.deferred_orders[-1].order_id

    def pop_defer_order(self, order_id) -> DeferredOrder:
        if order_id == 0 and len(self.deferred_orders) > 0:
            return self.deferred_orders.pop(0)
        else:
            for order in self.deferred_orders:
                if order.order_id == order_id:
                    self.deferred_orders.remove(order)
                    return order


class Trade:
    def __init__(self):
        self.balance = 0
        self.positions: List[Position] = []
        self.trans_count = 0
        self.stat = TradeStat()

    def pos_by_ticker(self, ticker: str) -> Position:
        for pos in self.positions:
            if pos.instrument.ticker.lower() == ticker.lower():
                return pos

    def pos_by_instrument(self, instrument: Instrument) -> Position:
        ticker = instrument.ticker
        return self.pos_by_ticker(ticker)

    def set_defer_order(self, instrument: Instrument, oper, order_type, price: float, count: int):
        pos = self.pos_by_instrument(instrument)
        if pos is None:
            pos = Position(instrument)
            self.positions.append(pos)
        pos.set_defer_order(oper, order_type, price, count)

    def buy(self, instrument: Instrument, price: float, count: int, order_type):
        self.trans_count = self.trans_count + 1
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
                self.stat.balance_history.append(self.balance)
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
                self.stat.balance_history.append(self.balance)
                pos.count = count - abs(pos.count)
                pos.mean_price = price + slip

    def sell(self, instrument: Instrument, price: float, count: int, order_type):
        self.trans_count = self.trans_count + 1
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
                self.stat.balance_history.append(self.balance)
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
                self.stat.balance_history.append(self.balance)
                pos.count = abs(pos.count) - count
                pos.mean_price = price - slip
