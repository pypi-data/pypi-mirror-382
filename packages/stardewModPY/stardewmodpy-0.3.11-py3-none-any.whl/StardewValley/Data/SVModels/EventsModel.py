from abc import ABC, abstractmethod
from ..Events import EventData

class EventsModel(EventData, ABC):
    def __init__(self, location:str):
        self.location = location
    