from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd
import os

from util.singleton import SingletonABCMeta


class Endpoint(metaclass=SingletonABCMeta):
    def __init__(self, name: str):
        self.name = name
        self.symbols: list[str] = []

        if not os.path.exists("cache"):
            os.makedirs("cache")
        self._cache_dir = os.path.join("cache", self.name)
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)

    def list_symbols(self) -> list[str]:
        return self.symbols

    def get_kline(self, symbol: str, since: datetime, until: datetime, timeframe: str, **kwargs) -> pd.DataFrame:
        raise NotImplementedError
