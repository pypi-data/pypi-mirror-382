from .model import modelsData
from typing import Optional


class NPCGiftTastesData(modelsData):
    def __init__(
        self,
        key: str,
        universal_ids: Optional[list[str]] = [],
        love_reaction_dialogue: Optional[str] = "",
        love_reference_ids: Optional[list[str]] = [],
        like_reaction_dialogue: Optional[str] = "",
        like_reference_ids: Optional[list[str]] = [],
        dislike_reaction_dialogue: Optional[str] = "",
        dislike_reference_ids: Optional[list[str]] = [],
        hate_reaction_dialogue: Optional[str] = "",
        hate_reference_ids: Optional[list[str]] = [],
        neutral_reaction_dialogue: Optional[str] = "",
        neutral_reference_ids: Optional[list[str]] = []
    ):
        super().__init__(key)
        self.universal_ids = universal_ids
        self.love_reaction_dialogue = love_reaction_dialogue
        self.love_reference_ids = love_reference_ids
        self.like_reaction_dialogue = like_reaction_dialogue
        self.like_reference_ids = like_reference_ids
        self.dislike_reaction_dialogue = dislike_reaction_dialogue
        self.dislike_reference_ids = dislike_reference_ids
        self.hate_reaction_dialogue = hate_reaction_dialogue
        self.hate_reference_ids = hate_reference_ids
        self.neutral_reaction_dialogue = neutral_reaction_dialogue
        self.neutral_reference_ids = neutral_reference_ids


    def getJson(self) -> str:
        if "Universal" in str(self.key):
            return f"{" ".join(self.universal_ids)}"
        else:
            return f"{self.love_reaction_dialogue}/{" ".join(self.love_reference_ids)}/{self.like_reaction_dialogue}/{" ".join(self.like_reference_ids)}/{self.dislike_reaction_dialogue}/{" ".join(self.dislike_reference_ids)}/{self.hate_reaction_dialogue}/{" ".join(self.hate_reference_ids)}/{self.neutral_reaction_dialogue}/{" ".join(self.neutral_reference_ids)}"
