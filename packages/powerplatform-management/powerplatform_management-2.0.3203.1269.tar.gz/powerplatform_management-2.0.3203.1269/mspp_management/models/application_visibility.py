from enum import Enum

class ApplicationVisibility(str, Enum):
    None_ = "None",
    CrmAdminCenter = "CrmAdminCenter",
    BapAdminCenter = "BapAdminCenter",
    OneAdminCenter = "OneAdminCenter",
    All = "All",

