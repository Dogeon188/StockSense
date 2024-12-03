import gymnasium as _gym
from gymnasium import spaces
import pandas as _pd
import numpy as _np
import stockcore.data as _scdata


class History:
    def __init__(self):
        self.total_assets_list = []

    def add(self, total_assets):
        self.total_assets_list.append(total_assets)

    def get_total_assets(self, idx):
        return self.total_assets_list[idx]
    def get_history(self):
        return self.total_assets_list


class Portfolio:
    def __init__(self, percentages_of_stocks_and_cash, total_money, prices_of_stocks):
        self.amount_of_stocks = []
        for idx, percentage in enumerate(percentages_of_stocks_and_cash[:-1]):
            self.amount_of_stocks.append(
                percentage * total_money / prices_of_stocks[idx])
        self.cash = percentages_of_stocks_and_cash[-1] * total_money

    def total_assets(self, prices_of_stocks):
        return sum([amount * price for amount, price in zip(self.amount_of_stocks, prices_of_stocks)]) + self.cash

    def trade_to_new_percentages(self, percentages_of_stocks_and_cash, prices_of_stocks, trading_fees):
        total_money = self.total_assets(prices_of_stocks)
        for idx, (percentage, price) in enumerate(zip(percentages_of_stocks_and_cash[:-1], prices_of_stocks)):
            stock_trade = (percentage * total_money / price) - \
                self.amount_of_stocks[idx]
            if stock_trade > 0:
                stock_trade = stock_trade / \
                    (1 - trading_fees + trading_fees * percentage)
                cash_trade = - stock_trade * price
                self.amount_of_stocks[idx] = self.amount_of_stocks[idx] + \
                    stock_trade * (1 - trading_fees)
                self.cash = self.cash + cash_trade
            else:
                stock_trade = stock_trade / (1 - trading_fees * percentage)
                cash_trade = - stock_trade * price
                self.amount_of_stocks[idx] = self.amount_of_stocks[idx] + stock_trade
                self.cash = self.cash + cash_trade * (1 - trading_fees)


class MultiStockTradingEnv(_gym.Env):
    """This class is a custom environment for multi stock trading. This is different from the `MultiDatasetTradingEnv` environment in gym-trading-env, as it allows to trade multiple stocks at the same time.   
    """

    metadata = {'render_modes': ['logs']}

    def __init__(self,
                 dfs: list[_pd.DataFrame],
                 windows=None,
                 trading_fees=0,
                 portfolio_initial_value=1000,
                 max_episode_duration='max',
                 verbose=1,
                 name="Stock",
                 render_mode="logs"
                 ):
        self.max_episode_duration = max_episode_duration
        self.verbose = verbose
        self.name = name
        self.render_mode = render_mode

        self.windows = windows
        self.trading_fees = trading_fees
        self.portfolio_initial_value = float(portfolio_initial_value)

        self._set_dfs(dfs)

        self.number_of_stocks = len(dfs)
        self.action_space = spaces.Discrete(self.number_of_stocks + 1)
        self.observation_space = spaces.Box(
            -_np.inf,
            _np.inf,
            shape=[self._nb_features]
        )
        if self.windows is not None:
            self.observation_space = spaces.Box(
                -_np.inf,
                _np.inf,
                shape=[self.windows, self._nb_features]
            )

        self.log_metrics = []

    def _set_dfs(self, dfs: list[_pd.DataFrame]):
        dfs = [df.copy() for df in dfs]
        self.dfs = dfs
        self._number_of_stocks = len(dfs)
        merged_df = self._dfs_preprocess(dfs)
        self.length_of_merged_df = len(merged_df)

        self._features_columns = [
            col for col in merged_df.columns if "feature" in col]
        self._nb_features = len(self._features_columns)

        self._obs_array = _np.array(
            merged_df[self._features_columns], dtype=_np.float32)
        self._price_array = [df["close"] for df in self.dfs]

    def _dfs_preprocess(self, dfs: list[_pd.DataFrame]):
        dfs = [df.copy() for df in dfs]
        dfs = [_scdata.data_preprocess(df, dropna=False) for df in dfs]
        for idx, df in enumerate(dfs):
            df.columns += f"_{idx}"
        merged_df = _pd.concat(dfs, axis=1)
        merged_df.dropna(inplace=True)
        return merged_df

    def get_dfs_length(self):
        return self.length_of_merged_df
    
    def _get_price(self, delta = 0):
        return [price.iloc[self._idx + delta] for price in self._price_array]
    
    def _get_obs(self):

        if self.windows is None:
            _step_index = self._idx
        else:
            _step_index = _np.arange(
                self._idx + 1 - self.windows, self._idx + 1)
        return self._obs_array[_step_index]

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self._step = 0
        self._percentages_of_stocks_and_cash = [
            0] * self.number_of_stocks + [1]  # 1 for cash

        self._idx = 0
        if self.windows is not None:
            self._idx = self.windows - 1
        if self.max_episode_duration != 'max':
            self._idx = _np.random.randint(
                low=self._idx,
                high=len(self.df) - self.max_episode_duration - self._idx
            )

        self._portfolio = Portfolio(
            percentages_of_stocks_and_cash=self._percentages_of_stocks_and_cash,
            total_money=self.portfolio_initial_value,
            prices_of_stocks=self._get_price()
        )

        self.historical_info = History()
        self.historical_info.add(self.portfolio_initial_value)

        return self._get_obs(), {}

    def _trade(self, percentages_of_stocks_and_cash, prices_of_stocks=None):
        self._portfolio.trade_to_new_percentages(
            percentages_of_stocks_and_cash=percentages_of_stocks_and_cash,
            prices_of_stocks=self._get_price() if prices_of_stocks is None else prices_of_stocks,
            trading_fees=self.trading_fees
        )
        self._percentages_of_stocks_and_cash = percentages_of_stocks_and_cash
        return

    def _take_action(self, actions: int):
        """For now, I just assume that the actions are the percentages of the stocks and cash.
        """
        actions_one_hot: list[int] = [0] * self.action_space.n
        actions_one_hot[actions] = 1
        percentages_of_stocks_and_cash = list(actions_one_hot)
        if percentages_of_stocks_and_cash != self._percentages_of_stocks_and_cash:
            self._trade(percentages_of_stocks_and_cash)

    def reward_function(self):
        return _np.log(self.historical_info.get_total_assets(-1) / self.historical_info.get_total_assets(-2))

    def step(self, actions=None):
        if actions is not None:
            self._take_action(actions)
        self._idx += 1
        self._step += 1

        prices_of_stocks = self._get_price()
        portfolio_value = self._portfolio.total_assets(prices_of_stocks)

        done, truncated = False, False

        if portfolio_value <= 0:
            done = True
        if self._idx >= self.length_of_merged_df - 1:
            truncated = True
        if isinstance(self.max_episode_duration, int) and self._step >= self.max_episode_duration - 1:
            truncated = True

        self.historical_info.add(portfolio_value)

        if not done:
            reward = self.reward_function()
            info = {}

        if done or truncated:
            if self.verbose > 0:
                self.log()
        return self._get_obs(), reward, done, truncated, info

    def log(self):
        # FIXME only consider last asset
        print("Portfolio Return : " + f"{100*(self.historical_info.get_total_assets(
            -1) / self.historical_info.get_total_assets(0) - 1):5.2f}%")
    
    def get_results(self):
        # TODO return necessary results
        return {
            "portfolio_value": 0,
            "portfolio_return": 0,
        }

    def render():
        pass