"""Module for collect and visualisation trade statistic"""

import matplotlib.pyplot as plt
from typing import Dict, List
from .providers import Instrument


class TradeStat:
    def __init__(self):
        self.balance_hist = []
        self.trans_count = 0
        self.all_candles: Dict[Instrument, List] = dict()
        self.buys: Dict[Instrument, Dict] = dict()
        self.sells: Dict[Instrument, Dict] = dict()
        self.user_indicators: Dict[Instrument, Dict[str, Dict]] = dict()

    def inc_trans(self):
        self.trans_count = self.trans_count + 1

    def add_candle(self, instrument: Instrument, date, time, open, low, high, close, lose, profit):
        data = dict()
        data['date'] = date
        data['time'] = time
        data['open'] = open
        data['low'] = low
        data['high'] = high
        data['close'] = close
        data['lose'] = lose
        data['profit'] = profit
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

    def show_trade_stat(self):
        all_loses = []
        print('Trans count = '+str(self.trans_count))
        for instrument in self.all_candles:
            loses = []
            for candle in self.all_candles[instrument]:
                loses.append(candle['lose'])
            all_loses.append(loses)
            print('Max lose of ' + instrument.ticker + ' = ' + str(max(*loses)))
        sum_loses = [sum(loses) for loses in zip(*all_loses)]
        # print(sum_loses)
        print('Permanent complex lose = '+str(max(*sum_loses)))
        print('Balance = '+str(self.balance_hist[-1]))
        plt.plot([num for num in range(0, len(self.balance_hist))], self.balance_hist, 'r-')
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

            if self.buys.get(instrument) is None or self.buys.get(instrument).get(timestamp) is None:
                buys.append(None)
            else:
                buys.append(self.buys[instrument][timestamp]['price'])

            if self.sells.get(instrument) is None or self.sells.get(instrument).get(timestamp) is None:
                sells.append(None)
            else:
                sells.append(self.sells[instrument][timestamp]['price'])

            if not (self.user_indicators.get(instrument) is None):
                for indicator in self.user_indicators[instrument]:
                    if indicators.get(indicator) is None:
                        indicators[indicator] = dict()
                        indicators[indicator]['style'] = ''
                        indicators[indicator]['candles'] = []
                        indicators[indicator]['subplot'] = False
                    if self.user_indicators[instrument][indicator].get(timestamp) is None:
                        indicators[indicator]['candles'].append(None)
                    else:
                        indicators[indicator]['candles'].append(self.user_indicators[instrument][indicator][timestamp])
                    indicators[indicator]['style'] = self.user_indicators[instrument][indicator]['style']
                    indicators[indicator]['subplot'] = self.user_indicators[instrument][indicator]['subplot']
        add_sub_plot = False
        for indicator in indicators:
            if indicators[indicator]['subplot']:
                add_sub_plot = True

        if add_sub_plot:
            figure, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
            for indicator in indicators:
                if indicators[indicator]['subplot']:
                    ax2.plot(timestamps, indicators[indicator]['candles'], indicators[indicator]['style'])
                else:
                    ax1.plot(timestamps, indicators[indicator]['candles'], indicators[indicator]['style'])

            ax1.plot(timestamps, all, 'b-', )
            ax1.plot(timestamps, buys, 'g^', timestamps, sells, 'rv')
        else:
            for indicator in indicators:
                plt.plot(timestamps, indicators[indicator]['candles'], indicators[indicator]['style'])
                plt.plot(timestamps, all, 'b-', )
                plt.plot(timestamps, buys, 'g^', timestamps, sells, 'rv')
        plt.show()

    def add_indicator(self, instrument, ind_name, date, time, value, chart_style='-', subplot=False):
        if self.user_indicators.get(instrument) is None:
            self.user_indicators[instrument] = dict()
        if self.user_indicators[instrument].get(ind_name) is None:
            self.user_indicators[instrument][ind_name] = dict()
        self.user_indicators[instrument][ind_name][date + time] = value
        self.user_indicators[instrument][ind_name]['style'] = chart_style
        self.user_indicators[instrument][ind_name]['subplot'] = subplot
