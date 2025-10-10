from enum import Enum

class LicenseModel(str, Enum):
    None_ = "None",
    Legacy = "Legacy",
    StorageDriven = "StorageDriven",

