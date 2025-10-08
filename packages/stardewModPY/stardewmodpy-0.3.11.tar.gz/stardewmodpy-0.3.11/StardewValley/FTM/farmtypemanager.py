from ..manifest import Manifest
from typing import Optional, Any
from .forageSpawnSettings import ForageSpawnSettings
from .largeObjectSpawnSettings import LargeObjectSpawnSettings
from .oreSpawnSettings import OreSpawnSettings
from .monsterSpawnSettings import MonsterSpawnSettings

class FarmTypeManager:
    def __init__(
        self,
        manifest:Manifest
    ):
        self.Manifest=manifest
        self.Manifest.ContentPackFor={
            "UniqueID": "Esca.FarmTypeManager",
            "MinimumVersion": "1.23.0"
        }
        self.fileName="content.json"

        self.contentFile={}

    def registryContentData(
        self,
        forageSpawn:Optional[ForageSpawnSettings]=None,
        largeObjectSpawn:Optional[LargeObjectSpawnSettings]=None,
        oreSpawn:Optional[OreSpawnSettings]=None,
        monsterSpawn:Optional[MonsterSpawnSettings]=None
    ):
        self.contentFile["ForageSpawnEnabled"]=forageSpawn.Enable
        self.contentFile["LargeObjectSpawnEnabled"]=largeObjectSpawn.Enable
        self.contentFile["OreSpawnEnabled"]=oreSpawn.Enable
        self.contentFile["MonsterSpawnEnabled"]=monsterSpawn.Enable
        if forageSpawn is not None:
            self.contentFile[forageSpawn.key]=forageSpawn.getJson()
        if largeObjectSpawn is not None:
            self.contentFile[largeObjectSpawn.key]=largeObjectSpawn.getJson()
        if oreSpawn is not None:
            self.contentFile[oreSpawn.key]=oreSpawn.getJson()
        if monsterSpawn is not None:
            self.contentFile[monsterSpawn.key]=monsterSpawn.getJson()
        