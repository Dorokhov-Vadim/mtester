# <h1>mtester :chart_with_upwards_trend:
> <h4>Python package for testing stock market automation strategies on historical data</h4>
> <h4>Synchronized data feed from different sources is supported for testing arbitrage trading algorithms.
> File processing and data synchronization when passing them to the strategy is optimized for memory consumption and is based on
> Python iterator protocol</h4>

####  Example of testing strategy:  


```
from mtester.testing import CandleTest
from mtester.instruments import Instrument
from mtester.providers import FinamSyncProvider
from mtester.strategies.ma_slow_fast import MASlowFast


i = {'rts': Instrument('rts', 10, 14.2, 10), 'si': Instrument('si', 1, 1, 1)}
provider = FinamSyncProvider(['Path/to/data_file_rts.txt', 'Path/to/data_file_si.txt'], [i['rts'], i['si']])
strategy = MASlowFast(window_size=400)
test = CandleTest(strategy, provider)
test.set_from_to_candles(from_candle=200000)
test.run()
test.show_trade_stat()
test.show_instrument(i['rts'])
```

####  Example of history RTS(futures) data file from Finam company(www.finam.ru):  
```
<DATE>;<TIME>;<OPEN>;<HIGH>;<LOW>;<CLOSE>;<VOL>
...
20200106;100000;155480.0000000;155960.0000000;155480.0000000;155790.0000000;3364
20200106;100100;155790.0000000;155810.0000000;155550.0000000;155560.0000000;1393
20200106;100200;155550.0000000;155600.0000000;155500.0000000;155590.0000000;1158
20200106;100300;155590.0000000;155660.0000000;155350.0000000;155370.0000000;1727
20200106;100400;155360.0000000;155370.0000000;155050.0000000;155150.0000000;2919
20200106;100500;155140.0000000;155140.0000000;154840.0000000;155080.0000000;2672
20200106;100600;155080.0000000;155180.0000000;155000.0000000;155150.0000000;1296
20200106;100700;155140.0000000;155160.0000000;155090.0000000;155110.0000000;477
20200106;100800;155110.0000000;155180.0000000;155050.0000000;155100.0000000;1017
20200106;100900;155100.0000000;155120.0000000;154960.0000000;155000.0000000;1164
20200106;101000;154990.0000000;155130.0000000;154910.0000000;155120.0000000;898
20200106;101100;155110.0000000;155190.0000000;155100.0000000;155170.0000000;487
20200106;101200;155170.0000000;155180.0000000;155090.0000000;155120.0000000;522
20200106;101300;155130.0000000;155140.0000000;155100.0000000;155140.0000000;224
...
```