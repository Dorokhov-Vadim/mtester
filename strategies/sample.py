from lib.mtester.base_strategies import BaseCandleStrategy
from lib.mtester.indicators.mov_average import MovingAverage
from typing import List, Dict
from lib.mtester.instruments import Instrument
from lib.mtester.providers import Candle


class Sample(BaseCandleStrategy):

    def on_strategy_create(self):
        self.add_indicator(MovingAverage(14),
                           self.pos_by_ticker('si').instrument,
                           "ma_fast",
                           color="r")

        self.add_indicator(MovingAverage(60),
                           self.pos_by_ticker('si').instrument,
                           "ma_slow",
                           color="b")

    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]]):

        si = self.pos_by_ticker('si').instrument
        cur_fast_prev = self.get_ind_by_candle(si,"ma_fast",0,closed_candles[si][-2])
        cur_fast = self.get_ind_by_candle(si, "ma_fast", 0, closed_candles[si][-1])
        cur_slow_prev = self.get_ind_by_candle(si, "ma_slow", 0, closed_candles[si][-2])
        cur_slow = self.get_ind_by_candle(si, "ma_slow", 0, closed_candles[si][-1])


        if None in (cur_slow_prev, cur_fast_prev):
            return

        if self.pos_by_ticker('si').count == 0 and cur_fast > cur_slow and cur_fast_prev < cur_slow_prev:
            self.buy_market(si, 1)

        if self.pos_by_ticker('si').count == 0 and cur_fast < cur_slow and cur_fast_prev > cur_slow_prev:
            self.sell_market(si, 1)

        if self.pos_by_ticker('si').count == 1 and cur_fast<cur_slow:
            self.sell_market(si, 2)

        if self.pos_by_ticker('si').count == -1 and cur_fast>cur_slow:
            self.buy_market(si, 2)


