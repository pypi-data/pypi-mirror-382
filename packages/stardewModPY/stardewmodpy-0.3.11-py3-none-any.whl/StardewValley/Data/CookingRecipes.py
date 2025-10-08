from .model import modelsData
from typing import Optional


class CookingRecipesData(modelsData):
    def __init__(
        self,
        key: str,
        Ingredients: str,
        Yield: str,
        Unlock_conditions: Optional[str] = "default",
        Display_name: Optional[str] = ""
    ):
        super().__init__(key)
        self.Ingredients = Ingredients
        self.Yield = Yield
        self.Unlock_conditions = Unlock_conditions
        self.Display_name = Display_name


    def getJson(self) -> str:
        return f"{self.Ingredients}/10 10/{self.Yield}/{self.Unlock_conditions}/{self.Display_name}"
