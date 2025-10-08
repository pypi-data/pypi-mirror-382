from .model import modelsData
from typing import Optional, Any

class MonsterSlayerQuests(modelsData):
    def __init__(
        self,
        *,
        key: str,
        DisplayName: str,
        Targets: list[str],
        Count: int,
        RewardItemId: Optional[str] = None,
        RewardItemPrice: Optional[int] = None,
        RewardDialogue: Optional[str] = None,
        RewardDialogueFlag: Optional[str] = None,
        RewardFlag: Optional[str] = None,
        RewardFlagAll: Optional[str] = None,
        RewardMail: Optional[str] = None,
        RewardMailAll: Optional[str] = None,
        CustomFields: Optional[dict[str, Any]] = None
    ):
        super().__init__(key)
        self.DisplayName = DisplayName
        self.Targets = Targets
        self.Count = Count
        self.RewardItemId = RewardItemId
        self.RewardItemPrice = RewardItemPrice
        self.RewardDialogue = RewardDialogue
        self.RewardDialogueFlag = RewardDialogueFlag
        self.RewardFlag = RewardFlag
        self.RewardFlagAll = RewardFlagAll
        self.RewardMail = RewardMail
        self.RewardMailAll = RewardMailAll
        self.CustomFields = CustomFields