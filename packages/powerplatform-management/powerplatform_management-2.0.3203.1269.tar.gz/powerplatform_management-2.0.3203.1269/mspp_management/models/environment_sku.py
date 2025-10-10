from enum import Enum

class EnvironmentSku(str, Enum):
    NotSpecified = "NotSpecified",
    Standard = "Standard",
    Premium = "Premium",
    Developer = "Developer",
    Basic = "Basic",
    Production = "Production",
    Sandbox = "Sandbox",
    Trial = "Trial",
    Default = "Default",
    Support = "Support",
    SubscriptionBasedTrial = "SubscriptionBasedTrial",
    Teams = "Teams",
    Platform = "Platform",

