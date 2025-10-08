from .model import modelsData
from typing import Optional, Any
from .XNA import Position, Rectangle
from .GameData import CommonFields, ItemSpawnFields ,Season, QuantityModifiers, QualityModifierMode, MusicContext, Music

class CreateOnLoad(modelsData):
    def __init__(
        self,
        *,
        MapPath:str,
        AlwaysActive: Optional[bool] = False,
        Type: Optional[str] = None
    ):
        self.MapPath = MapPath
        self.AlwaysActive = AlwaysActive
        self.Type = Type

class ArtifactSpots(CommonFields):
    def __init__(
        self,
        CommonFields: ItemSpawnFields,
        Chance: Optional[float]=None,
        ApplyGenerousEnchantment: Optional[bool]=None,
        OneDebrisPerDrop: Optional[bool]=None,
        ContinueOnDrop: Optional[bool]=None,
        Precedence: Optional[int]=None        
    ):
        super().__init__(CommonFields=CommonFields)
        self.Chance = Chance
        self.ApplyGenerousEnchantment = ApplyGenerousEnchantment
        self.OneDebrisPerDrop = OneDebrisPerDrop
        self.ContinueOnDrop = ContinueOnDrop
        self.Precedence = Precedence

    

class FishAreas(modelsData):
    def __init__(
        self,
        DisplayName: Optional[str] = None,
        Position: Optional[Rectangle] = None,
        CrabPotFishTypes: Optional[list[str]] = None,
        CrabPotJunkChance: Optional[float] = None
    ):
        self.DisplayName = DisplayName
        self.Position = Position
        self.CrabPotFishTypes = CrabPotFishTypes
        self.CrabPotJunkChance = CrabPotJunkChance

class Fish(CommonFields):
    def __init__(
        self,
        CommonFields: ItemSpawnFields,
        Chance: Optional[float] = None,
        Season: Optional[Season] = None,
        FishAreaId: Optional[str] = None,
        BobberPosition: Optional[Rectangle] = None,
        PlayerPosition: Optional[Rectangle] = None,
        MinFishingLevel: Optional[int] = None,
        ApplyDailyLuck: Optional[bool] = None,
        CuriosityLureBuff: Optional[float] = None,
        SpecificBaitBuff: Optional[float] = None,
        SpecificBaitMultiplier: Optional[float] = None,
        CatchLimit: Optional[int] = None,
        CanUseTrainingRod: Optional[bool] = None,
        IsBossFish: Optional[bool] = None,
        RequireMagicBait: Optional[bool] = None,
        MinDistanceFromShore: Optional[int] = None,
        MaxDistanceFromShore: Optional[int] = None,
        Precedence: Optional[int] = None,
        IgnoreFishDataRequirements: Optional[bool] = None,
        CanBeInherited: Optional[bool] = None,
        SetFlagOnCatch: Optional[str] = None,
        ChanceModifiers: Optional[list[QuantityModifiers]] = None,
        ChanceModifierMode: Optional[QualityModifierMode] = None,
        ChanceBoostPerLuckLevel: Optional[float] = None,
        UseFishCaughtSeededRandom: Optional[bool] = None
    ):
        super().__init__(CommonFields=CommonFields)
        self.Chance = Chance
        self.Season = Season
        self.FishAreaId = FishAreaId
        self.BobberPosition = BobberPosition
        self.PlayerPosition = PlayerPosition
        self.MinFishingLevel = MinFishingLevel
        self.ApplyDailyLuck = ApplyDailyLuck
        self.CuriosityLureBuff = CuriosityLureBuff
        self.SpecificBaitBuff = SpecificBaitBuff
        self.SpecificBaitMultiplier = SpecificBaitMultiplier
        self.CatchLimit = CatchLimit
        self.CanUseTrainingRod = CanUseTrainingRod
        self.IsBossFish = IsBossFish
        self.RequireMagicBait = RequireMagicBait
        self.MinDistanceFromShore = MinDistanceFromShore
        self.MaxDistanceFromShore = MaxDistanceFromShore
        self.Precedence = Precedence
        self.IgnoreFishDataRequirements = IgnoreFishDataRequirements
        self.CanBeInherited = CanBeInherited
        self.SetFlagOnCatch = SetFlagOnCatch
        self.ChanceModifiers = ChanceModifiers
        self.ChanceModifierMode = ChanceModifierMode
        self.ChanceBoostPerLuckLevel = ChanceBoostPerLuckLevel
        self.UseFishCaughtSeededRandom = UseFishCaughtSeededRandom

class Forage(CommonFields):
    def __init__(
        self,
        CommonFields: ItemSpawnFields,
        Chance: Optional[float] = None,
        Season: Optional[Season] = None,
        
    ):
        super().__init__(CommonFields=CommonFields)
        self.Chance = Chance
        self.Season = Season


        

class LocationsData(modelsData):
    def __init__(
        self,
        key:str,
        DisplayName: Optional[str] = None,
        DefaultArrivalTile: Optional[Position] = None,
        CreateOnLoad: Optional[CreateOnLoad] = None,
        CanPlantHere: Optional[bool] = None,
        CanHaveGreenRainSpawns: Optional[bool] = None,
        ExcludeFromNpcPathfinding: Optional[bool] = None,
        ArtifactSpots: Optional[list[ArtifactSpots]] = None,
        FishAreas: Optional[dict[str, FishAreas]] = None,
        Fish: Optional[list[Fish]] = None,
        Forage: Optional[list[Forage]] = None,
        MinDailyWeeds: Optional[int] = None,
        MaxDailyWeeds: Optional[int] = None,
        FirstDayWeedMultiplier: Optional[int] = None,
        MinDailyForageSpawn: Optional[int] = None,
        MaxDailyForageSpawn: Optional[int] = None,
        MaxSpawnedForageAtOnce: Optional[int] = None,
        ChanceForClay: Optional[float] = None,
        Music: Optional[list[Music]] = None,
        MusicDefault: Optional[str] = None,
        MusicContext: Optional[MusicContext] = None,
        MusicIgnoredInRain: Optional[bool] = None,
        MusicIgnoredInSpring: Optional[bool] = None,
        MusicIgnoredInSummer: Optional[bool] = None,
        MusicIgnoredInFall: Optional[bool] = None,
        MusicIgnoredInWinter: Optional[bool] = None,
        MusicIgnoredInFallDebris: Optional[bool] = None,
        MusicIsTownTheme: Optional[bool] = None,
        CustomFields: Optional[dict[str, str]] = None,
        FormerLocationNames: Optional[list[str]] = None
    ):
        super().__init__(key)
        self.DisplayName = DisplayName
        self.DefaultArrivalTile = DefaultArrivalTile
        self.CreateOnLoad = CreateOnLoad
        self.CanPlantHere = CanPlantHere
        self.CanHaveGreenRainSpawns = CanHaveGreenRainSpawns
        self.ExcludeFromNpcPathfinding = ExcludeFromNpcPathfinding
        self.ArtifactSpots = ArtifactSpots
        self.FishAreas = FishAreas
        self.Fish = Fish
        self.Forage = Forage
        self.MinDailyWeeds = MinDailyWeeds
        self.MaxDailyWeeds = MaxDailyWeeds
        self.FirstDayWeedMultiplier = FirstDayWeedMultiplier
        self.MinDailyForageSpawn = MinDailyForageSpawn
        self.MaxDailyForageSpawn = MaxDailyForageSpawn
        self.MaxSpawnedForageAtOnce = MaxSpawnedForageAtOnce
        self.ChanceForClay = ChanceForClay
        self.Music = Music
        self.MusicDefault = MusicDefault
        self.MusicContext = MusicContext
        self.MusicIgnoredInRain = MusicIgnoredInRain
        self.MusicIgnoredInSpring = MusicIgnoredInSpring
        self.MusicIgnoredInSummer = MusicIgnoredInSummer
        self.MusicIgnoredInFall = MusicIgnoredInFall
        self.MusicIgnoredInWinter = MusicIgnoredInWinter
        self.MusicIgnoredInFallDebris = MusicIgnoredInFallDebris
        self.MusicIsTownTheme = MusicIsTownTheme
        self.CustomFields = CustomFields
        self.FormerLocationNames = FormerLocationNames