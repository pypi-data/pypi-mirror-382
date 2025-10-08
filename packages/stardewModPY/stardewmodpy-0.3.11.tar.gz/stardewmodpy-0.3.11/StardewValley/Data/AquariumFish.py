from .model import modelsData
from typing import Optional
from .XNA  import Position
from .GameData import AquariumType

class AquariumFishData(modelsData):
    def __init__(
        self,
        key: str,
        SpriteIndex:int,
        type: AquariumType,
        idle: Optional[list[int]]=None,
        animation: Optional[list[int]]=None,
        dart: Optional[list[int]]=None,
        animation2: Optional[list[int]]=None,
        texture:Optional[str]=None,
        hatPosition: Optional[Position]=None
    ):
        super().__init__(key)
        self.SpriteIndex = SpriteIndex
        self.type = type
        self.idle = idle
        self.animation = animation
        self.dart = dart
        self.animation2 = animation2
        self.texture = texture
        self.hatPosition = hatPosition

    def getJson(self) -> str:
        json=f"{self.SpriteIndex}/{self.type}"
        optional_vars=["idle", "animation", "dart", "animation2", "texture"]
        for var in optional_vars:
            if hasattr(self, var) and getattr(self, var) is not None:
                if isinstance(getattr(self, var), list):
                    json+=f"/{' '.join(map(str, getattr(self, var)))}"
                json+=f"/{getattr(self, var)}"
            else:
                json+="/"

        
        if hasattr(self, "hatPosition") and self.hatPosition is not None:
            json+=f"/{self.hatPosition.X} {self.hatPosition.Y}"
        return json