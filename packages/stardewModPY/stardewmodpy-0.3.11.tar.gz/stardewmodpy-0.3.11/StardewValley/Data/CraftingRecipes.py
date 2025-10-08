from .model import modelsData
from typing import Optional


class CraftingRecipesData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Ingredients: str,
        Yield: str,
        BigCraftable: bool,
        UnlockConditions: Optional[str] = "null",
        DisplayName: Optional[str] = ""
    ):
        super().__init__(key)
        self.Ingredients = Ingredients
        self.Yield = Yield
        self.BigCraftable = BigCraftable
        self.UnlockConditions = UnlockConditions
        self.DisplayName = DisplayName


    def getJson(self) -> str:
        return f"{self.Ingredients}/Field/{self.Yield}/{self.BigCraftable}/{self.UnlockConditions}/{self.DisplayName}"
