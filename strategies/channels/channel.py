from lib.mtester.providers import Candle
from typing import List, Callable
from sklearn.linear_model import QuantileRegressor
from sklearn.utils.validation import column_or_1d


class Line:
    def __init__(self, coef, intercept):
        self.coef = coef
        self.intercept = intercept


class Channel:
    def __init__(self, data: List[Candle], data_preparer: Callable, start_candle_index=0, reduce_coef=1):
        self.data = data
        self.reduce_coef = reduce_coef
        self.low_quantile = 0.001
        self.high_quantile = 0.999
        self.data_preparer = data_preparer
        self.low_line = None
        self.high_line = None
        self.start_candle_index = start_candle_index
        self.x = None
        self.y = None

    def build_channel(self):
        x, y = self.data_preparer(self.data, reduce_window=self.reduce_coef, start_candle_index=self.start_candle_index)
        self.x = x
        self.y = y
        qr = QuantileRegressor(quantile=self.low_quantile, alpha=0)
        qr.fit(x, column_or_1d(y, warn=False))
        self.low_line = Line(qr.coef_[0], qr.intercept_)
        qr = QuantileRegressor(quantile=self.high_quantile, alpha=0)
        qr.fit(x, column_or_1d(y, warn=False))
        self.high_line = Line(qr.coef_[0], qr.intercept_)

    def low_line_at(self, x):
        return self.low_line.coef * x + self.low_line.intercept

    def high_line_at(self, x):
        return self.high_line.coef * x + self.high_line.intercept



