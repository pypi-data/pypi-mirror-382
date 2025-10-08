from .model import modelsData


class ConcessionsData(modelsData):
    def __init__(
        self, 
        *,
        key: str,
        Id: str,
        Name: str,
        DisplayName: str,
        Description: str,
        Price: int,
        Texture: str,
        SpriteIndex: int,
        ItemTags: list[str]
    ):
        super().__init__(key)
        self.Id = Id
        self.Name = Name
        self.DisplayName = DisplayName
        self.Description = Description
        self.Price = Price
        self.Texture = Texture
        self.SpriteIndex = SpriteIndex
        self.ItemTags = ItemTags
