from ...Data import modelsData
from .AddingToStats import AddingToStats
from typing import Optional

class ExtraSpawn(modelsData):
    def __init__(
        self,
        *,
        ItemId:str,
        RandomItemId:Optional[list[str]]=None,
        Chance:Optional[float]=None,
        Condition:Optional[str]=None,
        AvoidRepeat:Optional[bool]=None,
        MaxItems:Optional[int]=None,
        PerItemCondition:Optional[list[str]]=None,
        MinStack:Optional[int]=None,
        MaxStack:Optional[int]=None,
        Quality:Optional[int]=None,
        IsRecipe:Optional[bool]=None,
        ModData:Optional[dict[str,str]]=None


    ):
        self.ItemId=ItemId
        self.RandomItemId=RandomItemId
        self.Chance=Chance
        self.Condition=Condition
        self.AvoidRepeat=AvoidRepeat
        self.MaxItems=MaxItems
        self.PerItemCondition=PerItemCondition
        self.MinStack=MinStack
        self.MaxStack=MaxStack
        self.Quality=Quality
        self.IsRecipe=IsRecipe
        self.ModData=ModData

class MineSpawn(modelsData):
    def __init__(
        self,
        *,
        Floors:str,
        Condition:Optional[str]=None,
        Type:Optional[str]=None,
        SpawnFrequency:Optional[float]=None,
        AdditionalChancePerLevel:Optional[float]=None
    ):
        self.Floors=Floors
        self.Condition=Condition
        self.Type=Type
        self.SpawnFrequency=SpawnFrequency
        self.AdditionalChancePerLevel=AdditionalChancePerLevel

class OnDestroy(modelsData): #Conferir
    def __init__(
        self,
        *,
        Conditions:str,
        TriggerAction:Optional[str]=None,
        Message:Optional[str]=None,
        Confirm:Optional[str]=None,
        Reject:Optional[str]=None,
        ShowNote:Optional[dict]=None,
        ChangeMoney:Optional[str]=None,
        Health:Optional[str]=None,
        Stamina:Optional[str]=None,
        PlayMusic:Optional[str]=None,
        PlaySound:Optional[str]=None,
        AddQuest:Optional[str]=None,
        AddSpecialOrder:Optional[str]=None,
        RemoveQuest:Optional[str]=None,
        RemoveSpecialOrder:Optional[str]=None,
        AddItems:Optional[list[ExtraSpawn]]=None,
        RemoveItems:Optional[list[ExtraSpawn]]=None,
        AddFlags:Optional[list[str]]=None,
        RemoveFlags:Optional[list[str]]=None,
        AddFurniture:Optional[list[str]]=None,
    ):
        pass #corrigir


class CustomResource(modelsData):
    def __init__(
        self,
        *,
        Texture:str,
        SpriteIndex:int,
        Width:int,
        Height:int,
        Health:int,
        Tool:str,
        MinDrops:int,
        EasyCalc:Optional[bool]=None,
        ItemDropped:Optional[str]=None,
        ContextTags:Optional[str]=None,
        CustomFields:Optional[dict[str,str]]=None,


        


        
        Debris:Optional[str]=None,
        BreakingSound:Optional[str]=None,
        Sound:Optional[str]=None,
        Shake:Optional[bool]=None,
        MinToolLevel:Optional[int]=None,
        ImmuneToBombs:Optional[bool]=None,
        Light:Optional[dict]=None,
        
        CountTowards:Optional[AddingToStats]=None,
        Exp:Optional[int]=None,
        Skill:Optional[str]=None,


        FailSounds:Optional[list[str]]=None,
        SayWrongTool:Optional[str]=None,

        OnDestroy:Optional[OnDestroy]=None,
        MineSpawns:Optional[list[MineSpawn]]=None,


    ):
        self.Texture=Texture
        self.SpriteIndex=SpriteIndex
        self.Width=Width
        self.Height=Height
        self.Health=Health
        self.Tool=Tool
        self.MinDrops=MinDrops
        self.EasyCalc=EasyCalc
        self.ItemDropped=ItemDropped
        self.ContextTags=ContextTags
        self.CustomFields=CustomFields

class ItemDrops(CustomResource):
    def __init__(
        self,
        *,
        Texture:str,
        SpriteIndex:int,
        Width:int,
        Height:int,
        Health:int,
        Tool:str,
        MinDrops:int,
        EasyCalc:Optional[bool]=None,
        ItemDropped:Optional[str]=None,
        ContextTags:Optional[str]=None,
        CustomFields:Optional[dict[str,str]]=None,

        MaxDrops:Optional[int]=None,
        ExtraItems:Optional[list[ExtraSpawn]]=None,
        AddHay:Optional[int]=None,
        SecretNotes:Optional[bool]=None,
            
    ):
        super().__init__(
            Texture=Texture,
            SpriteIndex=SpriteIndex,
            Width=Width,
            Height=Height,
            Health=Health,
            Tool=Tool,
            MinDrops=MinDrops,
            EasyCalc=EasyCalc,
            MaxDrops=MaxDrops,
            ItemDropped=ItemDropped,
            ContextTags=ContextTags,
            CustomFields=CustomFields,
        )