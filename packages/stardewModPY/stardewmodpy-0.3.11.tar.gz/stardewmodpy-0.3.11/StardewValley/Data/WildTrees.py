from .model import modelsData
from typing import Any, Optional
from .GameData import Season, CommonFields, ItemSpawnFields, ChopItemsSize, QuantityModifiers, QualityModifierMode, Result, PlantedIn

class Textures(modelsData):
    def __init__(
        self,
        *,
        Texture:str,
        Season:Optional[Season]=None,
        Condition:Optional[str]=None
    ):
        self.Texture=Texture
        self.Season=Season
        self.Condition=Condition

class SeedDropItems(CommonFields):
    def __init__(
        self,
        *,
        CommonFields:ItemSpawnFields,
        Season:Optional[Season]=None,
        Chance:Optional[float]=None,
        ContinueOnDrop:Optional[bool]=None
    ):
        super().__init__(CommonFields=CommonFields)
        self.Season=Season
        self.Chance=Chance
        self.ContinueOnDrop=ContinueOnDrop

class ChopItems(CommonFields):
    def __init__(
        self,
        CommonFields:ItemSpawnFields,
        Season:Optional[Season]=None,
        Chance:Optional[float]=None,
        MinSize:Optional[ChopItemsSize]=None,
        MaxSize:Optional[ChopItemsSize]=None,
        ForStump:Optional[bool]=None
    ):
        super().__init__(CommonFields)
        self.Season=Season
        self.Chance=Chance
        self.MinSize=MinSize
        self.MaxSize=MaxSize
        self.ForStump=ForStump

class ShakeItems(CommonFields):
    def __init__(
        self,
        CommonFields:ItemSpawnFields,
        Season:Optional[Season]=None,
        Chance:Optional[float]=None
    ):
        super().__init__(CommonFields=CommonFields)
        self.Season=Season
        self.Chance=Chance

class TapItems(CommonFields):
    def __init__(
        self,
        CommonFields:ItemSpawnFields,
        DaysUntilReady:int,
        Season:Optional[Season]=None,
        Chance:Optional[float]=None,
        PreviousItemId: Optional[list[str]] = None,
        DaysUntilReadyModifiers: Optional[list[QuantityModifiers]] = None,
        DaysUntilReadyModifierMode: Optional[QualityModifierMode] = None
    ):
        super().__init__(CommonFields=CommonFields)
        self.Season=Season
        self.Chance=Chance
        self.DaysUntilReady=DaysUntilReady
        self.PreviousItemId=PreviousItemId
        self.DaysUntilReadyModifiers=DaysUntilReadyModifiers
        self.DaysUntilReadyModifierMode=DaysUntilReadyModifierMode

class PlantableLocationRules(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        Result:Result,
        Condition:Optional[str]=None,
        PlantedIn:Optional[PlantedIn]=None,
        DeniedMessage:Optional[str]=None
    ):
        self.Id=Id
        self.Result=Result
        self.Condition=Condition
        self.PlantedIn=PlantedIn
        self.DeniedMessage=DeniedMessage

class WildTreesData(modelsData):
    def __init__(
        self,
        key: str,
        Textures: list[Textures],
        SeedItemId: str = None,
        SeedPlantable: Optional[bool] = None,
        GrowthChance: Optional[float] = None,
        FertilizedGrowthChance: Optional[float] = None,
        SeedSpreadChance: Optional[float] = None,
        SeedOnShakeChance: Optional[float] = None,
        SeedOnChopChance: Optional[float] = None,
        DropWoodOnChop: Optional[bool] = None,
        DropHardwoodOnLumberChop: Optional[bool] = None,
        IsLeafy: Optional[bool] = None,
        IsLeafyInWinter: Optional[bool] = None,
        IsLeafyInFall: Optional[bool] = None,           
        GrowsInWinter: Optional[bool] = None,
        IsStumpDuringWinter: Optional[bool] = None,
        AllowWoodpeckers: Optional[bool] = None,
        UseAlternateSpriteWhenNotShaken: Optional[bool] = None,
        UseAlternateSpriteWhenSeedReady: Optional[bool] = None,
        DebrisColor: Optional[str] = None,
        SeedDropItems: Optional[list[SeedDropItems]] = None,
        ChopItems: Optional[list[ChopItems]] = None,
        ShakeItems: Optional[list[ShakeItems]] = None,
        TapItems: Optional[list[TapItems]] = None,
        PlantableLocationRules: Optional[list[PlantableLocationRules]] = None,
        CustomFields: Optional[dict[str, Any]] = None,
        GrowsMoss:Optional[bool] = None
    ):
        super().__init__(key)

        self.Textures = Textures
        self.SeedItemId = SeedItemId
        self.SeedPlantable = SeedPlantable
        self.GrowthChance = GrowthChance
        self.FertilizedGrowthChance = FertilizedGrowthChance
        self.SeedSpreadChance = SeedSpreadChance
        self.SeedOnShakeChance = SeedOnShakeChance
        self.SeedOnChopChance = SeedOnChopChance
        self.DropWoodOnChop = DropWoodOnChop
        self.DropHardwoodOnLumberChop = DropHardwoodOnLumberChop
        self.IsLeafy = IsLeafy
        self.IsLeafyInWinter = IsLeafyInWinter
        self.IsLeafyInFall = IsLeafyInFall
        self.GrowsInWinter = GrowsInWinter
        self.IsStumpDuringWinter = IsStumpDuringWinter
        self.AllowWoodpeckers = AllowWoodpeckers
        self.UseAlternateSpriteWhenNotShaken = UseAlternateSpriteWhenNotShaken
        self.UseAlternateSpriteWhenSeedReady = UseAlternateSpriteWhenSeedReady
        self.DebrisColor = DebrisColor
        self.PlantableLocationRules = PlantableLocationRules
        self.SeedDropItems = SeedDropItems
        self.ChopItems = ChopItems
        self.TapItems = TapItems
        self.ShakeItems = ShakeItems
        self.CustomFields = CustomFields
        self.GrowsMoss=GrowsMoss
