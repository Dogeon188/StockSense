import argparse
from matplotlib import pyplot as plt
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


def plot_data(df_dict: dict[str, pd.DataFrame], train_split_end_date, val_split_end_date, save_path: Path):
    # plot the data
    df_dict = {k: v for k, v in df_dict.items(
    ) if k != "BTC/USDT" and k != "ETH/USDT"}
    plt.figure(figsize=(14, 7))
    for symbol, df in df_dict.items():
        plt.plot(df.index, df["close"], label=symbol)
    dfs = list(df_dict.values())
    plt.xlim(dfs[0].index[0], dfs[0].index[-1])
    plt.ylim(-10, max(df["close"].max() for df in dfs) + 10)
    plt.fill_betweenx(
        plt.ylim(),
        dfs[0].index[0], train_split_end_date,
        color="green", alpha=0.1, label="train")
    plt.fill_betweenx(
        plt.ylim(),
        train_split_end_date, val_split_end_date,
        color="yellow", alpha=0.1, label="val")
    plt.fill_betweenx(
        plt.ylim(),
        val_split_end_date, dfs[0].index[-1],
        color="red", alpha=0.1, label="test")
    plt.title("Asset Prices")
    plt.legend()
    plt.savefig(save_path)
    plt.close()


def create_env(
    dfs: list[pd.DataFrame],
    params: BenchParameters,
    verbose: int = 0
) -> scenv.MultiStockTradingEnv:
    env = scenv.MultiStockTradingEnv(
        dfs=dfs,
        portfolio_initial_value=params.environment.initial_amount,
        trading_fees=params.environment.trading_fee,
        windows=params.environment.windows,
        verbose=verbose
    )
    # check_env(env)
    return env


def main(benchmark_path: Path, model_path: Path):
    # Create the output folder

    root = build_folders(Path(benchmark_path).stem +
                         "-" + Path(model_path).stem)

    # Load the configuration file

    bench_params = BenchParameters.from_json(benchmark_path)

    # Load the data

    print("Loading data...")
    df_dict = load_data(bench_params.data)
    dfs = list(df_dict.values())

    # make sure all the dataframes have the same length
    assert all(df.index.equals(dfs[0].index)
               for df in dfs), "Dataframes have different datetime indices"

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

    # Plot the data

    print("Plotting data...")
    plot_data(df_dict, train_split_end_date,
              val_split_end_date, root / "prices.png")

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

    if model_params.force_retrain or not (root / "model.zip").exists():
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

    # Plot the results

    date = env.get_date()[bench_params.environment.windows-1:]
    date = pd.to_datetime(date, unit="ms")
    hist = env.get_history()

    plt.figure(figsize=(14, 7))
    plt.plot(date, hist)
    plt.title("Portfolio Value")
    plt.savefig(root / "history.png")
    plt.close()

    plt.figure(figsize=(14, 7))
    reward_hist = env.get_history_reward()
    reward_hist_mean = pd.Series(reward_hist).rolling(20).mean()
    plt.plot(date[1:], reward_hist)
    plt.plot(date[1:], reward_hist_mean)
    plt.title("Reward History")
    plt.legend(["Reward", "Mean Reward (20)"])
    plt.savefig(root / "reward_history.png")
    plt.close()

    env.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Evaluate the performance of a trading strategy')
    parser.add_argument('benchmark', type=str,
                        help='Path to the benchmark configuration file')
    parser.add_argument('model', type=str,
                        help='Path to the model configuration file')
    args = parser.parse_args()

    benchmark_path = (Path("parameters/benchmarks", args.benchmark + ".json")
                      if not args.benchmark.endswith(".json")
                      else Path(args.benchmark))
    model_path = (Path("parameters/models", args.model + ".json")
                  if not args.model.endswith(".json")
                  else Path(args.model))

    try:
        if not benchmark_path.exists():
            available = list(Path('parameters/benchmarks').rglob('*.json'))
            available = [str(path) for path in available]
            print(
                f"Benchmark configuration file {benchmark_path} not found\nAvailable files: {available}")
            exit(1)
        if not model_path.exists():
            available = list(Path('parameters/models').rglob('*.json'))
            available = [path.stem for path in available]
            print(
                f"Model configuration file {model_path} not found\nAvailable files: {available}")
            exit(1)

        print(f"Using benchmark configuration file: {benchmark_path}")
        print(f"Using model configuration file: {model_path}")

        main(benchmark_path, model_path)
    except ResourceWarning as e:
        pass
