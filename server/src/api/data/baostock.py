from datetime import datetime
from .endpoint import Endpoint

class BaostockEndpoint(Endpoint):
    def __init__(self):
        super().__init__("baostock")
    
    def get(self, begin: datetime, end: datetime):
        raise NotImplementedError