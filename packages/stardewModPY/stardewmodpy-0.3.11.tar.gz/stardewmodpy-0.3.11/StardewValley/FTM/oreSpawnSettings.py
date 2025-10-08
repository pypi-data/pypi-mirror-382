from .areas import Areas
from .spawnTimingSettings import SpawnTimingSettings
from .extraConditions import ExtraConditions
from .GameData import StrictTileChecking
from .XNA import Coordinates

from typing import Optional

from .globalSpawnSettings import GlobalSpawnSettings

class OreAreas(Areas):
    def __init__(
        self,
        *,
        UniqueAreaID:str,
        MapName:str,
        MinimumSpawnsPerDay:str,
        MaximumSpawnsPerDay:str,
        SpawnTiming: SpawnTimingSettings,
        ExtraConditions: ExtraConditions,
        MiningLevelRequired:dict[str, int],
        StartingSpawnChance:dict[str, int],
        LevelTenSpawnChance:dict[str, int],
        PercentExtraSpawnsPerMiningLevel:int,
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
        self.MiningLevelRequired=MiningLevelRequired
        self.StartingSpawnChance=StartingSpawnChance
        self.LevelTenSpawnChance=LevelTenSpawnChance
        self.PercentExtraSpawnsPerMiningLevel=self.getMinimum(PercentExtraSpawnsPerMiningLevel, 0, 100)
        self.IncludeTerrainTypes=IncludeTerrainTypes
        self.IncludeCoordinates=[include.getJson() for include in IncludeCoordinates]
        self.StrictTileChecking=StrictTileChecking.getJson()

        self.ExcludeTerrainTypes=ExcludeTerrainTypes
        self.ExcludeCoordinates=[exclude.getJson() for exclude in ExcludeCoordinates]
        self.DaysUntilSpawnsExpire=DaysUntilSpawnsExpire

class OreSpawnSettings(GlobalSpawnSettings):
    def __init__(
        self,
        *,
        Enable:bool,
        Areas:list[OreAreas]=None,
        PercentExtraSpawnsPerMiningLevel:int=None,
        MiningLevelRequired:dict[str,int]=None,
        StartingSpawnChance:dict[str,int]=None,
        LevelTenSpawnChance:dict[str,int]=None,
        CustomTileIndex:Optional[list[int]]=None
    ):
        self.key="Ore_Spawn_Settings"
        self.Enable=Enable
        self.Areas=Areas
        self.PercentExtraSpawnsPerMiningLevel=PercentExtraSpawnsPerMiningLevel
        self.MiningLevelRequired=MiningLevelRequired
        self.StartingSpawnChance=StartingSpawnChance
        self.LevelTenSpawnChance=LevelTenSpawnChance
        self.CustomTileIndex=CustomTileIndex