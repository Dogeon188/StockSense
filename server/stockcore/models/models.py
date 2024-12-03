from stable_baselines3 import A2C
from stable_baselines3.common import base_class as _base

from ..environment import MultiStockTradingEnv
from ..parameters import ModelParameters


def build_model(params: ModelParameters, env: MultiStockTradingEnv) -> _base.BaseAlgorithm:
    if params.model == "A2C":
        return _build_model_a2c(params, env)
    else:
        raise ValueError(f"Model {params.model} not supported.")


def _build_model_a2c(params: ModelParameters, env: MultiStockTradingEnv) -> A2C:
    return A2C(
        'MlpPolicy', env,
        learning_rate=params.learning_rate,
        gamma=params.gamma,
        max_grad_norm=params.grad_clip,
        device="cpu"
    )

# TODO: Implement more models