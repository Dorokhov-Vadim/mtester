from .base_strategies import BaseCandleStrategy
from typing import Iterable
from .providers import CurCandle
from .trade_stat import TradeStat


class BaseTest:
    def run(self):
        raise Exception('Testing class must implement run method')


class CandleTest(BaseTest):
    def __init__(self, strategy: BaseCandleStrategy, data_provider: Iterable):
        self.strategy: BaseCandleStrategy = strategy
        self.data_provider = data_provider
        self.trade_stat = TradeStat()

    def run(self):
        if self.strategy is None:
            raise Exception('strategy is None')
        if self.data_provider is None:
            raise Exception('historical data is empty')
        print('Market testing is running...')
        closed_candles = []
        prev_close = None

        for data_batch in self.data_provider:
            if not isinstance(data_batch, list):
                data_batch = [data_batch]
            if len(closed_candles) > 0:

                for position in self.strategy.trade.positions:
                    for def_order in position.deferred_orders:
                        for candle in closed_candles:
                            if candle.instrument is position.instrument:
                                if prev_close is None:
                                    prev_close = candle.close

                                if candle.low <= prev_close <= candle.high and candle.low < def_order.price < candle.high:
                                    self.strategy.trade.buy(position.instrument, def_order.price, def_order.count,
                                                            def_order.order_type, candle.date, candle.time)
                                    position.deferred_orders.remove(def_order)

                                if prev_close < candle.low and prev_close < def_order.price < candle.high:
                                    self.strategy.trade.buy(position.instrument, def_order.price, def_order.count,
                                                            def_order.order_type, candle.date, candle.time)
                                    position.deferred_orders.remove(def_order)

                                if prev_close > candle.high and candle.low < def_order.price < prev_close:
                                    self.strategy.trade.buy(position.instrument, def_order.price, def_order.count,
                                                            def_order.order_type, candle.date, candle.time)
                                    position.deferred_orders.remove(def_order)
                                    prev_close = candle.close

                # stat collection
                lose = 0
                for candle in closed_candles:
                    for position in self.strategy.trade.positions:
                        if position.instrument is candle.instrument:
                            if position.mean_price > candle.low and position.count > 0:
                                lose = (position.mean_price - candle.low) * position.count
                            if position.mean_price < candle.high and position.count < 0:
                                lose = (candle.high - position.mean_price) * abs(position.count)
                    self.trade_stat.add_candle(candle.instrument, candle.date, candle.time, candle.open, candle.low,
                                               candle.high, candle.close, self.strategy.trade.balance, lose)
                    print(candle.date + ' '+candle.time+' '+str(self.strategy.trade.balance) + ' '+str(lose))



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
        print('Balance: ' + str(self.strategy.trade.balance))
        print('Operation count: ' + str(self.strategy.trade.trans_count))
        self.strategy.trade.stat.yield_curve()


