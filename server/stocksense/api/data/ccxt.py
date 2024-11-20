from datetime import datetime
import pandas as pd
import ccxt
from ccxt.base.errors import NetworkError
import os
from fastapi import HTTPException

from stocksense.util.ccxtdl import download as dl
from .endpoint import Endpoint

import warnings

warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="ccxt.base.exchange")


class CCXTEndpoint(Endpoint):
    def __init__(self, exchange_name: str):
        super().__init__(exchange_name)
        self._exchange = getattr(ccxt, exchange_name)()
        self.symbols = list(self._exchange.load_markets().keys())

    async def get_kline(self, symbol: str, since: datetime, until: datetime, timeframe: str) -> pd.DataFrame:
        """Get K-line data for a symbol

        Parameters
        ----------
        timeframe : str
            Timeframe for K-line data.
            Defaults to 1d if no parameter provided. Supported timeframe values:  
                1m, 2m, ..., 59m - for minutes  
                1h, 2h, ..., 23h - for hours  
                1d, ..., 7d - for days.
        """
        data_path = os.path.join(
            self._cache_dir, f"binance-{symbol.replace('/', '')}-{timeframe}.pkl")
        if not os.path.exists(data_path):
            await self._download_kline_data(symbol, since, until, timeframe)
        df = pd.read_pickle(data_path)
        # TODO: check if specified time range is available in the data
        return df.loc[(since < df.index) & (df.index < until), :]
        # return df

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
