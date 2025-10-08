from typing import Optional
from .colors import ColorsSet

class PrintFX:
    def __init__(self, color: str = "WHITE"):
        self.color_list = ColorsSet(color)

    def printfx(self, text: str, color: Optional[str] = None, end: str = "\n") -> None:
        if color:
            temp_color = ColorsSet(color)
            color_code = temp_color._getcolor()
        else:
            color_code = self.color_list._getcolor()
        
        reset_code = '\033[0m'
        print(f"{color_code}{text}{reset_code}", end=end)