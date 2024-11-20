import pandas as _pd


__all__ = ["data_preprocess"]

def data_preprocess(
    df: _pd.DataFrame,
    sort_by_date: bool = True,
    dropna: bool = True,
    inplace: bool = True,
) -> _pd.DataFrame:

    if not inplace:
        df = df.copy()

    if sort_by_date:
        df.sort_values("date", inplace=True)

    # TODO: add more features

    # Create the feature : ( close[t] - close[t-1] )/ close[t-1]
    df["feature_close"] = df["close"].pct_change()

    # Create the feature : open[t] / close[t]
    df["feature_open"] = df["open"] / df["close"]

    # Create the feature : high[t] / close[t]
    df["feature_high"] = df["high"] / df["close"]

    # Create the feature : low[t] / close[t]
    df["feature_low"] = df["low"] / df["close"]

    # Create the feature : volume[t] / max(*volume[t-7*24:t+1])
    df["feature_volume"] = df["volume"] / df["volume"].rolling(7 * 24).max()

    if dropna:
        df.dropna(inplace=True)  # Clean again !

    return df
