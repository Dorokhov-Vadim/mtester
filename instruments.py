"""Base class for inherit by user instrument abstraction"""


class Instrument:
    def __init__(self, ticker, price, step, step_price, slip):
        # instrument ticker
        self.ticker = ticker
        # instrument 1 lot price
        self.price = price
        # minimal instrument step
        self.step = step
        # price of one instrument step
        self.step_price = step_price
        # count of minimal instrument steps for sell/buy operation
        self.slip = slip
