from mtester.base_strategies import BaseCandleStrategy
from typing import List, Dict
from mtester.instruments import Instrument
from mtester.providers import Candle, CurCandle
import numpy as np
from sklearn.linear_model import LinearRegression

rts_count = 1
si_max_count = 15
si_act_val = 100
si_deact_val = 0
regression_act = 0.1
correlation_act = 0.8
moex_usd_coef = 0.2
si_usd_coef = 1000


class CorrelationSiRts(BaseCandleStrategy):
    def __init__(self, window_size):
        super().__init__(window_size)
        self.model = self.model = LinearRegression(fit_intercept=True)
        self.time_pos = 0

    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]], current_candle: Dict[Instrument, CurCandle]):
        data_si = []
        data_rts = []
        rts_instrument = self.pos_by_ticker('rts').instrument
        si_instrument = self.pos_by_ticker('si').instrument

        for candle in closed_candles[si_instrument]:
            data_si.append(candle.close)
        cur_price_si = current_candle[si_instrument].price
        last_closed_si = data_si[-1]
        # according to moex for rts:
        rts_step_price = moex_usd_coef * last_closed_si / si_usd_coef
        for candle in closed_candles[rts_instrument]:
            data_rts.append(candle.close)
        cur_price_rts = current_candle[rts_instrument].price

        rts_step = rts_instrument.step
        rts_instrument.step_price = rts_step_price
        last_closed_rts = data_rts[-1]
        nd_si = [[x] for x in data_si]
        nd_rts = [[x] for x in data_rts]
        self.model.fit(nd_rts, nd_si)
        coef = self.model.coef_[0][0]
        si_model = self.model.predict([[last_closed_rts]])[0][0]
        si_count = int(rts_step_price/(abs(coef) * rts_step))
        correl_coef = np.corrcoef(data_si, data_rts)[0][1]

        # ---------------Enter in position
        if si_count <= si_max_count and coef < -regression_act and correl_coef < -correlation_act:
            if ((si_model - last_closed_si) > si_act_val) \
                    and self.pos_by_instrument(rts_instrument).count == 0 \
                    and self.pos_by_instrument(si_instrument).count == 0:
                self.buy(rts_instrument,cur_price_rts,rts_count,'M')
                self.buy(si_instrument, cur_price_si,si_count,'M')

            if ((last_closed_si - si_model) > si_act_val) \
                    and self.pos_by_instrument(rts_instrument).count == 0 \
                    and self.pos_by_instrument(si_instrument).count == 0:
                self.sell(rts_instrument,cur_price_rts,rts_count,'M')
                self.sell(si_instrument, cur_price_si,si_count,'M')

        # --------------Output from position
        if (((si_model - last_closed_si) < si_deact_val)
            and self.pos_by_instrument(rts_instrument).count > 0
            and self.pos_by_instrument(si_instrument).count > 0):
            self.sell(rts_instrument, cur_price_rts, abs(self.pos_by_instrument(rts_instrument).count),'M')
            self.sell(si_instrument, cur_price_si, abs(self.pos_by_instrument(si_instrument).count),'M')

        if (((last_closed_si - si_model) < si_deact_val)
                and self.pos_by_instrument(rts_instrument).count < 0
                and self.pos_by_instrument(si_instrument).count < 0):
            self.buy(rts_instrument,cur_price_rts, abs(self.pos_by_instrument(rts_instrument).count),'M')
            self.buy(si_instrument, cur_price_si, abs(self.pos_by_instrument(si_instrument).count),'M')

        self.trade.stat.add_indicator(self.pos_by_ticker('si').instrument, 'si_model', self.cur_date,
                                      self.cur_time, si_model, 'y--')
        self.trade.stat.add_indicator(self.pos_by_ticker('si').instrument, 'si_fact', self.cur_date,
                                      self.cur_time, data_si[-1], 'b--')










