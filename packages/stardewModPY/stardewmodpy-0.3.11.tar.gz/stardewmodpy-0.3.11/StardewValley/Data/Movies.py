from .model import modelsData
from typing import Optional, Any
from .GameData import Season, CommonFields, ItemSpawnFields


class CranePrizesData(CommonFields):
    def __init__(
        self,
        *,
        CommonFields: ItemSpawnFields,
        Rarity: Optional[int] = None
    ):
        super().__init__(CommonFields=CommonFields)
        self.Rarity = Rarity


class ScenesData(modelsData):
    def __init__(
        self,
        *,
        Image: int,
        Music: str,
        Sound: str,
        MessageDelay: int,
        Script: str,
        Text: str,
        Shake: bool,
        ResponsePoint: str | None,
        ID: str
    ):
        super().__init__(None)
        self.Image = Image
        self.Music = Music
        self.Sound = Sound
        self.MessageDelay = MessageDelay
        self.Script = Script
        self.Text = Text
        self.Shake = Shake
        self.ResponsePoint = ResponsePoint
        self.ID = ID



class MoviesData(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        SheetIndex: int,
        Title: str,
        Description: str,
        Tags: list[str],
        Scenes: list[ScenesData],
        Seasons: Optional[list[Season]] = None,
        YearModulus: Optional[int] = None,
        YearRemainder: Optional[int] = None,
        Texture: Optional[str] = None,
        CranePrizes: Optional[list[CranePrizesData]] = None,
        ClearDefaultCranePrizeGroups: list[int] = None,
        CustomFields: Optional[dict[str, Any]] = None
    ):
        super().__init__(None)
        self.Id = Id
        self.SheetIndex = SheetIndex
        self.Title = Title
        self.Description = Description
        self.Tags = Tags
        self.Scenes = Scenes
        self.Seasons = Seasons
        self.YearModulus = YearModulus
        self.YearRemainder = YearRemainder
        self.Texture = Texture
        self.CranePrizes = CranePrizes
        self.ClearDefaultCranePrizeGroups = ClearDefaultCranePrizeGroups
        self.CustomFields = CustomFields
