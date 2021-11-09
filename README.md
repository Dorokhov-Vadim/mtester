# mtester
Python package for testing stock market automation strategies on historical data


#########     Proof of concept:    ###########

#########  Import data structures  ###########

from mtester.testing import CandleTest

from mtester.instruments import Instrument

from mtester.providers import FinamSyncProvider

from mtester.strategies.MA_slow_fast import MASlowFast



#########  Create test  ########## 

i = {'rts': Instrument('rts', 10, 14.2, 10), 'si': Instrument('si', 1, 1, 1)}

provider = FinamSyncProvider(['data/1m/temp_rts.txt', 'data/1m/temp_si.txt'], [i['rts'], i['si']])

strategy = MASlowFast(100)

test = CandleTest(strategy, provider)

test.run()

test.show_trade_stat()

test.show_instrument(i['rts'])

test.show_instrument(i['si'])
