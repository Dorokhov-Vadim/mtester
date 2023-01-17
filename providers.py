"""Classes for providing historical data (candles and tick price data)"""
from typing import Iterator, List, Set
from .instruments import Instrument


class Candle:
    def __init__(self, instrument):
        self.instrument: Instrument = instrument
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.vol = 0
        self.date = ''
        self.time = ''


class CurCandle:
    def __init__(self, instrument):
        self.instrument = instrument
        self.date = ''
        self.time = ''
        self.price = 0





class BaseCandlesProvider(Iterator):

    def __iter__(self):
        return self

    def __next__(self) -> Candle:
        raise Exception('BaseCandlesProvider subclass must implement __next__ method')


class BaseSyncProvider(Iterator):

    def __iter__(self):
        return self

    def __next__(self) -> List[Candle]:
        raise Exception('BaseSyncProvider subclass must implement __next__ method')


class FinamCandlesProvider(BaseCandlesProvider):

    def __init__(self, filename, instrument, el_sep=';'):
        self.instrument = instrument
        self.filename = filename
        self.file = open(filename, 'r')
        self.el_indexes = {}
        self.el_sep = el_sep
        header = next(self.file).rstrip()
        header = header.split(self.el_sep)
        for i in range(0, len(header)):
            self.el_indexes[i] = header[i].lstrip('<').rstrip('>')

    def __next__(self) -> Candle:
        row = next(self.file).rstrip()
        row = row.split(self.el_sep)
        candle = Candle(self.instrument)
        for i in range(0, len(row)):
            field_name = self.el_indexes[i].lower()
            if field_name in ('date', 'time'):
                field_val = str(row[i])
            else:
                field_val = float(row[i])
            candle.__dict__[field_name] = field_val
        return candle


class FinamSyncProvider(BaseSyncProvider):
    def __init__(self, file_names: List, instruments: List[Instrument], el_sep=';'):
        if len(file_names) != len(instruments):
            raise Exception('file_names list and instruments list have a different len')
        self.el_sep = el_sep
        self.timestamps: List[Set] = []
        self.intersect_stamps: Set = set()
        self.file_names = file_names
        self.instruments = instruments
        print('data loading...')
        for file_name in self.file_names:
            timestamps = set()
            provider = FinamCandlesProvider(file_name, None)
            for candle in provider:
                timestamps.add(candle.date + candle.time)
            self.timestamps.append(timestamps)
        self.intersect_stamps = self.timestamps[0]
        print('data sync...')
        for el in self.timestamps:
            self.intersect_stamps = self.intersect_stamps.intersection(el)
        self.opened_files: List[FinamCandlesProvider] = []
        idx = 0
        for file_name in self.file_names:
            self.opened_files.append(FinamCandlesProvider(file_name, self.instruments[idx], self.el_sep))
            idx = idx + 1

    def __iter__(self):
        return self

    def __next__(self) -> List[Candle]:
        candle_list = []
        for file in self.opened_files:
            for candle in file:
                if (candle.date + candle.time) in self.intersect_stamps:
                    candle_list.append(candle)
                    break
        if len(candle_list) == 0:
            raise StopIteration()
        return candle_list
