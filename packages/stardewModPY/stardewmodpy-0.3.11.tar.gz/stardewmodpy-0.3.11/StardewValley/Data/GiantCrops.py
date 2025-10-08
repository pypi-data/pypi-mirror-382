from .model import modelsData
from typing import Optional, Any
from .GameData import CommonFields, ItemSpawnFields
from .XNA import Position

class HarvestItems(CommonFields):
    def __init__(
        self,
        CommonFields: ItemSpawnFields,
        Chance: Optional[float] = None,
        ForShavingEnchantment: Optional[bool] = None,
        ScaledMinStackWhenShaving: Optional[int] = None,
        ScaledMaxStackWhenShaving: Optional[int] = None
    ):
        self.Chance = Chance
        self.ForShavingEnchantment = ForShavingEnchantment
        self.ScaledMinStackWhenShaving = ScaledMinStackWhenShaving
        self.ScaledMaxStackWhenShaving = ScaledMaxStackWhenShaving
        super().__init__(CommonFields=CommonFields)


class GiantCropsData(modelsData):
    def __init__(
        self,
        key: str,
        FromItemId: str,
        HarvestItems: list[HarvestItems],
        Texture: str,
        TexturePosition: Optional[Position] = None,
        TileSize: Optional[Position] = None,
        Health: Optional[int] = None,
        Chance: Optional[float] = None,
        Condition: Optional[str] = None,
        CustomFields: Optional[Any] = None
    ):
        super().__init__(key)
        self.FromItemId = FromItemId
        self.HarvestItems = HarvestItems
        self.Texture = Texture
        self.TexturePosition = TexturePosition
        self.TileSize = TileSize
        self.Health = Health
        self.Chance = Chance
        self.Condition = Condition
        self.CustomFields = CustomFields
