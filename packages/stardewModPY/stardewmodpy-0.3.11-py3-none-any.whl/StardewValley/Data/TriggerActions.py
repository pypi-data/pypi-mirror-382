from .model import modelsData
from typing import Any, Optional, List
from .GameData import  Trigger, mailType

class Actions:
    """
Use: Actions().Action(options)
    """
    def __init__(self):
        pass

    def AddBuff(self, buffID: str, duration: int = None):
        return f"AddBuff {buffID}" + (f" {duration}" if duration is not None else "")

    def RemoveBuff(self, buffID: str):
        return f"RemoveBuff {buffID}"

    def AddConversationTopic(self, topicID: str, dayDuration: int = 0):
        return f"AddConversationTopic {topicID} {dayDuration}"

    def RemoveConversationTopic(self, topicID: str):
        return f"RemoveConversationTopic {topicID}"

    def AddFriendshipPoints(self, npcName: str, count: int):
        return f"AddFriendshipPoints {npcName} {count}"

    def AddItem(self, itemID: str, count: int = 1, quality: int = 0):
        return f"AddItem {itemID} {count} {quality}"

    def RemoveItem(self, itemID: str, count: int = 1):
        return f"RemoveItem {itemID} {count}"

    def AddMail(self, player: str, mailID: str, mailType: mailType):
        return f"AddMail {player} {mailID} {mailType.getJson()}"

    def RemoveMail(self, player: str, mailID: str, mailType: mailType):
        return f"RemoveMail {player} {mailID} {mailType.getJson()}"

    def AddMoney(self, amount: int):
        return f"AddMoney {amount}"

    def AddQuest(self, questID: str):
        return f"AddQuest {questID}"

    def RemoveQuest(self, questID: str):
        return f"RemoveQuest {questID}"

    def AddSpecialOrder(self, orderID: str):
        return f"AddSpecialOrder {orderID}"

    def RemoveSpecialOrder(self, orderID: str):
        return f"RemoveSpecialOrder {orderID}"

    def ConditionQuery(self, query: str, action_if_true: str, action_false: str = None):
        if action_false:
            return f"If {query} ## {action_if_true} ## {action_false}"
        return f"If {query} ## {action_if_true}"

    def IncrementStat(self, statKey: str, amount: int = 1):
        return f"IncrementStat {statKey} {amount}"

    def MarkActionApplied(self, player: str, answerID: str, applied: bool = True):
        return f"MarkActionApplied {player} {answerID} {str(applied).lower()}"

    def MarkCookingRecipeKnown(self, player: str, recipeID: str, known: bool = True):
        return f"MarkCookingRecipeKnown {player} {recipeID} {str(known).lower()}"

    def MarkCraftingRecipeKnown(self, player: str, recipeKey: str, known: bool = True):
        return f"MarkCraftingRecipeKnown {player} {recipeKey} {str(known).lower()}"

    def MarkEventSeen(self, player: str, eventID: str, seen: bool = True):
        return f"MarkEventSeen {player} {eventID} {str(seen).lower()}"

    def MarkQuestionAnswered(self, player: str, answerID: str, answered: bool = True):
        return f"MarkQuestionAnswered {player} {answerID} {str(answered).lower()}"

    def MarkSongHeard(self, player: str, songID: str, heard: bool = True):
        return f"MarkSongHeard {player} {songID} {str(heard).lower()}"

    def Null(self):
        return "Null"

    def RemoveTemporaryAnimatedSprites(self):
        return "RemoveTemporaryAnimatedSprites"

    def SetNpcInvisible(self, npc: str, days: int):
        return f"SetNpcInvisible {npc} {days}"

    def SetNpcVisible(self, npc: str):
        return f"SetNpcVisible {npc}"

    
    

class TriggerActionsData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Id: str,
        Trigger: Trigger,
        
        Actions: Optional[List[Actions]] = None,
        Action: Optional[Actions] = None,
        HostOnly: Optional[bool] = None,
        Condition: Optional[str] = None,
        MarkActionApplied: Optional[bool] = None,
        SkipPermanentlyCondition: Optional[str] = None,
        CustomFields: Optional[dict[str,Any]] = None,
    ):
        super().__init__(key)

        if Actions is not None:
            if not isinstance(Actions, list):
                raise TypeError(f"'Actions' must be a list of strings, not a list of  of the class {type(Actions).__name__}")
            if not all(isinstance(a, str) for a in Actions):
                tipos_errados = [type(a).__name__ for a in Actions if not isinstance(a, str)]
                raise TypeError(f"'Actions' must be a list of strings, not a list of  of the class {type(Actions).__name__}")
            

        self.Id = Id
        self.Trigger = Trigger
        self.Actions = Actions
        self.Action = Action
        self.HostOnly = HostOnly
        self.Condition = Condition
        self.MarkActionApplied = MarkActionApplied
        self.SkipPermanentlyCondition = SkipPermanentlyCondition
        self.CustomFields = CustomFields
