from .model import modelsData
from typing import Optional


class HatsData(modelsData):
    def __init__(
        self, 
        key: str,
        name: str,
        description: str,
        show_real_hair: bool,
        skip_hairstyle_offset: bool,
        display_name: str,
        sprite_index: Optional[int] = -1,
        tags: Optional[str] = "",
        texture_name: Optional[str] = ""
    ):
        super().__init__(key)
        self.name = name
        self.description = description
        self.show_real_hair = show_real_hair
        self.skip_hairstyle_offset = skip_hairstyle_offset
        self.display_name = display_name
        self.sprite_index = "" if sprite_index == -1 else sprite_index
        self.tags = tags
        self.texture_name = texture_name


    def getJson(self) -> str:
        return f"{self.name}/{self.description}/{self.show_real_hair}/{self.skip_hairstyle_offset}/{self.tags}/{self.display_name}/{self.sprite_index}/{self.texture_name}"
