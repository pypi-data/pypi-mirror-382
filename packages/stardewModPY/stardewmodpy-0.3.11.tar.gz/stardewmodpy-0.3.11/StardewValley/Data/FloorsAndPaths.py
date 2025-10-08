from .model import modelsData
from typing import Optional


class FloorsAndPathsData(modelsData):
    def __init__(
        self,
        key:str,
        ID: str,
        ItemId: str,
        Texture: str,
        Corner: dict[str, int],
        PlacementSound: str,
        FootstepSound: str,
        WinterTexture: Optional[str] = "TerrainFeatures\\Flooring_winter",
        RemovalSound: Optional[str] = "axchop",
        RemovalDebrisType: Optional[int] = 14,
        ShadowType: Optional[str] = "None",
        ConnectType: Optional[str] = "Default",
        CornerSize: Optional[int] = 4,
        FarmSpeedBuff: Optional[float] = 0.1
    ):
        super().__init__(key)
        self.ID = ID
        self.ItemId = ItemId
        self.Texture = Texture
        self.Corner = Corner
        self.PlacementSound = PlacementSound
        self.FootstepSound = FootstepSound
        self.WinterTexture = WinterTexture
        self.RemovalSound = RemovalSound
        self.RemovalDebrisType = RemovalDebrisType
        self.ShadowType = ShadowType
        self.ConnectType = ConnectType
        self.CornerSize = CornerSize
        self.FarmSpeedBuff = FarmSpeedBuff
