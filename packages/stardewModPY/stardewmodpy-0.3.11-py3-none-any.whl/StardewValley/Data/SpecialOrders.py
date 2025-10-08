from .model import modelsData
from typing import Optional, Any
from .GameData import Duration, Season, ObjectivesTypes


class ObjectivesData(modelsData):
    def __init__(
        self,
        Type: ObjectivesTypes,
        Text: str,
        RequiredCount: str,
        Data: dict[str, str]
    ):
        self.Type = Type
        self.Text = Text
        self.RequiredCount = RequiredCount
        self.Data = Data

class FriendShip(modelsData):
    def __init__(
        self,
        Amount:int,
        TargetName:str
    ):
        self.Amount = f"{Amount}"
        self.TargetName = TargetName

class Gems(modelsData):
    def __init__(
        self,
        Amount:int
    ):
        self.Amount = f"{Amount}"
    
class Mails(modelsData):
    def __init__(
        self,
        MailReceived:str,
        NoLetters:bool,
        Host:bool
    ):
        self.MailReceived = f"{MailReceived}"
        self.NoLetters = str(NoLetters).lower()
        self.Host = str(Host).lower()

class Money(modelsData):
    def __init__(
        self,
        Amount:int|str,
        Multiplayer:Optional[int]=None
    ):
        self.Amount = f"{Amount}"
        if Multiplayer is not None:
            self.Multiplayer = f"{Multiplayer}"

class ResetEvent(modelsData):
    def __init__(
        self,
        ResetEvents:list[str]
    ):
        self.EventName = " ".join(ResetEvents)
        

class RewardsData(modelsData):
    def __init__(
        self,
        Type: FriendShip|Gems|Mails|Money|ResetEvent
    ):
        self.Type = Type.__class__.__name__
        self.Data = Type.getJson()
    
    


class RequiredTags(modelsData):
    def __init__(self):
        self.tags = []

    def season(self, value: Season, negate: bool):
        prefix = "!" if negate else ""
        self.tags.append(f"{prefix}season_{value.getJson().lower()}")

    def event(self, value: str, negate: bool):
        prefix = "!" if negate else ""
        self.tags.append(f"{prefix}event_{value}")

    def mail(self, value: str, negate: bool):
        prefix = "!" if negate else ""
        self.tags.append(f"{prefix}mail_{value}")

    def rule(self, value: str, negate: bool):
        prefix = "!" if negate else ""
        self.tags.append(f"{prefix}rule_{value}")

    def dropbox(self, value: str, negate: bool):
        prefix = "!" if negate else ""
        self.tags.append(f"{prefix}dropbox_{value}")

    def island(self, negate: bool):
        prefix = "!" if negate else ""
        self.tags.append(f"{prefix}island")

    def knows(self, npc_name: str, negate: bool):
        prefix = "!" if negate else ""
        self.tags.append(f"{prefix}knows_{npc_name}")

    def NOT_IMPLEMENTED(self):
        self.tags.append("NOT_IMPLEMENTED")

    def getJson(self) -> str:
        return ", ".join(self.tags)


class RequiredTagsValueModel(modelsData):
    def __init__(self):
        self.value = ""

    def getJson(self) -> str:
        return self.value

class RequiredElementsValue(RequiredTagsValueModel):
    class PICK_ITEM(RequiredTagsValueModel):
        def __init__(self, Items: list[str]):
            self.value = f"PICK_ITEM {', '.join(Items)}"
    
    class Text(RequiredTagsValueModel):
        def __init__(self, Text: str, Tags: str):
            self.value = f"TEXT|{Text}|Tags|{Tags}"
    
    class Target(RequiredTagsValueModel):
        def __init__(self, Target: str, LocalizedName: str):
            self.value = f"TARGET|{Target}|LocalizedName|{LocalizedName}"
    
    class SimpleSetting(RequiredTagsValueModel):
        def __init__(self, Setting: str):
            self.value = f"[{Setting}]"


class RandomizeElementsValues(modelsData):
    def __init__(
        self,
        RequiredTags: RequiredTags,
        Value: RequiredElementsValue.PICK_ITEM|RequiredElementsValue.Text|RequiredElementsValue.Target|RequiredElementsValue.SimpleSetting
    ):
        self.RequiredTags = RequiredTags
        self.Value = Value



class RandomizeElementsData(modelsData):
    def __init__(
        self,
        Name: str,
        Values: list[RandomizeElementsValues]
    ):
        self.Name = Name
        self.Values = Values


class SpecialOrdersData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Name:str,
        Requester: str,
        Duration: Duration,
        Repeatable: bool,
        Text: str,
        Objectives: list[ObjectivesData],
        Rewards: list[RewardsData],
        RequiredTags: Optional[RequiredTags|str]="",
        OrderType: Optional[str]="",
        SpecialRule: Optional[str]="",
        ItemToRemoveOnEnd: Optional[str] = None,
        MailToRemoveOnEnd: Optional[str] = None,
        RandomizedElements: list[RandomizeElementsData] = None,
        CustomFields: Optional[Any] = None
    ):
        super().__init__(key)
        self.Name = Name
        self.Requester = Requester
        self.Duration = Duration
        self.Repeatable = Repeatable
        self.RequiredTags = RequiredTags
        self.OrderType = OrderType
        self.SpecialRule = SpecialRule
        self.Text = Text
        self.Objectives = Objectives
        self.Rewards = Rewards
        self.ItemToRemoveOnEnd = ItemToRemoveOnEnd
        self.MailToRemoveOnEnd = MailToRemoveOnEnd
        self.RandomizedElements = RandomizedElements
        self.CustomFields = CustomFields
