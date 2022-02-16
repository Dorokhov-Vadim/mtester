from mtester.providers import Candle
from typing import List
from strategies.channels.channel import Channel
import matplotlib.pyplot as plt


def prepare_data(candles: List[Candle], reduce_window=1, start_candle_index=0):
    lows = []
    highs = []
    x = []
    y = []
    steps = 0

    def add_extremes():
        nonlocal lows, highs, start_candle_index, steps
        low = list()
        low.append(min(lows))
        y.append(low)
        high = list()
        high.append(max(highs))
        y.append(high)
        xl = list()
        xl.append(start_candle_index)
        x.append(xl)
        x.append(xl)
        steps = 0
        lows = []
        highs = []

    for candle in candles:
        lows.append(candle.low)
        highs.append(candle.high)
        steps = steps + 1
        if steps >= reduce_window:
            add_extremes()
        start_candle_index = start_candle_index + 1
    if steps > 0:
        add_extremes()
    return x, y


def draw_channel(ch: Channel):
    lows_y = []
    highs_y = []
    for i in ch.x:
        lows_y.append(ch.low_line.coef * float(i[0]) + ch.low_line.intercept)
    for i in ch.x:
        highs_y.append(ch.high_line.coef * float(i[0]) + ch.high_line.intercept)
    plt.plot(ch.x, ch.y, label="")
    plt.plot(ch.x, lows_y, label="")
    plt.plot(ch.x, highs_y, label="")
    plt.show()
