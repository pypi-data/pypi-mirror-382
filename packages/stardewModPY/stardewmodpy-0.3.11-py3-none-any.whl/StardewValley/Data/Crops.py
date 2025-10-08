from .model import modelsData
from typing import Optional, Any

class PlantableLocationRules(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Result: str="Default",
        Condition: Optional[str] = None,
        PlantedIn: Optional[str] = None,
        DeniedMessage: Optional[str] = None
    ):
        self.Id = Id
        self.Result = Result
        self.Condition = Condition
        self.PlantedIn = PlantedIn
        self.DeniedMessage = DeniedMessage


class CropsData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Seasons: list[str],
        DaysInPhase: list[int],
        HarvestItemId: str,
        Texture: str,

        RegrowDays: Optional[int] = None,
        IsRaised: Optional[bool] = None,
        IsPaddyCrop: Optional[bool] = None,
        NeedsWatering: Optional[bool] = None,        
        HarvestMethod: Optional[str] = None,
        HarvestMinStack: Optional[int] = None,
        HarvestMaxStack: Optional[int] = None,
        HarvestMinQuality: Optional[int] = None,
        HarvestMaxQuality: Optional[int] = None,
        HarvestMaxIncreasePerFarmingLevel: Optional[float] = None,
        ExtraHarvestChance: Optional[float] = None,
        SpriteIndex: Optional[int] = None,
        TintColors: Optional[list[str]] = None,
        CountForMonoculture: Optional[bool] = None,
        CountForPolyculture: Optional[bool] = None,
        PlantableLocationRules: Optional[list[PlantableLocationRules]] = None,
        CustomFields: Optional[dict[str, str]] = None
    ):
        super().__init__(key)
        self.Seasons = Seasons
        self.DaysInPhase = DaysInPhase
        self.HarvestItemId = HarvestItemId
        self.Texture = Texture

        self.RegrowDays = RegrowDays
        self.IsRaised = IsRaised
        self.IsPaddyCrop = IsPaddyCrop
        self.NeedsWatering = NeedsWatering
        self.HarvestMethod = HarvestMethod
        self.HarvestMinStack = HarvestMinStack
        self.HarvestMaxStack = HarvestMaxStack
        self.HarvestMinQuality = HarvestMinQuality
        self.HarvestMaxQuality = HarvestMaxQuality
        self.HarvestMaxIncreasePerFarmingLevel = HarvestMaxIncreasePerFarmingLevel
        self.ExtraHarvestChance = ExtraHarvestChance
        self.SpriteIndex = SpriteIndex
        self.TintColors = TintColors
        self.CountForMonoculture = CountForMonoculture
        self.CountForPolyculture = CountForPolyculture        
        self.PlantableLocationRules = PlantableLocationRules
        self.CustomFields = CustomFields

