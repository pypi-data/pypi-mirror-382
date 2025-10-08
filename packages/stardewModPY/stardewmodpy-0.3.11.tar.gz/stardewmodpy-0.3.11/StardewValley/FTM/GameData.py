from typing import Optional, Any
from ..Data.model import modelsData
from ..Data.GameData import Season

class Seasons(Season):
    def __init__(self):
        super().__init__()
    
    class All(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "All"

class StrictTileChecking(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Maximum"
    
    class Maximum(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Maximum"
    
    class High(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "High"
    
    class Medium(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Medium"
    
    class Low(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Low"
    
    class none(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "None"


class RelatedSkill(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "Farming"
    
    class Farming(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Farming"
    
    class Fishing(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Fishing"
    
    class Foraging(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Foraging"
    
    class Mining(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Mining"
    
    class Combat(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "Combat"

class FacingDirection(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "down"
    
    class down(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "down"
    
    class up(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "up"
    
    class left(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "left"
    
    class right(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "right"

class Gender(modelsData):
    def __init__(self):
        pass

    def getJson(self) -> str:
        return "M"
    
    class M(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "M"
    
    class F(modelsData):
        def __init__(self):
            pass

        def getJson(self) -> str:
            return "F"