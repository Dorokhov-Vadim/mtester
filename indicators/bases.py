"""Base class for all indicators classes"""


class BaseCandleIndicator:
    def get_value(self):
        raise Exception('Candles indicators must implement get_value() method')
