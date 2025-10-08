from .model import modelsData
from typing import Optional
from .spawnTimingSettings import SpawnTimingSettings
from .extraConditions import ExtraConditions
from .GameData import StrictTileChecking
from .XNA import Coordinates

class Areas(modelsData):
    def __init__(
        self,
        *,
        UniqueAreaID:str,
        MapName:str,
        MinimumSpawnsPerDay:str,
        MaximumSpawnsPerDay:str,
        SpawnTiming: SpawnTimingSettings,
        ExtraConditions: ExtraConditions,
        IncludeTerrainTypes:Optional[list[str]],
        IncludeCoordinates:Optional[list[Coordinates]],
        StrictTileChecking:Optional[StrictTileChecking],
        ExcludeTerrainTypes:Optional[list[str]]=None,
        ExcludeCoordinates:Optional[list[Coordinates]]=None,
        DaysUntilSpawnsExpire:Optional[int|None]=None
    ):
        self.UniqueAreaID=UniqueAreaID
        self.MapName=MapName
        self.MinimumSpawnsPerDay=MinimumSpawnsPerDay
        self.MaximumSpawnsPerDay=MaximumSpawnsPerDay
        self.SpawnTiming=SpawnTiming.getJson()
        self.ExtraConditions=ExtraConditions.getJson()
        self.IncludeTerrainTypes=IncludeTerrainTypes
        self.IncludeCoordinates=[include.getJson() for include in IncludeCoordinates]
        self.StrictTileChecking=StrictTileChecking.getJson()

        self.ExcludeTerrainTypes=ExcludeTerrainTypes
        self.ExcludeCoordinates=[exclude.getJson() for exclude in ExcludeCoordinates]
        self.DaysUntilSpawnsExpire=DaysUntilSpawnsExpire
    
    