from .model import modelsData
from typing import Optional


class OutfitParts(modelsData):
    def __init__(
        self,
        Id: str,
        ItemId: str,
        Color: Optional[str] = None,
        Gender: Optional[str] = None
    ):
        super().__init__(None)
        self.Id = Id
        self.ItemId = ItemId
        self.Color = Color
        self.Gender = Gender


class MakeoverOutfitsData(modelsData):
    def __init__(
        self,
        Id: str,
        OutfitParts: list[OutfitParts],
        Gender: Optional[str] = None
    ):
        super().__init__(None)
        self.Id = Id
        self.OutfitParts = OutfitParts
        self.Gender = Gender
