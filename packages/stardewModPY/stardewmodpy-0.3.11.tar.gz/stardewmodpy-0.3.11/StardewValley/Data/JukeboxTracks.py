from .model import modelsData
from typing import Optional


class JukeboxTracksData(modelsData):
    def __init__(
        self,        
        *,     
        key: str,   
        Name: Optional[str] = None,
        Available: Optional[bool] = None,
        AlternativeTrackIds: Optional[list[str]] = None
    ):
        super().__init__(key)
        self.Name = Name if Name else key
        self.Available = Available
        self.AlternativeTrackIds = AlternativeTrackIds
