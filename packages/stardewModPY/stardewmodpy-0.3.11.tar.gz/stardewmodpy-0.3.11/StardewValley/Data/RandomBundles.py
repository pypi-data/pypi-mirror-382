from .model import modelsData

class Items(modelsData):
    def __init__(
        self,
        Name: str,
        Count: int
    ):
        self.Name = Name
        self.Count = Count
    
    def getJson(self) -> str:
        return f"{self.Count} {self.Name}"
        

class Bundles(modelsData):
    def __init__(
        self,
        Name: str,
        Index: int,
        Sprite: str,
        Color: str,
        Items: list[Items],
        Pick: int,
        RequiredItems: int,
        Reward: Items
    ):
        self.Name = Name
        self.Index = Index
        self.Sprite = Sprite
        self.Color = Color
        self.Items = ", ".join([item.getJson() for item in Items])
        self.Pick = Pick
        self.RequiredItems = RequiredItems
        self.Reward = Reward


class BundleSets(modelsData):
    def __init__(
        self,
        Id: str,
        Bundles: list[Bundles]
    ):
        self.Id = Id
        self.Bundles = [bundle.getJson() for bundle in Bundles]


class RandomBundlesData(modelsData):
    def __init__(
        self,
        AreaName: list[str],
        Keys: str,
        BundleSets: list[BundleSets],
        Bundles: list[Bundles]
    ):
        super().__init__(None)
        self.AreaName = " ".join(AreaName)
        self.Keys = Keys
        self.BundleSets = BundleSets
        self.Bundles = Bundles

