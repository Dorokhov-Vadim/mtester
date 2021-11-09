# <h1>mtester @octocat :+1:
> <h4>Python package for testing stock market automation strategies on historical data</h4>


####  for example:    


```
from mtester.testing import CandleTest
from mtester.instruments import Instrument
from mtester.providers import FinamSyncProvider
from mtester.strategies.ma_slow_fast import MASlowFast
 

i = {'rts': Instrument('rts', 10, 14.2, 10), 'si': Instrument('si', 1, 1, 1)}
provider = FinamSyncProvider(['mtester/data/1m/rts.txt', 'mtester/data/1m/si.txt'], [i['rts'], i['si']])
strategy = MASlowFast(100)
test = CandleTest(strategy, provider)
test.run()
test.show_trade_stat()
test.show_instrument(i['rts'])
test.show_instrument(i['si'])
```