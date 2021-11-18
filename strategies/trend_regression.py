from mtester.base_strategies import BaseCandleStrategy
from typing import List, Dict
from mtester.instruments import Instrument
from mtester.providers import Candle, CurCandle
from sklearn.linear_model import LinearRegression
from mtester.indicators.stochastic_oscillator import StochasticOscillator

model_size = 20
stop_loss_size = 70
take_profit_size = 210
stoch_k = 14
k_smooth = 3
d_smooth = 3
super_coeff = 12
over_sell_level = 0.2
over_buy_level = 0.8
lots_count = 1


class TrendRegression(BaseCandleStrategy):
    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]],
                        current_candle: Dict[Instrument, CurCandle]):
        instrument = self.pos_by_ticker('si').instrument
        data_si = []
        times = [i for i in range(0, model_size)]
        cur_price_si = current_candle[instrument].price
        for candle in closed_candles[instrument]:
            data_si.append(candle.close)
        nd_si = [[x] for x in data_si[-model_size:]]
        nd_times = [[i] for i in times]

        model = LinearRegression(fit_intercept=True)
        model.fit(nd_times, nd_si)
        regression_coef = model.coef_[0][0]

        # ------------------------------------------------
        k, d = StochasticOscillator(closed_candles[instrument], stoch_k, k_smooth, d_smooth).get_value()
        k_super, d_super = StochasticOscillator(closed_candles[instrument], stoch_k*super_coeff, k_smooth*super_coeff, d_smooth*super_coeff).get_value()
        mean_price = self.pos_by_instrument(instrument).mean_price

        # ------------Output from position
        if self.pos_by_instrument(instrument).count == 1 and (cur_price_si - mean_price) > take_profit_size:
            self.sell(instrument, cur_price_si, lots_count, 'M')
            self.pos_by_instrument(instrument).pop_defer_order(0)

        if self.pos_by_instrument(instrument).count == -1 and (mean_price - cur_price_si) > take_profit_size:
            self.buy(instrument, cur_price_si, lots_count, 'M')
            self.pos_by_instrument(instrument).pop_defer_order(0)

        # ----------------Enter in position
        if self.pos_by_instrument(instrument).count == 0 and regression_coef > 0 \
                and k > d and k_super > d_super and d < over_sell_level:
            self.buy(instrument, cur_price_si, lots_count, 'M')
            self.set_defer_order(instrument, 'S', 'M', cur_price_si - stop_loss_size, lots_count)

        if self.pos_by_instrument(instrument).count == 0 and regression_coef < 0 \
                and k < d and k_super < d_super and d > over_buy_level:
            self.sell(instrument, cur_price_si, lots_count, 'M')
            self.set_defer_order(instrument, 'B', 'M', cur_price_si + stop_loss_size, lots_count)

        # ---------------Add custom user indicators in chart
        self.trade.stat.add_indicator(self.pos_by_ticker('si').instrument, 'k', self.cur_date,
                                      self.cur_time, k, 'b--', subplot=True)
        self.trade.stat.add_indicator(self.pos_by_ticker('si').instrument, 'd', self.cur_date,
                                      self.cur_time, d, 'b-', subplot=True)
        self.trade.stat.add_indicator(self.pos_by_ticker('si').instrument, 'k_super', self.cur_date,
                                      self.cur_time, k_super, 'r--', subplot=False)
        self.trade.stat.add_indicator(self.pos_by_ticker('si').instrument, 'd_super', self.cur_date,
                                      self.cur_time, d_super, 'r-', subplot=True)
