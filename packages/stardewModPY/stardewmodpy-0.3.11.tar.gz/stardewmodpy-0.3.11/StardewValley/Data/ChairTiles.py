from .model import modelsData
from .XNA import Rectangle, Position


class ChairTilesData(modelsData):
    def __init__(
        self, 
        TileSheetFilename: str,
        TileRect:Rectangle,
        Direction: str,
        Type: str,
        Draw: Position,
        isSeasonal: bool
    ):
        self.TileRect = TileRect
        super().__init__(f"{TileSheetFilename}/{self.TileRect.X}/{self.TileRect.Y}")
        self.Direction = Direction
        self.Type = Type
        self.Draw= Draw  
        self.isSeasonal = isSeasonal


    def getJson(self) -> str:
        return f"{self.TileRect.Width}/{self.TileRect.Height}/{self.Direction}/{self.Type}/{self.Draw.X}/{self.Draw.Y}/{str(self.isSeasonal).lower()}"

