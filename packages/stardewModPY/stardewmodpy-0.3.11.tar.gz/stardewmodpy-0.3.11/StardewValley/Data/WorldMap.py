from .model import modelsData
from .XNA import Rectangle
from typing import Optional, Any

class BaseTexture(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        Texture: str,
        SourceRect: Optional[Rectangle] = None,
        MapPixelArea: Optional[Rectangle] = None,
        Condition: Optional[str] = None
    ):
        self.Id = Id
        self.Texture = Texture
        self.SourceRect = SourceRect
        self.MapPixelArea = MapPixelArea
        self.Condition = Condition

class Tooltips(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Text: Optional[str],
        PixelArea: Optional[Rectangle] = None,
        Condition: Optional[str] = None,
        KnowCondition: Optional[str] = None,
        LeftNeighbor: Optional[str] = None,
        RightNeighbor: Optional[str] = None,
        UpNeighbor: Optional[str] = None,
        DownNeighbor: Optional[str] = None
    ):
        self.Id = Id
        self.Text = Text
        self.PixelArea = PixelArea
        self.Condition = Condition
        self.KnowCondition = KnowCondition
        self.LeftNeighbor = LeftNeighbor
        self.RightNeighbor = RightNeighbor
        self.UpNeighbor = UpNeighbor
        self.DownNeighbor = DownNeighbor

class ScrollTextZones(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        TileArea: Rectangle = None,
        ScrollText: str = None
    ):
        self.Id = Id
        self.TileArea = TileArea
        self.ScrollText = ScrollText

class WorldPositions(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        LocationContext: Optional[str] = None,
        LocationName: Optional[str] = None,
        LocationNames: Optional[list[str]] = None,
        TileArea: Optional[Rectangle] = None,
        MapPixelArea: Optional[Rectangle] = None,
        ScrollText: Optional[str] = None,
        Condition: Optional[str] = None,
        ScrollTextZones: Optional[list[ScrollTextZones]] = None,
        ExtendedTileArea: Optional[Rectangle] = None
    ):
        self.Id = Id
        self.LocationContext = LocationContext
        self.LocationName = LocationName
        self.LocationNames = LocationNames
        self.TileArea = TileArea
        self.MapPixelArea = MapPixelArea
        self.ScrollText = ScrollText
        self.Condition = Condition
        self.ScrollTextZones = ScrollTextZones
        self.ExtendedTileArea = ExtendedTileArea

class MapAreas(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        PixelArea:Rectangle,
        ScroolText:Optional[str]=None,
        Textures:Optional[list[BaseTexture]]=None,
        Tooltips:Optional[list[Tooltips]]=None,
        WorldPositions:Optional[list[WorldPositions]]=None,
        CustomFields:Optional[dict[str,Any]]=None
    ):
        self.Id = Id
        self.PixelArea = PixelArea
        self.ScroolText = ScroolText
        self.Textures = Textures
        self.Tooltips = Tooltips
        self.WorldPositions = WorldPositions
        self.CustomFields = CustomFields
        
class WorldMapData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        BaseTexture: Optional[BaseTexture] = None,
        MapAreas:Optional[list[MapAreas]] = None,
        MapNeighborIdAliases: Optional[dict[str, str]] = None

    ):
        super().__init__(key)
        self.BaseTexture = BaseTexture
        self.MapAreas = MapAreas
        self.MapNeighborIdAliases = MapNeighborIdAliases