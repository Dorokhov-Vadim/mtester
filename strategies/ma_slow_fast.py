from mtester.base_strategies import BaseCandleStrategy
from mtester.indicators.mov_average import MovingAverage
from mtester.indicators.stochastic_oscillator import StochasticOscillator
from typing import List, Dict
from mtester.instruments import Instrument
from mtester.providers import Candle, CurCandle

ma_slow = 80
ma_fast = 10


class MASlowFast(BaseCandleStrategy):
    def on_strategy_create(self):
        self.add_indicator(MovingAverage(14),
                           self.pos_by_ticker('si').instrument,
                           "ma_fast",
                           color="r")

        self.add_indicator(MovingAverage(60),
                           self.pos_by_ticker('si').instrument,
                           "ma_slow",
                           color="b")

    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]],
                        current_candle: Dict[Instrument, CurCandle]):
        si = self.pos_by_ticker('si').instrument

        cur_price_si = current_candle[si].price
        cur_fast_prev = self.get_ind_by_candle(si,"ma_fast",0,closed_candles[si][-2])
        cur_fast = self.get_ind_by_candle(si, "ma_fast", 0, closed_candles[si][-1])
        cur_slow_prev = self.get_ind_by_candle(si, "ma_slow", 0, closed_candles[si][-2])
        cur_slow = self.get_ind_by_candle(si, "ma_slow", 0, closed_candles[si][-1])

        if self.pos_by_ticker('si').count == 0 and cur_fast>cur_slow and cur_fast_prev<cur_slow_prev:
            self.buy(si, cur_price_si, 1, 'M')

        if self.pos_by_ticker('si').count == 1 and cur_fast<cur_slow:
            self.sell(si, cur_price_si, 1, 'M')








