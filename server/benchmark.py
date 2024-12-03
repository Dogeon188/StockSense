import argparse
import pandas as pd
import asyncio
from tqdm import tqdm
from stable_baselines3.common.env_checker import check_env
from pathlib import Path
import json

from stockcore.parameters import BenchParameters, DataParameters, ModelParameters
from stocksense.api import data as scdata
import stockcore.environment as scenv
from stockcore.models import build_model


OUTPUT_DIR = "./output"


def build_folders(root: str) -> Path:
    Path(OUTPUT_DIR, root).mkdir(parents=True, exist_ok=True)
    return Path(OUTPUT_DIR, root)


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


def create_env(
    dfs: list[pd.DataFrame],
    params: BenchParameters,
    verbose: int = 0
) -> scenv.MultiStockTradingEnv:
    env = scenv.MultiStockTradingEnv(
        dfs=dfs,
        portfolio_initial_value=params.environment.initial_amount,
        trading_fees=params.environment.trading_fee,
        verbose=verbose
    )
    check_env(env)
    return env


def main(benchmark_path: str, model_path: str):
    # Create the output folder

    root = build_folders(Path(benchmark_path).stem +
                         "-" + Path(model_path).stem)

    # Load the configuration file

    bench_params = BenchParameters.from_json(benchmark_path)

    # Load the data

    print("Loading data...")
    df_dict = load_data(bench_params.data)
    dfs = list(df_dict.values())

    # Split the data

    train_split_end = int(bench_params.data.train_ratio * len(dfs[0]))
    train_split_end_date = dfs[0].index[train_split_end]
    val_split_end = int(
        (bench_params.data.train_ratio + bench_params.data.val_ratio) * len(dfs[0]))
    val_split_end_date = dfs[0].index[val_split_end]

    train_split = {symbol: df[:train_split_end_date]
                   for symbol, df in df_dict.items()}
    val_split = {symbol: df[train_split_end_date:val_split_end_date]
                 for symbol, df in df_dict.items()}
    test_split = {symbol: df[val_split_end_date:]
                  for symbol, df in df_dict.items()}

    # Create the environment

    print("Creating environment...")
    env = create_env(
        list(train_split.values()),
        bench_params,
        verbose=bench_params.environment.verbose
    )

    # Build the model

    print("Building model...")
    model_params = ModelParameters.from_json(model_path)

    model = build_model(model_params, env)

    # Train or load the model

    if model_params.training:
        print("Training model...")
        model.learn(
            total_timesteps=env.get_dfs_length() * model_params.episodes,
            log_interval=1,
        )
        model.save(root / "model")
    else:
        print("Loading model...")
        model = model.load(root / "model")

    env.close()

    # Evaluate the model

    print("Evaluating model...")
    env = create_env(
        list(test_split.values()),
        bench_params,
        verbose=0
    )

    model.set_env(env)

    done, truncated = False, False
    observation, _ = env.reset()
    pbar = tqdm(total=env.get_dfs_length())
    while not done and not truncated:
        position_index = model.predict(observation)[0]
        pbar.update(1)
        observation, reward, done, truncated, info = env.step(position_index)
    pbar.close()

    # Log the results

    print("Logging results...")
    env.log()
    results = env.get_results()
    with open(root / "results.json", "w") as f:
        json.dump(results, f, indent=4)
    # TODO: Plot the results

    env.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Evaluate the performance of a trading strategy')
    parser.add_argument('benchmark', type=str,
                        help='Path to the benchmark configuration file')
    parser.add_argument('model', type=str,
                        help='Path to the model configuration file')
    args = parser.parse_args()
    try:
        main(args.benchmark, args.model)
    except ResourceWarning as e:
        pass
    except Exception as e:
        pass
