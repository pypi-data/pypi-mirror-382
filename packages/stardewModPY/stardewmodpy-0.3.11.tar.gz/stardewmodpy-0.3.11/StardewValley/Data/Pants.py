from .model import modelsData
from typing import Optional, Any


class PantsData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Name: Optional[str] = None,
        DisplayName: Optional[str] = None,
        Description: Optional[str] = None,
        Price: Optional[int] = None,
        Texture: Optional[str] = None,
        SpriteIndex: Optional[int] = None,
        DefaultColor: Optional[str] = None,
        CanBeDyed: Optional[bool] = None,
        IsPrismatic: Optional[bool] = None,
        CanChooseDuringCharacterCustomization: Optional[bool] = None,
        CustomFields: Optional[dict[str, Any]] = None
    ):
        super().__init__(key)
        self.Name = Name
        self.DisplayName = DisplayName
        self.Description = Description
        self.Price = Price
        self.Texture = Texture
        self.SpriteIndex = SpriteIndex
        self.DefaultColor = DefaultColor
        self.CanBeDyed = CanBeDyed
        self.IsPrismatic = IsPrismatic
        self.CanChooseDuringCharacterCustomization = CanChooseDuringCharacterCustomization
        self.CustomFields = CustomFields
