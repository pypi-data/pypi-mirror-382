from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .waf_rule_action import WafRuleAction
    from .web_application_firewall_configuration_managed_rules_properties_rule_groups_rules_default_state import WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules_defaultState

@dataclass
class WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Action to take for the rule
    default_action: Optional[WafRuleAction] = None
    # Default state of the rule
    default_state: Optional[WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules_defaultState] = None
    # Description of the rule
    description: Optional[str] = None
    # Unique identifier of the rule
    rule_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .waf_rule_action import WafRuleAction
        from .web_application_firewall_configuration_managed_rules_properties_rule_groups_rules_default_state import WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules_defaultState

        from .waf_rule_action import WafRuleAction
        from .web_application_firewall_configuration_managed_rules_properties_rule_groups_rules_default_state import WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules_defaultState

        fields: dict[str, Callable[[Any], None]] = {
            "defaultAction": lambda n : setattr(self, 'default_action', n.get_enum_value(WafRuleAction)),
            "defaultState": lambda n : setattr(self, 'default_state', n.get_enum_value(WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules_defaultState)),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "ruleId": lambda n : setattr(self, 'rule_id', n.get_str_value()),
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
        writer.write_enum_value("defaultAction", self.default_action)
        writer.write_enum_value("defaultState", self.default_state)
        writer.write_str_value("description", self.description)
        writer.write_str_value("ruleId", self.rule_id)
        writer.write_additional_data_value(self.additional_data)
    

