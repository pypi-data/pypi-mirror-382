from __future__ import annotations
from .model import modelsData
from typing import Optional, Tuple
from .XNA import Rectangle, Position
from .GameData import Direction

directions ={
    "Up":0,
    "Right":1,
    "Down":2,
    "Left":3
}

class Move:
    def __init__(self, actor: str, X: Optional[int] = 0, Y: Optional[int] = 0, direction: Optional[Direction] = None, continue_: Optional[bool] = False):
        if X != 0 and Y != 0:
            raise ValueError("It is not possible to set both X and Y at the same time.")
        self.actor = actor
        self.X = X
        self.Y = Y
        if direction is None:
            self.direction = 0
        else:
            self.direction = directions[direction]
        self.continue_ = continue_


    def getJson(self) -> str:
        json = f"{self.actor} {self.X} {self.Y} {self.direction}"

        if self.continue_:
            json += f" {str(self.continue_).lower()}"

        return json

class Precondition:
    def __init__(
        self,
        *, 
        ID:str,
        GameStateQuery: Optional[str] = None,
        ActiveDialogueEvent: Optional[str] = None,
        DayOfMonth: Optional[str] = None,
        DayOfWeek: Optional[str] = None,
        FestivalDay: Optional[bool] = None,
        GoldenWalnuts: Optional[int] = None,
        InUpgradedHouse: Optional[int] = None,
        NPCVisible: Optional[str] = None,
        NpcVisibleHere: Optional[str] = None,
        Random: Optional[float] = None,
        Season: Optional[str] = None,
        Time: Optional[tuple[int, int]] = None,  # Para parâmetros como Time <min> <max>
        UpcomingFestival: Optional[int] = None,
        Weather: Optional[str] = None,
        WorldState: Optional[str] = None,
        Year: Optional[int] = None,
        ChoseDialogueAnswers: Optional[str] = None,
        Dating: Optional[str] = None,
        EarnedMoney: Optional[int] = None,
        FreeInventorySlots: Optional[int] = None,
        Friendship: Optional[tuple[str, int]] = None,  # Para Friendship <name> <number>
        Gender: Optional[str] = None,
        HasItem: Optional[str] = None,
        HasMoney: Optional[int] = None,
        LocalMail: Optional[str] = None,
        MissingPet: Optional[str] = None,
        ReachedMineBottom: Optional[int] = None,
        Roommate: Optional[bool] = None,
        SawEvent: Optional[str] = None,
        SawSecretNote: Optional[int] = None,
        Shipped: Optional[tuple[str, int]] = None,  # Para Shipped <item ID> <number>
        Skill: Optional[tuple[str, int]] = None,  # Para Skill <name> <level>
        Spouse: Optional[str] = None,
        SpouseBed: Optional[bool] = None,
        Tile: Optional[tuple[int, int]] = None,  # Para Tile <x> <y>
        CommunityCenterOrWarehouseDone: Optional[bool] = None,
        DaysPlayed: Optional[int] = None,
        HostMail: Optional[str] = None,
        HostOrLocalMail: Optional[str] = None,
        IsHost: Optional[bool] = None,
        JojaBundlesDone: Optional[bool] = None,
        SendMail: Optional[str] = None,
        NotActiveDialogueEvent: Optional[bool] = None,
        NotCommunityCenterOrWarehouseDone: Optional[bool] = None,
        NotDayOfWeek: Optional[str] = None,
        NotFestivalDay: Optional[bool] = None,
        NotHostMail: Optional[str] = None,
        NotHostOrLocalMail: Optional[str] = None,
        NotLocalMail: Optional[str] = None,
        NotRoommate: Optional[bool] = None,
        NotSawEvent: Optional[str] = None,
        NotSeason: Optional[str] = None,
        NotSpouse: Optional[str] = None,
        NotUpcomingFestival: Optional[int] = None
    ):
        
        self.json = ID

        # Adicionando as variáveis para criar a string json
        if GameStateQuery is not None:
            self.json += f"/G {GameStateQuery}"
        if ActiveDialogueEvent is not None:
            self.json += f"/ActiveDialogueEvent {ActiveDialogueEvent}"
        if DayOfMonth is not None:
            self.json += f"/u {DayOfMonth}"
        if DayOfWeek is not None:
            self.json += f"/d {DayOfWeek}"
        if FestivalDay is not None:
            self.json += "/FestivalDay"
        if GoldenWalnuts is not None:
            self.json += f"/N {GoldenWalnuts}"
        if InUpgradedHouse is not None:
            self.json += f"/L {InUpgradedHouse}"
        if NPCVisible is not None:
            self.json += f"/v {NPCVisible}"
        if NpcVisibleHere is not None:
            self.json += f"/p {NpcVisibleHere}"
        if Random is not None:
            self.json += f"/r {Random}"
        if Season is not None:
            self.json += f"/Season {Season}"
        if Time is not None:
            min_time, max_time = Time
            self.json += f"/t {min_time} {max_time}"
        if UpcomingFestival is not None:
            self.json += f"/UpcomingFestival {UpcomingFestival}"
        if Weather is not None:
            self.json += f"/w {Weather}"
        if WorldState is not None:
            self.json += f"/WorldState {WorldState}"
        if Year is not None:
            self.json += f"/y {Year}"
        if ChoseDialogueAnswers is not None:
            self.json += f"/q {ChoseDialogueAnswers}"
        if Dating is not None:
            self.json += f"/D {Dating}"
        if EarnedMoney is not None:
            self.json += f"/m {EarnedMoney}"
        if FreeInventorySlots is not None:
            self.json += f"/c {FreeInventorySlots}"
        if Friendship is not None:
            name, number = Friendship
            self.json += f"/f {name} {number}"
        if Gender is not None:
            self.json += f"/g {Gender}"
        if HasItem is not None:
            self.json += f"/i {HasItem}"
        if HasMoney is not None:
            self.json += f"/M {HasMoney}"
        if LocalMail is not None:
            self.json += f"/n {LocalMail}"
        if MissingPet is not None:
            self.json += f"/h {MissingPet}"
        if ReachedMineBottom is not None:
            self.json += f"/b {ReachedMineBottom}"
        if Roommate is not None:
            self.json += "/R"
        if SawEvent is not None:
            self.json += f"/e {SawEvent}"
        if SawSecretNote is not None:
            self.json += f"/S {SawSecretNote}"
        if Shipped is not None:
            item_id, number = Shipped
            self.json += f"/s {item_id} {number}"
        if Skill is not None:
            skill_name, level = Skill
            self.json += f"/Skill {skill_name} {level}"
        if Spouse is not None:
            self.json += f"/O {Spouse}"
        if SpouseBed is not None:
            self.json += "/B"
        if Tile is not None:
            x, y = Tile
            self.json += f"/a {x} {y}"
        if CommunityCenterOrWarehouseDone is not None:
            self.json += "/C"
        if DaysPlayed is not None:
            self.json += f"/j {DaysPlayed}"
        if HostMail is not None:
            self.json += f"/Hn {HostMail}"
        if HostOrLocalMail is not None:
            self.json += f"/n {HostOrLocalMail}"
        if IsHost is not None:
            self.json += "/H"
        if JojaBundlesDone is not None:
            self.json += "/J"
        if SendMail is not None:
            self.json += f"/x {SendMail}"
        if NotActiveDialogueEvent is not None:
            self.json += "/!A"
        if NotCommunityCenterOrWarehouseDone is not None:
            self.json += "/!X"
        if NotDayOfWeek is not None:
            self.json += f"/!d {NotDayOfWeek}"
        if NotFestivalDay is not None:
            self.json += "/!F"
        if NotHostMail is not None:
            self.json += f"/!Hl {NotHostMail}"
        if NotHostOrLocalMail is not None:
            self.json += f"/!*l {NotHostOrLocalMail}"
        if NotLocalMail is not None:
            self.json += f"/!l {NotLocalMail}"
        if NotRoommate is not None:
            self.json += "/!R"
        if NotSawEvent is not None:
            self.json += f"/!k {NotSawEvent}"
        if NotSeason is not None:
            self.json += f"/!z {NotSeason}"
        if NotSpouse is not None:
            self.json += f"/!o {NotSpouse}"
        if NotUpcomingFestival is not None:
            self.json += f"/!U {NotUpcomingFestival}"
    
    def getJson(self) -> str:
        return self.json if self.json else ""



class CharacterID:
    def __init__(self, id:str, X:int, Y:int, direction:Direction):
        global directions
        self.json=f"{id} {X} {Y} {directions[direction]}"
    
    def getJson(self) -> str:
        return self.json

class Eventscripts:
    def __init__(
        self,
        music: str,
        coordinates: Tuple[int, int],
        characterID: list[CharacterID],

    ):
        self.music=music
        self.coordinates=f"{coordinates[0]} {coordinates[1]}"
        self.characterID=" ".join([character.getJson() for character in characterID])
        self.commands=[]
    
    def action(self, action:str):
        self.commands.append(f"action {action}")
    

    def addBigProp(self, x:int, y:int, objectID:str):
        self.commands.append(f"addBigProp {x} {y} {objectID}")
    
    def addConversationTopic(self, id:str, length:int):
        self.commands.append(f"addConversationTopic {id} {length}")
    
    def addCookingRecipe(self, recipe: str):
        self.commands.append(f"addCookingRecipe {recipe}")
    
    def addCraftingRecipe(self, recipe: str):
        self.commands.append(f"addCraftingRecipe {recipe}")
    
    def addFloorProp(self, prop_index: int, x: int, y: int, solid_width: int = 1, solid_height: int = 1, display_height: int = 1):
        self.commands.append(f"addFloorProp {prop_index} {x} {y} {solid_width} {solid_height} {display_height}")
    
    def addItem(self, item_id: str, count: int = 1, quality: int = 0):
        self.commands.append(f"addItem {item_id} {count} {quality}")
    
    def addLantern(self, row_in_texture: int, x: int, y: int, light_radius: int):
        self.commands.append(f"addLantern {row_in_texture} {x} {y} {light_radius}")
    
    def addObject(self, x: int, y: int, item_id: str, layer: int = -1):
        self.commands.append(f"addObject {x} {y} {item_id} {layer}")
    
    def addProp(self, prop_index: int, x: int, y: int, solid_width: int = 1, solid_height: int = 1, display_height: int = 1):
        self.commands.append(f"addProp {prop_index} {x} {y} {solid_width} {solid_height} {display_height}")
    
    def addQuest(self, quest_id: str):
        self.commands.append(f"addQuest {quest_id}")
    
    def addSpecialOrder(self, order_id: str):
        self.commands.append(f"addSpecialOrder {order_id}")
    
    def addTemporaryActor(self, sprite_asset_name: str, sprite_width: int, sprite_height: int, tile_x: int, tile_y: int, direction: Direction, breather: bool = True, actor_type: str = 'Character', override_name: str = ''):
        self.commands.append(f"addTemporaryActor \"{sprite_asset_name}\" {sprite_width} {sprite_height} {tile_x} {tile_y} {directions[direction]} {'true' if breather else 'false'} {actor_type} {override_name}")
    
    def advancedMove(self, actor: str, loop: bool, *moves: int) -> str:
        self.commands.append(f"advancedMove {actor} {int(loop)} {' '.join(str(m) for m in moves)}")

    def ambientLight(self, r: int, g: int, b: int) -> str:
        self.commands.append(f"ambientLight {r} {g} {b}")

    def animalNaming(self) -> str:
        self.commands.append("animalNaming")

    def animate(self, actor: str, flip: bool, loop: bool, frame_duration: int, *frames: int) -> None:
        self.commands.append(f"animate {actor} {int(flip)} {int(loop)} {frame_duration} {' '.join(str(f) for f in frames)}")

    def attachCharacterToTempSprite(self, actor: str) -> None:
        self.commands.append(f"attachCharacterToTempSprite {actor}")

    def awardFestivalPrize(self, item_type: Optional[str] = None, item_id: Optional[int] = None) -> None:
        if item_type and item_id is not None:
            self.commands.append(f"awardFestivalPrize {item_type} {item_id}")
        else:
            self.commands.append("awardFestivalPrize")

    def beginSimultaneousCommand(self, *commands: str) -> None:
        self.commands.append(f"beginSimultaneousCommand/{'/'.join(commands)}/endSimultaneousCommand")

    def broadcastEvent(self, useLocalFarmer: bool = False) -> None:
        self.commands.append(f"broadcastEvent {int(useLocalFarmer)}")

    def changeLocation(self, location: str) -> None:
        self.commands.append(f"changeLocation {location}")

    def changeMapTile(self, layer: int, x: int, y: int, tile_index: int) -> None:
        self.commands.append(f"changeMapTile {layer} {x} {y} {tile_index}")

    def changeName(self, actor: str, display_name: str) -> None:
        self.commands.append(f"changeName {actor} {display_name}")

    def changePortrait(self, npc: str, portrait: Optional[str] = None) -> None:
        if portrait:
            self.commands.append(f"changePortrait {npc} {portrait}")
        else:
            self.commands.append(f"changePortrait {npc}")

    def changeSprite(self, actor: str, sprite: Optional[str] = None) -> None:
        if sprite:
            self.commands.append(f"changeSprite {actor} {sprite}")
        else:
            self.commands.append(f"changeSprite {actor}")

    def changeToTemporaryMap(self, map: str, pan: Optional[bool] = None) -> None:
        if pan is not None:
            self.commands.append(f"changeToTemporaryMap {map} {int(pan)}")
        else:
            self.commands.append(f"changeToTemporaryMap {map}")

    def characterSelect(self) -> None:
        self.commands.append("characterSelect")

    def cutscene(self, cutscene: str) -> None:
        self.commands.append(f"cutscene {cutscene}")

    def doAction(self, x: int, y: int) -> None:
        self.commands.append(f"doAction {x} {y}")

    def dump(self, group: str) -> None:
        self.commands.append(f"dump {group}")
        
    def elliotbooktalk(self) -> None:
        self.commands.append("elliotbooktalk")

    def emote(self, actor: str, emote_id: int, continue_: bool = False) -> None:
        self.commands.append(f"emote {actor} {emote_id}" + (" true" if continue_ else ""))

    def end(self) -> None:
        self.commands.append("end")

    def endbed(self) -> None:
        self.commands.append("end bed")

    def endbeginGame(self) -> None:
        self.commands.append("end beginGame")
    
    def endcredits(self) -> None:
        self.commands.append("end credits")

    def enddialogue(self, npc: str, text: str) -> None:
        self.commands.append(f'end dialogue {npc} "{text}"')

    def enddialogueWarpOut(self, npc: str, text: str) -> None:
        self.commands.append(f'end dialogueWarpOut {npc} "{text}"')

    def endinvisible(self, npc: str) -> None:
        self.commands.append(f"end invisible {npc}")

    def endinvisibleWarpOut(self, npc: str) -> None:
        self.commands.append(f"end invisibleWarpOut {npc}")

    def endnewDay(self) -> None:
        self.commands.append("end newDay")

    def endposition(self, x: int, y: int) -> None:
        self.commands.append(f"end position {x} {y}")

    def endwarpOut(self) -> None:
        self.commands.append("end warpOut")

    def endwedding(self) -> None:
        self.commands.append("end wedding")

    

    def eventSeen(self, event_id: int, seen: bool = True) -> None:
        self.commands.append(f"eventSeen {event_id} {'true' if seen else 'false'}")

    def extendSourceRect(self, actor: str) -> None:
        self.commands.append(f"extendSourceRect {actor} reset")

    def extendSourceRect(self, actor: str, horizontal: int, vertical: int, ignore_updates: bool = False) -> None:
        self.commands.append(f"extendSourceRect {actor} {horizontal} {vertical}" + (" true" if ignore_updates else ""))


    def eyes(self, eyes: int, blink: int = -1000) -> None:
        self.commands.append(f"eyes {eyes} {blink}")

    def faceDirection(self, actor: str, direction: Direction, continue_: bool = False) -> None:
        self.commands.append(f"faceDirection {actor} {directions[direction]}" + (" true" if continue_ else ""))

    def fade(self, unfade: bool = False) -> None:
        self.commands.append("fade unfade" if unfade else "fade")

    def farmerAnimation(self, anim: str) -> None:
        self.commands.append(f"farmerAnimation {anim}")

    def farmerEat(self, object_id: int) -> None:
        self.commands.append(f"farmerEat {object_id}")

    def fork(self, event_id: int, req: str = None) -> None:
        self.commands.append(f"fork {req} {event_id}" if req else f"fork {event_id}")

    def friendship(self, npc: str, amount: int) -> None:
        self.commands.append(f"friendship {npc} {amount}")

    def globalFade(self, speed: float = 0.5, continue_: bool = False) -> None:
        self.commands.append(f"globalFade {speed}" + (" true" if continue_ else ""))

    def globalFadeToClear(self, speed: float = 0.5, continue_: bool = False) -> None:
        self.commands.append(f"globalFadeToClear {speed}" + (" true" if continue_ else ""))

    def glow(self, r: int, g: int, b: int, hold: bool = False) -> None:
        self.commands.append(f"glow {r} {g} {b}" + (" true" if hold else ""))

    def grandpaCandles(self) -> None:
        self.commands.append("grandpaCandles")


    def haltMusic(self) -> None:
        self.commands.append("haltMusic")

    def happyBirthday(self, npc: str) -> None:
        self.commands.append(f"happyBirthday {npc}")

    def hideTool(self) -> None:
        self.commands.append("hideTool")

    def holdItemAboveHead(self, item_id: int) -> None:
        self.commands.append(f"holdItemAboveHead {item_id}")

    def invisible(self, actor: str, invisible: bool = True) -> None:
        self.commands.append(f"invisible {actor} {'true' if invisible else 'false'}")

    def junimoNote(self, note_id: int) -> None:
        self.commands.append(f"junimoNote {note_id}")

    def lantern(self, on: bool = True) -> None:
        self.commands.append(f"lantern {'on' if on else 'off'}")

    def grandpaEvaluation(self) -> None:
        self.commands.append("grandpaEvaluation")

    def grandpaEvaluation2(self) -> None:
        self.commands.append("grandpaEvaluation2")

    def halt(self) -> None:
        self.commands.append("halt")

    def hideShadow(self, actor: str, hide: bool) -> None:
        self.commands.append(f"hideShadow {actor} {'true' if hide else 'false'}")

    def hospitaldeath(self) -> None:
        self.commands.append("hospitaldeath")

    def ignoreCollisions(self, character_id: str) -> None:
        self.commands.append(f"ignoreCollisions {character_id}")

    def ignore_event_tile_offset(self) -> None:
        self.commands.append("ignoreEventTileOffset")

    def ignoreMovementAnimation(self, actor: str, ignore: bool = True) -> None:
        self.commands.append(f"ignoreMovementAnimation {actor} {'true' if ignore else 'false'}")

    def itemAboveHead(self, item: str) -> None:
        self.commands.append(f"itemAboveHead {item}")
        
    def jump(self, actor: str, intensity: int = 8) -> None:
        self.commands.append(f"jump {actor} {intensity}")

    def loadActions(self, layer: str) -> None:
        self.commands.append(f"loadActions {layer}")
        
    def makeInvisible(self, x: int, y: int, x_dimension: int, y_dimension: int) -> None:
        self.commands.append(f"makeInvisible {x} {y} {x_dimension} {y_dimension}")



    def mail(self, letter:str):
        self.commands.append(f"mail {letter}")
        
    def mailReceived(self, letter:str, add:bool=True):
        self.commands.append(f"mailReceived {letter} {'true' if add else 'false'}")

    def mailToday(self, letter:str):
        self.commands.append(f"mailToday {letter}")

    def message (self, text:str):
        self.commands.append(f"message \"{text}\"")
        
    def minedeath(self) -> None:
        self.commands.append("minedeath")
        
    def money (self, amount:int) -> None:
        self.commands.append(f"money {amount}")
        
    def move (self, moves: list[Move]) -> None:
        move = "move "
        move += " ".join([move.getJson() for move in moves])
        self.commands.append(move)

    def pause (self, duration:int) -> None:
        self.commands.append(f"pause {duration}")
        
    def playMusic (self, music:str) -> None:
        self.commands.append(f"playMusic {music}")
        
    def playSound (self, track:str) -> None:
        self.commands.append(f"playSound {track}")
        
    def playerControl (self) -> None:
        self.commands.append("playerControl")
        
    def positionOffset (self, actor:str, x:int, y:int, Continue:bool) -> None:
        self.commands.append(f"positionOffset {actor} {x} {y} {'true' if Continue else 'false'}")
        
    def proceedPosition (self, actor:str) -> None:
        self.commands.append(f"proceedPosition {actor}")
        
    def questionnull(self, question:str, answer1:str, answer2:str) -> None:
        self.commands.append(f"question null {question}#{answer1}#{answer2}")
        
    def questionfork(self, answerindex:str, question:str, answers:list[str]) -> None:
        self.commands.append(f"question fork {answerindex} \"{question}#{'#'.join(answers)}\"")
        
    def questionAnswered (self, answer:str, answered:bool) -> None:
        self.commands.append(f"questionAnswered {answer} {'true' if answered else 'false'}")
        
    def quickQuestion(self, question: str, answers: list[str], answerscripts: list[AnswerScripts]) -> None:
        self.commands.append(f"quickQuestion {question}#{'#'.join(answers)}(break){"(break)".join([answerScript.getJson() for answerScript in answerscripts])}")

    def removeItem(self, item_id: str, count: int = None) -> None:
        self.commands.append(f"removeItem {item_id}" + (f" {count}" if count else ""))
        
    def removeObject(self, x: int, y: int) -> None:
        self.commands.append(f"removeObject {x} {y}")
        
    def removeQuest(self, quest_id: str) -> None:
        self.commands.append(f"removeQuest {quest_id}")
        
    def removeSpecialOrder(self, order_id: str) -> None:
        self.commands.append(f"removeSpecialOrder {order_id}")
        
    def removeSprite(self, x: int, y:int) -> None:
        self.commands.append(f"removeSprite {x} {y}")
        
    def removeTemporalySprites(self) -> None:
        self.commands.append("removeTemporalySprites")
        
    def removeTile(self, x:int, y:int, layer:str) -> None:
        self.commands.append(f"removeTile {x} {y} {layer}")
        
    def replaceWithClone(self, npc:str) -> None:
        self.commands.append(f"replaceWithClone {npc}")
        
    def resetVariable(self) -> None:
        self.commands.append("resetVariable")
        
    def rustyKey(self) -> None:
        self.commands.append("rustyKey")
        
    def screenFlash(self, alpha:float=0) -> None:
        self.commands.append(f"screenFlash {alpha}")
        
    def setRunning(self) -> None:
        self.commands.append("setRunning")
        
    def setSkipActions(self, actions:str) -> None:
        self.commands.append(f"setSkipActions {actions}")
        
    def shake(self, actor:str, duration:int=8) -> None:
        self.commands.append(f"shake {actor} {duration}")
        
    def showFrame(self, actor: str, frameID: str) -> None:
        self.commands.append(f"showFrame {actor} {frameID}")

    def showFrameFarmer(self, frame: str, flip: bool) -> None:
        self.commands.append(f"showFrameFarmer {frame} {'true' if flip else 'false'}")
        
    def skippable(self) -> None:
        self.commands.append("skippable")

    def speak(self, character: str, text: str):
        self.commands.append(f'speak {character} "{text}"')

    def specificTemporarySprite(self, sprite: str, otherparams: str):
        self.commands.append(f"specificTemporarySprite {sprite} {otherparams}")
    
    def speedfarmer(self, modifier:str):
        self.commands.append(f"speed farmer {modifier}")
    
    def speed(self, actor:str, speed:str):
        self.commands.append(f"speed {actor} {speed}")
    
    def splitSpeak(self, actor: str, text: str):
        self.commands.append(f"splitSpeak {actor} \" {text} \"")

    def startJittering(self):
        self.commands.append("startJittering")
    
    def stopAdvancedMoves(self):
        self.commands.append("stopAdvancedMoves")
    
    def stopAnimationfarmer(self):
        self.commands.append("stopAnimation farmer")
    
    def stopAnimation(self, actor: str, endframe:int):
        self.commands.append(f"stopAnimation {actor} {endframe}")
    
    def stopGlowing(self):
        self.commands.append("stopGlowing")
    
    def stopJittering(self):
        self.commands.append("stopJittering")

    def stopMusic(self):
        self.commands.append("stopMusic")
    
    def stopRunning(self):
        self.commands.append("stopRunning")
    
    def stopSound(self, soundID:str, immediate:bool=False):
        self.commands.append(f"stopSound {soundID} {'true' if immediate else 'false'}")
    
    def stopSwimming(self, actor:str):
        self.commands.append(f"stopSwimming {actor}")
    
    def swimming(self, actor:str):
        self.commands.append(f"swimming {actor}")
    
    def switchEvent(self, eventID:int):
        self.commands.append(f"switchEvent {eventID}")
    
    def temporarySprite(self, x:int, y:int, rowintexture:int, animationlength:int, animationinterval:int, flipped:bool, layerdepth:float):
        self.commands.append(f"temporarySprite {x} {y} {rowintexture} {animationlength} {animationinterval} {'true' if flipped else 'false'} {layerdepth}")

    def temporaryAnimatedSprite(self, texture: str, rectangle:Rectangle, interval:int, frames: int, loops:int, tile:Position, flicker:bool, flip:bool, sorttileY:int, alphafade: float, scale:float, scalechange:float, rotation:float, rotationchange:float, flags:list[str]):
        self.commands.append(f"temporaryAnimatedSprite {texture} {rectangle.getJson()} {interval} {frames} {loops} {tile.getJson()} {'true' if flicker else 'false'} {'true' if flip else 'false'} {sorttileY} {alphafade} {scale} {scalechange} {rotation} {rotationchange} {' '.join(flags)}")
    
    def textAboveHead(self, actor:str, text:str):
        self.commands.append(f"textAboveHead {actor} \"{text}\"")
    
    def tossConcession(self, actor:str, concessionId:str):
        self.commands.append(f"tossConcession {actor} {concessionId}")
    
    def translateName(self, actor:str, translationkey:str):
        self.commands.append(f"translateName {actor} {translationkey}")
    
    def tutorialMenu(self):
        self.commands.append("tutorialMenu")
    
    def updateMinigame(self, eventdata:str):
        self.commands.append(f"updateMinigame {eventdata}")
    
    def viewportmove(self, X:int, Y:int, duration:str):
        self.commands.append(f"viewport move {X} {Y} {duration}")
    
    def viewport (self, X:int, Y:int, commands:Optional[str]=None):
        res= f"viewport {X} {Y}"
        if commands is not None:
            res+=" "+commands
        self.commands.append(res)
    
    def waitForAllStationary(self):
        self.commands.append("waitForAllStationary")
    
    def waitForOtherPlayers(self):
        self.commands.append("waitForOtherPlayers")
    
    def warp(self, actor:str, x:int, y:int, Continue:bool=False):
        self.commands.append(f"warp {actor} {x} {y}{' continue' if Continue else ''}")

    def warpFarmers(self, code:str):
        self.commands.append(f"warpFarmers {code}")
    
    def getJson(self) -> str:
        return f"{self.music}/{self.coordinates}/{self.characterID}/{'/'.join(self.commands)}" if self.commands else f"{self.music}/{self.coordinates}/{self.characterID}"

class AnswerScripts(Eventscripts):
    def __init__(self):
        self.commands=[]
    
    def getJson(self):
        return f"{'\\'.join(self.commands)}"
    
class EventData(modelsData):
    def __init__(
        self, 
        key:Precondition,
        value:Eventscripts
    ):
        super().__init__(key.getJson())
        self.value = value.getJson()
    
    def getJson(self) -> str:
        return self.value

