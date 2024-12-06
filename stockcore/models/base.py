import torch as _torch
import torch.nn as _nn
from gymnasium import Env as _Env
from abc import ABC, abstractmethod


class DQNBase(_nn.Module, ABC):
    def __init__(self, env: _Env = None, n_observations: int = None, n_actions: int = None) -> None:
        super(DQNBase, self).__init__()
        if env is not None and (n_observations is not None or n_actions is not None):
            raise ValueError("Please provide either env or n_observations and n_actions, not both.")
        if env is not None:
            self.n_observations = env.observation_space.shape[0]
            self.n_actions = env.action_space.n
        elif n_observations is not None and n_actions is not None:
            self.n_observations = n_observations
            self.n_actions = n_actions
        else:
            raise ValueError("Please provide either env or n_observations and n_actions.")

    @abstractmethod
    def forward(self, x: _torch.Tensor) -> _torch.Tensor:
        raise NotImplementedError
    
    def act(self, x: _torch.Tensor, epsilon: float = 0.0) -> _torch.Tensor:
        """Select an action based on the epsilon-greedy policy.

        Parameters
        ----------
        x : _torch.Tensor
            The input state.
        epsilon : float, optional
            The probability of selecting a random action. If epsilon is 0 (by default), the greedy policy is used.

        Returns
        -------
        _torch.Tensor
            A tensor containing a single value, representing the selected action.
        """
        if _torch.rand(1).item() < epsilon:
            return _torch.randint(self.n_actions, (1,1))
        else:
            with _torch.no_grad():
                return self.forward(x).max(1).indices.view(1, 1)
