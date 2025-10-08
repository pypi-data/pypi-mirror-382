from .model import modelsData
from .XNA import Position, Rectangle
from typing import Optional, Any
from .GameData import Season, HomeRegion, Manner, SocialAnxiety, Optimism, Calendar, Gender, SocialTab, EndSlideShow, Direction


class SpouseRoom:
    def __init__(self, MapAsset:str, MapSourceRect:Rectangle):
        self.MapAsset=MapAsset
        self.MapSourceRect=MapSourceRect
    def getJson(self) -> dict:
        return {
            "MapAsset": self.MapAsset,
            "MapSourceRect": self.MapSourceRect.getJson()
        }

class SpousePatio(SpouseRoom):
    def __init__(
        self,
        MapAsset:str,
        MapSourceRect:Rectangle,
        SpriteAnimationFrames:list[list[int]],
        SpriteAnimationPixelOffset:Position

    ):
        super().__init__(MapAsset, MapSourceRect)
        self.SpriteAnimationFrames=SpriteAnimationFrames
        self.SpriteAnimationPixelOffset=SpriteAnimationPixelOffset
    
    def getJson(self) -> dict:
        json = super().getJson()  # Obtém o dicionário da classe pai
        json.update({
            "SpriteAnimationFrames": self.SpriteAnimationFrames,
            "SpriteAnimationPixelOffset": self.SpriteAnimationPixelOffset.getJson()
        })
        return json

class WinterStarGifts(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        ItemId:str,
        MinStack:int,
        MaxStack:int,
        Quality:int,
        ToolUpgradeLevel:int=-1,
        IsRecipe:bool=False,
        StackModifierMode:str="Stack",
        QualityModifierMode:str="Stack",

        Condition:Optional[str]=None,
        RandomItemId:Optional[list[str]]=None,
        MaxItems:Optional[int]=None,

        ObjectInternalName:Optional[str]=None,
        ObjectDisplayName:Optional[str]=None,
        ObjectColor:Optional[str]=None,
        StackModifiers:Optional[Any]=None,
        QualityModifiers:Optional[Any]=None,

        ModData:Optional[dict[str, Any]]=None,
        PerItemCondition:Optional[Any]=None,
    ):
        self.Id=Id
        self.ItemId=ItemId
        self.MinStack=MinStack
        self.MaxStack=MaxStack
        self.Quality=Quality
        self.ObjectInternalName=ObjectInternalName
        self.ObjectDisplayName=ObjectDisplayName
        self.ObjectColor=ObjectColor
        self.ToolUpgradeLevel=ToolUpgradeLevel
        self.IsRecipe=IsRecipe
        self.StackModifiers=StackModifiers
        self.StackModifierMode=StackModifierMode
        self.QualityModifiers=QualityModifiers
        self.QualityModifierMode=QualityModifierMode
        self.ModData=ModData
        self.PerItemCondition=PerItemCondition
        self.Condition=Condition
        self.MaxItems=MaxItems
        self.RandomItemId=RandomItemId
    

class Home(modelsData):
    def __init__( 
        self,
        Id:str,
        Tile:Position,
        Direction:Direction,
        Location:Optional[str]=None,
        Condition:Optional[str]=None
    ):
        self.Id=Id
        self.Tile=Tile
        self.Direction=Direction.lower()
        self.Location=Location
        self.Condition=Condition

        

class Appearance(modelsData):
    def __init__(
        self,
        Id:str,
        Season:Optional[Season]=None,
        Indoors:Optional[bool]=None,
        Outdoors:Optional[bool]=None,
        Condition:Optional[str]=None,
        Portrait:Optional[str]=None,
        Sprite:Optional[str]=None,
        IsIslandAttire:Optional[bool]=None,
        Precedence:Optional[int]=None,
        Weight:Optional[int]=None

    ):
        self.Id=Id
        self.Season=Season.lower()
        self.Indoors=Indoors
        self.Outdoors=Outdoors
        self.Condition=Condition
        self.Portrait=Portrait
        self.Sprite=Sprite
        self.IsIslandAttire=IsIslandAttire
        self.Precedence=Precedence
        self.Weight=Weight

class CharactersData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        DisplayName: str,
        Language: Optional[str] = None,
        Gender: Optional[Gender] = None,
        Age: Optional[str] = None,
        Manner: Optional[Manner] = None,
        SocialAnxiety: Optional[SocialAnxiety] = None,
        Optimism: Optional[Optimism] = None,
        BirthDay: Optional[int] = None,
        BirthSeason: Optional[Season]=None,
        HomeRegion: Optional[HomeRegion]=None,
        IsDarkSkinned: Optional[bool] = None,
        CanSocialize: Optional[str] = None,
        CanBeRomanced: Optional[bool] = None,
        CanReceiveGifts: Optional[bool] = None,
        CanCommentOnPurchasedShopItems: Optional[bool] = None,
        CanGreetNearbyCharacters: Optional[bool] = None,
        CanVisitIsland: Optional[str] = None,
        LoveInterest: Optional[str] = None,
        Calendar: Optional[Calendar] = None,
        SocialTab: Optional[SocialTab] = None,
        SpouseAdopts: Optional[str] = None,
        SpouseWantsChildren: Optional[str] = None,
        SpouseGiftJealousy: Optional[str] = None,
        SpouseGiftJealousyFriendshipChange: Optional[int] = None,
        SpouseRoom: Optional[SpouseRoom] = None,
        SpousePatio: Optional[SpousePatio] = None,
        SpouseFloors: Optional[list[str]] = None,
        SpouseWallpapers: Optional[list[str]] = None,
        IntroductionsQuest: Optional[bool] = None,
        ItemDeliveryQuests: Optional[str] = None,
        PerfectionScore: Optional[bool] = None,
        EndSlideShow: Optional[EndSlideShow] = None,
        FriendsAndFamily: Optional[dict[str, str]] = None,
        DumpsterDiveEmote: Optional[int] = None,
        DumpsterDiveFriendshipEffect: Optional[int] = None,
        FlowerDanceCanDance: Optional[bool] = None,
        WinterStarParticipant: Optional[str] = None,
        WinterStarGifts: Optional[list[WinterStarGifts]] = None,
        UnlockConditions: Optional[str] = None,
        SpawnIfMissing: Optional[bool] = None,        
        Home: Optional[list[Home]] = None,
        TextureName: Optional[str] = None,
        Appearance: Optional[list[Appearance]] = None,
        MugShotSourceRect: Optional[Rectangle] = None,
        Size: Optional[Position] = None,
        Breather: Optional[bool] = True,
        BreathChestRect: Optional[Rectangle] = None,
        BreathChestPosition: Optional[Position] = None,
        Shadow: Optional[Position] = None,
        EmoteOffset: Optional[Position] = None,

        ShakePortraits: Optional[list[int]] = None,
        KissSpriteIndex: Optional[int] = None,
        KissSpriteFacingRight: Optional[bool] = None,

        HiddenProfileEmoteSound: Optional[str] = None,
        HiddenProfileEmoteDuration: Optional[int] = None,
        HiddenProfileEmoteStartFrame: Optional[int] = None,
        HiddenProfileEmoteFrameCount: Optional[int] = None,
        HiddenProfileEmoteFrameDuration: Optional[float] = None,
        FormerCharacterNames: Optional[list[str]] = None,
        FestivalVanillaActorIndex: Optional[int] = None,
        CustomFields: Optional[dict[str,str]] = None
    ):
        super().__init__(key)
        self.DisplayName = DisplayName
        self.FriendsAndFamily = FriendsAndFamily
        self.Language = Language
        self.Gender = Gender
        self.Age = Age
        self.Manner = Manner
        self.SocialAnxiety = SocialAnxiety
        self.Optimism = Optimism
        self.BirthDay = BirthDay
        self.BirthSeason = BirthSeason.lower()
        self.HomeRegion = HomeRegion
        self.IsDarkSkinned = IsDarkSkinned
        self.CanSocialize = CanSocialize
        self.CanBeRomanced = CanBeRomanced
        self.CanReceiveGifts = CanReceiveGifts
        self.CanCommentOnPurchasedShopItems = CanCommentOnPurchasedShopItems
        self.CanGreetNearbyCharacters = CanGreetNearbyCharacters
        self.CanVisitIsland = CanVisitIsland
        self.LoveInterest = LoveInterest
        self.Calendar = Calendar
        self.SocialTab = SocialTab
        self.SpouseAdopts = SpouseAdopts
        self.SpouseWantsChildren = SpouseWantsChildren
        self.SpouseGiftJealousy = SpouseGiftJealousy
        self.SpouseGiftJealousyFriendshipChange = SpouseGiftJealousyFriendshipChange
        self.SpouseRoom = SpouseRoom
        self.SpousePatio = SpousePatio
        self.SpouseFloors = SpouseFloors
        self.SpouseWallpapers = SpouseWallpapers
        self.IntroductionsQuest = IntroductionsQuest
        self.ItemDeliveryQuests = ItemDeliveryQuests
        self.PerfectionScore = PerfectionScore
        self.EndSlideShow = EndSlideShow
        self.DumpsterDiveEmote = DumpsterDiveEmote
        self.DumpsterDiveFriendshipEffect = DumpsterDiveFriendshipEffect
        self.FlowerDanceCanDance = FlowerDanceCanDance
        self.WinterStarParticipant = WinterStarParticipant
        self.WinterStarGifts = WinterStarGifts
        self.UnlockConditions = UnlockConditions
        self.SpawnIfMissing = SpawnIfMissing
        self.Home = Home
        self.TextureName = TextureName
        self.Appearance = Appearance
        self.MugShotSourceRect = MugShotSourceRect
        self.Size = Size
        self.Breather = Breather
        self.BreathChestRect = BreathChestRect
        self.BreathChestPosition = BreathChestPosition        
        self.Shadow = Shadow
        self.EmoteOffset = EmoteOffset
        self.ShakePortraits = ShakePortraits
        self.KissSpriteIndex = KissSpriteIndex
        self.KissSpriteFacingRight = KissSpriteFacingRight
        self.HiddenProfileEmoteSound = HiddenProfileEmoteSound
        self.HiddenProfileEmoteDuration = HiddenProfileEmoteDuration
        self.HiddenProfileEmoteStartFrame = HiddenProfileEmoteStartFrame
        self.HiddenProfileEmoteFrameCount = HiddenProfileEmoteFrameCount
        self.HiddenProfileEmoteFrameDuration = HiddenProfileEmoteFrameDuration
        self.FormerCharacterNames = FormerCharacterNames
        self.FestivalVanillaActorIndex = FestivalVanillaActorIndex
        self.CustomFields = CustomFields


    
