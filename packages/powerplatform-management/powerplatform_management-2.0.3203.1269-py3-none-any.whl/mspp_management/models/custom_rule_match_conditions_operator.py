from enum import Enum

class CustomRule_matchConditions_operator(str, Enum):
    GeoMatch = "GeoMatch",
    Equals = "Equals",
    Contains = "Contains",
    StartsWith = "StartsWith",
    EndsWith = "EndsWith",

