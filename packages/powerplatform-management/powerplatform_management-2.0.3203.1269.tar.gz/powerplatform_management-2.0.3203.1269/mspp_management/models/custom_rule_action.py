from enum import Enum

class CustomRule_action(str, Enum):
    Allow = "Allow",
    Block = "Block",
    Log = "Log",

