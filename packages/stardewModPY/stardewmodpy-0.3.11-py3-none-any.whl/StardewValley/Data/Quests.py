from .model import modelsData
from typing import Optional, Any
from .GameData import QuestTypes


class QuestsData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Type: QuestTypes,
        Title: str,
        Description: str,
        Objective_Hint: Optional[str] = "",
        Completion_Requirements: Optional[str] = None,
        Next_Quest_Ids: Optional[int] = -1,
        Money_Reward: int = 0,
        Reward_Description: Optional[int] = -1,
        Can_Be_Cancelled: Optional[bool] = False,
        Reaction_Text: Optional[str] = None
    ):
        super().__init__(key)
        self.value = f"{Type}/{Title}" if Type != "SecretLostItem" else f"{Type}/..."

        if Type != "Building":
            if Type == "SecretLostItem":
                self.value += "/..."

            elif Type == "Social":
                self.value += "/."

            else:
                self.value += f"/{Description}"

        if Type != "ItemHarvest":
            self.value += f"/{Objective_Hint}" if Type != "SecretLostItem" else f"/..."

        if not Type in ("Monster", "Location"):
            self.value += f"/{Completion_Requirements}"

        self.value += f"/{Next_Quest_Ids}/{Money_Reward}/{Reward_Description}/{str(Can_Be_Cancelled).lower()}"

        if Type in ("SecretLostItem", "LostItem", "ItemDelivery"):
            self.value += f"/{Reaction_Text}"


# ID: Type/Title/Description/Hint/Requirement/Next Quests/Money Reward/-1/Cancellable/Reaction Text

# Basic: 0 - 1 - 2 - 3 - 4 (Nulo) - 5 - 6 - 7 - 8
# Fishing: 0 - 1 - 2 - 3 - 4 (-1) - 5 - 6 - 7 - 8

# Crafting: 0 - 1 - 2 - 3 - 4 - 5 - 6 - 7 - 8

# SecretLostItem: 0 - 1 (...) - 2 (...) - 3 (...) - 4 - 5 - 6 - 7 - 8 - 9
# LostItem: 0 - 1 - 2 - 3 - 4 - 5 - 6 - 7 - 8 - 9
# ItemDelivery: 0 - 1 - 2 - 3 - 4 - 5 - 6 - 7 - 8 - 9


# Building: 0 - 1 - 3 - 4 - 5 - 6 - 7 - 8

# ItemHarvest: 0 - 1 - 2 - 4 - 5 - 6 - 7 - 8

# Monster: 0 - 1 - 2 - 3 - 5 - 6 - 7 - 8
# Location: 0 - 1 - 2 - 3 - 5 - 6 - 7 - 8


    def getJson(self) -> str:
        return f"{self.Type}/{self.Title}/{self.Description}/{self.Objective_Hint}/{self.Completion_Requirements}"
