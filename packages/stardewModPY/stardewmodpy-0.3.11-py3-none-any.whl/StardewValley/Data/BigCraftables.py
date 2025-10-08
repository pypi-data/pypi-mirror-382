from typing import Optional, List
from .model import modelsData
from .GameData import Fragility

class BigCraftablesData(modelsData):
    def __init__(self,
        key: str,
        Name: str,
        DisplayName: str,
        Description: str,
        *,
        Price: Optional[int] = None,
        Fragility: Optional[Fragility]= None,
        CanBePlacedOutdoors: Optional[bool] = None,
        CanBePlacedIndoors: Optional[bool] = None,
        IsLamp: Optional[bool] = None, 
        Texture: Optional[str] = None,
        SpriteIndex: Optional[int] = None, 
        ContextTags: Optional[List[str]] = None,
        CustomFields: Optional[dict[str,str]] = None
    ):
        super().__init__(key)
        self.Name = Name
        self.DisplayName = DisplayName
        self.Description = Description
        self.Price = Price
        self.Fragility = Fragility
        self.CanBePlacedOutdoors = CanBePlacedOutdoors
        self.CanBePlacedIndoors = CanBePlacedIndoors
        self.IsLamp = IsLamp
        self.Texture = Texture
        self.SpriteIndex = SpriteIndex
        self.ContextTags = ContextTags
        self.CustomFields = CustomFields
