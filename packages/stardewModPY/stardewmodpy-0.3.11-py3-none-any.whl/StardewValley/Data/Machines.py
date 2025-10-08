from .model import modelsData
from typing import Optional, Any
from .GameData import CommonFields, ItemSpawnFields, PreserveType, QuantityModifiers, QualityModifierMode

class Trigger(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "ItemPlacedInMachine"
    
    class ItemPlacedInMachine(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "ItemPlacedInMachine"
    
    class OutputCollected(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "OutputCollected"
    
    class MachinePutDown(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "MachinePutDown"
    
    class DayUpdate(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "DayUpdate"
        
class Triggers(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        Trigger: Optional[Trigger] = None,
        RequiredItemId: Optional[str] = None,
        RequiredTags: Optional[list[str]] = None,
        RequiredCount: Optional[int] = None,
        Condition: Optional[str] = None
    ):
        self.Id = Id
        self.Trigger = Trigger
        self.RequiredItemId = RequiredItemId
        self.RequiredTags = RequiredTags
        self.RequiredCount = RequiredCount
        self.Condition = Condition

class OutputItem(CommonFields):
    def __init__(
        self,
        *,
        CommonFields: ItemSpawnFields,
        PreserveType: PreserveType,
        PreserveId: Optional[str],
        CopyColor: Optional[bool],
        CopyPrice: Optional[bool],
        CopyQuality: Optional[bool],
        PriceModifiers: Optional[QuantityModifiers],
        PriceModifierMode: Optional[QualityModifierMode],
        IncrementMachineParentSheetIndex: Optional[int],
        OutputMethod: Optional[str],
        CustomData: Optional[dict[str, Any]]
    ):
        super().__init__(CommonFields=CommonFields)
        self.PreserveType = PreserveType
        self.PreserveId = PreserveId
        self.CopyColor = CopyColor
        self.CopyPrice = CopyPrice
        self.CopyQuality = CopyQuality
        self.PriceModifiers = PriceModifiers
        self.PriceModifierMode = PriceModifierMode
        self.IncrementMachineParentSheetIndex = IncrementMachineParentSheetIndex
        self.OutputMethod = OutputMethod
        self.CustomData = CustomData
class OutputRules(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        Triggers: Optional[list[Triggers]] = None,
        OutputItem: Optional[list[OutputItem]] = None,
        UseFirstValidOutput: Optional[bool] = None,
        MinutesUntilReady: Optional[int] = None,
        DaysUntilReady: Optional[int] = None,
        InvalidCountMessage: Optional[str] = None,
        RecalculateOnCollect: Optional[bool] = None
    ):
        self.Id = Id
        self.Triggers = Triggers
        self.OutputItem = OutputItem
        self.UseFirstValidOutput = UseFirstValidOutput
        self.MinutesUntilReady = MinutesUntilReady
        self.DaysUntilReady = DaysUntilReady
        self.InvalidCountMessage = InvalidCountMessage
        self.RecalculateOnCollect = RecalculateOnCollect
        
class AdditionalConsumedItems(modelsData):
    def __init__(
        self,
        *,
        ItemId: str,
        RequiredCount: Optional[int]=None,
        InvalidCountMessage: Optional[str]=None
    ):
        self.ItemId = ItemId
        self.RequiredCount = RequiredCount
        self.InvalidCountMessage = InvalidCountMessage

class MachinesData(modelsData):
    def __init__(
        self, 
        key:str,
        OutputRules: Optional[list[OutputRules]] = None,
        AdditionalConsumedItems: Optional[list[AdditionalConsumedItems]] = None,
        AllowFairyDust: Optional[bool] = None,
        ReadyTimeModifiers: Optional[list[QuantityModifiers]] = None,
        ReadyTimeModifierMode: Optional[QualityModifierMode] = None
    ):
        super().__init__(key)
        self.OutputRules = OutputRules
        self.AdditionalConsumedItems = AdditionalConsumedItems
        self.AllowFairyDust = AllowFairyDust
        self.ReadyTimeModifiers = ReadyTimeModifiers
        self.ReadyTimeModifierMode = ReadyTimeModifierMode
