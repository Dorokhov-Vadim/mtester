"""Base class for all indicators classes"""
from ..providers import Candle
from typing import  List, Dict


class BaseCandleIndicator:
    def get_value(self, candles: List[Candle]):
        raise Exception(self.__class__.__name__ +' must implement get_value() method')

class IndicatorData:
    def __init__(self, indicator: BaseCandleIndicator, panel=0, type='scatter', color='b', marker='o'):
        self.indicator = indicator
        # self.instrument = instrument
        self.panel = panel
        self.type = type
        self.color = color
        self.marker = marker
        self.lines: List[Dict[str, float]] = []

    def calc_indicator_for_candles(self, instrument_candles: List[Candle]):
        i = 0
        for line_value in self.indicator.get_value(instrument_candles):
            if len(self.lines) < (i+1):
                self.lines.append({})
            self.lines[i][instrument_candles[-1].date + instrument_candles[-1].time] = line_value
            i = i + 1

