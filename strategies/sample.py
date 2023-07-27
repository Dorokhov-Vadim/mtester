from ..base_strategies import BaseCandleStrategy
from ..indicators.mov_average import MovingAverage
from typing import List, Dict
from ..instruments import Instrument
from ..providers import Candle


class Sample(BaseCandleStrategy):

    def on_strategy_create(self):
        self.add_indicator(MovingAverage(5),
                           self.pos_by_ticker('si').instrument,
                           "ma_fast",
                           color="r")

        self.add_indicator(MovingAverage(30),
                           self.pos_by_ticker('si').instrument,
                           "ma_slow",
                           color="b")

    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]]):
        si = self.pos_by_ticker('si').instrument
        fast_prev = self.get_ind_by_candle(si, "ma_fast", 0, closed_candles[si][-2])
        fast = self.get_ind_by_candle(si, "ma_fast", 0, closed_candles[si][-1])
        slow_prev = self.get_ind_by_candle(si, "ma_slow", 0, closed_candles[si][-2])
        slow = self.get_ind_by_candle(si, "ma_slow", 0, closed_candles[si][-1])

        if None in (slow_prev, fast_prev):
            return

        if self.pos_by_ticker('si').count == 0 and fast > slow and fast_prev < slow_prev:
            self.buy_market(si, 1)

        if self.pos_by_ticker('si').count == 0 and fast < slow and fast_prev > slow_prev:
            self.sell_market(si, 1)

        if self.pos_by_ticker('si').count == 1 and fast < slow:
            self.sell_market(si, 2)

        if self.pos_by_ticker('si').count == -1 and fast > slow:
            self.buy_market(si, 2)
