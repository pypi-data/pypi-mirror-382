class AquariumType:
    Eel="eel"
    Cephalopod="cephalopod"
    Crawl="crawl"
    Ground="ground"
    Fish="fish"
    Front_crawl="front_crawl"

class MusicContext:
    Default="Default"
    SubLocation="SubLocation"
           
class AudioCategory:
    Default="Default"
    Music="Music"
    Sound="Sound"
    Ambient="Ambient"
    Footsteps="Footsteps"

class Fragility:
    PickUpWithAnyTool = 0
    DestroyedIfHitWithAxeHoePickaxe = 1
    CantBeRemovedOncePlaced = 2

class PreserveType:
    Jelly="Jelly"
    Juice="Juice"
    Pickle="Pickle"
    Roe="Roe"
    AgedRoe="AgedRoe"
    Wine="Wine"

class Modification:
    Multiply="Multiply"
    Add="Add"
    Subtract="Subtract"
    Divide="Divide"
    Set="Set"

class GeneralType:
    Basic="Basic"
    Arch="Arch"
    Minerals="Minerals"
    Litter="Litter"
    Quest="Quest"
    Crafting="Crafting"
    Fish="Fish"
    Cooking="Cooking"
    Seeds="Seeds"
    Ring="Ring"
    Interactive="interactive"
    asdf="asdf"

class Duration:
    Day="Day"
    ThreeDays="ThreeDays"
    Week="Week"
    TwoWeeks="TwoWeeks"
    Month="Month"

class ObjectivesTypes:
    Collect="Collect"    
    Deliver="Deliver"    
    Fish="Fish"    
    Gift="Gift"
    JKScore="JKScore"    
    ReachMineFloor="ReachMineFloor"    
    Ship="Ship"    
    Donate="Donate"    
    Slay="Slay"

class QuestTypes:
    Basic="Basic"    
    Crafting="Crafting"    
    Location="Location"    
    Building="Building"
    ItemDelivery="ItemDelivery"
    Monster="Monster"
    ItemHarvest="ItemHarvest"
    LostItem="LostItem"
    SecretLostItem="SecretLostItem"
    Social="Social"

class Season:
    Spring="Spring"        
    Summer="Summer"        
    Fall="Fall"        
    Winter="Winter"

class Gender:
    Male="Male"
    Female="Female"
    Undefined="Undefined"

class Age:
    Adult="Adult"
    Teen="Teen"
    
    

class Social:
    Neutral="Neutral"
    
class Manner(Social):
    Polite="Polite"    
    Rude="Rude"

class SocialAnxiety(Social):
    Outgoing="Outgoing"
    
    Shy="Shy"

class Optimism(Social):
    Negative="Negative"
    Positive="Positive"


class HomeRegion:
    Town="Town"    
    Desert="Desert"
    Other="Other"


class Calendar:
    HiddenAlways="HiddenAlways"    
    HiddenUntilMet="HiddenUntilMet"    
    AlwaysShown="AlwaysShown"
        

class SocialTab(Calendar):
    UnknownUntilMet="UnknownUntilMet"


class EndSlideShow:
    Hidden="Hidden"        
    MainGroup="MainGroup"
    TrailingGroup="TrailingGroup"

class StackSizeVisibility:
    Hide="Hide"    
    Show="Show"    
    ShowIfMultiple="ShowIfMultiple"

class Quality:
    Normal=0
    Silver=1
    Gold=2
    Iridium=3

class QualityModifierMode:
    Stack="Stack"
    Minimum="Minimum"
    Maximum="Maximum"
        
class AvailableStockLimit:
    none="None"  
    Player="Player"    
    Global="Global"

class ToolUpgradeLevel:
    Normal=0
    Copper=1
    Steel=2
    Gold=3
    IridiumTool=4
    BambooPole=0
    TrainingRod=1
    FiberglassRod=2
    IridiumRod=3
    AdvancedIridiumRod=4

class Trigger:
    DayStarted="DayStarted"
    DayEnding="DayEnding"
    LocationChanged="LocationChanged"

class mailType:
    Tomorrow="tomorrow"
    Now="now"
    Received="received"
    All="all"

class WeaponsType:
    StabbingSword = 0
    Dagger = 1
    Club = 2
    Hammer = 2
    SlashingSword = 3

class ChopItemsSize:
    Seed="Seed"
    Sprout="Sprout"
    Sapling="Sapling"
    Bush="Bush"
    Tree="Tree"
    Both="Both"

class Result:
    Default="Default"
    Allow="Allow"
    Deny="Deny"

class PlantedIn:
    Ground="Ground"
    GardenPot="GardenPot"
    any="Any"

class Direction:
    Down="Down"
    Left="Left"
    Right="Right"
    Up="Up"