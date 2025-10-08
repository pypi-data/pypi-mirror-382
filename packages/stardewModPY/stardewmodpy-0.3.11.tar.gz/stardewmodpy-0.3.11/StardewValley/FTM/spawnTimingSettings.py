from ..Data.model import modelsData
from typing import Optional

class SpawnTimingSettings(modelsData):
    def __init__(
        self,
        *,
        StartTime:int,
        EndTime:int,
        MinimumTimeBetweenSpawns:Optional[int]=None,
        MaximumSimultaneousSpawns:Optional[int]=None,
        OnlySpawnIfAPlayerIsPresent:Optional[bool]=None,
        SpawnSound:str=""
    ):
        self.StartTime=StartTime
        self.EndTime=EndTime
        self.MinimumTimeBetweenSpawns=MinimumTimeBetweenSpawns if MinimumTimeBetweenSpawns>=10 else 10
        self.MaximumSimultaneousSpawns=MaximumSimultaneousSpawns if MaximumSimultaneousSpawns>=1 else 1
        self.OnlySpawnIfAPlayerIsPresent=OnlySpawnIfAPlayerIsPresent
        self.SpawnSound=SpawnSound