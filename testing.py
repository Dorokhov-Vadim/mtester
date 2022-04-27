from .base_strategies import BaseCandleStrategy
from typing import Iterable
from .providers import CurCandle


class BaseTest:
    def run(self):
        raise Exception('Testing class must implement run method')


class CandleTest(BaseTest):
    def __init__(self, strategy: BaseCandleStrategy, data_provider: Iterable, from_num_candle=0, to_num_candle=0,
                 show_balance_changing=False):
        self.strategy: BaseCandleStrategy = strategy
        self.data_provider = data_provider
        self.from_num_candle = from_num_candle
        self.to_num_candle = to_num_candle
        self.show_balance_changing = show_balance_changing

    def set_from_to_candles(self, *, from_candle=0, to_candle=0):
        self.from_num_candle = from_candle
        self.to_num_candle = to_candle

    def show_trade_stat(self):
        self.strategy.trade.stat.show_trade_stat()

    def show_instrument(self, instrument):
        self.strategy.trade.stat.show_instrument(instrument)

    def is_allow_interval(self, candle_num):
        res = False
        if self.from_num_candle <= candle_num <= self.to_num_candle \
                or ((self.from_num_candle == 0) and candle_num <= self.to_num_candle) \
                or ((self.to_num_candle == 0) and candle_num >= self.from_num_candle) \
                or ((self.from_num_candle == 0) and (self.to_num_candle == 0)):
            res = True
        return res

    def run(self):
        candle_count = 0
        if self.strategy is None:
            raise Exception('strategy is None')
        if self.data_provider is None:
            raise Exception('historical data is empty')
        print('Market testing is running...')
        closed_candles = []
        prev_close = None
        for data_batch in self.data_provider:
            candle_count = candle_count + 1
            if self.is_allow_interval(candle_count):
                if not isinstance(data_batch, list):
                    data_batch = [data_batch]
                if len(closed_candles) > 0:
                    for position in self.strategy.trade.positions:
                        for candle in closed_candles:
                            if prev_close is None:
                                prev_close = dict()
                            for def_order in position.deferred_orders:
                                if candle.instrument is position.instrument:
                                    if (prev_close[candle.instrument] > candle.high and candle.low < def_order.price <
                                        prev_close[candle.instrument]) \
                                            or ((prev_close[candle.instrument] <= candle.low) and (prev_close[
                                                                                                       candle.instrument] <= def_order.price <= candle.high)) \
                                            or (candle.low <= prev_close[candle.instrument] <= candle.high
                                                and candle.low < def_order.price < candle.high):
                                        if def_order.oper == 'B':
                                            self.strategy.trade.buy(position.instrument, def_order.price,
                                                                    def_order.count,
                                                                    def_order.order_type, candle.date, candle.time)
                                            self.strategy.trade.stat.add_buy(position.instrument, candle.date,
                                                                             candle.time, def_order.price,
                                                                             def_order.count)

                                        if def_order.oper == 'S':
                                            self.strategy.trade.sell(position.instrument, def_order.price,
                                                                     def_order.count,
                                                                     def_order.order_type, candle.date, candle.time)
                                            self.strategy.trade.stat.add_sell(position.instrument, candle.date,
                                                                              candle.time, def_order.price,
                                                                              def_order.count)

                                        position.deferred_orders.remove(def_order)
                            prev_close[candle.instrument] = candle.close
                    self.strategy.trade.stat.balance_hist.append(self.strategy.trade.balance)
                    # stat collection

                    for candle in closed_candles:
                        lose = 0
                        profit = 0
                        for position in self.strategy.trade.positions:
                            if position.instrument is candle.instrument:
                                coef = position.instrument.step_price / position.instrument.step
                                if position.mean_price > candle.low and position.count > 0:
                                    lose = (position.mean_price - candle.low) * position.count * coef
                                if position.mean_price < candle.high and position.count < 0:
                                    lose = (candle.high - position.mean_price) * abs(position.count) * coef
                                if position.mean_price < candle.high and position.count > 0:
                                    profit = (candle.high - position.mean_price) * position.count * coef
                                if position.mean_price > candle.low and position.count < 0:
                                    profit = (position.mean_price - candle.low) * abs(position.count) * coef
                        self.strategy.trade.stat.add_candle(candle.instrument, candle.date,
                                                            candle.time, candle.open, candle.low,
                                                            candle.high, candle.close,
                                                            lose, profit)

                    cur_data_batch = dict()
                    for now_candle in data_batch:
                        cur_candle = CurCandle(now_candle.instrument)
                        cur_candle.date = now_candle.date
                        cur_candle.time = now_candle.time
                        cur_candle.price = now_candle.open
                        cur_data_batch[now_candle.instrument] = cur_candle

                    self.strategy.cur_date = data_batch[0].date
                    self.strategy.cur_time = data_batch[0].time
                    self.strategy.receive_data(closed_candles, cur_data_batch)
                closed_candles = data_batch
        print('Market testing is done.')
