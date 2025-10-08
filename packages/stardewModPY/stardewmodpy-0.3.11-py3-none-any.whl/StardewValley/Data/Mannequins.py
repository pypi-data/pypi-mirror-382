from .model import modelsData
from typing import Optional, Any


class MannequinsData(modelsData):
    def __init__(
        self,
        key: str,
        Id: str,
        DisplayName: str,
        Description: str,
        Texture: str,
        SheetIndex: int,
        FarmerTexture: str,
        DisplaysClothingAsMale: Optional[bool] = None,
        Cursed: Optional[bool] = None,
        CustomFields: Optional[dict[str, Any]] = None
    ):
        super().__init__(key)
        self.Id = Id
        self.DisplayName = DisplayName
        self.Description = Description
        self.Texture = Texture
        self.SheetIndex = SheetIndex
        self.FarmerTexture = FarmerTexture
        self.DisplaysClothingAsMale = DisplaysClothingAsMale
        self.Cursed = Cursed
        self.CustomFields = CustomFields
