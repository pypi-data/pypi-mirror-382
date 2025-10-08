from ...helper import Helper
from ...contentpatcher import Include, Load, EditData, EditImage, EditMap

class svmodel:
    def __init__(self, mod: Helper):
        self.mod = mod
        self.contents()
    
    def contents(self):
        self.mod.content.registryContentData(
            Include(
                FromFile=self.__class__.__name__
            )
        )
    
    def registryContentData(self, contentData:Load|EditData|EditImage|EditMap):
        self.mod.content.registryContentData(contentData, contentFile=self.__class__.__name__)