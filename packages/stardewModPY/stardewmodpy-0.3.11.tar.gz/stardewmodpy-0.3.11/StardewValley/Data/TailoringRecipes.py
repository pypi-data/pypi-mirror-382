from .model import modelsData
from typing import Optional


class TailoringRecipesData(modelsData):
    def __init__(
        self,
        Id: str,
        FirstItemTags: list[str],
        SecondItemTags: list[str],
        SpendRightItem: bool,
        CraftedItemId: str,
        CraftedItemIds: Optional[list[str]] = None,
        CraftedItemIdFeminine: Optional[str] = None
    ):
        super().__init__(None)
        self.Id = Id
        self.FirstItemTags = FirstItemTags
        self.SecondItemTags = SecondItemTags
        self.SpendRightItem = SpendRightItem
        self.CraftedItemId = CraftedItemId
        self.CraftedItemIds = CraftedItemIds
        self.CraftedItemIdFeminine = CraftedItemIdFeminine
