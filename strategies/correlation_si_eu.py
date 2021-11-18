import math

from mtester.base_strategies import BaseCandleStrategy
from typing import List, Dict
from mtester.instruments import Instrument
from mtester.providers import Candle, CurCandle
import numpy as np
from sklearn.linear_model import LinearRegression


si_count = 1
eu_count = 1
eu_act_val = 70
eu_deact_val = 0


class CorrelationSiEu(BaseCandleStrategy):
    def __init__(self, window_size):
        super().__init__(window_size)
        self.model_ed = LinearRegression(fit_intercept=True)
        self.model_si_eu = LinearRegression(fit_intercept=True)

    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]], current_candle: Dict[Instrument, CurCandle]):
        data_eu = []
        data_si = []
        data_ed = []
        si_instrument = self.pos_by_ticker('si').instrument
        eu_instrument = self.pos_by_ticker('eu').instrument
        ed_instrument = self.pos_by_ticker('ed').instrument
        for candle in closed_candles[eu_instrument]:
            data_eu.append(candle.close)
        cur_price_eu = current_candle[eu_instrument].price
        last_closed_eu = data_eu[-1]
        for candle in closed_candles[si_instrument]:
            data_si.append(candle.close)
        cur_price_si = current_candle[si_instrument].price
        for candle in closed_candles[ed_instrument]:
            data_ed.append(candle.close)
        times = [i for i in range(0, len(data_ed))]
        nd_eu = [[x] for x in data_eu]
        nd_si = [[x] for x in data_si]
        nd_times = [[x] for x in times]
        nd_ed = [[x] for x in data_ed]
        self.model_si_eu.fit(nd_si, nd_eu)
        self.model_ed.fit(nd_times, nd_ed)
        regr_si_eu_coef = self.model_si_eu.coef_[0][0]
        trend_direct = self.model_ed.coef_[0][0]
        eu_model = self.model_si_eu.predict([[last_closed_eu]])[0][0]
        correl_coef = np.corrcoef(data_si, data_eu)[0][1]

        # ----------Enter in position
        if correl_coef > 0.9:
            if ((eu_model - last_closed_eu) > eu_act_val) and trend_direct > 0 and regr_si_eu_coef > 1 \
                    and self.pos_by_instrument(si_instrument).count == 0 \
                    and self.pos_by_instrument(eu_instrument).count == 0:
                self.sell(si_instrument,cur_price_si,si_count, 'M')
                self.buy(eu_instrument, cur_price_eu,eu_count, 'M')

            if ((last_closed_eu - eu_model) > eu_act_val) and trend_direct < 0 and regr_si_eu_coef > 1 \
                    and self.pos_by_instrument(si_instrument).count == 0 \
                    and self.pos_by_instrument(eu_instrument).count == 0:
                self.buy(si_instrument,cur_price_si,si_count, 'M')
                self.sell(eu_instrument, cur_price_eu,eu_count, 'M')

        # ----------Output from position
        if (((eu_model - last_closed_eu) < eu_deact_val)
            and self.pos_by_instrument(si_instrument).count < 0
            and self.pos_by_instrument(eu_instrument).count > 0):
            self.buy(si_instrument,cur_price_si,abs(self.pos_by_instrument(si_instrument).count),'M')
            self.sell(eu_instrument, cur_price_eu,abs(self.pos_by_instrument(eu_instrument).count),'M')

        if (((last_closed_eu - eu_model) < eu_deact_val)
                and self.pos_by_instrument(si_instrument).count > 0
                and self.pos_by_instrument(eu_instrument).count < 0):
            self.sell(si_instrument,cur_price_si,abs(self.pos_by_instrument(si_instrument).count),'M')
            self.buy(eu_instrument, cur_price_eu,abs(self.pos_by_instrument(eu_instrument).count),'M')

        self.trade.stat.add_indicator(self.pos_by_ticker('eu').instrument, 'eu_model', self.cur_date,
                                      self.cur_time, eu_model, 'y--')
        self.trade.stat.add_indicator(self.pos_by_ticker('eu').instrument, 'eu_fact', self.cur_date,
                                      self.cur_time, data_eu[-1], 'b--')










