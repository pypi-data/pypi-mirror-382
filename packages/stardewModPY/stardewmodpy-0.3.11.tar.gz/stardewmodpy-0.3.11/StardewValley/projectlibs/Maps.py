from .libModel import libModel

class Maps(libModel):
    def __init__(self, optionals: dict, modName: str):
        super().__init__(optionals, modName)
        self.imports="from Maps.Maps import Maps" if self.optionals["Maps"] else ""
        
        self.implements="Maps(self)" if self.optionals["Maps"] else ""

        self.classData=f"""from StardewValley.Data.SVModels import Maps as MapsModel
from StardewValley import Helper

class Maps(MapsModel):
    def __init__(self, mod: Helper):
        super().__init__(mod)
        self.mod.assetsFileIgnore=[]
    
    def contents(self):
        super().contents()

"""
        self.import_file="Maps.py"
        self.classFileData_imports="""from StardewValley.Data.SVModels import svmodel, MapsModel
from StardewValley.Data import LocationsData"""

        self.classFileData_Father="(MapsModel)"
        self.classFileData_params="*, maps: svmodel"
        
    def add_import(self, name):
        pass

    def buildClassData(self, name):
        self.classFileData=f"""{self.classFileData_imports}

class {name}{self.classFileData_Father}:
    def __init__(self{self.classFileData_params}):
        super().__init__(map_name="{name}", map_file="assets/Maps/{name}.tmx", maps=maps)
        
    def contents(self):
        super().contents()

        LocationsData(
            key=self.map_name,
            DisplayName={name},
            DefaultArrivalTile={"X": 16, "Y": 16},
            CreateOnLoad={"MapPath": f"Maps/{self.map_name}", "AlwaysActive":True},
            FormerLocationNames=[f"Custom_{self.map_name}"],
        ).register(
            LogName=f"Add Location {self.map_name}", 
            Target="Data/Locations",
            mod=self.maps.mod,
            contentFile=self.maps.__class__.__name__
        )
"""