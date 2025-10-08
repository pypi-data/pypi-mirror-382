from .model import modelsData

class AchievementsData(modelsData):
    def __init__(
            self, key: str,
            Name: str,
            Description:str,
            DisplayAchievementOnCollectionsTabBeforeItsEarned:bool,
            PrerequisiteAchievement:int,
            HatEarned:str
        ):
        super().__init__(key)
        self.Name = Name
        self.Description = Description
        self.DisplayAchievementOnCollectionsTabBeforeItsEarned = DisplayAchievementOnCollectionsTabBeforeItsEarned
        self.PrerequisiteAchievement = PrerequisiteAchievement
        self.HatEarned = HatEarned
    def getJson(self) -> str:
        return "^".join([self.Name, self.Description, str(self.DisplayAchievementOnCollectionsTabBeforeItsEarned).lower(), str(self.PrerequisiteAchievement), self.HatEarned])
    
    