from typing import Optional, Any
from .model import modelsData
from .GameData import AudioCategory



class AudioChangesData(modelsData):
    def __init__(self,
        key:str,
        ID:str,
        FilePaths:list[str],
        Category: AudioCategory,
        StreamVorbis: bool,
        Looped: bool,
        UseReverb:bool,
        CustomFields: Optional[dict[str,str]] = None
    ):
        super().__init__(key)
        self.ID = ID
        self.FilePaths = FilePaths
        self.Category = Category
        self.StreamVorbis = StreamVorbis
        self.Looped = Looped
        self.UseReverb = UseReverb
        self.CustomFields = CustomFields