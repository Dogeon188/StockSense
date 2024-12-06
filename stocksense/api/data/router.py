from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from datetime import datetime
import pandas as pd
from ccxt.base.errors import NetworkError

from .endpoint import Endpoint
from .ccxt import CCXTEndpoint
# from .baostock import BaostockEndpoint
from .yfinance import YFinanceEndpoint


router = APIRouter(
    prefix="/data",
    tags=["data"],
    responses={404: {"description": "Not found"}},
)

endpoints: dict[str, Endpoint] = {
    # "baostock": BaostockEndpoint(),
    "yfinance": YFinanceEndpoint(),
}

try:
    endpoints["binance"] = CCXTEndpoint("binance")
    endpoints["huobi"] = CCXTEndpoint("huobi")
    endpoints["bitfinex2"] = CCXTEndpoint("bitfinex2")
except NetworkError:
    pass

@router.get("/endpoints")
async def get_endpoints() -> list[str]:
    """Get all available endpoints

    Returns
    -------
    dict
        A dictionary containing all available endpoints
    """
    return list(endpoints.keys())


def get_endpoint(endpoint: str) -> Endpoint:
    if endpoint not in endpoints:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoints[endpoint]


@router.get("/endpoints/{endpoint}/symbols")
async def get_symbols(endpoint: str) -> list[str]:
    return get_endpoint(endpoint).list_symbols()


async def get_kline_df(
    endpoint: str,
    symbol: str,
    since: datetime,
    until: datetime,
    timeframe: str = "1d",
) -> pd.DataFrame:
    """Get K-line data for a symbol

    Parameters
    ----------
    endpoint : str
        Name of the endpoint
    symbol : str
        Symbol for the K-line data
    since : datetime
        Start date for the K-line data
    until : datetime
        End date for the K-line data
    timeframe : str
        Timeframe for K-line data.
        Defaults to 1d if no parameter provided. Supported values:  
            1m, 2m....59m for minutes  
            1h, 2h....23h - for hours  
            1d...7d - for days.

    Returns
    -------
    pd.DataFrame
        K-line data for the symbol. Contains columns:
        - date : datetime, beginning of the timeframe
        - unix : int, unix timestamp of the beginning of the timeframe (milliseconds)
        - open : float, opening price
        - high : float, highest price
        - low : float, lowest price
        - close : float, closing price
        - volume : float, volume of the asset traded
    """
    return await get_endpoint(endpoint).get_kline(symbol, since, until, timeframe)


@router.get("/endpoints/{endpoint}/kline", response_class=PlainTextResponse)
async def get_kline_csv(
    endpoint: str,
    symbol: str,
    since: int,
    until: int,
    timeframe: str = "1d",
) -> str:
    """Get K-line data for a symbol in CSV format

    Parameters
    ----------
    endpoint : str
        Name of the endpoint
    symbol : str
        Symbol for the K-line data
    since : int
        Start date for the K-line data in unix timestamp (milliseconds)
    until : int
        End date for the K-line data in unix timestamp (milliseconds)
    timeframe : str, optional
        Timeframe for K-line data.
        Defaults to 1d if no parameter provided. Supported values:  
            1m, 2m....59m for minutes  
            1h, 2h....23h - for hours  
            1d...7d - for days.

    Returns
    -------
    str
        K-line data for the symbol in CSV string format. Contains columns:
        - date : datetime, beginning of the timeframe
        - unix : int, unix timestamp of the beginning of the timeframe (milliseconds)
        - open : float, opening price
        - high : float, highest price
        - low : float, lowest price
        - close : float, closing price
        - volume : float, volume of the asset traded
    """
    _since = datetime.fromtimestamp(since / 1000)
    _until = datetime.fromtimestamp(until / 1000)
    df = await get_kline_df(endpoint, symbol, _since, _until, timeframe)
    return df.to_csv()
