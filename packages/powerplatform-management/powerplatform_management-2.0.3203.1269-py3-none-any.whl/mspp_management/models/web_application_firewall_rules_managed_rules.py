from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .web_application_firewall_rules_managed_rules_rule_group_overrides import WebApplicationFirewallRules_managedRules_RuleGroupOverrides
    from .web_application_firewall_rules_managed_rules_rule_set_action import WebApplicationFirewallRules_managedRules_RuleSetAction

@dataclass
class WebApplicationFirewallRules_managedRules(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # List of exclusions for the rule set
    exclusions: Optional[list[str]] = None
    # The RuleGroupOverrides property
    rule_group_overrides: Optional[list[WebApplicationFirewallRules_managedRules_RuleGroupOverrides]] = None
    # Action to take for the rule set
    rule_set_action: Optional[WebApplicationFirewallRules_managedRules_RuleSetAction] = None
    # Type of the managed rule set
    rule_set_type: Optional[str] = None
    # Version of the managed rule set
    rule_set_version: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WebApplicationFirewallRules_managedRules:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WebApplicationFirewallRules_managedRules
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WebApplicationFirewallRules_managedRules()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .web_application_firewall_rules_managed_rules_rule_group_overrides import WebApplicationFirewallRules_managedRules_RuleGroupOverrides
        from .web_application_firewall_rules_managed_rules_rule_set_action import WebApplicationFirewallRules_managedRules_RuleSetAction

        from .web_application_firewall_rules_managed_rules_rule_group_overrides import WebApplicationFirewallRules_managedRules_RuleGroupOverrides
        from .web_application_firewall_rules_managed_rules_rule_set_action import WebApplicationFirewallRules_managedRules_RuleSetAction

        fields: dict[str, Callable[[Any], None]] = {
            "Exclusions": lambda n : setattr(self, 'exclusions', n.get_collection_of_primitive_values(str)),
            "RuleGroupOverrides": lambda n : setattr(self, 'rule_group_overrides', n.get_collection_of_object_values(WebApplicationFirewallRules_managedRules_RuleGroupOverrides)),
            "RuleSetAction": lambda n : setattr(self, 'rule_set_action', n.get_enum_value(WebApplicationFirewallRules_managedRules_RuleSetAction)),
            "RuleSetType": lambda n : setattr(self, 'rule_set_type', n.get_str_value()),
            "RuleSetVersion": lambda n : setattr(self, 'rule_set_version', n.get_str_value()),
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
        writer.write_collection_of_primitive_values("Exclusions", self.exclusions)
        writer.write_collection_of_object_values("RuleGroupOverrides", self.rule_group_overrides)
        writer.write_enum_value("RuleSetAction", self.rule_set_action)
        writer.write_str_value("RuleSetType", self.rule_set_type)
        writer.write_str_value("RuleSetVersion", self.rule_set_version)
        writer.write_additional_data_value(self.additional_data)
    

