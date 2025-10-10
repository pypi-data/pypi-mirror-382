from enum import Enum

class WebApplicationFirewallRules_managedRules_RuleSetAction(str, Enum):
    Allow = "Allow",
    Block = "Block",
    Log = "Log",

