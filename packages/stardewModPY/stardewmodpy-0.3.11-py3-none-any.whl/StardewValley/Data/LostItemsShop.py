from .model import modelsData
from typing import Optional


class LostItemsShopData(modelsData):
    def __init__(
        self,
        Id: str,
        ItemId: str,
        RequireMailReceived: Optional[str] = None,
        RequireEventSeen: Optional[str] = None
    ):
        super().__init__(None)
        self.Id = Id
        self.ItemId = ItemId
        self.RequireMailReceived = RequireMailReceived
        self.RequireEventSeen = RequireEventSeen
