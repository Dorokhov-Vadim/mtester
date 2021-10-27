from .base_strategies import BaseCandleStrategy
from typing import Iterable
from .trading import Position

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

        for data_batch in self.data_provider:
            if not isinstance(data_batch, list):
                data_batch = [data_batch]
            for position in self.strategy.trade.positions:
                for def_order in position.deferred_orders:
                    for candle in data_batch:
                        if candle.instrument is position.instrument and candle.low < def_order.price < candle.high:
                            if def_order.oper == "B":
                                self.strategy.trade.buy(position.instrument, def_order.price, def_order.count,
                                                        def_order.order_type)

                            if def_order.oper == "S":
                                self.strategy.trade.sell(position.instrument, def_order.price, def_order.count,
                                                         def_order.order_type)

            self.strategy.receive_data(data_batch)

        print('Market testing is done.')

