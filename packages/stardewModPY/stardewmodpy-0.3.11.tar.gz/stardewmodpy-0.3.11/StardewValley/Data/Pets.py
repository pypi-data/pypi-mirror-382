from .model import modelsData
from typing import Optional, Any
from .XNA import Position, Rectangle
from .GameData import CommonFields


class PetGiftData(CommonFields):
    def __init__(
        self,
        *,
        Id:str,
        CommonFields: CommonFields,
        MinimumFriendshipThreshold: Optional[int] = None,
        Weight: Optional[float] = None
    ):
        super().__init__(None)
        self.Id = Id
        self.CommonFields = CommonFields
        self.MinimumFriendshipThreshold = MinimumFriendshipThreshold
        self.Weight = Weight


class BreedsData(modelsData):
    def __init__(
        self,
        *,
        Id: str,
        Texture: str,
        IconTexture: str,
        IconSourceRect: Rectangle,
        CanBeChosenAtStart: Optional[bool] = None,
        CanBeAdoptedFromMarnie: Optional[bool] = None,
        AdoptionPrice: Optional[int] = None,
        BarkOverride: Optional[str] = None,
        VoicePitch: Optional[float] = 1.0
    ):
        super().__init__(None)
        self.Id = Id
        self.Texture = Texture
        self.IconTexture = IconTexture
        self.IconSourceRect = IconSourceRect
        self.CanBeChosenAtStart = CanBeChosenAtStart
        self.CanBeAdoptedFromMarnie = CanBeAdoptedFromMarnie
        self.AdoptionPrice = AdoptionPrice
        self.BarkOverride = BarkOverride
        self.VoicePitch = VoicePitch

class SummitPerfectionEvent(modelsData):
    """
    Motion Position to getStr() not getJson()
    """
    def __init__(
        self,
        SourceRect: Rectangle,
        AnimationLength: int,
        Motion: Position,
        PingPong: bool
    ):
        self.SourceRect = SourceRect
        self.AnimationLength = AnimationLength
        self.Motion = Motion
        self.PingPong = PingPong

class BehaviorChanges(modelsData):
    def __init__(
        self,
        *,
        Weight:float,
        OutsideOnly:bool,
        UpBehavior:Optional[str] = None,
        DownBehavior:Optional[str] = None,
        LeftBehavior:Optional[str] = None,
        RightBehavior:Optional[str] = None,
        Behavior:Optional[str] = None
    ):
        self.Weight = Weight
        self.OutsideOnly = OutsideOnly
        self.UpBehavior = UpBehavior
        self.DownBehavior = DownBehavior
        self.LeftBehavior = LeftBehavior
        self.RightBehavior = RightBehavior
        self.Behavior = Behavior

class Animation(modelsData):
    def __init__(
        self,
        *,
        Frame: int,
        Duration: int,
        HitGround: bool,
        Jump: bool,
        Sound: Optional[str] = None,
        SoundRangeFromBorder: Optional[int] = None,
        SoundRange: Optional[int] = None,
        SoundIsVoice: Optional[bool] = None
    ):
        self.Frame = Frame
        self.Duration = Duration
        self.HitGround = HitGround
        self.Jump = Jump
        self.Sound = Sound
        self.SoundRangeFromBorder = SoundRangeFromBorder
        self.SoundRange = SoundRange
        self.SoundIsVoice = SoundIsVoice

class Behaviors(modelsData):
    def __init__(
        self,
        *,
        Id:str,
        Direction: Optional[str] = None,
        RandomizeDirection: Optional[bool] = None,
        IsSideBehavior: Optional[bool] = None,
        WalkInDirection: Optional[bool] = None,
        MoveSpeed: Optional[int] = None,
        SoundOnStart: Optional[str] = None,
        SoundRange: Optional[int] = None,
        SoundRangeFromBorder: Optional[int] = None,
        SoundIsVoice: Optional[bool] = None,
        AnimationEndBehaviorChanges: Optional[list[BehaviorChanges]] = None,
        TimeoutBehaviorChanges: Optional[list[BehaviorChanges]] = None,
        PlayerNearbyBehaviorChanges: Optional[list[BehaviorChanges]] = None,
        RandomBehaviorChanges: Optional[float] = None,
        JumpLandBehaviorChanges: Optional[list[BehaviorChanges]] = None,
        Duration: Optional[int] = None,
        MinimumDuration: Optional[int] = None,
        MaximumDuration: Optional[int] = None,
        RandomBehaviorChangeChance: Optional[float] = None,
        Animation: Optional[list[Animation]] = None,
        Shake: Optional[int] = None,
        LoopMode: Optional[str] = None,
        AnimationMinimumLoops:Optional[int] = None,
        AnimationMaximumLoops:Optional[int] = None
    ):
        self.Id = Id
        self.Direction = Direction
        self.RandomizeDirection = RandomizeDirection
        self.IsSideBehavior = IsSideBehavior
        self.WalkInDirection = WalkInDirection
        self.MoveSpeed = MoveSpeed
        self.SoundOnStart = SoundOnStart
        self.SoundRange = SoundRange
        self.SoundRangeFromBorder = SoundRangeFromBorder
        self.SoundIsVoice = SoundIsVoice
        self.AnimationEndBehaviorChanges = AnimationEndBehaviorChanges
        self.TimeoutBehaviorChanges = TimeoutBehaviorChanges
        self.PlayerNearbyBehaviorChanges = PlayerNearbyBehaviorChanges
        self.RandomBehaviorChanges = RandomBehaviorChanges
        self.JumpLandBehaviorChanges = JumpLandBehaviorChanges
        self.Duration = Duration
        self.MinimumDuration = MinimumDuration
        self.MaximumDuration = MaximumDuration
        self.RandomBehaviorChangeChance = RandomBehaviorChangeChance
        self.Animation = Animation
        self.Shake = Shake
        self.LoopMode = LoopMode
        self.AnimationMinimumLoops = AnimationMinimumLoops
        self.AnimationMaximumLoops = AnimationMaximumLoops

class PetsData(modelsData):
    def __init__(
        self,
        *,
        key: str,
        DisplayName: str,
        BarkSound: str,
        ContentSound: str,
        Breeds: list[BreedsData],
        RepeatContentSoundAfter: Optional[int] = None,
        EmoteOffset: Optional[Position] = None,
        EventOffset: Optional[Position] = None,
        AdoptionEventLocation: Optional[str] = None,
        AdoptionEventId: Optional[str] = None,
        SummitPerfectionEvent: Optional[SummitPerfectionEvent] = None,
        GiftChance: Optional[float] = None,
        Gifts: Optional[list[PetGiftData]] = None,
        MoveSpeed: Optional[int] = None,
        SleepOnBedChance: Optional[float] = None,
        SleepNearBedChance: Optional[float] = None,
        SleepOnRugChance: Optional[float] = None,
        Behaviors: Optional[list[Behaviors]] = None,
        CustomFields: Optional[dict[str, Any]] = None

    ):
        super().__init__(key)
        self.DisplayName = DisplayName
        self.BarkSound = BarkSound
        self.ContentSound = ContentSound
        self.Breeds = Breeds
        self.RepeatContentSoundAfter = RepeatContentSoundAfter
        self.EmoteOffset = EmoteOffset
        self.EventOffset = EventOffset
        self.AdoptionEventLocation = AdoptionEventLocation
        self.AdoptionEventId = AdoptionEventId
        self.SummitPerfectionEvent = SummitPerfectionEvent
        self.GiftChance = GiftChance
        self.Gifts = Gifts
        self.MoveSpeed = MoveSpeed
        self.SleepOnBedChance = SleepOnBedChance
        self.SleepNearBedChance = SleepNearBedChance
        self.SleepOnRugChance = SleepOnRugChance
        self.Behaviors = Behaviors
        self.CustomFields = CustomFields
