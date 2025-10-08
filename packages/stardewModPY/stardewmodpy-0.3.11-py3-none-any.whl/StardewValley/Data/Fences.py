from .model import modelsData
from typing import Optional
from .XNA import Position


class FencesData(modelsData):
    def __init__(
        self, 
        key: str,
        Health: int,
        Texture: str,
        PlacementSound: str,
        RemovalToolIds: list[str],
        RemovalToolTypes: list[str],
        RemovalSound: Optional[str] = None,
        RemovalDebrisType: Optional[int] = None,
        RepairHealthAdjustmentMinimum: Optional[float] = None,
        RepairHealthAdjustmentMaximum: Optional[float] = None,
        HeldObjectDrawOffset: Optional[Position] = None,
        LeftEndHeldObjectDrawX: Optional[float] = None,
        RightEndHeldObjectDrawX: Optional[float] = None
    ):
        super().__init__(key)
        self.Health = Health
        self.Texture = Texture
        self.PlacementSound = PlacementSound
        self.RemovalToolIds = RemovalToolIds
        self.RemovalToolTypes = RemovalToolTypes
        self.RemovalSound = RemovalSound
        self.RemovalDebrisType = RemovalDebrisType
        self.RepairHealthAdjustmentMinimum = RepairHealthAdjustmentMinimum
        self.RepairHealthAdjustmentMaximum = RepairHealthAdjustmentMaximum
        self.HeldObjectDrawOffset = HeldObjectDrawOffset
        self.LeftEndHeldObjectDrawX = LeftEndHeldObjectDrawX
        self.RightEndHeldObjectDrawX = RightEndHeldObjectDrawX

    def getJson(self, useGetStr = None, ignore = None):
        useGetStr.append("HeldObjectDrawOffset")
        return super().getJson(useGetStr, ignore)
    