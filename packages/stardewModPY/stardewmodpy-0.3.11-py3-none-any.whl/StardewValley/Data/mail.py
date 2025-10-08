from .model import modelsData


class mailData(modelsData):
    def __init__(
        self,
        key: str,
        letter_text: str,
        letter_name: str
    ):
        super().__init__(key)
        self.letter_text = letter_text
        self.letter_name = letter_name


    def getJson(self) -> str:
        return f"{self.letter_text}[#]{self.letter_name}"
