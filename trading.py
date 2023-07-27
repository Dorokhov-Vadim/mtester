from typing import List, Dict
from .instruments import Instrument
from .trade_stat import TradeStat
from .providers import Candle


class Position:
    def __init__(self, instrument: Instrument):
        self.instrument: Instrument = instrument
        self.count = 0
        self.mean_price = 0


class LimitOrder:
    def __init__(self, price, count, life_time):
        self.price: float = price
        self.count: int = count
        self.life_time: int = life_time
        self.cur_life: int = 0
        self.deleted = False


class DeferredOrder:

    def __init__(self, price: float, count: int):
        self.price: float = price
        self.count: int = count
        self.deleted = False


class Trade:
    def __init__(self):
        self.balance = 0
        self.positions: List[Position] = []
        self.trans_count = 0
        self.stat = TradeStat()
        self.buys_limit: Dict[Instrument, List[LimitOrder]] = {}
        self.sells_limit: Dict[Instrument, List[LimitOrder]] = {}
        self.buys_deferred: Dict[Instrument, List[DeferredOrder]] = {}
        self.sells_deferred: Dict[Instrument, List[DeferredOrder]] = {}

    def pos_by_ticker(self, ticker: str) -> Position:
        for pos in self.positions:
            if pos.instrument.ticker.lower() == ticker.lower():
                return pos

    def pos_by_instrument(self, instrument: Instrument) -> Position:
        ticker = instrument.ticker
        return self.pos_by_ticker(ticker)

    def buy(self, instrument: Instrument, price: float, count: int, order_type, date, time):
        print('buy  : '+instrument.ticker+' '+ date + ' / ' + time + ' / price = '+str(price) + ' / count = '+str(count))

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
            pos.mean_price = (pos.mean_price * pos.count + (price + slip) * count) / (pos.count + count)
            pos.count = pos.count + count
        # closing short position
        else:
            # if not (short -> long)
            if abs(pos.count) >= count:
                margin = (pos.mean_price - (price + slip)) * count
                self.balance = self.balance + (margin // instrument.step) * instrument.step_price
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
                self.balance = self.balance + (margin // instrument.step) * instrument.step_price
                # self.stat.balance_history.append(self.balance)
                pos.count = count - abs(pos.count)
                pos.mean_price = price + slip
        if self.stat.max_load.get(instrument) is None:
            self.stat.max_load[instrument] = 0
        self.stat.max_load[instrument] = max(abs(pos.count), self.stat.max_load[instrument])
        print('Balance = ' + str(self.balance))
        print(self.pos_by_instrument(instrument).count)

    def sell(self, instrument: Instrument, price: float, count: int, order_type, date, time):
        print('sell : '+instrument.ticker+' ' + date + ' / ' + time + ' / price = '+str(price) + ' / count = '+str(count))
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
        print(self.pos_by_instrument(instrument).count)


    def limit_orders_processing(self, candles_dict: dict[Instrument, List[Candle]]):

        for instrument in self.buys_limit:
            candle_low = candles_dict[instrument][-1].low
            self.buys_limit[instrument] = [order for order in self.buys_limit[instrument]
                                           if not order.deleted and order.life_time > order.cur_life]
            for order in self.buys_limit[instrument]:
                if candle_low < order.price:
                    self.buy(instrument, order.price, order.count, "L",
                             candles_dict[instrument][-1].date,
                             candles_dict[instrument][-1].time)
                    order.deleted = True
                order.cur_life = order.cur_life + 1

        for instrument in self.sells_limit:
            candle_high = candles_dict[instrument][-1].high
            self.sells_limit[instrument] = [order for order in self.sells_limit[instrument]
                                            if not order.deleted and order.life_time > order.cur_life]
            for order in self.sells_limit[instrument]:

                if candle_high > order.price:
                    self.sell(instrument, order.price, order.count, "L",
                              candles_dict[instrument][-1].date,
                              candles_dict[instrument][-1].time)
                    order.deleted = True
                order.cur_life = order.cur_life + 1

    def defer_orders_processing(self, candles_dict: dict[Instrument, List[Candle]]):
        for instrument in self.sells_deferred:
            candle_open = candles_dict[instrument][-1].open
            candle_low = candles_dict[instrument][-1].low

            self.sells_deferred[instrument] = [order for order in self.sells_deferred[instrument]
                                               if not order.deleted]
            for order in self.sells_deferred[instrument]:
                if candle_open <= order.price:
                    self.sell(instrument, candle_open, order.count, "M",
                              candles_dict[instrument][-1].date,
                              candles_dict[instrument][-1].time)
                    order.deleted = True
                elif candle_open > order.price > candle_low:
                    self.sell(instrument, order.price, order.count, "M",
                              candles_dict[instrument][-1].date,
                              candles_dict[instrument][-1].time)
                    order.deleted = True

        for instrument in self.buys_deferred:
            candle_open = candles_dict[instrument][-1].open
            candle_high = candles_dict[instrument][-1].high

            self.buys_deferred[instrument] = [order for order in self.buys_deferred[instrument]
                                              if not order.deleted]
            for order in self.buys_deferred[instrument]:
                if candle_open >= order.price:
                    self.buy(instrument, candle_open, order.count, "M",
                             candles_dict[instrument][-1].date,
                             candles_dict[instrument][-1].time)
                    order.deleted = True
                elif candle_open < order.price < candle_high:
                    self.buy(instrument, order.price, order.count, "M",
                             candles_dict[instrument][-1].date,
                             candles_dict[instrument][-1].time)
                    order.deleted = True
