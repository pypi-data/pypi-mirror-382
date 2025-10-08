from .areas import Areas

from typing import Optional
from .spawnTimingSettings import SpawnTimingSettings
from .extraConditions import ExtraConditions
from .GameData import StrictTileChecking, RelatedSkill
from .XNA import Coordinates
from .globalSpawnSettings import GlobalSpawnSettings


class LargueObjectAreas(Areas):
    def __init__(
        self,
        *,
        ObjectTypes:list[str],
        FindExistingObjectLocations:bool,
        RelatedSkill:RelatedSkill,
        UniqueAreaID:str,
        MapName:str,        
        MinimumSpawnsPerDay:str,
        MaximumSpawnsPerDay:str,
        SpawnTiming: SpawnTimingSettings,
        ExtraConditions: ExtraConditions,        
        PercentExtraSpawnsPerSkillLevel:int,
        IncludeTerrainTypes:Optional[list[str]],
        IncludeCoordinates:Optional[list[Coordinates]],
        StrictTileChecking:Optional[StrictTileChecking],
        
        ExcludeTerrainTypes:Optional[list[str]]=None,
        ExcludeCoordinates:Optional[list[Coordinates]]=None,
        DaysUntilSpawnsExpire:Optional[int|None]=None
    ):
        self.ObjectTypes=ObjectTypes
        self.FindExistingObjectLocations=FindExistingObjectLocations
        self.RelatedSkill=RelatedSkill.getJson()
        self.UniqueAreaID=UniqueAreaID
        self.MapName=MapName
        self.MinimumSpawnsPerDay=MinimumSpawnsPerDay
        self.MaximumSpawnsPerDay=MaximumSpawnsPerDay
        self.SpawnTiming=SpawnTiming.getJson()
        self.ExtraConditions=ExtraConditions.getJson()
        self.PercentExtraSpawnsPerSkillLevel=self.getMinimum(PercentExtraSpawnsPerSkillLevel, 0, 100)
        self.IncludeTerrainTypes=IncludeTerrainTypes
        self.IncludeCoordinates=[include.getJson() for include in IncludeCoordinates]
        self.StrictTileChecking=StrictTileChecking.getJson()

        self.ExcludeTerrainTypes=ExcludeTerrainTypes
        self.ExcludeCoordinates=[exclude.getJson() for exclude in ExcludeCoordinates]
        self.DaysUntilSpawnsExpire=DaysUntilSpawnsExpire

class LargeObjectSpawnSettings(GlobalSpawnSettings):
    def __init__(
        self,
        *,
        Enable:bool,
        Areas:list[LargueObjectAreas]=None,
        CustomTileIndex:Optional[list[int]]=None
    ):
        self.key="LargeObject_Spawn_Settings"
        self.Enable=Enable
        self.Areas=Areas
        self.CustomTileIndex=CustomTileIndex