from .model import modelsData
from .Events import Eventscripts

class Responses(modelsData):
    def __init__(
        self,
        *,
        ResponsePoint: str,
        Script: Eventscripts,
        Text: str,
    ):
        self.ResponsePoint = ResponsePoint
        self.Script = Script
        self.Text = Text

class SpecialResponses(modelsData):
    def __init__(
        self,
        *,
        BeforeMovie: Responses,
        DuringMovie: Responses,
        AfterMovie: Responses
    ):
        self.BeforeMovie = BeforeMovie
        self.DuringMovie = DuringMovie
        self.AfterMovie = AfterMovie
        
class ReactionData(modelsData):
    def __init__(
        self,
        *,
        Tag: str,
        Response: str,
        Whitelist: list[str],
        SpecialResponses: SpecialResponses,
        Id: str
    ):
        self.Tag = Tag
        self.Response = Response
        self.Whitelist = Whitelist
        self.SpecialResponses = SpecialResponses
        self.Id = Id


class MoviesReactionsData(modelsData):
    def __init__(
        self,
        *,
        NPCName: str,
        Reactions: list[ReactionData]
    ):
        super().__init__(None)
        self.NPCName = NPCName
        self.Reactions = Reactions
