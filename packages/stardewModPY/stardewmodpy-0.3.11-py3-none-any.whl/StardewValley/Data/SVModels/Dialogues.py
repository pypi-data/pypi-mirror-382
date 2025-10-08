from .svmodel import svmodel
from ..model import modelsData
from ...contentpatcher import EditData, Load

class Dialogues(svmodel):
    """
    The assets/blank.json file is important for the correct loading of dialogs.
    """
    def __init__(self, mod, Dialogues_List:list[modelsData]):
        self.Dialogues_List=Dialogues_List
        super().__init__(mod)

    def contents(self):
        super().contents()
        for dialogue in self.Dialogues_List:
            self.registryContentData(
                Load(
                    LogName=f"Carregando dialogo {dialogue.__class__.__name__}",
                    Target=f"Characters/Dialogue/{dialogue.__class__.__name__}",
                    FromFile=f"assets/blank.json"
                )
            )
            self.registryContentData(
                EditData(
                    LogName=f"Add {dialogue.__class__.__name__}",
                    Target=f"Characters/Dialogue/{dialogue.__class__.__name__}",
                    Entries={key:value for key, value in dialogue.getJson().items()}
                )
            )
        