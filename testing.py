from .base_strategies import BaseCandleStrategy
from typing import Iterable
from .providers import BaseCandlesProvider, BaseSyncProvider


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
            if isinstance(self.data_provider, BaseCandlesProvider):
                for position in self.strategy.trade.positions:
                    for def_order in position.deferred_orders:
                        if data_batch.low < def_order.price < data_batch.high:
                            if def_order.oper == "B":
                                self.strategy.trade.buy(position.instrument, def_order.price, def_order.count, def_order.order_type)
                            if def_order.oper == "S":
                                self.strategy.trade.sell(position.instrument, def_order.price, def_order.count, def_order.order_type)

            if isinstance(self.data_provider, BaseSyncProvider):
                for position in self.strategy.trade.positions:
                    pass
        print('Market testing is done.')
