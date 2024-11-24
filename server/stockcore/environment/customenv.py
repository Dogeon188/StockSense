from gym_trading_env.environments import TradingEnv as _TradingEnv
from gymnasium import spaces
import pandas as pd

class MultiStockTradingEnv(_TradingEnv):
    """(Inherits from TradingEnv) This class is a custom environment for multi stock trading. This is different from the `MultiDatasetTradingEnv` environment in gym-trading-env, as it allows to trade multiple stocks at the same time.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the time, open, high, low, close and volume of the stock(s) to trade.

    num_stocks : int | None, optional
        The number of stocks to trade, by default 2

    Returns
    -------
    TradingEnv
        A MultiStockTradingEnv environment    
    """

    metadata = {'render_modes': ['logs']}

    def __init__(self,
                df: pd.DataFrame, 
                *args, 

                num_stocks: int = 2,
                **kwargs):
        super().__init__(df, *args, **kwargs)

        self.action_space = spaces.Box(low=0, high=1, shape=(num_stocks, ), dtype=np.float32)