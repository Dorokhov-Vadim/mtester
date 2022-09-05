"""Module for collect and visualisation trade statistic"""

import matplotlib.pyplot as plt
from typing import Dict, List
from .providers import Instrument
import pandas as pd
import mplfinance as mpf
from .indicators.bases import IndicatorData

class TradeStat:
    def __init__(self):
        self.balance_hist = []
        self.trans_count = 0
        self.all_candles: Dict[Instrument, List] = dict()
        self.buys: Dict[Instrument, Dict] = dict()
        self.sells: Dict[Instrument, Dict] = dict()
        self.indicators: Dict[Instrument, List[IndicatorData]] = {}

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
        _, (ax1) = plt.subplots(1, 1, sharex=True, num="Balance dynamic")
        ax1.plot([num for num in range(0, len(self.balance_hist))], self.balance_hist, 'r-')
        plt.show()

    def show_instrument(self, instrument):
        indicators = []
        ind_sub_plots = []
        df_dict = dict()
        df_dict['Date'] = []
        df_dict['Open'] = []
        df_dict['Low'] = []
        df_dict['High'] = []
        df_dict['Close'] = []
        df_dict['Buys'] = []
        df_dict['Sells'] = []
        if self.indicators.get(instrument) is not None:
            for indicator_data in self.indicators[instrument]:
                for _ in indicator_data.lines:
                    indicators.append([])

        for candle in self.all_candles[instrument]:
            df_dict['Date'].append(candle['date'] + candle['time'])
            df_dict['Open'].append(candle['open'])
            df_dict['Low'].append(candle['low'])
            df_dict['High'].append(candle['high'])
            df_dict['Close'].append(candle['close'])
            if self.buys[instrument].get(candle['date'] + candle['time']) is None:
                df_dict['Buys'].append(None)
            else:
                df_dict['Buys'].append(self.buys[instrument][candle['date'] + candle['time']]['price'])

            if self.sells[instrument].get(candle['date'] + candle['time']) is None:
                df_dict['Sells'].append(None)
            else:
                df_dict['Sells'].append(self.sells[instrument][candle['date'] + candle['time']]['price'])
            # user indicators to dataframes
            if self.indicators.get(instrument) is not None:
                i = 0
                for indicator_data in self.indicators[instrument]:
                    for line in indicator_data.lines:
                        indicators[i].append(line.get(candle['date'] + candle['time']))
                        i = i + 1

        # for ind in indicators:
        #     ind_sub_plots.append(mpf.make_addplot(pd.DataFrame(ind), panel = 1))
        if self.indicators.get(instrument) is not None:
            i = 0
            for indicator_data in self.indicators[instrument]:
                for _ in indicator_data.lines:
                    ind_sub_plots.append(mpf.make_addplot(pd.DataFrame(indicators[i]),
                                                          panel=indicator_data.panel,
                                                          color=indicator_data.color,
                                                          type=indicator_data.type))
                    i = i + 1

        df = pd.DataFrame(df_dict)
        df = df.set_index('Date')
        df.index = pd.to_datetime(df.index)

        buys = mpf.make_addplot(pd.DataFrame(df_dict['Buys']), color='g', type='scatter', marker='^')
        sells = mpf.make_addplot(pd.DataFrame(df_dict['Sells']), color='r', type='scatter', marker='v')



        mpf.plot(df, type='candle',
                 title='\nInstrument: ' + instrument.ticker,
                 addplot=[buys, sells] + ind_sub_plots ,
                 warn_too_much_data=len(self.all_candles[instrument]))

    def get_line(self, instrument: Instrument, name, line_num):
        for ind in self.indicators[instrument]:
            if ind.name == name:
                return ind.lines[line_num]

    def get_ind_by_candle(self,instrument: Instrument, name, line_num, candle):
        for ind in self.indicators[instrument]:
            if ind.name == name:
                return ind.lines[line_num].get(candle.date+candle.time)
