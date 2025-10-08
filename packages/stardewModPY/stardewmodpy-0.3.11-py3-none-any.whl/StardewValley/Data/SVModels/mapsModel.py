from .svmodel import svmodel
from ...contentpatcher import Load, EditData, EditImage, EditMap, Include
from ..AdditionalFarms import AdditionalFarmsData

class MapsModel:
    def __init__(
        self,
        *,
        map_name:str=None,
        map_file:str=None,
        maps: svmodel
    ):
        self.maps = maps
        self.map_name = map_name if map_name is not None else self.__class__.__name__
        self.map_file = map_file if map_file is not None else f"assets/Maps/{self.map_name}.tmx"
        self.contents()
    
    def registryContentData(self, contentData:Load|EditData|EditImage|EditMap|Include):
        self.maps.mod.content.registryContentData(
            contentData,
            contentFile=self.map_name
        )
        

    def contents(self):
        self.maps.mod.content.registryContentData(
            Include(
                FromFile=self.map_name
            )
        )

        self.registryContentData(
            Load(
                LogName=f"Carregando {self.map_name}",
                Target=f"Maps/{self.map_name}",
                FromFile=self.map_file
            )
        )

class FarmModel(MapsModel):
    def __init__(
        self,
        *,
        map_name:str=None,
        map_file:str=None,
        maps: svmodel
    ):
        super().__init__(map_name=map_name, map_file=map_file, maps=maps)
    
    def contents(self):
        super().contents()
        self.registryFarm()
        
    def registryFarm(self):
        self.registryContentData(
            EditData(
                LogName="Add Map Farm {self.map_name} to String Maps List",
                Target="Strings/1_6_Strings",
                Entries={
                    self.map_name: self.map_name
                }
            )
        )
    
        self.registryContentData(
            Load(
                LogName="Add Farm {self.map_name} To Intro Map",
                Target=f"LooseSprites/{self.map_name}Icon",
                FromFile=f"assets/Maps/{self.map_name}Icon.png"
            )
        )

        self.registryContentData(
            Load(
                LogName="Add Farm {self.map_name} To Intro Map World",
                Target=f"LooseSprites/{self.map_name}Map",
                FromFile=f"assets/Maps/{self.map_name}Map.png"
            )
        )

        farm_additional=AdditionalFarmsData(
            key=f"{self.maps.mod.content.Manifest.UniqueID}/{self.map_name}",
            Id=f"{self.maps.mod.content.Manifest.UniqueID}/{self.map_name}",
            TooltipStringPath=f"Strings/1_6_Strings:{self.map_name}",
            MapName=self.map_name,
            IconTexture=f"LooseSprites/{self.map_name}Icon",
            WorldMapTexture=f"LooseSprites/{self.map_name}Map",
            SpawnMonstersByDefault=True
        )

        self.registryContentData(
            EditData(
                LogName=f"Add Farm {self.map_name} To tile",
                Target="Data/AdditionalFarms",
                Entries={
                    farm_additional.key: farm_additional.getJson()
                }
            )
        )