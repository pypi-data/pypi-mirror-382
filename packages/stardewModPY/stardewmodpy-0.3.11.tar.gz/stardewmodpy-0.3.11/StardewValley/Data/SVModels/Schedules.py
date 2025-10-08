
from .svmodel import svmodel
from ... import Load, EditData, Helper

class Schedules(svmodel):
    """
    It is important to have an assets/blank.json file with an empty dictionary for loading the Schedules.
    """
    def __init__(self, mod: Helper, Schedules_List:list=[]):
        self.Schedules_List=Schedules_List
        super().__init__(mod)
    
    def contents(self):
        super().contents()
        
        for schedule in self.Schedules_List:
            self.registryContentData(
                Load(
                    LogName=f"Carregando schedule {schedule.__class__.__name__}",
                    Target=f"Characters/schedules/{schedule.__class__.__name__}",
                    FromFile=f"assets/blank.json"
                )
            )

            self.registryContentData(
                EditData(
                    LogName=f"Add schedule {schedule.__class__.__name__}",
                    Target=f"Characters/schedules/{schedule.__class__.__name__}",
                    Entries=schedule.json
                )
            )
        