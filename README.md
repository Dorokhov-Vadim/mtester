# <h1>mtester :chart_with_upwards_trend:
> <h4>Python package for testing stock market automation strategies on historical data</h4>


####  Example of strategy class:  

```
from mtester.base_strategies import BaseCandleStrategy
from mtester.indicators.mov_average import MovingAverage
from typing import List, Dict
from mtester.instruments import Instrument
from mtester.providers import Candle, CurCandle

ma_slow = 100
ma_fast = 10


class MASlowFast(BaseCandleStrategy):
    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]],
                        current_candle: Dict[Instrument, CurCandle]):
        data_rts = closed_candles[self.pos_by_ticker('rts').instrument]
        cur_price_rts = current_candle[self.pos_by_ticker('rts').instrument].price
        self.trade.stat.add_indicator(self.pos_by_ticker('rts').instrument, 'rts_fast', self.cur_date,
                                      self.cur_time, MovingAverage(data_rts, ma_fast).get_value(), 'y-')
        self.trade.stat.add_indicator(self.pos_by_ticker('rts').instrument, 'rts_slow', self.cur_date,
                                      self.cur_time, MovingAverage(data_rts, ma_slow).get_value(), 'r-')

        if MovingAverage(data_rts, ma_fast).get_value() > MovingAverage(data_rts, ma_slow).get_value() \
                and self.pos_by_ticker('rts').count == 0:
            self.buy(self.pos_by_ticker('rts').instrument, cur_price_rts, 1, 'M')
        if MovingAverage(data_rts, ma_fast).get_value() < MovingAverage(data_rts, ma_slow).get_value() \
                and self.pos_by_ticker('rts').count == 0:
            self.sell(self.pos_by_ticker('rts').instrument, cur_price_rts, 1, 'M')

        if MovingAverage(data_rts, ma_fast).get_value() > MovingAverage(data_rts, ma_slow).get_value() \
                and self.pos_by_ticker('rts').count < 0:
            self.buy(self.pos_by_ticker('rts').instrument, cur_price_rts, 2, 'M')

        if MovingAverage(data_rts, ma_fast).get_value() < MovingAverage(data_rts, ma_slow).get_value() \
                and self.pos_by_ticker('rts').count > 0:
            self.sell(self.pos_by_ticker('rts').instrument, cur_price_rts, 2, 'M')
```

####  Example of testing strategy:    


```
from mtester.testing import CandleTest
from mtester.instruments import Instrument
from mtester.providers import FinamSyncProvider
from strategies.ma_slow_fast import MASlowFast


i = {'rts': Instrument('rts', 10, 14.2, 10), 'si': Instrument('si', 1, 1, 1)}
provider = FinamSyncProvider(['data/1m/rts_now.txt', 'data/1m/si_now.txt'], [i['rts'], i['si']])
strategy = MASlowFast(window_size=400)
test = CandleTest(strategy, provider)
test.set_interval(0, 0)
test.run()
test.show_trade_stat()
test.show_instrument(i['rts'])
```
