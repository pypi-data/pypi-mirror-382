from .model import modelsData


class FurnitureData(modelsData):
    def __init__(
        self,
        key: str,
        name: str,
        type: str,
        tilesheet_size: int,
        bounding_box_size: int,
        rotations: int,
        price: int,
        placement_restriction: int,
        display_name: str,
        sprite_index: int,
        texture: str,
        off_limits_for_random_sale: bool,
        context_tags: str
    ):
        super().__init__(key)
        self.name = name
        self.type = type
        self.tilesheet_size = tilesheet_size
        self.bounding_box_size = bounding_box_size
        self.rotations = rotations
        self.price = price
        self.placement_restriction = placement_restriction
        self.display_name = display_name
        self.sprite_index = sprite_index
        self.texture = texture
        self.off_limits_for_random_sale = "true" if off_limits_for_random_sale else "false"
        self.context_tags = context_tags


    def getJson(self) -> str:
        return f"{self.name}/{self.type}/{self.tilesheet_size}/{self.bounding_box_size}/{self.rotations}/{self.price}/{self.placement_restriction}/{self.display_name}/{self.sprite_index}/{self.texture}/{self.off_limits_for_random_sale}/{self.context_tags}"
