from enum import Enum

class WafRuleType(str, Enum):
    MatchRule = "MatchRule",
    RateLimitRule = "RateLimitRule",

