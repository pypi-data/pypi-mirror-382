from enum import Enum

class CatalogVisibility(str, Enum):
    None_ = "None",
    AdminCenter = "AdminCenter",
    Teams = "Teams",
    All = "All",

