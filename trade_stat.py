"""Module for collect and visualisation trade statistic"""
import matplotlib as mpl
import matplotlib.pyplot as plt

class TradeStat:
    def __init__(self):
        self.balance_history = []

    def yield_curve(self):
        x = 0
        X = []
        for row in self.balance_history:
            x = x + 1
            X.append(x)
        plt.plot(X, self.balance_history, '-', color="green")
        plt.show()

