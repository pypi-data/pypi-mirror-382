from .model import modelsData


class HairData(modelsData):
    def __init__(
        self,
        key: str,
        texture: str,
        tileX: int,
        tileY: int,
        usesUniqueLeftSprite: bool,
        coveredIndex: int,
        isBaldStyle: bool
    ):
        super().__init__(key)
        self.texture = texture
        self.tileX = tileX
        self.tileY = tileY 
        self.usesUniqueLeftSprite = "true" if usesUniqueLeftSprite else "false"
        self.coveredIndex = coveredIndex
        self.isBaldStyle = "true" if isBaldStyle else "false"


    def getJson(self) -> str:
        return f"{self.texture}/{self.tileX}/{self.tileY}/{self.usesUniqueLeftSprite}/{self.coveredIndex}/{self.isBaldStyle}"