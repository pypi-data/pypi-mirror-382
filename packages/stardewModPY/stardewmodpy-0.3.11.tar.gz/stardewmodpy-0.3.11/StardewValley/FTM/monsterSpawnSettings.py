from .model import modelsData
from typing import Optional
from .GameData import FacingDirection, RelatedSkill, Gender, StrictTileChecking

from .XNA import Coordinates
from .spawnTimingSettings import SpawnTimingSettings
from .extraConditions import ExtraConditions
from .areas import Areas

from .globalSpawnSettings import GlobalSpawnSettings


class MonsterTypeSettings(modelsData):
    def __init__(
        self,
        *,
        SpawnWeight:Optional[int]=None,
        HP:Optional[int]=None,
        CurrentHP:Optional[int]=None,
        PersistentHP:bool=None,
        Damage:Optional[int]=None,
        Defense:Optional[int]=None,
        DodgeChance:Optional[int]=None,
        EXP:Optional[int]=None,
        Loot:Optional[list[int|str]]=None,        
        ExtraLoot:Optional[bool]=None,
        SightRange:Optional[int]=None,
        SeesPlayersAtSpawn:Optional[bool]=None,
        RangedAttacks:Optional[bool]=None,
        InstantKillImmunity:Optional[bool]=None,
        StunImmunity:Optional[bool]=None,
        FacingDirection:Optional[FacingDirection]=None,
        Segments:Optional[int]=None,
        Sprite:Optional[str]=None,
        Color:Optional[str]=None,
        MinColor:Optional[str]=None,
        MaxColor:Optional[str]=None,
        Gender:Optional[Gender]=None,
        RelatedSkill:Optional[RelatedSkill]=None,

        MinimumSkillLevel:Optional[int]=None,
        MaximumSkillLevel:Optional[int]=None,
        PercentExtraHPPerSkillLevel:Optional[int]=None,
        PercentExtraDamagePerSkillLevel:Optional[int]=None,
        PercentExtraDefensePerSkillLevel:Optional[int]=None,
        PercentExtraDodgeChancePerSkillLevel:Optional[int]=None,
        PercentExtraEXPPerSkillLevel:Optional[int]=None
    ):
        self.SpawnWeight=self.getMinimum(SpawnWeight, 1, None)
        self.HP=self.getMinimum(HP, 1, None)
        self.CurrentHP=self.getMinimum(CurrentHP, 1, None)
        self.PersistentHP=PersistentHP
        self.Damage=self.getMinimum(Damage, 0, None)
        self.Defense=self.getMinimum(Defense, 0, None)
        self.DodgeChance=self.getMinimum(DodgeChance, 0, None)
        self.EXP=self.getMinimum(EXP, 0, None)
        self.Loot=Loot
        self.ExtraLoot=ExtraLoot
        self.SightRange=self.getMinimum(SightRange, -2, None)
        self.SeesPlayersAtSpawn=SeesPlayersAtSpawn
        self.RangedAttacks=RangedAttacks
        self.InstantKillImmunity=InstantKillImmunity
        self.StunImmunity=StunImmunity
        self.FacingDirection=FacingDirection.getJson()
        self.Segments=self.getMinimum(Segments, 0, None)
        self.Sprite=Sprite
        self.Color=Color
        self.MinColor=MinColor
        self.MaxColor=MaxColor
        self.Gender=Gender.getJson()
        self.RelatedSkill=RelatedSkill.getJson()

        self.MinimumSkillLevel=self.getMinimum(MinimumSkillLevel, 0, None)
        self.MaximumSkillLevel=self.getMinimum(MaximumSkillLevel, 0, None)
        self.PercentExtraHPPerSkillLevel=self.getMinimum(PercentExtraHPPerSkillLevel, 0, 100)
        self.ExtraDamagePerSkillLevel=self.getMinimum(PercentExtraDamagePerSkillLevel, 0, 100)
        self.ExtraDefensePerSkillLevel=self.getMinimum(PercentExtraDefensePerSkillLevel, 0, 100)
        self.ExtraDodgeChancePerSkillLevel=self.getMinimum(PercentExtraDodgeChancePerSkillLevel, 0, 100)
        self.ExtraEXPPerSkillLevel=self.getMinimum(PercentExtraEXPPerSkillLevel, 0, 100)

    

class MonsterTypes(modelsData):
    def __init__(
        self,
        *,
        MonsterName:str,
        Settings:MonsterTypeSettings
    ):
        self.MonsterName=MonsterName
        self.Settings=Settings

class MonsterAreas(Areas):
    def __init__(
        self,
        *,
        MonsterTypes:list[MonsterTypes],
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
        self.MonsterTypes=[monter.getJson() for monter in MonsterTypes]
        self.UniqueAreaID=UniqueAreaID
        self.MapName=MapName
        self.MinimumSpawnsPerDay=MinimumSpawnsPerDay
        self.MaximumSpawnsPerDay=MaximumSpawnsPerDay
        self.SpawnTiming=SpawnTiming.getJson()
        self.ExtraConditions=ExtraConditions.getJson()
        self.IncludeTerrainTypes=IncludeTerrainTypes
        self.IncludeCoordinates=[coordinate.getJson() for coordinate in IncludeCoordinates]
        self.StrictTileChecking=StrictTileChecking.getJson()
        self.ExcludeTerrainTypes=ExcludeTerrainTypes
        self.ExcludeCoordinates=[coordinate.getJson() for coordinate in ExcludeCoordinates]
        self.DaysUntilSpawnsExpire=DaysUntilSpawnsExpire

class MonsterSpawnSettings(GlobalSpawnSettings):
    def __init__(
        self,
        *,
        Enable:bool,
        Areas:list[MonsterAreas]=None,
        CustomTileIndex:Optional[list[int]]=None
    ):
        self.key="Monster_Spawn_Settings"
        self.Enable=Enable
        self.Areas=Areas
        self.CustomTileIndex=CustomTileIndex