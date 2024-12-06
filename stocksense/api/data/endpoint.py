from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Optional
import pandas as pd
import os

from stocksense.util.singleton import SingletonABCMeta


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
        """Get a list of symbols available on the endpoint

        Returns
        -------
        list[str]
            List of symbols available on the endpoint
        """
        return self.symbols

    async def get_kline(self, symbol: str, since: datetime, until: datetime, timeframe: str) -> pd.DataFrame:
        """Get K-line data for a symbol

        Parameters
        ----------
        symbol : str
            The symbol to get data for
        since : datetime
            Start of the time range
        until : datetime
            End of the time range
        timeframe : str
            Timeframe for K-line data.
            Defaults to 1d if no parameter provided. Supported values:  
                1m, 2m, ..., 59m - for minutes  
                1h, 2h, ..., 23h - for hours  
                1d, ..., 7d - for days.

        Returns
        -------
        pd.DataFrame
            K-line data for the symbol. Contains columns:
            - date : datetime, beginning of the timeframe
            - unix : int, unix timestamp of the beginning of the timeframe
            - open : float, opening price
            - high : float, highest price
            - low : float, lowest price
            - close : float, closing price
            - volume : float, volume of the asset traded
        """
        raise NotImplementedError

    def get_multiple_kline(self, symbol: list[str], begin: datetime, end: datetime, timeframe: str) -> dict[str, pd.DataFrame]:
        """Get K-line data for multiple symbols

        Parameters
        ----------
        symbol : list
            List of symbols to get data for
        begin : datetime
            Start of the time range
        end : datetime
            End of the time range
        timeframe : str
            Timeframe for K-line data.
            Defaults to 1d if no parameter provided. Supported values:  
                1m, 2m, ..., 59m - for minutes  
                1h, 2h, ..., 23h - for hours  
                1d, ..., 7d - for days.

        Returns
        -------
        dict[str, pd.DataFrame]
            A dictionary containing K-line data for each symbol. Each value is a DataFrame containing columns:
            - date : datetime, beginning of the timeframe
            - unix : int, unix timestamp of the beginning of the timeframe
            - open : float, opening price
            - high : float, highest price
            - low : float, lowest price
            - close : float, closing price
            - volume : float, volume of the asset traded
        """
        raise NotImplementedError

    async def watch_ticker(
            self,
            symbol: str,
            timeframe: str,
            callback: Callable[[pd.DataFrame], bool],
            /,
            interval: Optional[int],
            limit: Optional[int]) -> None:
        """Subscribe to K-line data updates for a symbol

        Parameters
        ----------
        symbol : str
            The symbol to watch
        timeframe : str
            Timeframe for K-line data.
            Defaults to 1d if no parameter provided. Supported timeframe values:  
                1m, 2m, ..., 59m - for minutes  
                1h, 2h, ..., 23h - for hours  
                1d, ..., 7d - for days.
        callback : Callable[[pd.DataFrame], bool]
            A callback function that will be called each time new data is available.
            A single argument is passed to the callback: a DataFrame containing the new data.
            The function should return True to continue watching, or False to stop.
        interval : Optional[int]
            Time interval in seconds between each data fetch
        limit : Optional[int]
            Number of data points to fetch each time
        """
        raise NotImplementedError
