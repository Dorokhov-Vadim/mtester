import math

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
        # Init data structure
        rts_count = 1
        si_max_count = 14
        si_act_val = 80
        data_si = []
        data_rts = []
        rts_instrument = self.pos_by_ticker('rts').instrument
        si_instrument = self.pos_by_ticker('si').instrument












