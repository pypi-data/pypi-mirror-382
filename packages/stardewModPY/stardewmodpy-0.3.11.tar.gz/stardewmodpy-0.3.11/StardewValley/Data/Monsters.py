from .model import modelsData


class ObjectsToDropData(modelsData):
    def __init__(
        self,
        IdItem: str,
        Probability: float
    ):
        super().__init__(None)
        self.IdItem = IdItem
        self.Probability = str((Probability / 100))[1:5] if Probability < 100 and Probability > 0.1 else ".001"


    def getJson(self) -> str:
        return f"{self.IdItem} {self.Probability}"


class MonstersData(modelsData):
    def __init__(
        self,
        key: str,
        display_name: str,
        health: int,
        damage: int,
        minimum_coins_to_drop: int,
        maximum_coins_to_drop: int,
        glider: bool,
        duration_of_random_movements: int,
        objects_to_drop: list[ObjectsToDropData],
        defense: int,
        jitteriness: float,
        distance_threshold_for_moving_towards_player: int,
        speed: int,
        chance_of_attacks_missing: float,
        mine_monster: bool,
        experience_gained: int
    ):
        super().__init__(key)
        self.health = health
        self.damage = damage
        self.minimum_coins_to_drop = minimum_coins_to_drop
        self.maximum_coins_to_drop = maximum_coins_to_drop
        self.glider = "true" if glider else "false"
        self.duration_of_random_movements = duration_of_random_movements
        self.objects_to_drop = objects_to_drop
        self.defense = defense
        self.jitteriness = str((jitteriness / 100))[1:5] if jitteriness < 100 and jitteriness > 0.1 else ".001"
        self.distance_threshold_for_moving_towards_player = distance_threshold_for_moving_towards_player
        self.speed = speed
        self.chance_of_attacks_missing = str((chance_of_attacks_missing / 100))[1:5] if chance_of_attacks_missing < 100 and chance_of_attacks_missing > 0.1 else ".001"
        self.mine_monster = "true" if mine_monster else "false"
        self.experience_gained = experience_gained
        self.display_name = display_name


    def getJson(self) -> str:
        return f"{self.health}/{self.damage}/{self.minimum_coins_to_drop}/{self.maximum_coins_to_drop}/{self.glider}/{self.duration_of_random_movements}/{" ".join(item.getJson() for item in self.objects_to_drop)}/{self.defense}/{self.jitteriness}/{self.distance_threshold_for_moving_towards_player}/{self.speed}/{self.chance_of_attacks_missing}/{self.mine_monster}/{self.experience_gained}/{self.display_name}"
