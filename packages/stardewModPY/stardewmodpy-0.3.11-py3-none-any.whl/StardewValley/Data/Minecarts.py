from .model import modelsData
from typing import Optional, Any
from .XNA import Position


class Destinations(modelsData):
    def __init__(
        self,
        Id: str,
        DisplayName: str,
        TargetLocation: str,
        TargetTile: Position,
        TargetDirection: Optional[str] = None,
        Condition: Optional[str] = None,        
        Price: Optional[int] = None,
        BuyTicketMessage: Optional[str] = None,
        CustomFields: Optional[dict[str, Any]] = None
    ):
        super().__init__(None)
        self.Id = Id
        self.DisplayName = DisplayName
        self.TargetLocation = TargetLocation
        self.TargetTile = TargetTile
        self.TargetDirection = TargetDirection
        self.Price = Price
        self.BuyTicketMessage = BuyTicketMessage
        self.Condition = Condition
        self.CustomFields = CustomFields

class MinecartsData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Destinations: list[Destinations],
        UnlockCondition: Optional[str] = None,
        LockedMessage: Optional[str] = None,
        ChooseDestinationMessage: Optional[str] = None,
        BuyTicketMessage: Optional[str] = None
    ):
        super().__init__(key)
        self.Destinations = Destinations
        self.UnlockCondition = UnlockCondition
        self.LockedMessage = LockedMessage
        self.ChooseDestinationMessage = ChooseDestinationMessage
        self.BuyTicketMessage = BuyTicketMessage

