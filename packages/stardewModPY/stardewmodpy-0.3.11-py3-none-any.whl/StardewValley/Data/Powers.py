from .model import modelsData
from typing import Optional, Any
from .XNA import Position


class PowersData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        DisplayName: str,
        TexturePath: str,
        TexturePosition: Position,
        UnlockedCondition: str,
        Description: Optional[str] = None,
        CustomFields: Optional[dict[str, Any]] = None
    ):
        super().__init__(key)
        self.DisplayName = DisplayName
        self.TexturePath = TexturePath
        self.TexturePosition = TexturePosition
        self.UnlockedCondition = UnlockedCondition
        self.Description = Description
        self.CustomFields = CustomFields


    
