from ..model import modelsData
from typing import Optional


class QuantityModifiers(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        Condition: Optional[str] = None,
        Amount: Optional[float] = None,
        RandomAmount: Optional[list[float]] = None
    ):
        self.Id = Id
        self.Condition = Condition
        self.Amount = Amount
        self.RandomAmount = RandomAmount

