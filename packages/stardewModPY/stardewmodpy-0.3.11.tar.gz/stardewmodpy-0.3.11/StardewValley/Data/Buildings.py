from typing import Optional, List, Any
from .model import modelsData
from .XNA import Position, Rectangle
from .GameData import QuantityModifiers

class BuildMaterials(modelsData):
    def __init__(self, *, ItemId:str, Amount: int):
        self.ItemId = ItemId
        self.Amount = Amount

class AdditionalPlacementTiles(modelsData):
    def __init__(
        self,
        *,
        TileArea: Rectangle,
        OnlyNeedsToBeNextToWater: bool = False,
    ):
        self.TileArea = TileArea
        self.OnlyNeedsToBeNextToWater = OnlyNeedsToBeNextToWater

class IndoorItems(modelsData):
    def __init__(self, *, Id: str, ItemId: str, Tile: Position, Indestructible: bool = False, ClearTile: bool = False):
        self.Id = Id
        self.ItemId = ItemId
        self.Tile = Tile
        self.Indestructible = Indestructible
        self.ClearTile = ClearTile

class IndoorItemMoves(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Source: Position,
        Destination: Position,
        Size: Position,
        UnlessItemId: Optional[str] = None,
    ):
        self.Id = Id
        self.Source = Source
        self.Destination = Destination
        self.Size = Size
        self.UnlessItemId = UnlessItemId
    
    

class Skins(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        Name:str,
        Description:str,
        Texture:str,
        Condition:Optional[str]=None,
        NameForGeneralType: Optional[str] = None,
        BuildDays: Optional[int] = None,
        BuildCost: Optional[int] = None,
        BuildMaterials: Optional[List[BuildMaterials]] = None,
        ShowAsSeparateConstructionEntry: Optional[bool] = None,
        Metadata: Optional[dict[str, str]] = None
    ):
        self.Id = Id
        self.Name = Name
        self.Description = Description
        self.Texture = Texture
        self.Condition = Condition
        self.NameForGeneralType = NameForGeneralType
        self.BuildDays = BuildDays
        self.BuildCost = BuildCost
        self.BuildMaterials = BuildMaterials
        self.ShowAsSeparateConstructionEntry = ShowAsSeparateConstructionEntry
        self.Metadata = Metadata

class DrawLayers(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        SourceRect: Rectangle,
        DrawPosition: Position, #use getStr() to return a valid value for this variable
        Texture: Optional[str] = None,
        DrawInBackground: Optional[bool] = None,
        SortTileOffset: Optional[float] = 0.0,
        OnlyDrawIfChestHasContents: Optional[str] = None,
        FrameCount: Optional[int] = None,
        FramesPerRow: Optional[int] = None,
        FrameDuration: Optional[int] = None,
        AnimalDoorOffset: Optional[Position] = None
    ):
        self.Id = Id
        self.SourceRect = SourceRect
        self.DrawPosition = DrawPosition
        self.Texture = Texture
        self.DrawInBackground = DrawInBackground
        self.SortTileOffset = SortTileOffset
        self.OnlyDrawIfChestHasContents = OnlyDrawIfChestHasContents
        self.FrameCount = FrameCount
        self.FramesPerRow = FramesPerRow
        self.FrameDuration = FrameDuration
        self.AnimalDoorOffset = AnimalDoorOffset
    
    def getJson(self, useGetStr = None):
        return super().getJson(useGetStr=["DrawPosition"])
    




class ProducedItems(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        ItemId: str,
        RandomItemId: Optional[list[str]] = None,
        Condition: Optional[str] = None,
        PerItemCondition: Optional[str] = None,
        MaxItems: Optional[int] = None,
        IsRecipe: Optional[bool] = None,
        Quality: Optional[int] = None,
        MinStack: Optional[int] = None,
        MaxStack: Optional[int] = None,
        ObjectInternalName: Optional[str] = None,
        ObjectDisplayName: Optional[str] = None,
        ObjectColor: Optional[str] = None,
        ToolUpgradeLevel: Optional[int] = None,
        QualityModifiers: Optional[list[QuantityModifiers]] = None,
        StackModifiers: Optional[list[QuantityModifiers]] = None,
        QualityModifierMode: Optional[str] = None,
        StackModifierMode: Optional[str] = None,
        ModData: Optional[dict[str,str]] = None
    ):
        self.Id = Id
        self.ItemId = ItemId
        self.RandomItemId = RandomItemId
        self.Condition = Condition
        self.PerItemCondition = PerItemCondition
        self.MaxItems = MaxItems
        self.IsRecipe = IsRecipe
        self.Quality = Quality
        self.MinStack = MinStack
        self.MaxStack = MaxStack
        self.ObjectInternalName = ObjectInternalName
        self.ObjectDisplayName = ObjectDisplayName
        self.ObjectColor = ObjectColor
        self.ToolUpgradeLevel = ToolUpgradeLevel
        self.QualityModifiers = QualityModifiers
        self.StackModifiers = StackModifiers
        self.QualityModifierMode = QualityModifierMode
        self.StackModifierMode = StackModifierMode
        self.ModData = ModData


class ItemConversions(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        RequiredTags: list[str],
        SourceChest: str,
        DestinationChest: str,
        ProducedItems: list[ProducedItems]=None,
        RequiredCount: Optional[int] = None,
        MaxDailyConversion: Optional[int] = None
    ):
        self.Id = Id
        self.RequiredTags = RequiredTags
        self.SourceChest = SourceChest
        self.DestinationChest = DestinationChest
        self.ProducedItems = ProducedItems
        self.RequiredCount = RequiredCount
        self.MaxDailyConversion = MaxDailyConversion

class Chests(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Type: str,
        Sound: Optional[str] = None,
        InvalidItemMessage: Optional[str] = None,
        InvalidCountMessage: Optional[str] = None,
        ChestFullMessage: Optional[str] = None,
        InvalidItemMessageCondition: Optional[str] = None,
        DisplayTile: Optional[Position] = None, #use getStr() to return a valid value for this variable
        DisplayHeight: Optional[float] = None
    ):
        self.Id = Id
        self.Type = Type
        self.Sound = Sound
        self.InvalidItemMessage = InvalidItemMessage
        self.InvalidCountMessage = InvalidCountMessage
        self.ChestFullMessage = ChestFullMessage
        self.InvalidItemMessageCondition = InvalidItemMessageCondition
        self.DisplayTile = DisplayTile
        self.DisplayHeight = DisplayHeight
    
    def getJson(self, useGetStr = None): #customized because of getStr functions
        return super().getJson(useGetStr=["DisplayTile"])
    

class ActionTiles(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Tile:Position,
        Action: str
    ):
        self.Id = Id
        self.Tile = Tile
        self.Action = Action
    

class TileProperties:
    def __init__(
        self,
        *,
        Id: str,
        Name: str,
        Value: str,
        Layer:str,
        TileArea: Rectangle        
    ):
        self.Id = Id
        self.Name = Name
        self.Value = Value
        self.Layer = Layer
        self.TileArea = TileArea
    
    def getJson(self) -> dict:
        return {"Id": self.Id, "Name": self.Name, "Value": self.Value, "Layer": self.Layer, "TileArea": self.TileArea.getJson()}
        

class BuildingsData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Name: str,
        Description: str,
        Texture: str,
        NameForGeneralType: Optional[str] = None, 
        Builder: Optional[str] = None,
        BuildCost: Optional[int] = None,
        BuildMaterials: Optional[List[BuildMaterials]] = None, 
        BuildDays: Optional[int] = None, 
        BuildCondition: Optional[str] = None, 
        BuildMenuDrawOffset: Optional[Position] = None,   
        AdditionalPlacementTiles: Optional[list[AdditionalPlacementTiles]] = None,
        IndoorItems: Optional[list[IndoorItems]] = None,        
        MagicalConstruction: Optional[bool] = None,        
        AddMailOnBuild: Optional[list[str]] = None,        
        BuildingToUpgrade: Optional[str] = None,
        IndoorItemMoves: Optional[list[IndoorItemMoves]] = None, 
        UpgradeSignTile: Optional[Position] = None,#use getStr() to return a valid value for this variable
        UpgradeSignHeight: float = 0.0,
        Size: Optional[Position] = None,
        CollisionMap: Optional[str] = None,
        HumanDoor: Optional[Position] = None,
        AnimalDoor: Optional[Rectangle]=None,
        AnimalDoorOpenDuration: Optional[float] = None,
        AnimalDoorCloseDuration: Optional[float] = None,
        AnimalDoorOpenSound: Optional[str] = None, 
        AnimalDoorCloseSound: Optional[str] = None,
        SourceRect: Optional[Rectangle] = None,
        Skins: Optional[list[Skins]] = None,
        FadeWhenBehind: Optional[bool] = None,
        DrawOffset: Optional[Position] = None,#use getStr() to return a valid value for this variable
        SeasonOffset: Optional[Position] = None,
        SortTileOffset: Optional[float] = None,
        AllowsFlooringUnderneath: Optional[bool] = None, 
        DrawLayers: Optional[list[DrawLayers]] = None,
        DrawShadow: bool = True,
        IndoorMap: Optional[str] = None, 
        IndoorMapType: Optional[str] = None,
        NonInstancedIndoorLocation: Optional[str] = None,
        MaxOccupants: Optional[int] = None, 
        AllowAnimalPregnancy: Optional[bool] = None, 
        ValidOccupantTypes: Optional[list[str]] = None,
        HayCapacity: Optional[int] = None,        
        ItemConversions: Optional[list[ItemConversions]] = None,         
        Chests: Optional[list[Chests]] = None,        
        ActionTiles: Optional[list[ActionTiles]] = None,
        DefaultAction: Optional[str] = None,
        TileProperties: Optional[list[TileProperties]] = [],
        AdditionalTilePropertyRadius: Optional[int] = None, 
        Metadata: Optional[dict[str, str]] = None,
        BuildingType: Optional[str] = None,
        ModData: Optional[dict[str, str]] = None,
        CustomFields: Optional[dict[str, Any]] = None
    
    ):
        super().__init__(key)
        self.Name = Name
        self.Description = Description
        self.Texture = Texture
        self.Builder = Builder
        self.NameForGeneralType = NameForGeneralType
        self.BuildCost = BuildCost
        self.BuildMaterials = BuildMaterials
        self.BuildDays = BuildDays
        self.BuildCondition = BuildCondition
        self.BuildMenuDrawOffset = BuildMenuDrawOffset
        self.AdditionalPlacementTiles = AdditionalPlacementTiles
        self.IndoorItems = IndoorItems
        self.MagicalConstruction = MagicalConstruction
        self.AddMailOnBuild = AddMailOnBuild
        self.BuildingToUpgrade = BuildingToUpgrade        
        self.IndoorItemMoves = IndoorItemMoves
        self.UpgradeSignTile = UpgradeSignTile
        self.UpgradeSignHeight = UpgradeSignHeight
        self.Size = Size
        self.CollisionMap = CollisionMap
        self.HumanDoor = HumanDoor
        self.AnimalDoor = AnimalDoor
        self.AnimalDoorOpenDuration = AnimalDoorOpenDuration
        self.AnimalDoorCloseDuration = AnimalDoorCloseDuration
        self.AnimalDoorOpenSound = AnimalDoorOpenSound
        self.AnimalDoorCloseSound = AnimalDoorCloseSound
        self.SourceRect = SourceRect
        self.Skins = Skins
        self.FadeWhenBehind = FadeWhenBehind
        self.DrawOffset = DrawOffset
        self.SeasonOffset = SeasonOffset
        self.SortTileOffset = SortTileOffset
        self.AllowsFlooringUnderneath = AllowsFlooringUnderneath
        self.DrawLayers = DrawLayers
        self.DrawShadow = DrawShadow
        self.IndoorMap = IndoorMap        
        self.IndoorMapType = IndoorMapType
        self.NonInstancedIndoorLocation = NonInstancedIndoorLocation
        self.MaxOccupants = MaxOccupants
        self.AllowAnimalPregnancy = AllowAnimalPregnancy
        self.ValidOccupantTypes = ValidOccupantTypes
        self.HayCapacity = HayCapacity
        self.ItemConversions = ItemConversions
        self.Chests = Chests
        self.ActionTiles = ActionTiles
        self.DefaultAction = DefaultAction
        self.TileProperties = TileProperties
        self.AdditionalTilePropertyRadius = AdditionalTilePropertyRadius
        self.Metadata = Metadata
        self.BuildingType = BuildingType
        self.ModData = ModData
        self.CustomFields = CustomFields
    
    def getJson(self, useGetStr = None):
        return super().getJson(useGetStr=["UpgradeSignTile", "DrawOffset"])