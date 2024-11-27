from datetime import datetime
import pandas as pd
import os
from stocksense.api.data.endpoint import Endpoint
import yfinance as yf


class YFinanceEndpoint(Endpoint):
    def __init__(self):
        super().__init__("yfinance")

    async def get_kline(self, symbol: str, begin: datetime, end: datetime, timeframe: str) -> pd.DataFrame:
        data_path = os.path.join(
            self._cache_dir, f"yfinance-{symbol}-{begin.date()}-{end.date()}-{timeframe}.pkl")
        if not os.path.exists(data_path):
            self._download([symbol], begin=begin, end=end, timeframe=timeframe)
        return pd.read_pickle(data_path)

    async def get_multiple_kline(self, symbols: list[str], begin: datetime, end: datetime, timeframe: str) -> dict[str, pd.DataFrame]:
        # not tested (!)
        data_paths = {symbol: os.path.join(
            self._cache_dir, f"yfinance-{symbol}-{begin.date()}-{end.date()}-{timeframe}.pkl") for symbol in symbols}
        _symbols = [symbol for (symbol, path) in data_paths.items() if not os.path.exists(path)]
        if _symbols:
            self._download(_symbols, begin=begin, end=end,
                          timeframe=timeframe, data_path=data_paths[_symbols[0]])
        return {symbol: pd.read_pickle(path) for (symbol, path) in data_paths.items()}

    def _download(self, symbol: list[str], begin: datetime, end: datetime, timeframe: str) -> None:
        try:
            result: pd.DataFrame = yf.download(
                symbol,
                start=begin.date(),
                end=end.date(),
                interval=timeframe,
                timeout=10)
            result.drop("Adj Close", axis=1, inplace=True)
            result.rename({"Close": "close", "Open": "open", "High": "high", "Low": "low",
                           "Volume": "volume"}, axis=1, inplace=True)
            result.index.name = "date"

            for ticker in symbol:
                _res = result.xs(ticker, level="Ticker", axis=1)
                _res.rename_axis(None, axis=1, inplace=True)
                _res.insert(0, "unix", _res.index.astype(int) // 10**6)
                data_path = os.path.join(
                    self._cache_dir, f"yfinance-{ticker}-{begin.date()}-{end.date()}-{timeframe}.pkl")
                _res.to_pickle(data_path)
        except:
            raise Exception("Failed to download data from Yahoo Finance")
