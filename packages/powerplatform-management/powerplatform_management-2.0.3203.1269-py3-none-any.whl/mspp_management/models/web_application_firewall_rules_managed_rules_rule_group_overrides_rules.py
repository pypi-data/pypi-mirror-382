from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .waf_rule_action import WafRuleAction
    from .web_application_firewall_rules_managed_rules_rule_group_overrides_rules_enabled_state import WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules_EnabledState

@dataclass
class WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Action to take for the rule
    action: Optional[WafRuleAction] = None
    # State of the rule
    enabled_state: Optional[WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules_EnabledState] = None
    # List of exclusions for the rule
    exclusions: Optional[list[str]] = None
    # ID of the rule
    rule_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .waf_rule_action import WafRuleAction
        from .web_application_firewall_rules_managed_rules_rule_group_overrides_rules_enabled_state import WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules_EnabledState

        from .waf_rule_action import WafRuleAction
        from .web_application_firewall_rules_managed_rules_rule_group_overrides_rules_enabled_state import WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules_EnabledState

        fields: dict[str, Callable[[Any], None]] = {
            "Action": lambda n : setattr(self, 'action', n.get_enum_value(WafRuleAction)),
            "EnabledState": lambda n : setattr(self, 'enabled_state', n.get_enum_value(WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules_EnabledState)),
            "Exclusions": lambda n : setattr(self, 'exclusions', n.get_collection_of_primitive_values(str)),
            "RuleId": lambda n : setattr(self, 'rule_id', n.get_str_value()),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_enum_value("Action", self.action)
        writer.write_enum_value("EnabledState", self.enabled_state)
        writer.write_collection_of_primitive_values("Exclusions", self.exclusions)
        writer.write_str_value("RuleId", self.rule_id)
        writer.write_additional_data_value(self.additional_data)
    

