from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd
import os
from stocksense.api.data.endpoint import Endpoint
import yfinance as yf

from stocksense.util.singleton import SingletonABCMeta

class YFinanceEndpoint(Endpoint):
    def __init__(self):
        super().__init__("yfinance")

    def get_kline(self, symbol: str, begin: datetime, end: datetime, timeframe: str) -> pd.DataFrame:
        """Get data for a symbol

        Parameters
        ----------
        symbol : list
        """
        data_path = os.path.join(
            self._cache_dir, f"yfinance-{symbol}-{begin.date()}-{end.date()}-{timeframe}.pkl")
        if not os.path.exists(data_path):
            self.download(symbol, start=begin.date(), end=end.date(), interval=timeframe, data_path=data_path)
        result = pd.read_pickle(data_path)
        return result
    
    def get_multiple_kline(self, symbol: list, begin: datetime, end: datetime, timeframe: str) -> pd.DataFrame:
        """Get data for multiple symbols

        Parameters
        ----------
        symbol : list
        """
        data_path = os.path.join(
            self._cache_dir, f"yfinance-{symbol.join('_')}-{begin.date()}-{end.date()}-{timeframe}.pkl")
        if not os.path.exists(data_path):
            self.download(symbol, start=begin.date(), end=end.date(), interval=timeframe, data_path=data_path)
        result = pd.read_pickle(data_path)
        return result
    
    def download(self, symbol, begin: datetime, end: datetime, timeframe: str, data_path: str):
        try:
            result =  yf.download(symbol, start=begin.date(), end=end.date(), interval=timeframe, timeout = 10)
            result.to_pickle(data_path)
        except:
            raise Exception("Failed to download data from Yahoo Finance")