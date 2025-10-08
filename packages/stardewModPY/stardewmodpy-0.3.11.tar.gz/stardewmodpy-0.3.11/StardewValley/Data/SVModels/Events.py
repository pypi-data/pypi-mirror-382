from .svmodel import svmodel
from .EventsModel import EventsModel

from ...helper import Helper
from ...contentpatcher import EditData

class Events(svmodel):
    def __init__(self, mod:Helper, Events_List:list[EventsModel]):
        self.Events_List=Events_List
        super().__init__(mod)
    
    def contents(self):
        super().contents()
        
        
        for event in self.Events_List:
            self.registryContentData(
                EditData(
                    LogName=f"Add {event.location}",
                    Target=f"Data/Events/{event.location}",
                    Entries={
                        event.key.getJson():event.value.getJson()
                    }
                )
            )
    
