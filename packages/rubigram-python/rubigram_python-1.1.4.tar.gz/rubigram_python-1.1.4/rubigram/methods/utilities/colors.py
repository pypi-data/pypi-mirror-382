
import rubigram


class Colors:
    """
    A class to represent various color codes for terminal text formatting.

    Attributes:
        YELLOW (str): Yellow color code.
        ORANGE (str): Orange color code.
        WHITE (str): White color code.
        MAGENTA (str): Purple color code.
        RED (str): Red color code.
        GREEN (str): Green color code.
        CYAN (str): Cyan color code.
        BOLD (str): Bold text format code.
        RESET (str): Reset text format code.
    """

    YELLOW = '\033[33m'
    ORANGE = '\033[38;5;214m'
    WHITE = '\033[97m'
    MAGENTA = '\033[95m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    CYAN = "\033[96m"
    BG_CYAN_BLACK = "\033[30m\033[46m"
    BOLD = '\033[1m'
    RESET = '\033[0m'
