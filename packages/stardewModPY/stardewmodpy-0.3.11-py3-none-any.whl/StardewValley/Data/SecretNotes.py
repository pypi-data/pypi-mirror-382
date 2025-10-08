from .model import modelsData
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..helper import Helper

class SecretNotesData(modelsData):
    def __init__(
        self,
        key: str,
        Contents:str,
        Title:Optional[str]=None,
        Conditions:Optional[str]=None,
        Location:Optional[str]=None,
        LocationContext:Optional[str]=None,
        ObjectId:Optional[str]=None,
        NoteTexture:Optional[str]=None,
        NoteTextureIndex:Optional[int]=None,
        NoteTextColor:Optional[str]=None,
        NoteImageTexture:Optional[str]=None,
        NoteImageTextureIndex:Optional[int]=None,
        ActionsOnFirstRead:Optional[list[str]]=None,
    ):
        super().__init__(key)
        self.Contents = Contents
        self.Title = Title
        self.Conditions = Conditions
        self.Location = Location
        self.LocationContext = LocationContext
        self.ObjectId = ObjectId
        self.NoteTexture = NoteTexture
        self.NoteTextureIndex = NoteTextureIndex
        self.NoteTextColor = NoteTextColor
        self.NoteImageTexture = NoteImageTexture
        self.NoteImageTextureIndex = NoteImageTextureIndex
        self.ActionsOnFirstRead = ActionsOnFirstRead
    
    def register(self, LogName:str, mod:"Helper", contentFile:Optional[str]="content", When:Optional[dict[str,str]]=None):
        Target="Mods/ichortower.SecretNoteFramework/Notes"
        if mod.content.Manifest.Dependencies is None:
            mod.content.Manifest.Dependencies = []

        if not any(dep.get("UniqueID") == "ichortower.SecretNoteFramework" for dep in mod.content.Manifest.Dependencies):
            mod.content.Manifest.Dependencies.append({"UniqueID": "ichortower.SecretNoteFramework", "IsRequired": True})

        return super().register(LogName, mod, contentFile, When, Target)
