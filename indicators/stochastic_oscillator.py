from .bases import BaseCandleIndicator
from typing import List
from ..providers import Candle


class StochasticOscillator(BaseCandleIndicator):
    def __init__(self, k_len, k_smoth, d_smoth):
        self.k_len = k_len
        self.k_smoth = k_smoth
        self.d_smoth = d_smoth

    def get_value(self, candles: List[Candle]):
        if len(candles) < self.k_len + self.k_smoth + self.d_smoth:
            return None
        candles = candles[-(self.k_len + self.k_smoth + self.d_smoth):]
        lows = []
        highs = []
        k_vals = []
        k_smothed = []
        for candle in candles:
            lows.append(candle.low)
            highs.append(candle.high)
        i = 0
        for candle in candles:
            i = i + 1
            if i >= self.k_len:
                cur_price = candle.close
                k_vals.append((cur_price - min(lows[i-self.k_len:i])) / (max(highs[i-self.k_len:i]) - min(lows[i-self.k_len:i])))
        for i in range(1, len(k_vals)+1):
            if i >= self.k_smoth:
                k_smothed.append(sum(k_vals[i-self.k_smoth:i]) / self.k_smoth)
        d_smothed = (sum(k_smothed[-self.d_smoth:]) / self.d_smoth)
        return k_smothed[-1], d_smothed
