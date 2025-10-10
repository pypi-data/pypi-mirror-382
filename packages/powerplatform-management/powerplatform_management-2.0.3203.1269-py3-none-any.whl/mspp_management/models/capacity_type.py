from enum import Enum

class CapacityType(str, Enum):
    None_ = "None",
    Database = "Database",
    File = "File",
    Log = "Log",
    TrialDatabase = "TrialDatabase",
    TrialFile = "TrialFile",
    TrialLog = "TrialLog",
    SubscriptionTrialDatabase = "SubscriptionTrialDatabase",
    SubscriptionTrialFile = "SubscriptionTrialFile",
    SubscriptionTrialLog = "SubscriptionTrialLog",
    M365Database = "M365Database",
    M365EnvironmentCount = "M365EnvironmentCount",
    SubscriptionTrialEnvironmentCount = "SubscriptionTrialEnvironmentCount",
    CapacityPass = "CapacityPass",
    ApiCallCount = "ApiCallCount",
    FinOpsDatabase = "FinOpsDatabase",
    FinOpsFile = "FinOpsFile",
    PIProcess = "PIProcess",

