# Color all

class ColorsSet:
    COLORS = {
        "BLACK": '\033[30m',
        "RED": '\033[31m', 
        "CYAN": '\033[36m',
        "GREEN": '\033[32m', 
        "WHITE": '\033[37m',
        "YELLOW": '\033[33m', 
        "MAGENTA": '\033[35m',
        "BLUE": '\033[34m', 
        "BRIGHT_BLACK": '\033[90m',
        "BRIGHT_RED": '\033[91m', 
        "BRIGHT_GREEN": '\033[92m',
        "BRIGHT_YELLOW": '\033[93m', 
        "BRIGHT_BLUE": '\033[94m',
        "BRIGHT_MAGENTA": '\033[95m', 
        "BRIGHT_CYAN": '\033[96m',
        "BRIGHT_WHITE": '\033[97m'
    }

    def __init__(self, colors: str):
        self.colors = colors.upper()

        if self.colors not in self.COLORS:
            raise ValueError(f"Invalid color: {self.colors}")
        
    def _getcolor(self):
        return self.COLORS[self.colors]