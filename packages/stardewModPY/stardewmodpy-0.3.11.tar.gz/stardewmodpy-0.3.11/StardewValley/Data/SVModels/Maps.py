from .svmodel import svmodel
from .mapsModel import MapsModel
from ...helper import Helper

class Maps(svmodel):
    def __init__(self, mod: Helper):
        super().__init__(mod)
        

    def contents(self):
        super().contents()
        