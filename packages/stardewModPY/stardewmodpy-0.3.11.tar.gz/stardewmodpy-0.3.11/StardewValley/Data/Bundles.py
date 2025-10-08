from .model import modelsData

class Requirements:
    def __init__(
        self,
        itemID:int,
        count:int,
        minQuality:int=0
    ):
        self.itemID = itemID
        self.count = count
        self.minQuality = minQuality
    
    def getJson(self) -> str:
        return f"{self.itemID} {self.count} {self.minQuality}"

class Reward:
    def __init__(
        self,
        itemType:int,
        itemID:int,
        count:int
    ):
        self.itemType = itemType
        self.itemID = itemID
        self.count = count
    
    def getJson(self) -> str:
        return f"{self.itemType} {self.itemID} {self.count}"

class BundlesData(modelsData):
    def __init__(
        self, 
        roomID: str,
        spriteIndex:str,
        bundle_name: str,
        reward: Reward,
        requirements: list[Requirements],
        color: int,
        item_count: int,
        display_name: str
    ):
        super().__init__(f"{roomID}/{spriteIndex}")
        self.bundle_name = bundle_name
        self.reward = reward
        self.requirements = requirements
        self.color = color
        self.item_count = item_count
        self.display_name = display_name


    def getJson(self) -> str:
        reqList=' '.join([req.getJson() for req in self.requirements])
        return f"{self.bundle_name}/{self.reward.getJson()}/{reqList}/{self.color}/{self.item_count}//{self.display_name}"
