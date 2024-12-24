import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import datetime


EXCHANGE_LIMIT_RATES = {
    "bitfinex2": {
        "limit": 10_000,
        "pause_every": 1,
        "pause": 3,  # seconds
    },
    "binance": {
        "limit": 1_000,
        "pause_every": 10,
        "pause": 1,  # seconds
    },
    "huobi": {
        "limit": 1_000,
        "pause_every": 10,
        "pause": 1,  # seconds
    }
}

# TODO: make this more pythonic


async def _ohlcv(exchange, symbol, timeframe, limit, step_since, timedelta):
    result = await exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit, since=step_since)
    result_df = pd.DataFrame(
        result, columns=["timestamp_open", "open", "high", "low", "close", "volume"])
    for col in ["open", "high", "low", "close", "volume"]:
        result_df[col] = pd.to_numeric(result_df[col])
    result_df["date_open"] = pd.to_datetime(
        result_df["timestamp_open"], unit="ms")
    result_df["date_close"] = pd.to_datetime(
        result_df["timestamp_open"] + timedelta, unit="ms")

    return result_df


async def _download_symbol(exchange, symbol, timeframe='5m', since=int(datetime.datetime(year=2020, month=1, day=1).timestamp()*1E3), until=int(datetime.datetime.now().timestamp()*1E3), limit=1000, pause_every=10, pause=1):
    timedelta = int(pd.Timedelta(timeframe).to_timedelta64()/1E6)
    tasks = []
    results = []
    for step_since in range(since, until, limit * timedelta):
        tasks.append(
            asyncio.create_task(
                _ohlcv(exchange, symbol, timeframe, limit, step_since, timedelta))
        )
        if len(tasks) >= pause_every:
            results.extend(await asyncio.gather(*tasks))
            await asyncio.sleep(pause)
            tasks = []
    if len(tasks) > 0:
        results.extend(await asyncio.gather(*tasks))
    final_df = pd.concat(results, ignore_index=True)
    final_df = final_df.loc[(since < final_df["timestamp_open"]) & (
        final_df["timestamp_open"] < until), :]
    # del final_df["timestamp_open"]

    final_df.rename(columns={"date_open": "date", "timestamp_open": "unix"}, inplace=True)
    final_df.set_index('date', drop=True, inplace=True)
    final_df.sort_index(inplace=True)
    final_df.dropna(inplace=True)
    final_df.drop_duplicates(inplace=True)
    final_df.drop(columns=["date_close"], inplace=True)
    return final_df


async def _download_symbols(exchange_name, symbols, dir, timeframe,  **kwargs):
    exchange = getattr(ccxt, exchange_name)({'enableRateLimit': True})
    for symbol in symbols:
        df = await _download_symbol(exchange=exchange, symbol=symbol, timeframe=timeframe, **kwargs)
        save_file = (
            f"{dir}/{exchange_name}-{symbol.replace('/', '')}-{timeframe}.pkl")
        print(
            f"{symbol} downloaded from {exchange_name} and stored at {save_file}")
        df.to_pickle(save_file)
    await exchange.close()


async def download(
        exchange_names: list[str],
        symbols: list[str],
        timeframe: str,
        dir: str,
        since: datetime.datetime,
        until: datetime.datetime = datetime.datetime.now()):
    """Download OHLCV data for a list of symbols from a list of exchanges

    Parameters
    ----------
    exchange_names : list[str]
        List of exchange names. See https://github.com/ccxt/ccxt for a list of supported exchanges
    symbols : list[str]
        List of symbols to download data for. Available symbols depend on the exchange
    timeframe : str
        Timeframe for the OHLCV data.
        Defaults to 1d if no parameter provided. Supported timeframe values:  
            1m,2m....59m for minutes  
            1h, 2h....23h - for hours  
            1d...7d - for days.
    dir : str
        Directory to store the downloaded data
    since : datetime.datetime
        Start datetime for the data
    until : datetime.datetime, optional
        End datetime for the data, by default datetime.datetime.now()
    """
    tasks = []
    for exchange_name in exchange_names:

        limit = EXCHANGE_LIMIT_RATES[exchange_name]["limit"]
        pause_every = EXCHANGE_LIMIT_RATES[exchange_name]["pause_every"]
        pause = EXCHANGE_LIMIT_RATES[exchange_name]["pause"]
        tasks.append(
            _download_symbols(
                exchange_name=exchange_name, symbols=symbols, timeframe=timeframe, dir=dir,
                limit=limit, pause_every=pause_every, pause=pause,
                since=int(since.timestamp()*1E3), until=int(until.timestamp()*1E3)
            )
        )
    await asyncio.gather(*tasks)
