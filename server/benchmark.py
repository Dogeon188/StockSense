import argparse
import pandas as pd
import asyncio
from tqdm import tqdm

from stockcore.parameters import Parameters, DataParameters
from stocksense.api import data as scdata
import stockcore.environment as scenv


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
    results = asyncio.run(_load_data(data_params))
    return dict(zip(data_params.symbols, results))


def main(config_path):
    # Load the configuration file
    params = Parameters.from_json(config_path)

    # Load the data
    print("Loading data...")
    df_dict = load_data(params.data)
    dfs = list(df_dict.values())

    # Split the data

    train_split_end = int(params.data.train_ratio * len(dfs[0]))
    train_split_end_date = dfs[0].index[train_split_end]
    val_split_end = int((params.data.train_ratio + params.data.val_ratio) * len(dfs[0]))
    val_split_end_date = dfs[0].index[val_split_end]

    train_split = {symbol: df[:train_split_end_date] for symbol, df in df_dict.items()}
    val_split = {symbol: df[train_split_end_date:val_split_end_date] for symbol, df in df_dict.items()}
    test_split = {symbol: df[val_split_end_date:] for symbol, df in df_dict.items()}

    # Create the environment
    print("Creating environment...")
    env = scenv.MultiStockTradingEnv(
        dfs=list(train_split.values())[:2],
        name="StockTradingEnv@{}".format(config_path),
        portfolio_initial_value=params.environment.initial_amount,
        trading_fees=params.environment.trading_fee,
        verbose=0
    )

    done, truncated = False, False
    observation = env.reset()
    pbar = tqdm(total=env.get_dfs_length())
    while not done and not truncated:
        # Pick a position by its index in your position list (=[-1, 0, 1])....usually something like : position_index = your_policy(observation)
        # random policy
        position_index = env.action_space.sample() # At every timestep, pick a random position index from your position list (=[-1, 0, 1])
        pbar.update(1)
        observation, reward, done, truncated, info = env.step(position_index)
    pbar.close()
    env.log()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Evaluate the performance of a trading strategy')
    parser.add_argument('config', type=str,
                        help='Path to the configuration file')
    args = parser.parse_args()
    main(args.config)
