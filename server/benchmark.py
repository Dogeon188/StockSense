import argparse
import pandas as pd
import asyncio

from stockcore.parameters import Parameters, DataParameters
from stocksense.api import data as scdata


async def _load_data(data_params: DataParameters) -> pd.DataFrame:
    tasks = []
    for symbol in data_params.symbols:
        tasks.append(scdata.get_kline_df(
            data_params.endpoint,
            symbol=symbol,
            timeframe=data_params.timeframe,
            since=data_params.since,
            until=data_params.until
        ))
    results = await asyncio.gather(*tasks)
    return results

def load_data(data_params: DataParameters) -> dict[str, pd.DataFrame]:
    print("Loading data...")
    results = asyncio.run(_load_data(data_params))
    return dict(zip(data_params.symbols, results))


def main(config_path):
    # Load the configuration file
    params = Parameters.from_json(config_path)
    data = load_data(params.data)
    print(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Evaluate the performance of a trading strategy')
    parser.add_argument('config', type=str,
                        help='Path to the configuration file')
    args = parser.parse_args()
    main(args.config)
