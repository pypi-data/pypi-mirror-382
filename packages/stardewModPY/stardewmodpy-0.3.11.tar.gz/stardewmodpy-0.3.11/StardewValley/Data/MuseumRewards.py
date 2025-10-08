from .model import modelsData
from typing import Any, Optional
from .TriggerActions import Actions

class TargetContextTags(modelsData):
    def __init__(
        self,
        *,
        Tag:str,
        Count:int
    ):
        self.Tag = Tag
        self.Count = Count

class MuseumRewardsData(modelsData):
    def __init__(
        self,
        key: str,
        TargetContextTags: list[TargetContextTags],
        RewardActions: list[Actions],
        FlagOnCompletion: Optional[bool] = None,
        RewardItemId: Optional[str] = None,
        RewardItemCount: Optional[int] = None,
        RewardItemIsSpecial: Optional[bool] = None,
        RewardItemIsRecipe: Optional[bool] = None,
        CustomFields: Optional[dict[str, Any]] = None
    ):
        super().__init__(key)
        self.TargetContextTags = TargetContextTags
        self.RewardActions = RewardActions
        self.RewardItemId = RewardItemId
        self.RewardItemCount = RewardItemCount
        self.RewardItemIsSpecial = RewardItemIsSpecial
        self.RewardItemIsRecipe = RewardItemIsRecipe
        self.FlagOnCompletion = FlagOnCompletion
        self.CustomFields = CustomFields
