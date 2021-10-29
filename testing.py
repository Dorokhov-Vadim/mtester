from .base_strategies import BaseCandleStrategy
from typing import Iterable


class BaseTest:
    def run(self):
        raise Exception('Testing class must implement run method')


class CandleTest(BaseTest):
    def __init__(self, strategy: BaseCandleStrategy, data_provider: Iterable):
        self.strategy: BaseCandleStrategy = strategy
        self.data_provider = data_provider

    def run(self):
        if self.strategy is None:
            raise Exception('strategy is None')
        if self.data_provider is None:
            raise Exception('historical data is empty')
        print('Market testing is running...')
        prev_data_batch = []

        for data_batch in self.data_provider:
            if not isinstance(data_batch, list):
                data_batch = [data_batch]
            if len(prev_data_batch) > 0:
                for position in self.strategy.trade.positions:
                    for def_order in position.deferred_orders:
                        for candle in prev_data_batch:
                            if candle.instrument is position.instrument and candle.low < def_order.price < candle.high:
                                if def_order.oper == "B":
                                    self.strategy.trade.buy(position.instrument, def_order.price, def_order.count,
                                                            def_order.order_type)

                                if def_order.oper == "S":
                                    self.strategy.trade.sell(position.instrument, def_order.price, def_order.count,
                                                             def_order.order_type)
                for now_candle in data_batch:
                    cur_data_dict = dict()
                    cur_data_dict['date'] = now_candle.date
                    cur_data_dict['time'] = now_candle.time
                    cur_data_dict['price'] = now_candle.open
                    self.strategy.cur_data[now_candle.instrument] = cur_data_dict

                self.strategy.receive_data(prev_data_batch)
            prev_data_batch = data_batch
        print('Market testing is done.')
        print('Balance: ' + str(self.strategy.trade.balance))
        print('Operation count: ' + str(self.strategy.trade.trans_count))
        self.strategy.trade.stat.yield_curve()


