from __future__ import annotations

from typing import Optional, List, Any

class modelsData:
    def __init__(self, key: str|int):
        self.key=key

    def getJson(self, useGetStr:Optional[list[str]]=None) -> dict: #customized because of getStr functions
        json = {}
        useGetStr = useGetStr or []
        for attr, value in vars(self).items():
            if value is not None and attr not in ["key"]:
                if isinstance(value, list):
                    new_list  = []
                    for item in value:
                        if not isinstance(item, (str, int, float, bool, list, dict, tuple, set)):
                            if hasattr(item, "getStr") and attr in useGetStr and callable(item.getStr):
                                new_list.append(item.getStr())
                            elif hasattr(item, "getJson") and callable(item.getJson):
                                new_list.append(item.getJson())
                            else:
                                raise TypeError(f"Item da lista '{attr}' é uma classe personalizada sem getJson/getStr")
                        else:
                            new_list.append(item)
                    json[attr] = new_list
                if not isinstance(value, (str, int, float, bool, list, dict, tuple, set)):
                    if hasattr(value, "getStr") and attr in useGetStr and callable(value.getStr):
                        json[attr] = value.getStr()
                    elif hasattr(value, "getJson") and callable(value.getJson):
                        json[attr] = value.getJson()
                    else:
                        raise TypeError(f"Variable '{attr}' is a custom class but has neither getJson() nor getStr()")
                else:
                    json[attr] = value
        
        return json
    
    def getMinimum(self, value: int | None, min_val: int | None, max_val: int | None) -> int | None:
        if value is None:
            return None
        if min_val is None and max_val is None:
            return value
    
        if min_val is None:
            return value if value <= max_val else max_val
    
        if max_val is None:
            return value if value >= min_val else min_val
        
        if value < min_val:
            return min_val
        
        
        if value > max_val:
            return max_val
        
        return value