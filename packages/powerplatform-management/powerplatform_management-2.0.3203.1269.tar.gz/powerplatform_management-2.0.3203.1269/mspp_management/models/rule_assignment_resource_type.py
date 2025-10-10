from enum import Enum

class RuleAssignment_resourceType(str, Enum):
    NotSpecified = "NotSpecified",
    EnvironmentGroup = "EnvironmentGroup",
    Environment = "Environment",

