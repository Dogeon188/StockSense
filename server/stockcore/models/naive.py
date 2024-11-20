from gymnasium import Env
import torch
import torch.nn as nn
import torch.nn.functional as F

from .base import DQNBase


class NaiveDQN(DQNBase):
    def __init__(self, env: Env = None, n_observations: int = None, n_actions: int = None) -> None:
        super().__init__(env, n_observations, n_actions)
        self.layer1 = nn.Linear(self.n_observations, 128)
        self.layer2 = nn.Linear(128, 128)
        self.layer3 = nn.Linear(128, self.n_actions)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)
