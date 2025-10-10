from enum import Enum

class WafRuleAction(str, Enum):
    Allow = "Allow",
    Block = "Block",
    Log = "Log",
    AnomalyScoring = "AnomalyScoring",

