from ..model import modelsData
from typing import Optional
from .Stock import QuantityModifiers

class Music(modelsData):
    def __init__(
        self,
        Track: str,
        Id: Optional[str] = None,
        Condition: Optional[str] = None
    ):
        self.Track = Track
        self.Id = Id
        self.Condition = Condition
        
class ItemSpawnFields(modelsData):
    def __init__(
        self,
        Id: str=None,
        ItemId: str=None,
        RandomItemId: Optional[list[str]]=None,
        Condition: Optional[str]=None,
        PerItemCondition: Optional[str]=None,
        MaxItems: Optional[int]=None,
        IsRecipe: Optional[bool]=None,
        Quality: Optional[int]=None,
        MinStack: Optional[int]=None,
        MaxStack: Optional[int]=None,
        ObjectInternalName: Optional[str]=None,
        ObjectDisplayName: Optional[str]=None,
        ObjectColor: Optional[str]=None,
        ToolUpgradeLevel: Optional[int]=None,
        QualityModifiers: Optional[list[QuantityModifiers]]=None,
        StackModifiers: Optional[list[QuantityModifiers]]=None,
        QualityModifierMode: Optional[str]=None,
        StackModifierMode: Optional[str]=None,
        ModData: Optional[dict[str,str]]=None
    ):
        self.Condition = Condition
        self.Id = Id
        self.ItemId = ItemId
        self.RandomItemId = RandomItemId
        self.MaxItems = MaxItems
        self.MinStack = MinStack
        self.MaxStack = MaxStack
        self.Quality = Quality
        self.ObjectInternalName = ObjectInternalName
        self.ObjectDisplayName = ObjectDisplayName
        self.ObjectColor = ObjectColor
        self.ToolUpgradeLevel = ToolUpgradeLevel
        self.IsRecipe = IsRecipe
        self.StackModifiers = StackModifiers
        self.StackModifierMode = StackModifierMode
        self.QualityModifiers = QualityModifiers
        self.QualityModifierMode = QualityModifierMode
        self.ModData = ModData
        self.PerItemCondition = PerItemCondition

class CommonFields(modelsData):
    def __init__(
        self,
        CommonFields: ItemSpawnFields=None
    ):
        self.CommonFields = CommonFields
    
    def getJson(self, useGetStr:Optional[list[str]]=None, ignore: Optional[list[str]]=None) -> dict: #customized because of getStr functions
        ignore_finish = ["CommonFields"]
        if ignore is not None:
            ignore_finish.extend(ignore)

        json = self.CommonFields.getJson()
        json.update(super().getJson(useGetStr=useGetStr,ignore=ignore_finish))
        return json