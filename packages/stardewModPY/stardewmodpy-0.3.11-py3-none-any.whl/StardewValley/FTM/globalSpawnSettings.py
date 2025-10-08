from .model import modelsData
from typing import Optional
from .areas import Areas


class GlobalSpawnSettings(modelsData):
    def __init__(
        self,
        Enable:bool,
        Areas:list[Areas]=[],
        CustomTileIndex:Optional[list[int]]=[] 
    ):
        self.Enable=Enable
        self.Areas=Areas
        self.CustomTileIndex=CustomTileIndex
        
    def getJson(self):
        json = {}
        for attr, value in vars(self).items():
            if value is not None and attr not in ["key", "Enable"]:
                if isinstance(value, list):
                    new_list  = []
                    for item in value:
                        if not isinstance(item, (str, int, float, bool, list, dict, tuple, set)):
                            if hasattr(item, "getJson") and callable(item.getJson):
                                new_list.append(item.getJson())
                            else:
                                raise TypeError(f"Variable in list '{attr}' is a custom class but has neither getJson()")
                        else:
                            new_list.append(item)
                    json[attr] = new_list
                if not isinstance(value, (str, int, float, bool, list, dict, tuple, set)):
                    if hasattr(value, "getJson") and callable(value.getJson):
                        json[attr] = value.getJson()
                    else:
                        raise TypeError(f"Variable '{attr}' is a custom class but has neither getJson()")
                else:
                    json[attr] = value
        
        return json