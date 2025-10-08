from .model import modelsData
from typing import Optional
from .XNA import Rectangle, Position

class AlternatePurchaseTypes(modelsData):
    def __init__(self, Id: str, AnimalIds: list[str], Condition: Optional[str]=None):
        self.Id = Id
        self.Condition = Condition
        self.AnimalIds = AnimalIds
    
    

class ProduceItemIds(modelsData):
    def __init__(self, Id: str, MinimumFriendship: int, ItemId:str, Condition: Optional[str]=None):  
        self.Id = Id
        self.MinimumFriendship = MinimumFriendship
        self.ItemId = ItemId
        self.Condition = Condition

     

class AnimalSkin(modelsData):
    def __init__(self, Id: str, Weight: Optional[float]=None, Texture: Optional[str]=None, HarvestTexture: Optional[str]=None, BabyTexture: Optional[str]=None):
        self.Id = Id
        self.Weight = Weight
        self.Texture = Texture
        self.HarvestTexture = HarvestTexture
        self.BabyTexture = BabyTexture
    

class FarmAnimalShadowData(modelsData):
    def __init__(self, Visible:bool, Offset:Position, Scale:float):
        self.Visible = Visible
        self.Offset = Offset
        self.Scale = Scale
    

class StatToIncrementOnProduce(modelsData):
    def __init__(self, Id: str, StatName:str, RequiredItemId:Optional[str]=None, RequiredTags:Optional[list[str]]=None):
        self.Id = Id
        self.StatName = StatName
        self.RequiredItemId = RequiredItemId
        self.RequiredTags = RequiredTags

class FarmAnimalsData(modelsData):
    def __init__(
        self, 
        key: str,
        DisplayName: str,
        House: str,
        Texture: str,
        Gender: Optional[str] = None,
        PurchasePrice: Optional[int] = None,
        ShopTexture: Optional[str] = None,
        ShopSourceRect: Optional[Rectangle] = None,
        RequiredBuilding: Optional[str] = None,
        UnlockCondition: Optional[str] = None,
        ShopDisplayName: Optional[str] = None,
        ShopDescription: Optional[str] = None,
        ShopMissingBuildingDescription: Optional[str] = None,
        AlternatePurchaseTypes: Optional[list[AlternatePurchaseTypes]] = None,
        EggItemIds: Optional[list[str]] = None,
        IncubationTime: Optional[int] = None,
        IncubatorParentSheetOffset: Optional[int] = None,
        BirthText: Optional[str] = None,
        DaysToMature: Optional[int] = None,
        CanGetPregnant: Optional[bool] = None,
        ProduceItemIds: Optional[list[ProduceItemIds]] = None,
        DeluxeProduceItemIds: Optional[list[ProduceItemIds]] = None,
        DaysToProduce: Optional[int] = None,
        ProduceOnMature: Optional[bool] = None,
        FriendshipForFasterProduce: Optional[int] = None,
        DeluxeProduceMinimumFriendship: Optional[int] = None,
        DeluxeProduceCareDivisor: Optional[float] = None,
        DeluxeProduceLuckMultiplier: Optional[float] = None,
        HarvestType: Optional[str] = None,
        HarvestTool: Optional[str] = None,
        CanEatGoldenCrackers: Optional[bool] = None,
        Sound: Optional[str] = None,
        BabySound: Optional[str] = None,
        HarvestedTexture: Optional[str] = None,
        BabyTexture: Optional[str] = None,
        UseFlippedRightForLeft: Optional[bool] = None,
        SpriteWidth: Optional[int] = None,
        SpriteHeight: Optional[int] = None,
        EmoteOffset: Optional[Position] = None,
        SwimOffset: Optional[Position] = None,
        Skins: Optional[list[AnimalSkin]] = None,
        SleepFrame: Optional[int] = None,
        UseDoubleUniqueAnimationFrames: Optional[bool] = None,
        ShadowWhenBaby: Optional[FarmAnimalShadowData] = None,
        ShadowWhenBabySwims: Optional[FarmAnimalShadowData] = None,
        ShadowWhenAdult: Optional[FarmAnimalShadowData] = None,
        ShadowWhenAdultSwims: Optional[FarmAnimalShadowData] = None,
        Shadow: Optional[FarmAnimalShadowData] = None,
        ProfessionForFasterProduce: Optional[int] = None,
        ProfessionForHappinessBoost: Optional[int] = None,
        ProfessionForQualityBoost: Optional[int] = None,
        CanSwim: Optional[bool] = None,
        BabiesFollowAdults: Optional[bool] = None,
        GrassEatAmount: Optional[int] = None,
        HappinessDrain: Optional[int] = None,
        SellPrice: Optional[int] = None,
        CustomFields: Optional[dict[str, str]] = None,
        ShowInSummitCredits: Optional[bool] = None,
        StatToIncrementOnProduce: Optional[list[StatToIncrementOnProduce]] = None,
        UpDownPetHitboxTileSize: Optional[Position] = None, #usar getStr()
        LeftRightPetHitboxTileSize: Optional[Position] = None, #usar getStr()
        BabyUpDownPetHitboxTileSize: Optional[Position] = None, #usar getStr()
        BabyLeftRightPetHitboxTileSize: Optional[Position] = None #usar getStr()
    ):
        super().__init__(key)
        self.DisplayName = DisplayName
        self.House = House
        self.Texture = Texture
        self.Gender = Gender
        self.PurchasePrice = PurchasePrice
        self.ShopTexture = ShopTexture
        self.ShopSourceRect = ShopSourceRect
        self.RequiredBuilding = RequiredBuilding
        self.UnlockCondition = UnlockCondition
        self.ShopDisplayName = ShopDisplayName
        self.ShopDescription = ShopDescription
        self.ShopMissingBuildingDescription = ShopMissingBuildingDescription
        self.AlternatePurchaseTypes = AlternatePurchaseTypes
        self.EggItemIds = EggItemIds
        self.IncubationTime = IncubationTime
        self.IncubatorParentSheetOffset = IncubatorParentSheetOffset
        self.BirthText = BirthText
        self.DaysToMature = DaysToMature
        self.CanGetPregnant = CanGetPregnant
        self.ProduceItemIds = ProduceItemIds
        self.DeluxeProduceItemIds = DeluxeProduceItemIds
        self.DaysToProduce = DaysToProduce
        self.ProduceOnMature = ProduceOnMature
        self.FriendshipForFasterProduce = FriendshipForFasterProduce
        self.DeluxeProduceMinimumFriendship = DeluxeProduceMinimumFriendship
        self.DeluxeProduceCareDivisor = DeluxeProduceCareDivisor
        self.DeluxeProduceLuckMultiplier = DeluxeProduceLuckMultiplier
        self.HarvestType = HarvestType
        self.HarvestTool = HarvestTool        
        self.CanEatGoldenCrackers = CanEatGoldenCrackers
        self.Sound = Sound
        self.BabySound = BabySound
        self.HarvestedTexture = HarvestedTexture
        self.BabyTexture = BabyTexture
        self.UseFlippedRightForLeft = UseFlippedRightForLeft
        self.SpriteWidth = SpriteWidth
        self.SpriteHeight = SpriteHeight
        self.EmoteOffset = EmoteOffset
        self.SwimOffset = SwimOffset
        self.Skins = Skins
        self.SleepFrame = SleepFrame
        self.UseDoubleUniqueAnimationFrames = UseDoubleUniqueAnimationFrames
        self.ShadowWhenBaby = ShadowWhenBaby
        self.ShadowWhenBabySwims = ShadowWhenBabySwims
        self.ShadowWhenAdult = ShadowWhenAdult
        self.ShadowWhenAdultSwims = ShadowWhenAdultSwims
        self.Shadow = Shadow
        self.ProfessionForFasterProduce = ProfessionForFasterProduce
        self.ProfessionForHappinessBoost = ProfessionForHappinessBoost
        self.ProfessionForQualityBoost = ProfessionForQualityBoost
        self.CanSwim = CanSwim
        self.BabiesFollowAdults = BabiesFollowAdults
        self.GrassEatAmount = GrassEatAmount
        self.HappinessDrain = HappinessDrain
        self.SellPrice = SellPrice
        self.CustomFields = CustomFields
        self.ShowInSummitCredits = ShowInSummitCredits
        self.StatToIncrementOnProduce = StatToIncrementOnProduce
        self.UpDownPetHitboxTileSize = UpDownPetHitboxTileSize
        self.LeftRightPetHitboxTileSize = LeftRightPetHitboxTileSize
        self.BabyUpDownPetHitboxTileSize = BabyUpDownPetHitboxTileSize
        self.BabyLeftRightPetHitboxTileSize = BabyLeftRightPetHitboxTileSize

