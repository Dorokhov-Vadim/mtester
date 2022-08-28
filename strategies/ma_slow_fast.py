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
        self.add_indicator(StochasticOscillator(14,3,3), self.pos_by_ticker('si').instrument, panel=1, color='r', type = 'scatter', marker='^')

    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]],
                        current_candle: Dict[Instrument, CurCandle]):

        cur_price_rts = current_candle[self.pos_by_ticker('rts').instrument].price
        cur_price_si = current_candle[self.pos_by_ticker('si').instrument].price

        if self.pos_by_ticker('rts').count == 0:
            self.sell(self.pos_by_ticker('rts').instrument, cur_price_rts, 1, 'M')
            self.set_defer_order(self.pos_by_ticker('rts').instrument,'B','M',118000,1)

        if self.pos_by_ticker('si').count == 0:
            self.buy(self.pos_by_ticker('si').instrument, cur_price_si, 1, 'M')
            self.set_defer_order(self.pos_by_ticker('si').instrument, 'S', 'M', 62320, 1)





