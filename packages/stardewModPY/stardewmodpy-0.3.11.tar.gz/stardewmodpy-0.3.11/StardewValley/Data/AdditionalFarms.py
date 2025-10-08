from typing import Optional, Dict, Any
from .model import modelsData

class AdditionalFarmsData(modelsData):
    def __init__(
        self,
        key: int,
        Id: str,
        TooltipStringPath: str,
        MapName: str,
        IconTexture: str,
        WorldMapTexture: str,
        SpawnMonstersByDefault: bool = None,
        ModData: Optional[Dict[str, str]] = None,
        CustomFields:  Optional[dict[str,Any]] = None
    ):        
        super().__init__(key)
        self.Id = Id
        self.TooltipStringPath = TooltipStringPath
        self.MapName = MapName
        self.IconTexture = IconTexture
        self.WorldMapTexture = WorldMapTexture
        self.SpawnMonstersByDefault = SpawnMonstersByDefault
        self.ModData = ModData
        self.CustomFields = CustomFields

    