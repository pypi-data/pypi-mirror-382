from .model import modelsData
from typing import Optional, Any
from .GameData import Season

class PassiveFestivalsData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        DisplayName: str,
        Season: Season,
        StartDay: int,
        EndDay: int,
        StartTime: int,
        StartMessage: str,
        MapReplacements: dict[str, str],
        Condition: Optional[str] = "",
        ShowOnCalendar: Optional[bool] = True,
        DailySetupMethod: Optional[str] = None,
        CleanupMethod: Optional[str] = None,
        CustomFields: Optional[dict[str, Any]] = None
    ):
        super().__init__(key)
        self.DisplayName = DisplayName
        self.Season = Season
        self.StartDay = StartDay
        self.EndDay = EndDay
        self.StartTime = StartTime
        self.StartMessage = StartMessage
        self.MapReplacements = MapReplacements
        self.Condition = Condition
        self.ShowOnCalendar = ShowOnCalendar
        self.DailySetupMethod = DailySetupMethod
        self.CleanupMethod = CleanupMethod
        self.CustomFields = CustomFields
