from .model import modelsData
from typing import Any, Optional
from .GameData import ToolUpgradeLevel

class UpgradeFrom(modelsData):
    def __init__(
        self,
        Price: int,
        RequiredToolId:str,
        TradeItemId:str,
        TradeItemAmount:int,
        Condition:str
    ):
        self.Price = Price
        self.RequiredToolId = RequiredToolId
        self.TradeItemId = TradeItemId
        self.TradeItemAmount = TradeItemAmount
        self.Condition = Condition

class ToolsData(modelsData):
    def __init__(
        self,
        key: str,
        ClassName: str,
        Name: str,
        DisplayName: str,
        Description: str,
        Texture: str,
        SpriteIndex: int,
        CanBeLostOnDeath: bool,
        AttachmentSlots: Optional[int]=None,
        SalePrice: Optional[int]=None,
        MenuSpriteIndex: Optional[int]=None,
        UpgradeLevel: Optional[ToolUpgradeLevel|int]=None,
        ConventionalUpgradeFrom: Optional[str] = None,
        UpgradeFrom: Optional[list[UpgradeFrom]] = None,
        ModData: Optional[Any] = None,
        SetProperties: Optional[dict[str, Any]] = None,
        CustomFields: Optional[dict[str, Any]] = None
    ):
        super().__init__(key)

        self.ClassName = ClassName
        self.Name = Name
        self.AttachmentSlots = AttachmentSlots
        self.SalePrice = SalePrice
        self.DisplayName = DisplayName
        self.Description = Description
        self.Texture = Texture
        self.SpriteIndex = SpriteIndex
        self.MenuSpriteIndex = MenuSpriteIndex
        self.UpgradeLevel = UpgradeLevel
        self.ConventionalUpgradeFrom = ConventionalUpgradeFrom
        self.UpgradeFrom = UpgradeFrom
        self.CanBeLostOnDeath = CanBeLostOnDeath
        self.SetProperties = SetProperties
        self.ModData = ModData
        self.CustomFields = CustomFields

    
