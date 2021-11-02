"""Module for collect and visualisation trade statistic"""

import matplotlib.pyplot as plt
from typing import Dict, List
from .providers import Instrument


class TradeStat:
    def __init__(self):
        self.all_candles: Dict[Instrument, List] = dict()
        self.buys: Dict[Instrument, Dict] = dict()
        self.sells: Dict[Instrument, Dict] = dict()
        self.user_indicators: Dict[Instrument, Dict[str, Dict]] = dict()

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
        if self.buys.get(instrument) is None:
            self.buys[instrument] = dict()
        self.buys[instrument][date + time] = data

    def add_sell(self, instrument, date, time, price, count):
        data = dict()
        data['price'] = price
        data['count'] = count
        if self.sells.get(instrument) is None:
            self.sells[instrument] = dict()
        self.sells[instrument][date + time] = data

    def show_trade_stat(self, instrument):
        balance = []
        loses = []
        index = 0
        timestamps = []

        for candle in self.all_candles[instrument]:
            index = index + 1
            timestamps.append(index)
            balance.append(candle['balance'])
            loses.append(candle['lose'])
            # timestamp = candle['date'] + candle['time']

        print('Max lose = ' + str(max(*loses)))
        plt.plot(timestamps, balance, 'r--')
        plt.show()

    def show_instrument(self, instrument):
        all = []
        buys = []
        sells = []
        timestamps = []
        indicators = dict()
        index = 0

        for candle in self.all_candles[instrument]:
            all.append(candle['close'])
            index = index + 1
            timestamps.append(index)
            timestamp = candle['date'] + candle['time']

            if self.buys.get(instrument).get(timestamp) is None:
                buys.append(None)
            else:
                buys.append(self.buys[instrument][timestamp]['price'])

            if self.sells.get(instrument).get(timestamp) is None:
                sells.append(None)
            else:
                sells.append(self.sells[instrument][timestamp]['price'])

            if not (self.user_indicators.get(instrument) is None):
                for indicator in self.user_indicators[instrument]:
                    if indicators.get(indicator) is None:
                        indicators[indicator] = []
                    if self.user_indicators[instrument][indicator].get(timestamp) is None:
                        indicators[indicator].append(None)
                    else:
                        indicators[indicator].append(self.user_indicators[instrument][indicator][timestamp])
        for indicator in indicators:
            plt.plot(timestamps, indicators[indicator], 'g--', )
        plt.plot(timestamps, all, 'b--',)
        plt.plot(timestamps, buys, 'g^', timestamps, sells, 'rv')

        plt.show()

    def add_indicator(self, instrument, ind_name, date, time, value, chart_style='-'):
        if self.user_indicators.get(instrument) is None:
            self.user_indicators[instrument] = dict()
        if self.user_indicators[instrument].get(ind_name) is None:
            self.user_indicators[instrument][ind_name] = dict()
        self.user_indicators[instrument][ind_name][date + time] = value
        self.user_indicators[instrument][ind_name]['style'] = chart_style




