from enum import Enum

class ExternalCurrencyType(str, Enum):
    AI = "AI",
    AppPass = "AppPass",
    AppPassForTeams = "AppPassForTeams",
    Invoice = "Invoice",
    MCSSessions = "MCSSessions",
    MCSMessages = "MCSMessages",
    PAHostedRPA = "PAHostedRPA",
    PAUnattendedRPA = "PAUnattendedRPA",
    PerFlowPlan = "PerFlowPlan",
    PortalAddOns = "PortalAddOns",
    PortalLogins = "PortalLogins",
    PortalViews = "PortalViews",
    PowerPagesAuthenticated = "PowerPagesAuthenticated",
    PowerPagesAnonymous = "PowerPagesAnonymous",
    PowerAutomatePerProcess = "PowerAutomatePerProcess",
    ProcessMiningDataStorage = "ProcessMiningDataStorage",
    SCMessages = "SCMessages",
    VAConversations = "VAConversations",

