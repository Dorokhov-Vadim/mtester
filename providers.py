"""Classes for providing historical data (candles and tick price data)"""
from typing import Iterator, List, Set


class Candle:
    def __init__(self):
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.vol = 0
        self.date = None
        self.time = None


class FinamCandlesProvider(Iterator):

    def __init__(self, filename, el_sep=';'):
        self.filename = filename
        self.file = open(filename, 'r')
        self.el_indexes = {}
        self.el_sep = el_sep
        header = next(self.file).rstrip()
        header = header.split(self.el_sep)
        for i in range(0, len(header)):
            self.el_indexes[i] = header[i].lstrip('<').rstrip('>')

    def __iter__(self):
        return self

    def __next__(self) -> Candle:
        row = next(self.file).rstrip()
        row = row.split(self.el_sep)
        candle = Candle()
        for i in range(0, len(row)):
            candle.__dict__[self.el_indexes[i].lower()] = row[i]
        return candle


class FinamSyncProvider(Iterator):
    def __init__(self, file_names: List, el_sep=';'):
        self.el_sep = el_sep
        self.timestamps: List[Set] = []
        self.intersect_stamps: Set = set()
        self.file_names = file_names
        for file_name in self.file_names:
            timestamps = set()
            provider = FinamCandlesProvider(file_name)
            for candle in provider:
                timestamps.add(candle.date + candle.time)
            self.timestamps.append(timestamps)
        self.intersect_stamps = self.timestamps[0]
        for el in self.timestamps:
            self.intersect_stamps = self.intersect_stamps.intersection(el)
        self.opened_files: List[FinamCandlesProvider] = []
        for file_name in self.file_names:
            self.opened_files.append(FinamCandlesProvider(file_name, self.el_sep))

    def __iter__(self):
        return self

    def __next__(self):
        candle_list = []
        for file in self.opened_files:
            for candle in file:
                if (candle.date + candle.time) in self.intersect_stamps:
                    candle_list.append(candle)
                    break
        if len(candle_list) == 0:
            raise StopIteration()
        return candle_list











