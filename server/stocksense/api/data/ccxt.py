from datetime import datetime
import pandas as pd
import ccxt
from ccxt.base.exchange import Exchange
from ccxt.base.errors import NetworkError
import os
from fastapi import HTTPException
import asyncio
from typing import Callable

from stocksense.util.ccxtdl import download as dl
from .endpoint import Endpoint


class CCXTEndpoint(Endpoint):
    def __init__(self, exchange_name: str):
        super().__init__(exchange_name)
        self._exchange: Exchange = getattr(ccxt, exchange_name)()
        self.symbols = list(self._exchange.load_markets().keys())

    async def get_kline(self, symbol: str, since: datetime, until: datetime, timeframe: str) -> pd.DataFrame:
        data_path = os.path.join(
            self._cache_dir, f"binance-{symbol.replace('/', '')}-{timeframe}.pkl")
        if not os.path.exists(data_path):
            await self._download_kline_data(symbol, since, until, timeframe)
        df = pd.read_pickle(data_path)
        # TODO: check if specified time range is available in the data
        return df.loc[(since < df.index) & (df.index < until), :]
        # return df

    async def watch_ticker(
            self,
            symbol: str,
            timeframe: str,
            callback: Callable[[pd.DataFrame], bool] = lambda: True,
            /,
            interval: int = 5,
            limit: int = 100) -> None:
        while True:
            raw = self._exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(
                raw, columns=["unix", "open", "high", "low", "close", "volume"])
            df["date"] = pd.to_datetime(df["unix"], unit="ms")
            df.set_index("date", inplace=True)
            # yield df
            if not callback(df):
                break
            await asyncio.sleep(interval)

    async def _download_kline_data(self, symbol: str, since: datetime, until: datetime, timeframe: str):
        try:
            await dl(
                exchange_names=["binance"],
                symbols=[symbol],
                timeframe=timeframe,
                dir=self._cache_dir,
                since=since,
                until=until,
            )
        except NetworkError:
            raise HTTPException(
                status_code=503, detail="Network error: API request failed")
