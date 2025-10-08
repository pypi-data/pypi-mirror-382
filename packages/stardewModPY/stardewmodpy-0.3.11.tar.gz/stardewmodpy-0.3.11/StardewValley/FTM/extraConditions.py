from ..Data.model import modelsData
from .GameData import Seasons

from typing import Optional, Any

class ExtraConditions(modelsData):
    def __init__(
        self,
        *,
        Years:list[str]=None,
        Seasons:list[Seasons]=None,
        Days:list[str]=None,
        WeatherYesterday:list[str]=None,
        WeatherToday:list[str]=None,
        WeatherTomorrow:list[str]=None,
        GameStateQueries:list[str]=None,
        CPConditions:dict[str, str]=None,
        EPUPreconditions:list[str]=None,
        LimitedNumberOfSpawns:Optional[int]=None
    ):
        self.Years=Years        
        self.Seasons=Seasons
        self.Days=Days
        self.WeatherYesterday=WeatherYesterday
        self.WeatherToday=WeatherToday
        self.WeatherTomorrow=WeatherTomorrow
        self.GameStateQueries=GameStateQueries
        self.CPConditions=CPConditions
        self.EPUPreconditions=EPUPreconditions
        self.LimitedNumberOfSpawns=LimitedNumberOfSpawns