from datetime import datetime
import pandas as pd
from ccxt import binance
from ccxt.base.errors import NetworkError
import os
from util.ccxtdl import download as dl
from fastapi import HTTPException

from .endpoint import Endpoint


class BinanceEndpoint(Endpoint):
    def __init__(self):
        super().__init__("binance")
        self.symbols = list(map(
            lambda s: s + "/USDT", binance().describe()["options"]["networksById"].values()))

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
            print(
                f"{symbol} downloaded from binance and stored at {self._cache_dir}")
        except NetworkError:
            raise HTTPException(status_code=503, detail="Network error: API request failed")
