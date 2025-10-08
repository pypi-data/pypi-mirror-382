from typing import List, Optional
from .Data.model import modelsData

class Dependencies(modelsData):
    def __init__(
        self,
        *,
        UniqueID: str,
        MinimumVersion: str
    ):
        self.UniqueID = UniqueID
        self.MinimumVersion = MinimumVersion

class Manifest(modelsData):
    def __init__(
        self,
        *,
        Name: str,
        Author: str,
        Version: str,
        Description: str,
        UniqueID: str,
        ContentPackFor: Optional[Dependencies] = None,
        UpdateKeys: List[str] = None,
        MinimumApiVersion: Optional[str] = None,
        Dependencies: Optional[List[Dependencies]] = None
    ):
        self.Name = Name
        self.Author = Author
        self.Version = Version
        self.Description = Description
        self.UniqueID = UniqueID
        self.UpdateKeys = UpdateKeys
        self.ContentPackFor = ContentPackFor
        self.MinimumApiVersion = MinimumApiVersion
        self.Dependencies = Dependencies