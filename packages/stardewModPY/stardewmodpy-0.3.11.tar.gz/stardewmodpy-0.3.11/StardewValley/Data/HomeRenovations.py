from .model import modelsData
from typing import Optional, Any
from .XNA import Rectangle

class Requirements(modelsData):
    def __init__(
        self,
        Type:str,
        Key:str,
        Value:str
    ):
        self.Key=Key
        self.Type = Type
        self.Value = Value


class RectGroups(modelsData):
    def __init__(
        self,
        Rects: list[Rectangle]
    ):
        self.Rects = Rects

class HomeRenovationsData(modelsData):
    def __init__(
        self, 
        key: str,
        *,
        TextStrings: str,
        AnimationType: str = None,
        CheckForObstructions: bool,
        Price:int,
        RoomId:str,
        Requirements: list[Requirements],
        RenovateActions: list[Requirements],
        RectGroups: list[RectGroups],
        SpecialRect: Optional[str] = None,
        CustomFields: Optional[Any] = None
    ):
        super().__init__(key)
        self.TextStrings = TextStrings
        self.AnimationType = AnimationType
        self.CheckForObstructions = CheckForObstructions
        self.Price = Price
        self.RoomId = RoomId
        self.Requirements = Requirements
        self.RenovateActions = RenovateActions
        self.RectGroups = RectGroups
        self.SpecialRect = SpecialRect
        self.CustomFields = CustomFields


    
