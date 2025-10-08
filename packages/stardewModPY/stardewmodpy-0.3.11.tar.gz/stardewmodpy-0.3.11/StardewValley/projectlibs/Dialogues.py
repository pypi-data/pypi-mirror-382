from .libModel import libModel

class Dialogues(libModel):
    def __init__(self, optionals, modName):
        super().__init__(optionals, modName)

        self.imports="""import Dialogues as Dialogues_List
from StardewValley.Data.SVModels.Dialogues import Dialogues
""" if self.optionals["Dialogues"] else ""

        self.implements="Dialogues(mod=self, Dialogues_List=[])" if self.optionals["Dialogues"] else ""

        self.classFileData_imports="""from StardewValley.Characters import dialogueData
"""
        self.classFileData_Father="(dialogueData)"
        self.classFileData_contents="""self.Introduction = ""
        self.FlowerDance_Accept = ""
        self.AcceptBirthdayGift_Positive = ""
        self.AcceptBirthdayGift_Negative = ""
        self.GreenRain = ""
        self.GreenRainFinished = ""
        self.GreenRain_2 = ""
        self.Mon = ""
        self.Tue = ""
        self.Wed = ""
        self.Thu = ""
        self.Fri = ""
        self.Sat = ""
        self.Sun = ""
        """