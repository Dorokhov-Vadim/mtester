from mtester.base_strategies import BaseCandleStrategy
from typing import List, Dict
from mtester.instruments import Instrument
from mtester.providers import Candle, CurCandle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.linear_model import LinearRegression
from datetime import datetime


class Correlation(BaseCandleStrategy):

    def on_candle_close(self, closed_candles: Dict[Instrument, List[Candle]], current_candle: Dict[Instrument, CurCandle]):
        data_si = []
        for candle in closed_candles[self.pos_by_ticker('si').instrument]:
            data_si.append(candle.close)
        cur_price_si = current_candle[self.pos_by_ticker('si').instrument].price
        data_rts = []
        for candle in closed_candles[self.pos_by_ticker('rts').instrument]:
            data_rts.append(candle.close)
        cur_price_rts = current_candle[self.pos_by_ticker('rts').instrument].price


        nd_si = []
        nd_rts = []
        for x in data_si:
            nd_si.append([x])
        for x in data_rts:
            nd_rts.append([x])

        model = LinearRegression(fit_intercept=True)
        model.fit(nd_rts, nd_si)


        # Predict
        # nd_si_model = model.predict(nd_rts)
        si_predict = model.predict([[cur_price_rts]])
        print(si_predict[0][0])
        self.trade.stat.add_indicator(self.pos_by_ticker('si').instrument, 'si_model', self.cur_date,
                                      self.cur_time, si_predict[0][0], 'rs')
        self.trade.stat.add_indicator(self.pos_by_ticker('si').instrument, 'si_fact', self.cur_date,
                                      self.cur_time, cur_price_si, 'gs')
        # plt.figure()
        # plt.scatter(nd_rts, nd_si, c="k", label="fact data")
        # plt.plot(nd_rts, nd_si_model, c="g", label="model_data", linewidth=2)
        # plt.show()
        # exit()







