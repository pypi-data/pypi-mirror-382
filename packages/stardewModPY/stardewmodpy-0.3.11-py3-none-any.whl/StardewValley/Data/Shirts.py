from .model import modelsData
from typing import Optional, Any


class ShirtsData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Texture: str,
        SpriteIndex: int,
        Name: Optional[str] = None,
        DisplayName: Optional[str] = None,
        Description: Optional[str] = None,
        Price: Optional[int]=None,
        DefaultColor: Optional[str] = None,
        CanBeDyed: Optional[bool] = None,
        IsPrismatic: Optional[bool] = None,
        HasSleeves: Optional[bool] = None,
        CanChooseDuringCharacterCustomization: Optional[bool] = None,
        CustomFields: Optional[dict[str, Any]] = None
    ):
        super().__init__(key)
        self.Texture = Texture
        self.Name = Name
        self.DisplayName = DisplayName
        self.Description = Description
        self.Price = Price
        self.SpriteIndex = SpriteIndex
        self.DefaultColor = DefaultColor
        self.CanBeDyed = CanBeDyed
        self.IsPrismatic = IsPrismatic
        self.HasSleeves = HasSleeves
        self.CanChooseDuringCharacterCustomization = CanChooseDuringCharacterCustomization
        self.CustomFields = CustomFields
