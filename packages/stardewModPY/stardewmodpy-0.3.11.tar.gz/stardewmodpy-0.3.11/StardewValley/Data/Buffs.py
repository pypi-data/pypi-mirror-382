from typing import Optional
from .model import modelsData
from .TriggerActions import Actions

class Effects:
    def __init__(
        self,
        *,
        FarmingLevel:Optional[float]=0,
        FishingLevel:Optional[float]=0,
        ForagingLevel:Optional[float]=0,
        LuckLevel:Optional[float]=0,
        MiningLevel:Optional[float]=0,
        CombatLevel:Optional[float]=0,
        Attack:Optional[float]=0,
        Defense:Optional[float]=0,
        MagneticRadius:Optional[float]=0,
        MaxStamina:Optional[float]=0,
        Speed:Optional[float]=0,
        Immunity:Optional[float]=0,
        KnockbackMultiplier:Optional[float]=0,
        WeaponSpeedMultiplier:Optional[float]=0,
        AttackMultiplier:Optional[float]=0,
        CriticalChanceMultiplier:Optional[float]=0,
        CriticalPowerMultiplier:Optional[float]=0,
        WeaponPrecisionMultiplier:Optional[float]=0
    ):
        self.FarmingLevel=FarmingLevel
        self.FishingLevel=FishingLevel
        self.ForagingLevel=ForagingLevel
        self.LuckLevel=LuckLevel
        self.MiningLevel=MiningLevel        
        self.CombatLevel=CombatLevel
        self.Attack=Attack
        self.Defense=Defense
        self.MagneticRadius=MagneticRadius
        self.MaxStamina=MaxStamina
        self.Speed=Speed
        self.Immunity=Immunity
        self.KnockbackMultiplier=KnockbackMultiplier
        self.WeaponSpeedMultiplier=WeaponSpeedMultiplier
        self.AttackMultiplier=AttackMultiplier
        self.CriticalChanceMultiplier=CriticalChanceMultiplier
        self.CriticalPowerMultiplier=CriticalPowerMultiplier
        self.WeaponPrecisionMultiplier=WeaponPrecisionMultiplier
        
    def getJson(self) -> dict:
        return {
            "FarmingLevel": self.FarmingLevel,
            "FishingLevel": self.FishingLevel,
            "ForagingLevel": self.ForagingLevel,
            "LuckLevel": self.LuckLevel,
            "MiningLevel": self.MiningLevel,
            "CombatLevel": self.CombatLevel,
            "Attack": self.Attack,
            "Defense": self.Defense,
            "MagneticRadius": self.MagneticRadius,
            "MaxStamina": self.MaxStamina,
            "Speed": self.Speed,
            "Immunity": self.Immunity,
            "KnockbackMultiplier": self.KnockbackMultiplier,
            "WeaponSpeedMultiplier": self.WeaponSpeedMultiplier,
            "AttackMultiplier": self.AttackMultiplier,
            "CriticalChanceMultiplier": self.CriticalChanceMultiplier,
            "CriticalPowerMultiplier": self.CriticalPowerMultiplier,
            "WeaponPrecisionMultiplier": self.WeaponPrecisionMultiplier
        }


class BuffsData(modelsData):
    def __init__(
        self,
        *,
        key:str,
        DisplayName:str,
        Duration:int,
        IconTexture:str,
        IconSpriteIndex:Optional[int]=None,
        Description:Optional[str]=None,
        IsDebuff:Optional[bool]=None,
        GlowColor:Optional[str]=None, 
        MaxDuration:Optional[int]=None,
        Effects:Optional[Effects]=None,

        ActionsOnApply:Optional[list[Actions]]=None,
        CustomFields:Optional[dict[str,str]]=None
    ):
        super().__init__(key)
        self.DisplayName=DisplayName
        self.Duration=Duration
        self.IconTexture=IconTexture
        self.IconSpriteIndex=IconSpriteIndex
        self.Description=Description
        self.IsDebuff=IsDebuff
        self.GlowColor=GlowColor
        self.MaxDuration=MaxDuration
        self.Effects=Effects
        self.ActionsOnApply=ActionsOnApply
        self.CustomField=CustomFields