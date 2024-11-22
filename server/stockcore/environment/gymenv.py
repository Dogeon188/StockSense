import gymnasium as _gym
from gym_trading_env.environments import TradingEnv as _TradingEnv
from gym_trading_env.environments import MultiDatasetTradingEnv as _MultiDatasetTradingEnv
from typing import Any


# TODO: make all arguments visible here

def make_trading_env(
    max_episode_steps,
    disable_env_checker,
    **kwargs: Any,
) -> _TradingEnv:
    """Make a `TradingEnv` environment. Please refer to :class:`gym_trading_env.environments.TradingEnv` for more information.

    ## Warning
    Please don't try to import :class:`TradingEnv` directly from :pkg:`gym_trading_env.environments`, as this will pollute your namespace.

    Parameters
    ----------
    max_episode_steps : int | None, optional
        See :meth:`gymnasium.make` for more information, by default None

    disable_env_checker : bool | None, optional
        See :meth:`gymnasium.make` for more information, by default None

    kwargs : Any
        Additional keyword arguments, see :meth:`gym_trading_env.environments.TradingEnv.__init__` for more information.

    Returns
    -------
    TradingEnv
        A TradingEnv environment
    """
    return _gym.make(
        max_episode_steps=max_episode_steps,
        disable_env_checker=disable_env_checker,
        id="TradingEnv",
        **kwargs,
    )


def make_multi_dataset_trading_env(
    max_episode_steps,
    disable_env_checker,
    **kwargs: Any,
) -> _MultiDatasetTradingEnv:
    """Make a `MultiDatasetTradingEnv` environment. Please refer to :class:`gym_trading_env.environments.MultiDatasetTradingEnv` for more information.

    ## Warning
    Please don't try to import :class:`MultiDatasetTradingEnv` directly from :pkg:`gym_trading_env.environments`, as this will pollute your namespace.

    Parameters
    ----------
    max_episode_steps : int | None, optional
        See :meth:`gymnasium.make` for more information, by default None

    disable_env_checker : bool | None, optional
        See :meth:`gymnasium.make` for more information, by default None

    kwargs : Any
        Additional keyword arguments, see :meth:`gym_trading_env.environments.MultiDatasetTradingEnv.__init__` for more information.
    """
    return _gym.make(
        max_episode_steps=max_episode_steps,
        disable_env_checker=disable_env_checker,
        id="MultiDatasetTradingEnv",
        **kwargs,
    )
