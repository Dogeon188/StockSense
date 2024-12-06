import argparse
from typing import Union
import gymnasium as gym
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import asyncio
from tqdm import tqdm
from pathlib import Path
import json
import sys
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import VecEnv

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


class ValidationCallback(BaseCallback):
    """
    :param eval_env: The environment for validation
    :param eval_freq: Evaluate the agent every 'eval_freq' call of the callback
    :param n_eval_episodes: The number of episodes to test the agent
    :param log_path: Path to a folder where the evaluations ('evaluations.npz') will be saved. It will be updated at each evaluation
    """

    def __init__(
        self,
        val_env: Union[gym.Env, VecEnv],
        val_freq: int = 1000,
        n_eval_episodes: int = 5,
        verbose: int = 1
    ):
        super().__init__(verbose)
        self.eval_env = val_env
        self.eval_freq = val_freq
        self.n_eval_episodes = n_eval_episodes

    def _on_step(self) -> bool:
        """
        This method will be called by the model after each call to `env.step()`.

        :return: If the callback returns False, training is aborted early.
        """
        if self.verbose <= 0:
            return True
        if self.num_timesteps % self.eval_freq == 0:
            return_values, mean_reward = self.evaluate_model()
            print(f"At Step {self.num_timesteps}, "
                  f"average portfolio return over {self.n_eval_episodes} episode(s): {np.mean(return_values):5.2f}%")
        return True

    def evaluate_model(self) -> tuple[list[float], float]:
        """
        Evaluate the model performance in validation env
        """
        return_values = []
        for _ in range(self.n_eval_episodes):
            episode_reward = []
            done, truncated = False, False
            obs, info = self.eval_env.reset()
            while not done and not truncated:
                action, _states = self.model.predict(obs)
                obs, rewards, done, truncated, info = self.eval_env.step(
                    action)
            history_dqn = self.eval_env.get_history()
            episode_reward.append(rewards)
            return_values.append(100 * (history_dqn[-1] / history_dqn[0] - 1))

        mean_reward = np.mean(episode_reward)
        return return_values, mean_reward


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
    train_env = create_env(
        list(train_split.values()),
        bench_params,
        verbose=bench_params.environment.verbose
    )

    val_env = create_env(
        list(val_split.values()),
        bench_params,
        verbose=0
    )
    val_callback = ValidationCallback(
        val_env=val_env,
        val_freq=bench_params.environment.val_freq,
        n_eval_episodes=bench_params.environment.n_val_episodes,
        verbose=1
    )

    # Build the model

    print("Building model...")
    model_params = ModelParameters.from_json(model_path)

    model = build_model(model_params, train_env)

    # Train or load the model

    if model_params.force_retrain or not (root / "model.zip").exists():
        print("Training model...")
        model.learn(
            total_timesteps=train_env.get_dfs_length() * model_params.episodes,
            log_interval=1,
            callback=val_callback
        )
        model.save(root / "model")
        print(f"Model saved at {root / 'model.zip'}")
    else:
        print("Loading model...")
        model = model.load(root / "model")

    train_env.close()

    # Evaluate the model

    print("Evaluating model...")
    test_env = create_env(
        list(test_split.values()),
        bench_params,
        verbose=0
    )

    model.set_env(test_env)

    done, truncated = False, False
    observation, _ = test_env.reset()
    pbar = tqdm(total=test_env.get_dfs_length())
    while not done and not truncated:
        position_index = model.predict(observation)[0]
        pbar.update(1)
        observation, reward, done, truncated, info = test_env.step(
            position_index)
    pbar.close()

    # Log the results

    print("Logging results...")
    test_env.log()

    date = test_env.get_date()[bench_params.environment.windows-1:]
    date = pd.to_datetime(date, unit="ms")
    hist = pd.Series(test_env.get_history())
    reward_hist = pd.Series(test_env.get_history_reward())
    reward_hist_mean = reward_hist.rolling(20).mean()
    reward_hist_std = reward_hist.rolling(20).std()

    # Plot the results

    plt.figure(figsize=(14, 7))
    plt.plot(date, hist)
    plt.title("Portfolio Value")
    plt.savefig(root / "history.png")
    plt.close()

    plt.figure(figsize=(14, 7))
    plt.plot(
        date[1:], reward_hist,
        color="C0", alpha=0.1)
    plt.plot(
        date[1:], reward_hist_mean,
        color="C1")
    plt.fill_between(
        date[1:],
        reward_hist_mean - reward_hist_std,
        reward_hist_mean + reward_hist_std,
        color="C1",
        alpha=0.3
    )
    plt.title("Reward History")
    plt.legend(["Reward", "Mean Reward (20)"])
    plt.savefig(root / "reward_history.png")
    plt.close()

    test_env.close()

    # Save the results

    results = {
        "date": date.index,
        "history": hist,
        "reward_history": pd.concat([pd.Series([None]), reward_hist], ignore_index=True),
    }
    pd.DataFrame(results, index=None).to_csv(root / "results.csv", index=False)

    print(f"History saved at {root / 'results.csv'}")


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

    def handler(exception_type, exception, traceback):
        if exception_type == KeyboardInterrupt:
            print("Interrupted by user")
            sys.exit(1)
        elif exception_type == ResourceWarning:
            pass  # ignore, may be raised by stable-baselines not closing temporary files
        else:
            sys.__excepthook__(exception_type, exception, traceback)

    sys.excepthook = handler

    main(benchmark_path, model_path)
