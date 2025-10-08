class Position:
    def __init__(self, X: int, Y: int):
        self.X = X
        self.Y = Y

    def getJson(self) -> dict:
        return {
            "X": self.X,
            "Y": self.Y
        }
    
    def getStr(self) -> str:
        return f"{self.X}, {self.Y}"

class Rectangle(Position):
    def __init__(self, X: int, Y: int, Width: int, Height: int):
        super().__init__(X, Y)
        self.Width = Width
        self.Height = Height

    def getJson(self) -> dict:
        json = super().getJson()  # Obtém o dicionário da classe pai
        json.update({
            "Width": self.Width,
            "Height": self.Height
        })
        return json