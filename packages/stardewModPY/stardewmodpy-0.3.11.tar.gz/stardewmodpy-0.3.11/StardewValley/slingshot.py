from .manifest import Manifest
from typing import Optional

class validItemIds:
    def __init__(self, value:str|list[str]):
        self.value=value
        
    def getJson(self):
        return self.value

class ammoDamageValues:
    def __init__(self, itemID:str, value:str):
        self.itemID=itemID
        self.value=value
        
    def getJson(self):
        return {self.itemID:self.value}
    
class explosiveAmmunitionIds(validItemIds):
    def __init__(self, value:str|list[str]):
        super().__init__(value)
    
    def getJson(self):
        return super().getJson()

class explosionItemIds(validItemIds):
    def __init__(self, value:str|list[str]):
        super().__init__(value)
    
    def getJson(self):
        return super().getJson()

class validCategories(validItemIds):
    def __init__(self, value:str|list[str]):
        super().__init__(value)
    
    def getJson(self):
        return super().getJson()

class SlingShotFramework:
    def __init__(self, manifest:Manifest):
        self.Manifest=manifest
        self.Manifest.ContentPackFor={
            "UniqueID": "alichan.SlingShotFramework"
        }

        self.fileName="SlingShot.json"
        
        self.contentFile={
            "validItemIds":[],
            "ammoDamageValues":{},
            "explosiveAmmunitionIds":[],
            "explosionItemIds":[],
            "validCategories":[]
        }

    def registryContentData(self, contentData:validItemIds|ammoDamageValues|explosiveAmmunitionIds|explosionItemIds|validCategories):
        if contentData.__class__.__name__=="ammoDamageValues":
            self.contentFile[contentData.__class__.__name__][contentData.itemID]=contentData.value
        else:
            self.contentFile[contentData.__class__.__name__].extend(contentData.getJson())
        