from dataclasses import dataclass
from datetime import datetime
import json
import re


def parse_date(date: float | str | datetime) -> datetime:
    if type(date) is float:
        return datetime.fromtimestamp(date)
    elif type(date) is str:
        if re.match(r"\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}", date):
            return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        elif re.match(r"\d{4}-\d{1,2}-\d{1,2}", date):
            return datetime.strptime(date, "%Y-%m-%d")
        else:
            raise ValueError(
                "Invalid date format. Please use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'.")
    return date


@dataclass
class DataParameters:
    endpoint: str
    symbols: list[str]
    since: datetime
    until: datetime
    timeframe: str = "1d"
    train_ratio: float = 0.7
    val_ratio: float = 0.1
    test_ratio: float = 0.2

    def __post_init__(self):
        if not 0.0 <= self.train_ratio + self.val_ratio + self.test_ratio <= 1.0:
            raise ValueError(
                "The sum of train_ratio, val_ratio, and test_ratio must be between 0 and 1.")
        self.since = parse_date(self.since)
        self.until = parse_date(self.until)


@dataclass
class EnvironmentParameters:
    initial_amount: float = 1000
    trading_fee: float = 0.0001
    verbose: int = 0


@dataclass
class BenchParameters:
    data: DataParameters
    environment: EnvironmentParameters

    @staticmethod
    def from_object(
        data: dict,
        environment: dict
    ):
        return BenchParameters(
            data=DataParameters(**data),
            environment=EnvironmentParameters(**environment)
        )

    @staticmethod
    def from_json(json_file: str):
        with open(json_file, "r") as file:
            return BenchParameters.from_object(**json.load(file))


@dataclass
class ModelParameters:
    model: str
    training: bool = False
    episodes: int = 100
    batch_size: int = 64
    learning_rate: float = 0.0001
    memory: int = 100
    grad_clip: int = 100
    gamma: float = 0.99
    epsilon_start: float = 0.9
    epsilon_end: float = 0.05
    epsilon_decay: int = 1000

    params: dict = None

    @staticmethod
    def from_object(
        model: str,
        training: bool = False,
        episodes: int = 100,
        learning_rate: float = 0.0001,
        grad_clip: int = 100,
        gamma: float = 0.99,
        **params
    ):
        return ModelParameters(
            model=model,
            training=training,
            episodes=episodes,
            learning_rate=learning_rate,
            grad_clip=grad_clip,
            gamma=gamma,
            params=params
        )

    @staticmethod
    def from_json(json_file: str):
        with open(json_file, "r") as file:
            return ModelParameters.from_object(**json.load(file))
