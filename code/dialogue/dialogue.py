from typing import List

class Line():
    def __init__(self, text: str, choices: List[str]):
        self.text = text
        self.choices = choices

class Dialogue():
    def __init__(self, lines: List[Line] = []):
        self.dialogue_index: int = 0
        self.lines: List[Line] = lines
        