from .model import modelsData
from typing import Optional, Any


class IncomingPhoneCallsData(modelsData):
    def __init__(
        self, 
        key: str,
        Dialogue: str,
        FromNpc: Optional[str] = None,
        FromPortrait: Optional[str] = None,
        FromDisplayName: Optional[str] = None,
        MaxCalls: Optional[int] = None,
        TriggerCondition: Optional[str] = None,
        RingCondition: Optional[str] = None,
        IgnoreBaseChance: Optional[bool] = None,
        SimpleDialogueSplitBy: Optional[str] = None,
        CustomFields: Optional[dict[str, str]] = None
    ):
        super().__init__(key)
        self.Dialogue = Dialogue
        self.FromNpc = FromNpc
        self.FromPortrait = FromPortrait
        self.FromDisplayName = FromDisplayName
        self.MaxCalls = MaxCalls
        self.TriggerCondition = TriggerCondition
        self.RingCondition = RingCondition
        self.IgnoreBaseChance = IgnoreBaseChance
        self.SimpleDialogueSplitBy = SimpleDialogueSplitBy
        self.CustomFields = CustomFields


    
