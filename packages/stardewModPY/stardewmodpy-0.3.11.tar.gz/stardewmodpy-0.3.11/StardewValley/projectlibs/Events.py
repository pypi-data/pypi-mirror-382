from .libModel import libModel

class Events(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import Events as Events_list
from StardewValley.Data.SVModels.Events import Events
""" if self.optionals["Events"] else ""
        
        self.implements="Events(mod=self, Events_list=[])" if self.optionals["Events"] else ""

        self.classFileData_imports="""from StardewValley.Data import EventData, Eventscripts, Precondition, CharacterID
from StardewValley.Data.GameData import Direction
"""

        self.classFileData_Father="(EventData)"
        self.classFileData_contents="""self.key=Precondition(
            ID="###name###",
            ...
        )
        self.value=Eventscripts(
            music="jingleBell",
            coordinates=(0, 0),
            characterID=[
                CharacterID("farmer", 0, 0, Direction.Down),
                CharacterID("###name###", 0, 5, Direction.Down)
            ]
        )
        self.value.skippable()
        self.value.pause(1500)
        self.value.end()
        self.location="Farm"
        """