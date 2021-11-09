from mtester.base_strategies import BaseCandleStrategy
from mtester.indicators.mov_average import MovingAverage
from typing import List, Dict
from mtester.instruments import Instrument
from mtester.providers import Candle, CurCandle

window_size = 38
ma_fast = 8


class MASlowFast(BaseCandleStrategy):
    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]], current_candle: Dict[Instrument, CurCandle]):

        data_si = closed_candles[self.pos_by_ticker('si').instrument]
        cur_price_si = current_candle[self.pos_by_ticker('si').instrument].price
        data_rts = closed_candles[self.pos_by_ticker('rts').instrument]
        cur_price_rts = current_candle[self.pos_by_ticker('rts').instrument].price

        if len(data_si) >= self.window_size:

            self.trade.stat.add_indicator(self.pos_by_ticker('si').instrument, 'si_fast', self.cur_date,
                                          self.cur_time, MovingAverage(data_si, ma_fast).get_value(), 'y-')
            self.trade.stat.add_indicator(self.pos_by_ticker('si').instrument, 'si_slow', self.cur_date,
                                          self.cur_time, MovingAverage(data_si, window_size).get_value(), 'r-')
            self.trade.stat.add_indicator(self.pos_by_ticker('rts').instrument, 'rts_fast', self.cur_date,
                                          self.cur_time, MovingAverage(data_rts, ma_fast).get_value(), 'y-')
            self.trade.stat.add_indicator(self.pos_by_ticker('rts').instrument, 'rts_slow', self.cur_date,
                                          self.cur_time, MovingAverage(data_rts, window_size).get_value(), 'r-')

            if MovingAverage(data_si, ma_fast).get_value() > MovingAverage(data_si, window_size).get_value() and self.pos_by_ticker('si').count == 0:
                self.buy(self.pos_by_ticker('si').instrument, cur_price_si, 1, 'M')

            if MovingAverage(data_si, ma_fast).get_value() < MovingAverage(data_si, window_size).get_value() and self.pos_by_ticker('si').count == 0:
                self.sell(self.pos_by_ticker('si').instrument, cur_price_si, 1, 'M')

            if MovingAverage(data_si, ma_fast).get_value() > MovingAverage(data_si, window_size).get_value() and self.pos_by_ticker('si').count < 0:
                self.buy(self.pos_by_ticker('si').instrument, cur_price_si, 2, 'M')

            if MovingAverage(data_si, ma_fast).get_value() < MovingAverage(data_si, window_size).get_value() and self.pos_by_ticker('si').count > 0:
                self.sell(self.pos_by_ticker('si').instrument, cur_price_si, 2, 'M')
            ##############################################
            if MovingAverage(data_rts, ma_fast).get_value() > MovingAverage(data_rts, window_size).get_value() and self.pos_by_ticker('rts').count == 0:
                self.buy(self.pos_by_ticker('rts').instrument, cur_price_rts, 1, 'M')

            if MovingAverage(data_rts, ma_fast).get_value() < MovingAverage(data_rts, window_size).get_value() and self.pos_by_ticker('rts').count == 0:
                self.sell(self.pos_by_ticker('rts').instrument, cur_price_rts, 1, 'M')

            if MovingAverage(data_rts, ma_fast).get_value() > MovingAverage(data_rts, window_size).get_value() and self.pos_by_ticker('rts').count < 0:
                self.buy(self.pos_by_ticker('rts').instrument, cur_price_rts, 2, 'M')

            if MovingAverage(data_rts, ma_fast).get_value() < MovingAverage(data_rts, window_size).get_value() and self.pos_by_ticker('rts').count > 0:
                self.sell(self.pos_by_ticker('rts').instrument, cur_price_rts, 2, 'M')