from .libModel import libModel

class NPCS(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import NPCS as NPCs_List
from StardewValley.Data.SVModels import NPCs
"""
        
        self.implements="NPCs(mod=self, NPCs_List=[])" if self.optionals["NPCs"] else ""

        self.classFileData_imports="""from StardewValley.Data import CharactersData, Home, Position
from StardewValley.Data.GameData import Gender, SocialAnxiety, Manner, Optimism, Season, HomeRegion, Age, Direction
"""
        self.classFileData_Father="(CharactersData)"
        self.classFileData_contents="""self.key=###name###
        self.DisplayName=###name###
        self.Gender=Gender.Undefined
        self.Age=Age.Adult
        self.Manner=Manner.Neutral
        #self.SocialAnxiety=SocialAnxiety.Neutral
        self.Optimism=Optimism.Neutral
        self.BirthSeason=Season.Spring
        self.BirthDay=1
        self.HomeRegion="Town"
        self.CanBeRomanced=False
        self.Home=[
            Home(
                Id="###name###House",
                Tile=Position(10, 10),
                Direction=Direction.Right,
                Location="Town"
            ).getJson()
        ]"""