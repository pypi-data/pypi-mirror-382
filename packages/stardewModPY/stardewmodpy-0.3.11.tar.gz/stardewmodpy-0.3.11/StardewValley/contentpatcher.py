from typing import Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .manifest import Manifest

#subclasses of ContentData are used in the classes Load, EditData, EditImage and EditMap

class ToArea:
    def __init__(self, X:int, Y:int, Width:int, Height:int):
        self.X=X
        self.Y=Y
        self.Width=Width
        self.Height=Height
    
    def getJson(self) -> dict[str, int]:
        return {
            "X":self.X,
            "Y":self.Y,
            "Width":self.Width,
            "Height":self.Height
        }


class Position:
    def __init__(self, X: int, Y: int):
        self.X = X
        self.Y = Y


    def getJson(self) -> dict[str, int]:
        return {
            "X": self.X,
            "Y": self.Y
        }


class WarpPosition:
    def __init__(self, fromX: int, fromY: int, toArea: str, toX: int, toY: int):
        self.fromX = fromX
        self.fromY = fromY
        self.toArea = toArea
        self.toX = toX
        self.toY = toY


    def getJson(self) -> str:
        return f"{self.fromX} {self.fromY} {self.toArea} {self.toX} {self.toY}"


class MapTiles:
    def __init__(self, Layer: str, Position: Position, SetTilesheet:Optional[str]=None, SetIndex:Optional[str]=None, SetProperties: Optional[dict[str, str]] = None, Remove: bool=False):
        self.Layer = Layer
        self.Position = Position.getJson()
        self.SetTilesheet=SetTilesheet
        self.SetIndex=SetIndex   
        self.SetProperties = SetProperties
        self.Remove=Remove


    def getJson(self) -> dict:
        json = {
            "Position": self.Position,
            "Layer": self.Layer
        }

        if self.SetTilesheet:
            json["SetTilesheet"]=self.SetTilesheet

        if self.SetIndex:
            json["SetIndex"]=self.SetIndex
        
        if self.SetProperties:
            json["SetProperties"] = self.SetProperties
        if self.Remove:
            json["Remove"]=self.Remove

        return json

class MapProperties:
    def __init__(self):
        self.json={}
    
    def CanBuildHere(self):
        self.json["CanBuildHere"]="T"
    
    def BuildCondition(self, query:str):
        self.json["BuildCondition"]=query
    
    def LooserBuildRestrictions(self):
        self.json["LooserBuildRestrictions"]="T"
    
    def ValidBuildRect(self, x:int, y:int, width:int, height:int):
        self.json["ValidBuildRect"]=[x,y,width,height]

class TextOperations:
    def __init__(self, Operation:str, Target:list[str], Value:str, Delimiter:str=" "):
        self.Operation=Operation
        self.Target=Target
        self.Value=Value
        self.Delimiter=Delimiter
    
    def getJson(self) -> dict[str, str]:
        return {
            "Operation": self.Operation,
            "Target": self.Target,
            "Value": self.Value,
            "Delimiter": self.Delimiter
        }

class MoveEntries:
    def __init__(
        self,
        ID:str,
        BeforeID:Optional[str]=None,
        AfterID:Optional[str]=None,
        ToPosition:Optional[str]=None

    ):
        self.ID=ID,
        self.BeforeID=BeforeID
        self.AfterID=AfterID
        self.ToPosition=ToPosition
    
    def getJson(self) -> dict[str, str]:
        json= {
            "ID": self.ID
        }
        json["BeforeID"]=self.BeforeID
        json["AfterID"]=self.AfterID
        json["ToPosition"]=self.ToPosition
        return json

class ContentData:
    def __init__(self):
        self.Action = self.__class__.__name__
        self.json={
            "Action":self.Action
        }

class Include(ContentData):
    def __init__(
        self,
        FromFile:str,
        When:Optional[dict[str, str]]=None,
        Update:Optional[str]=None,
        LocalTokens:Optional[dict[str, str|int]]=None
    ):
        super().__init__()
        self.fileName=FromFile
        self.json["FromFile"]=f"assets/{FromFile}.json"
        if When:
            self.json["When"]=When
        if Update:
            self.json["Update"]=Update
        if LocalTokens:
            self.json["LocalTokens"]=LocalTokens

class Load(ContentData):
    def __init__(
            self,
            LogName:str,
            Target:str,
            FromFile:str,
            When:Optional[dict[str, str]]=None,
            Update:Optional[str]=None,
            LocalTokens:Optional[dict[str, str|int]]=None,
            Priority:Optional[str]=None,
            TargetLocale:Optional[str]=None
        ):
        super().__init__()
        self.json["LogName"]=LogName
        self.json["Target"]=Target
        self.json["FromFile"]=FromFile
        if When:
            self.json["When"]=When
        if Update:
            self.json["Update"]=Update
        if LocalTokens:
            self.json["LocalTokens"]=LocalTokens
        if Priority:
            self.json["Priority"]=Priority
        if TargetLocale:
            self.json["TargetLocale"]=TargetLocale

class EditData(ContentData):
    def __init__(
            self,
            LogName:str,
            Target:str,
            TargetField:Optional[list[str]]=None,
            Entries:Optional[dict]=None,
            Fields:Optional[dict]=None,
            MoveEntries:Optional[list[MoveEntries]]=None,
            TextOperations:Optional[list[TextOperations]]=None,
            When:Optional[dict[str, str]]=None,
            Update:Optional[str]=None,
            LocalTokens:Optional[dict[str, str|int]]=None,
            Priority:Optional[str]=None,
            TargetLocale:Optional[str]=None
        ):
        super().__init__()
        self.json["LogName"]=LogName
        self.json["Target"]=Target
        if TargetField:
            self.json["TargetField"]=TargetField
        if Entries:
            self.json["Entries"]=Entries
        if Fields:
            self.json["Fields"]=Fields
        if MoveEntries:
            self.json["MoveEntries"]=[entry.getJson() for entry in MoveEntries]
        if TextOperations:
            self.json["TextOperations"]=[operation.getJson() for operation in TextOperations]
        if When:
            self.json["When"]=When
        if Update:
            self.json["Update"]=Update
        if LocalTokens:
            self.json["LocalTokens"]=LocalTokens
        if Priority:
            self.json["Priority"]=Priority
        if TargetLocale:   
            self.json["TargetLocale"]=TargetLocale
        

class EditMap(ContentData):
    def __init__(
        self, 
        LogName:str, 
        Target:str, 
        TargetLocale: Optional[str]=None,
        FromFile:Optional[str] = None,
        FromArea: Optional[ToArea] = None,
        ToArea: Optional[ToArea] = None, 
        PatchMode: Optional[str] = None,
        MapProperties: Optional[dict[str, str]] = None,
        AddNpcWarps:Optional[list[WarpPosition]]=None, 
        AddWarps: Optional[list[WarpPosition]] = None,
        TextOperations: Optional[list[TextOperations]] = None,
        MapTiles: Optional[list[MapTiles]] = None, 
        Priority: Optional[str] = None,
        LocalTokens: Optional[dict[str, str|int]] = None,
        Update:Optional[str]=None, 
        When:Optional[dict[str, str]]=None
    ):
        super().__init__()
        self.json["LogName"]=LogName
        self.json["Target"]=Target
        if TargetLocale:
            self.json["TargetLocale"]=TargetLocale
        if FromFile:
            self.json["FromFile"] = FromFile
        if FromArea:
            self.json["FromArea"] = FromArea.getJson()
        if ToArea:
            self.json["ToArea"] = ToArea.getJson()
        if PatchMode:
            self.json["PatchMode"] = PatchMode
        if MapProperties:   
            self.json["MapProperties"] = MapProperties

        if AddNpcWarps:
            self.json["AddNpcWarps"] = [warp.getJson() for warp in AddNpcWarps]
        if AddWarps:
            self.json["AddWarps"] = [warp.getJson() for warp in AddWarps]
        
        if TextOperations:  
            self.json["TextOperations"] = [operation.getJson() for operation in TextOperations]
        if MapTiles:
            self.json["MapTiles"] = [tile.getJson() for tile in MapTiles]
        if Priority:
            self.json["Priority"] = Priority
        if LocalTokens:
            self.json["LocalTokens"] = LocalTokens
        if Update:
            self.json["When"]=Update
        if When:
            self.json["When"]=When

class EditImage(ContentData):
    def __init__(
            self,
            LogName:str, 
            Target:str,
            FromFile:str,
            TargetLocale:Optional[str]=None,
            FromArea:Optional[dict[ToArea]]=None,
            ToArea:Optional[dict[ToArea]]=None,
            PatchMode:Optional[str]=None,
            When:Optional[dict[str, str]]=None,
            Update:Optional[str]=None,
            LocalTokens:Optional[dict[str, str|int]]=None,
            Priority:Optional[str]=None,
            
        ):
        super().__init__()
        self.json["LogName"]=LogName
        self.json["Target"]=Target

        self.json["FromFile"]=FromFile
        if TargetLocale:
            self.json["TargetLocale"]=TargetLocale
        if FromArea:
            self.json["FromArea"]=FromArea.getJson()
        if ToArea:
            self.json["ToArea"]=ToArea.getJson()
        if PatchMode:
            self.json["PatchMode"]=PatchMode
        if When:
            self.json["When"]=When
        if Update:
            self.json["Update"]=Update
        if LocalTokens:
            self.json["LocalTokens"]=LocalTokens
        if Priority:
            self.json["Priority"]=Priority

class ConfigSchema():
    def __init__(
        self,
        key:str,
        AllowValues:Optional[list[str]]=None,
        AllowBlank:Optional[bool]=None,
        AllowMultiple:Optional[bool]=None,
        Default:Optional[str]=None,
        Section:Optional[str]=None
    ):
        self.key=key
        self.AllowValues=AllowValues
        self.AllowBlank=AllowBlank
        self.AllowMultiple=AllowMultiple
        self.Default=Default
        self.Section=Section

    def getJson(self):
        json={}
        if self.AllowValues is not None:
            json["AllowValues"] = ",".join(self.AllowValues)
        if self.AllowBlank is not None:
            json["AllowBlank"] = self.AllowBlank
        if self.AllowMultiple is not None:
            json["AllowMultiple"] = self.AllowMultiple
        if self.Default is not None:
            json["Default"] = self.Default
        if self.Section is not None:
            json["Section"] = self.Section
        return json
         

class CustomLocations():
    def __init__(
        self,
        Name:str,
        FromMap:str,
        MigrateLegacyNames:Optional[list[str]]=None
    ):
        self.Name=Name
        self.FromMap=FromMap
        self.MigrateLegacyNames=MigrateLegacyNames
    
    def getJson(self):
        json={
            "Name":self.Name,
            "FromMap":self.FromMap,            
        }
        if self.MigrateLegacyNames:
            json["MigrateLegacyNames"] = self.MigrateLegacyNames
        return json

class ContentPatcher:
    def __init__(self, manifest:"Manifest"):
        self.Manifest=manifest
        self.Manifest.ContentPackFor={
            "UniqueID": "Pathoschild.ContentPatcher"
        }

        self.fileName="content.json"

        self.contentFile={
            "Format": "2.5.0",
            "Changes": []
        }

        self.contentFiles={}

        self.extraContents={}
    
    def registryContentData(self, contentData:Include|Load|EditData|EditImage|EditMap, contentFile:str="content"):
        if contentData.__class__.__name__=="Include":
            self.contentFiles[contentData.fileName]={
                "Changes":[

                ]
            }
        if contentFile=="content":
            self.contentFile["Changes"].append(contentData.json)
        else:
            self.contentFiles[contentFile]["Changes"].append(contentData.json)
    
    
    def addCustomLocation(self, customLocations:CustomLocations):
        self.contentFile["CustomLocations"].append(customLocations.getJson())
    
    def addConfigSchema(self, configSchema:ConfigSchema):
        if "ConfigSchema" not in self.contentFile:
            self.contentFile["ConfigSchema"] = {}
        self.contentFile["ConfigSchema"][configSchema.key]=configSchema.getJson()