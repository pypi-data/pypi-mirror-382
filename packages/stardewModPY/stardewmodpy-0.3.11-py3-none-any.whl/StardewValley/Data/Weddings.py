from .model import modelsData
from .Events import Eventscripts
from typing import Optional, Any

class Attendees(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Id:str,
        Setup:str,
        Celebration:Optional[Eventscripts|str]=None,
        Condition:Optional[str]=None,
        IgnoreUnlockConditions:Optional[bool]=None
    ):
        super().__init__(key=key)
        self.Id=Id
        self.Setup=Setup
        self.Celebration=Celebration
        self.Condition=Condition
        self.IgnoreUnlockConditions=IgnoreUnlockConditions