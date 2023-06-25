from typing import List, Dict
from .trading import Trade, Position, LimitOrder, DeferredOrder
from .providers import Candle, CurCandle
from .instruments import Instrument
from .indicators.bases import IndicatorData
import warnings


class BaseCandleStrategy:
    def __init__(self, window_size: int):
        self.cur_candles: Dict[Instrument, CurCandle] = {}
        self.cur_date = ''
        self.cur_time = ''
        self.trade = Trade()
        self.window_size = window_size
        self.candles_dict: Dict[Instrument, List[Candle]] = {}
        self.is_created = False

    def pos_by_ticker(self, ticker: str) -> Position:
        return self.trade.pos_by_ticker(ticker)

    def pos_by_instrument(self, instrument: Instrument) -> Position:
        return self.trade.pos_by_instrument(instrument)

    def buy(self, instrument: Instrument, price: float, count: int, order_type):
        self.trade.buy(instrument, price, count, order_type, self.cur_date, self.cur_time)

    def sell(self, instrument: Instrument, price: float, count: int, order_type):
        self.trade.sell(instrument, price, count, order_type, self.cur_date, self.cur_time)

    def buy_market(self, instrument: Instrument, count: int):
        self.buy(instrument, self.cur_candles[instrument].price, count, 'M')

    def sell_market(self, instrument: Instrument, count: int):
        self.sell(instrument, self.cur_candles[instrument].price, count, 'M')

    def set_limit_buy(self, instrument: Instrument, count: int, price: float, life_time: int):
        if price > self.cur_candles[instrument].price:
            self.buy_market(instrument, count)
            return
        if self.trade.buys_limit.get(instrument) is None:
            self.trade.buys_limit[instrument] = []
        self.trade.buys_limit[instrument].append(LimitOrder(price, count, life_time))

    def set_limit_sell(self, instrument: Instrument, count: int, price: float, life_time: int):
        if price < self.cur_candles[instrument].price:
            self.sell_market(instrument, count)
            return
        if self.trade.sells_limit.get(instrument) is None:
            self.trade.sells_limit[instrument] = []
        self.trade.sells_limit[instrument].append(LimitOrder(price, count, life_time))

    def receive_data(self, candles: List[Candle]):
        candles_len = 0
        for candle in candles:
            if self.trade.pos_by_instrument(candle.instrument) is None:
                self.trade.positions.append(Position(candle.instrument))
            if self.candles_dict.get(candle.instrument) is None:
                self.candles_dict[candle.instrument] = []
            candles_len = len(self.candles_dict[candle.instrument])
            if candles_len >= self.window_size:
                self.candles_dict[candle.instrument].pop(0)
            self.candles_dict[candle.instrument].append(candle)
        if candles_len == self.window_size:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if not self.is_created:
                    self.on_strategy_create()
                    self.is_created = True
                self.calc_indicators_for_candles()
                self.trade.limit_orders_processing(self.candles_dict)
                self.trade.defer_orders_processing(self.candles_dict)
                self.on_candle_close(self.candles_dict)

    def on_strategy_create(self):
        raise Exception(self.__class__.__name__ + ' class must implement on_strategy_create method')

    # Main callback for user's strategies
    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]]):
        raise Exception(self.__class__.__name__ + ' class must implement on_candle_close method')

    def add_indicator(self, indicator, instrument, name, **kwargs):
        if self.trade.stat.indicators.get(instrument) is None:
            self.trade.stat.indicators[instrument] = list()
        self.trade.stat.indicators[instrument].append(IndicatorData(indicator, name, **kwargs))

    def calc_indicators_for_candles(self):
        for instrument in self.trade.stat.indicators:
            for ind_data in self.trade.stat.indicators[instrument]:
                ind_data.calc_indicator_for_candles(self.candles_dict[instrument])

    def get_line(self, instrument: Instrument, name, line_num=0):
        return self.trade.stat.get_line(instrument, name, line_num)

    def get_ind_by_candle(self, instrument: Instrument, name, line_num, candle):
        return self.trade.stat.get_ind_by_candle(instrument, name, line_num, candle)

    def set_defer_buy(self, instrument: Instrument, price: float, count: int):
        if price < self.cur_candles[instrument].price:
            print('WARNING: SET DEFER BUY: CURRENT PRICE IS UPPER THEN ORDER PRICE')
            self.buy_market(instrument, count)
            return
        if self.trade.buys_deferred.get(instrument) is None:
            self.trade.buys_deferred[instrument] = []
        self.trade.buys_deferred[instrument].append(DeferredOrder(price, count))

    def set_defer_sell(self, instrument: Instrument, price: float, count: int):
        if price > self.cur_candles[instrument].price:
            print('WARNING: SET DEFER SELL: CURRENT PRICE IS LOWER THEN ORDER PRICE')
            self.sell_market(instrument, count)
            return
        if self.trade.sells_deferred.get(instrument) is None:
            self.trade.sells_deferred[instrument] = []

        self.trade.sells_deferred[instrument].append(DeferredOrder(price, count))

    def get_limit_buys(self,  instrument: Instrument):
        if self.trade.buys_limit.get(instrument) is None:
            return []
        return self.trade.buys_limit[instrument]

    def get_limit_sells(self,  instrument: Instrument):
        if self.trade.sells_limit.get(instrument) is None:
            return []
        return self.trade.sells_limit[instrument]

    def get_defer_buys(self, instrument: Instrument):
        if self.trade.buys_deferred.get(instrument) is None:
            return []
        return self.trade.buys_deferred[instrument]

    def get_defer_sells(self, instrument: Instrument):
        if self.trade.sells_deferred.get(instrument) is None:
            return []
        return self.trade.sells_deferred[instrument]

    def cancel_all_defer_buy(self, instrument: Instrument):
        if self.trade.buys_deferred.get(instrument) is not None:
            self.trade.buys_deferred[instrument] = []

    def cancel_all_defer_sell(self, instrument: Instrument):
        if self.trade.sells_deferred.get(instrument) is not None:
            self.trade.sells_deferred[instrument] = []

    def cancel_all_limit_buy(self, instrument: Instrument):
        if self.trade.buys_limit.get(instrument) is not None:
            self.trade.buys_limit[instrument] = []

    def cancel_all_limit_sell(self, instrument: Instrument):
        if self.trade.sells_limit.get(instrument) is not None:
            self.trade.sells_limit[instrument] = []

