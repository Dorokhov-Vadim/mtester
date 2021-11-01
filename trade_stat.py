"""Module for collect and visualisation trade statistic"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from typing import Dict, List
from .providers import Candle, Instrument


class TradeStat:
    def __init__(self):
        self.all_candles: Dict[Instrument, List] = dict()
        self.buys: Dict[Instrument, Dict] = dict()
        self.sells: Dict[Instrument, Dict] = dict()

    def add_candle(self, instrument: Instrument, date, time, open, low, high, close, balance, lose):
        data = dict()
        data['date'] = date
        data['time'] = time
        data['open'] = open
        data['low'] = low
        data['high'] = high
        data['close'] = close
        data['balance'] = balance
        data['lose'] = lose
        if self.all_candles.get(instrument) is None:
            self.all_candles[instrument] = []
        self.all_candles[instrument].append(data)


    def add_buy(self, instrument, date, time, price, count):
        data = dict()
        data['price'] = price
        data['count'] = count
        self.buys[instrument][date + time] = data

    def add_sell(self, instrument, date, time, price, count):
        data = dict()
        data['price'] = price
        data['count'] = count
        self.sells[instrument][date + time] = data



    def yield_curve(self):
        pass
        # x = 0
        # X = []
        # for row in self.balance_history:
        #     x = x + 1
        #     X.append(x)
        # plt.plot(X, self.balance_history, '-', color="green")
        # plt.show()

