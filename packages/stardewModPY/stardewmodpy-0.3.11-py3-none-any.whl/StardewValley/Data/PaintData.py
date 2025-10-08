from typing import Optional
from .model import modelsData

class Offset(modelsData):
    def __init__(self, Name:str, x:int, y:int):
        self.Name = Name
        self.x = x
        self.y = y
    
    def getJson(self) -> str:
        return f"{self.x} {self.y}"
    
class PaintData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Red: Optional[Offset] = None,
        Blue: Optional[Offset] = None,
        Green: Optional[Offset] = None,
    ):
        super().__init__(key)
        self.Red = Red
        self.Blue = Blue
        self.Green = Green
    
    def getJson(self) -> str:
        parts = []
        for offset in (self.Red, self.Blue, self.Green):
            if offset is not None:
                # adiciona nome e offset separados por barra
                parts.append(offset.Name)
                parts.append(offset.getJson())
            else:
                # não tem nome nem offset, coloca duas strings vazias para manter as barras
                parts.append("")
                parts.append("")
        return "/".join(parts)