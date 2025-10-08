from .model import modelsData

class AdditionalWallpaperFlooringData(modelsData):
    def __init__(self, key: str, Id: str, Texture: str, IsFlooring: bool, Count: int):
        super().__init__(key)
        self.Id = Id
        self.Texture = Texture
        self.IsFlooring = IsFlooring
        self.Count = Count
