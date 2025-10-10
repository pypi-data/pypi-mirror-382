from enum import Enum

class GetRuleTypeQueryParameterType(str, Enum):
    Managed = "managed",
    Custom = "custom",

