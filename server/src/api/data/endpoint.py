from abc import ABC, abstractmethod
from datetime import datetime
from util.singleton import SingletonABCMeta

class Endpoint(metaclass=SingletonABCMeta):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get(self, begin: datetime, end: datetime):
        raise NotImplementedError