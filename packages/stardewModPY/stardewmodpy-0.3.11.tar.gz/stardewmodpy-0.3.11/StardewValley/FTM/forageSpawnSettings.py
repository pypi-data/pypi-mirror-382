from .areas import Areas
from typing import Optional, Any
from .spawnTimingSettings import SpawnTimingSettings
from .extraConditions import ExtraConditions
from .GameData import StrictTileChecking
from .XNA import Coordinates
from .globalSpawnSettings import GlobalSpawnSettings

class ForageAreas(Areas):
    def __init__(
        self,
        *,
        SpringItemIndex:Any,
        SummerItemIndex:Any,
        FallItemIndex:Any,
        WinterItemIndex:Any,
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
        self.SpringItemIndex=SpringItemIndex
        self.SummerItemIndex=SummerItemIndex
        self.FallItemIndex=FallItemIndex
        self.WinterItemIndex=WinterItemIndex
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

class ForageSpawnSettings(GlobalSpawnSettings):
    def __init__(
        self,
        *,
        Enable:bool,
        Areas:list[ForageAreas]=None,
        PercentExtraSpawnsPerForagingLevel:int=None,
        SpringItemIndex:list[Any]=None,
        SummerItemIndex:list[Any]=None,
        FallItemIndex:list[Any]=None,
        WinterItemIndex:list[Any]=None,
        CustomTileIndex:Optional[list[int]]=None
    ):
        self.key="Forage_Spawn_Settings"
        self.Enable=Enable
        self.Areas=Areas
        self.PercentExtraSpawnsPerForagingLevel=PercentExtraSpawnsPerForagingLevel
        self.SpringItemIndex=SpringItemIndex
        self.SummerItemIndex=SummerItemIndex
        self.FallItemIndex=FallItemIndex
        self.WinterItemIndex=WinterItemIndex
        self.CustomTileIndex=CustomTileIndex