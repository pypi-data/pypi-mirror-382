from typing import Optional
from ..Data.GameData import Direction
from ..Data.Events import directions


class scheduleValueData:
    def __init__(
        self,
        time:Optional[int]= None,
        special_command: Optional[str]=None,
        location:Optional[str]=None,
        tileX: Optional[int]=None,
        tileY: Optional[int]=None,
        facingDirection: Optional[Direction]=None,
        animation: Optional[str]=None,
        dialogue:Optional[str]=None
    ):
        self.value=""
        if special_command:
            self.value=special_command
        else:
            self.value=f"{time} {location} {tileX} {tileY} {directions[facingDirection]}"
            if animation:
                self.value+=f" {animation}"
            if dialogue:
                self.value+=f" {dialogue}"


    def getJson(self) -> str:
        return self.value


class scheduleData:
    def __init__(
        self,
        value: list[scheduleValueData]
    ):
        self.value = value


    def getJson(self) -> str:
        return "/".join([value.getJson() for value in self.value])
