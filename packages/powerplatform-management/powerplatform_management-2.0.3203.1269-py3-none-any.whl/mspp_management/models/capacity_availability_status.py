from enum import Enum

class CapacityAvailabilityStatus(str, Enum):
    None_ = "None",
    Available = "Available",
    AvailableByOverflow = "AvailableByOverflow",
    NotAvailable = "NotAvailable",

