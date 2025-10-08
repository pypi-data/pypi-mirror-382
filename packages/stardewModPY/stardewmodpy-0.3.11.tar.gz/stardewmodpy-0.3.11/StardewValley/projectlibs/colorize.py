class colorize:
    def __init__(self):
        self.black=30
        self.red=31
        self.green=32
        self.yellow=33
        self.blue=34
        self.magenta=35
        self.cyan=36
        self.white=37
    
    def colorize(self, color:int):
        return f"\033[{color}m"
    def reset(self):
        return "\033[0m"