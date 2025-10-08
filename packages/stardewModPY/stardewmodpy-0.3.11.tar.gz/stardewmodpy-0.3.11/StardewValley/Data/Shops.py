from .model import modelsData
from .GameData import StackSizeVisibility, QualityModifierMode, ToolUpgradeLevel, Modification, AvailableStockLimit, CommonFields
from .XNA import Rectangle
from typing import Optional, Any


class ShopModifiersData(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Modification: Modification,
        Condition: Optional[str] = None,
        Amount: Optional[float] = None,
        RandomAmount: Optional[list[float]] = None
    ):
        self.Id = Id
        self.Modification = Modification
        self.Condition = Condition
        self.Amount = Amount
        self.RandomAmount = RandomAmount
    
    


class Items(CommonFields):
    def __init__(
        self,
        *,
        CommonFields: CommonFields,
        Price: Optional[int] = None,
        TradeItemId: Optional[str] = None,
        TradeItemAmount: Optional[int] = None,
        ApplyProfitMargins: Optional[bool] = None,
        IgnoreShopPriceModifiers: Optional[bool] = None,
        AvailableStockModifiers: Optional[list[ShopModifiersData]] = None,
        PriceModifiers: Optional[list[ShopModifiersData]] = None,
        AvailableStockModifierMode: Optional[QualityModifierMode] = None,
        PriceModifierMode: Optional[QualityModifierMode] = None,
        AvoidRepeat: Optional[bool] = None,
        UseObjectDataPrice: Optional[bool] = None,
        AvailableStock: Optional[int] = None,
        AvailableStockLimit: Optional[AvailableStockLimit] = None,
        ActionsOnPurchase: Optional[list[str]] = None,
        CustomFields: Optional[Any] = None
    ):
        self.CommonFields = CommonFields
        self.Price = Price
        self.TradeItemId = TradeItemId
        self.TradeItemAmount = TradeItemAmount
        self.ApplyProfitMargins = ApplyProfitMargins
        self.IgnoreShopPriceModifiers = IgnoreShopPriceModifiers
        self.AvailableStockModifiers = AvailableStockModifiers
        self.PriceModifiers = PriceModifiers
        self.AvailableStockModifierMode = AvailableStockModifierMode
        self.PriceModifierMode = PriceModifierMode
        self.AvoidRepeat = AvoidRepeat
        self.UseObjectDataPrice = UseObjectDataPrice
        self.AvailableStock = AvailableStock
        self.AvailableStockLimit = AvailableStockLimit
        self.ActionsOnPurchase = ActionsOnPurchase
        self.CustomFields = CustomFields


class ShopOwnersDialoguesData(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Dialogue: str,
        RandomDialogue: Optional[list[str]] = None,
        Condition: Optional[str] = None,
    ):
        self.Id = Id
        self.Dialogue = Dialogue
        self.RandomDialogue = RandomDialogue
        self.Condition = Condition



class ShopOwnersData(modelsData):
    def __init__(
        self,
        *,
        Name: str,
        Id: Optional[str],
        Condition: Optional[str] = None,
        Portrait: Optional[str] = None,
        Dialogues: Optional[list[ShopOwnersDialoguesData]] = [],
        RandomizeDialogueOnOpen: Optional[bool] = True,
        ClosedMessage: Optional[str] = None
    ):
        self.Name = Name
        self.Id = Id
        self.Condition = Condition
        self.Portrait = Portrait
        self.Dialogues = Dialogues
        self.RandomizeDialogueOnOpen = RandomizeDialogueOnOpen
        self.ClosedMessage = ClosedMessage










class VisualThemeData(modelsData):
    def __init__(
        self,
        *,
        Condition: Optional[str] = None,
        WindowBorderTexture: Optional[str]=None,
        WindowBorderSourceRect: Optional[Rectangle]=None,
        PortraitBackgroundTexture: Optional[str] = None,
        PortraitBackgroundSourceRect: Optional[Rectangle] = None,
        DialogueBackgroundTexture: Optional[str] = None,
        DialogueBackgroundSourceRect: Optional[Rectangle] = None,
        DialogueColor: Optional[str] = None,
        DialogueShadowColor: Optional[str] = None,
        ItemRowBackgroundTexture: Optional[str]=None,
        ItemRowBackgroundSourceRect: Optional[Rectangle]=None,
        ItemRowBackgroundHoverColor: Optional[str] = None,
        ItemRowTextColor: Optional[str] = None,
        ItemIconBackgroundTexture: Optional[str] = None,
        ItemIconBackgroundSourceRect: Optional[Rectangle] = None,
        ScrollUpTexture: Optional[str] = None,
        ScrollUpSourceRect: Optional[Rectangle] = None,
        ScrollDownTexture: Optional[str] = None,
        ScrollDownSourceRect: Optional[Rectangle] = None,
        ScrollBarFrontTexture: Optional[str] = None,
        ScrollBarFrontSourceRect: Optional[Rectangle] = None,
        ScrollBarBackTexture: Optional[str] = None,
        ScrollBarBackSourceRect: Optional[Rectangle] = None
    ):
        self.Condition = Condition
        self.WindowBorderTexture = WindowBorderTexture
        self.WindowBorderSourceRect = WindowBorderSourceRect
        self.PortraitBackgroundTexture = PortraitBackgroundTexture
        self.PortraitBackgroundSourceRect = PortraitBackgroundSourceRect
        self.DialogueBackgroundTexture = DialogueBackgroundTexture
        self.DialogueBackgroundSourceRect = DialogueBackgroundSourceRect
        self.DialogueColor = DialogueColor
        self.DialogueShadowColor = DialogueShadowColor
        self.ItemRowBackgroundTexture = ItemRowBackgroundTexture
        self.ItemRowBackgroundSourceRect = ItemRowBackgroundSourceRect
        self.ItemRowBackgroundHoverColor = ItemRowBackgroundHoverColor
        self.ItemRowTextColor = ItemRowTextColor
        self.ItemIconBackgroundTexture = ItemIconBackgroundTexture
        self.ItemIconBackgroundSourceRect = ItemIconBackgroundSourceRect
        self.ScrollUpTexture = ScrollUpTexture
        self.ScrollUpSourceRect = ScrollUpSourceRect
        self.ScrollDownTexture = ScrollDownTexture
        self.ScrollDownSourceRect = ScrollDownSourceRect
        self.ScrollBarFrontTexture = ScrollBarFrontTexture
        self.ScrollBarFrontSourceRect = ScrollBarFrontSourceRect
        self.ScrollBarBackTexture = ScrollBarBackTexture
        self.ScrollBarBackSourceRect = ScrollBarBackSourceRect

class ShopsData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Items: list[Items],
        SalableItemTags: Optional[list[str]] = None,
        Owners: Optional[list[ShopOwnersData]]=None,
        Currency: Optional[int] = None,
        ApplyProfitMargins: Optional[bool] = None,
        StackSizeVisibility: Optional[StackSizeVisibility] = None,
        OpenSound: Optional[str] = None,
        PurchaseSound: Optional[str] = None,
        purchaseRepeatSound: Optional[str] = None,
        PriceModifiers: Optional[ShopModifiersData] = None,
        PriceModifierMode: Optional[QualityModifierMode] = None,
        VisualTheme: Optional[list[VisualThemeData]] = None,
        CustomFields: Optional[dict[str,str]] = None
    ):
        super().__init__(key)
        self.Items = Items
        self.SalableItemTags = SalableItemTags
        self.Owners = Owners
        self.Currency = Currency
        self.ApplyProfitMargins = ApplyProfitMargins
        self.StackSizeVisibility = StackSizeVisibility
        self.OpenSound = OpenSound
        self.PurchaseSound = PurchaseSound
        self.purchaseRepeatSound = purchaseRepeatSound
        self.PriceModifiers = PriceModifiers
        self.PriceModifierMode = PriceModifierMode
        self.VisualTheme = VisualTheme
        self.CustomFields = CustomFields
