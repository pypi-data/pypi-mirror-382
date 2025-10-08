from .model import modelsData
from typing import Any, Optional
from .GameData import WeaponsType, CommonFields

class Projectiles(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Damage: Optional[int] = None,
        Explodes: Optional[bool] = None,
        Bounces: Optional[int] = None,
        MaxDistance: Optional[int] = None,
        Velocity: Optional[int] = None,
        RotationVelocity: Optional[int] = None,
        TailLength: Optional[int] = None,
        FireSound: Optional[str] = None,
        BounceSound: Optional[str] = None,
        CollisionSound: Optional[str] = None,
        MinAngleOffset: Optional[int] = None,
        MaxAngleOffset: Optional[int] = None,
        SpriteIndex: Optional[int] = None,
        Item: Optional[CommonFields] =None
    ):
        self.Id= Id
        self.Damage = Damage
        self.Explodes = Explodes
        self.Bounces = Bounces
        self.MaxDistance = MaxDistance
        self.Velocity = Velocity
        self.RotationVelocity = RotationVelocity
        self.TailLength = TailLength
        self.FireSound = FireSound
        self.BounceSound = BounceSound
        self.CollisionSound = CollisionSound
        self.MinAngleOffset = MinAngleOffset
        self.MaxAngleOffset = MaxAngleOffset
        self.SpriteIndex = SpriteIndex
        self.Item = Item



class WeaponsData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        Name: str,
        DisplayName: str,
        Description: str,
        Type: WeaponsType,
        Texture: str,
        SpriteIndex: int,
        MinDamage: int,
        MaxDamage: int,
        CanBeLostOnDeath: bool,
        Knockback: Optional[float] = None,
        Speed: Optional [int] = None, 
        Precision: Optional [int] = None,
        Defense: Optional [int] = None,
        AreaOfEffect: Optional [int] = None,
        CritChance: Optional [float] = None,
        CritMultiplier: Optional [float] = None,
        MineBaseLevel: Optional [int] = None,
        MineMinLevel: Optional [int] = None,
        Projectiles: Optional [Projectiles] = None,
        CustomFields: Optional[dict[str, Any]] = None
    ):
        super().__init__(key)

        self.Name = Name
        self.DisplayName = DisplayName
        self.Description = Description
        self.Type = Type
        self.Texture = Texture
        self.SpriteIndex = SpriteIndex
        self.MinDamage = MinDamage
        self.MaxDamage = MaxDamage
        self.CanBeLostOnDeath = CanBeLostOnDeath
        self.Knockback = Knockback
        self.Speed = Speed
        self.Precision = Precision
        self.Defense = Defense
        self.AreaOfEffect = AreaOfEffect
        self.CritChance = CritChance
        self.CritMultiplier = CritMultiplier
        self.MineBaseLevel = MineBaseLevel
        self.MineMinLevel = MineMinLevel
        self.Projectiles = Projectiles
        self.CustomFields = CustomFields
