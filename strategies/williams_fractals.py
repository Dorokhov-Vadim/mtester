from mtester.base_strategies import BaseCandleStrategy
from typing import List, Dict
from mtester.instruments import Instrument
from mtester.providers import Candle, CurCandle


sl = 100
tp = 450


class WilliamsFractals(BaseCandleStrategy):
    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]], current_candle: Dict[Instrument, CurCandle]):
        si = self.pos_by_ticker('rts').instrument
        data = closed_candles[si][-5:]
        cur_price = current_candle[si].price
        prev_high = closed_candles[si][-1].high
        prev_low = closed_candles[si][-1].low

        lows = [i.low for i in data]
        highs = [i.high for i in data]

        min_low = min(lows)
        max_high = max(highs)

        if prev_high > self.pos_by_instrument(si).mean_price + tp and self.pos_by_instrument(si).count == 1:
            self.sell(si, self.pos_by_instrument(si).mean_price + tp,1,'L')
            self.pos_by_instrument(si).pop_defer_order(0)

        if prev_low < self.pos_by_instrument(si).mean_price - tp and self.pos_by_instrument(si).count == -1:
            self.buy(si, self.pos_by_instrument(si).mean_price - tp,1,'L')
            self.pos_by_instrument(si).pop_defer_order(0)

        if data[2].low == min_low and self.pos_by_instrument(si).count == 0:
            self.buy(si, cur_price, 1, 'M')
            self.set_defer_order(si, 'S', 'M', cur_price - sl, 1)

        if data[2].high == max_high and self.pos_by_instrument(si).count == 0 :
            self.sell(si, cur_price, 1, 'M')
            self.set_defer_order(si, 'B', 'M', cur_price + sl, 1)