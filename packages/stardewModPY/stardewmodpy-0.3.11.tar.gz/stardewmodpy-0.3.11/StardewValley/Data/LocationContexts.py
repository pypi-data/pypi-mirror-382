from .model import modelsData
from typing import Optional, Any
from .GameData import Music

class PassOutMail(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Mail: str,
        MaxPassOutCost: Optional[int] = None,
        Condition: Optional[str] = None,
        SkipRandomSelection: Optional[bool] = None
    ):
        self.Id = Id
        self.Mail = Mail
        self.MaxPassOutCost = MaxPassOutCost
        self.Condition = Condition
        self.SkipRandomSelection = SkipRandomSelection

class PassOutLocations(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Location: str,
        Position: dict[str, int],
        Condition: Optional[str] = None
    ):
        self.Id = Id
        self.Location = Location
        self.Position = Position
        self.Condition = Condition

class WeatherConditions(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Condition: Optional[str] = None,
        Weather: str
    ):
        self.Id = Id
        self.Condition = Condition
        self.Weather = Weather


        
class LocationContextsData(modelsData):
    def __init__(
        self,
        key: str,
        *,
        AllowRainTotem: Optional[bool] = None,
        RainTotemAffectsContext: Optional[str] = None,
        MaxPassOutCost: Optional[int] = None,
        PassOutMail: Optional[list[PassOutMail]] = None,
        PassOutLocations: Optional[list[PassOutLocations]] = None,
        ReviveLocations: Optional[list[PassOutLocations]] = None,
        SeasonOverride: Optional[str] = None,
        WeatherConditions: Optional[list[WeatherConditions]] = None,
        CopyWeatherFromLocation: Optional[str] = None,
        DefaultMusic: Optional[str] = None,
        DefaultMusicCondition: Optional[str] = None,
        DefaultMusicDelayOneScreen: Optional[bool] = None,
        Music: Optional[list[Music]] = None,
        DayAmbience: Optional[str] = None,
        NightAmbience: Optional[str] = None,
        PlayRandomAmbientSounds: Optional[bool] = True,
        CustomFields: Optional[dict[str, str]] = None
    ):
        super().__init__(key)
        self.AllowRainTotem = AllowRainTotem
        self.RainTotemAffectsContext = RainTotemAffectsContext
        self.MaxPassOutCost = MaxPassOutCost
        self.PassOutMail = PassOutMail
        self.PassOutLocations = PassOutLocations
        self.ReviveLocations = ReviveLocations
        self.SeasonOverride = SeasonOverride
        self.WeatherConditions = WeatherConditions
        self.CopyWeatherFromLocation = CopyWeatherFromLocation
        self.DefaultMusic = DefaultMusic
        self.DefaultMusicCondition = DefaultMusicCondition
        self.DefaultMusicDelayOneScreen = DefaultMusicDelayOneScreen
        self.Music = Music
        self.DayAmbience = DayAmbience
        self.NightAmbience = NightAmbience
        self.PlayRandomAmbientSounds = PlayRandomAmbientSounds
        self.CustomFields = CustomFields
