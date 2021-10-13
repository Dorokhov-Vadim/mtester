
from .trading import CandleEvent


class BaseTest:
    def __init__(self):
        self.strategy = None
        self.data = None

    def run(self):
        raise Exception('Testing class must implement run method')


class CandleTest(BaseTest):

    def run(self):
        print('Market testing is running...')



        if self.strategy is None:
            raise Exception('strategy is None')
        if self.data is None :
            raise Exception('historical data is empty')
        print('Market testing is done.')

