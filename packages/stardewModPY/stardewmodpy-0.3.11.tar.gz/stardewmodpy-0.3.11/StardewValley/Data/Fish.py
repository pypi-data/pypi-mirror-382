from .model import modelsData


class FishData(modelsData):
    def __init__(
        self, 
        key: str,
        name: str,
        chance_to_dart: str,
        darting_randomess: str,
        min_size: str,
        max_size: str,
        minTime_maxTime: str,
        season: str,
        weather: str,
        locations: str,
        max_depth: str,
        spawn_multiplier: str,
        depth_multiplier: str,
        fishing_level: str,
        first_catch_tutorial_eligible: str
    ):
        super().__init__(key)
        self.name = name
        self.chance_to_dart = chance_to_dart
        self.darting_randomess = darting_randomess
        self.min_size = min_size
        self.max_size = max_size
        self.minTime_maxTime = minTime_maxTime
        self.season = season
        self.weather = weather
        self.locations = locations
        self.max_depth = max_depth
        self.spawn_multiplier = spawn_multiplier
        self.depth_multiplier = depth_multiplier
        self.fishing_level = fishing_level
        self.first_catch_tutorial_eligible = first_catch_tutorial_eligible


    def getJson(self) -> str:
        return f"{self.name}/{self.chance_to_dart}/{self.darting_randomess}/{self.min_size}/{self.max_size}/{self.minTime_maxTime}/{self.season}/{self.weather}/{self.locations}/{self.max_depth}/{self.spawn_multiplier}/{self.depth_multiplier}/{self.fishing_level}/{self.first_catch_tutorial_eligible}"
