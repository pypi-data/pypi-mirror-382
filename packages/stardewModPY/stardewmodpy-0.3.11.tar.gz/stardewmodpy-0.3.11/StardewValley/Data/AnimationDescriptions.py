from .model import modelsData
from typing import Optional
from .XNA import Position

class AnimationDescriptionsData(modelsData):
    def __init__(
        self,
        key: str,
        frames:list[int],
        repeatframes: list[int],
        leavingframes: list[int],
        messagekey:Optional[str]=None,
        laying_down: Optional[bool]=None,
        offset: Optional[Position]=None
    ):
        super().__init__(key)
        self.frames = frames
        self.repeatframes = repeatframes
        self.leavingframes = leavingframes
        self.messagekey = messagekey
        self.laying_down = laying_down
        self.offset = offset

    def getJson(self) -> str:
        json=f"{" ".join(str(f) for f in self.frames)}/{" ".join(str(f) for f in self.repeatframes)}/{" ".join(str(f) for f in self.leavingframes)}"
        if self.messagekey is not None or self.laying_down is not None or self.offset is not None:
            json += f"/{self.messagekey}" if self.messagekey is not None else "/"
            if self.laying_down is not None and self.laying_down == True:
                json += f"/laying_down"
            else:
                json += "/"
            if self.offset is not None:
                json += f"/offset {self.offset.X} {self.offset.Y}"
        return json

    def register(self, LogName, mod, contentFile = "content", When = None, Target = None):
        return super().register(LogName, mod, contentFile, When, "Data/animationDescriptions")