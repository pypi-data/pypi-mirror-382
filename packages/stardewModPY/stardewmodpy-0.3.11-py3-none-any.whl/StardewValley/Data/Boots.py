from typing import Optional
from .model import modelsData
class BootsData(modelsData):
    def __init__(
        self,
        *,
        key:int,
        Name:str,
        Description:str,
        AddedDefense:int,
        AddedImmunity:int,
        ColorIndex:int,
        DisplayName:str,
        ColorTexture:Optional[str]=None,
        SpriteIndex:Optional[int]=None,
        Texture:Optional[str]=None


    ):
        super().__init__(key)
        self.Name = Name
        self.Description = Description
        self.Price=(AddedDefense*100)+(AddedImmunity*100)
        self.AddedDefense = AddedDefense
        self.AddedImmunity = AddedImmunity
        self.ColorIndex = ColorIndex
        self.DisplayName = DisplayName
        self.ColorTexture = ColorTexture
        self.SpriteIndex = SpriteIndex
        self.Texture = Texture
    
    def getJson(self) -> str:
        res= f"{self.Name}/{self.Description}/{self.Price}/{self.AddedDefense}/{self.AddedImmunity}/{self.ColorIndex}/{self.DisplayName}"
        if hasattr(self, "ColorTexture") and self.ColorTexture is not None and hasattr(self, "SpriteIndex") and self.SpriteIndex is not None and hasattr(self, "Texture") and self.Texture is not None:
            res+="/{self.ColorTexture}/{self.SpriteIndex}/{self.Texture}"
        return res

