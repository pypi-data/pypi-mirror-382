
class Coordinates:
    def __init__(
        self,
        X:int,
        Y:int,
        toX:int,
        toY:int
    ):
        self.X=X
        self.Y=Y
        self.toX=toX
        self.toY=toY
        
    def getJson(self) -> str:
        return f"{self.X},{self.Y}/{self.toX},{self.toY}"