from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .web_application_firewall_rules_managed_rules_rule_group_overrides_rules import WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules

@dataclass
class WebApplicationFirewallRules_managedRules_RuleGroupOverrides(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # List of exclusions for the rule group
    exclusions: Optional[list[str]] = None
    # Name of the rule group
    rule_group_name: Optional[str] = None
    # The Rules property
    rules: Optional[list[WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WebApplicationFirewallRules_managedRules_RuleGroupOverrides:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WebApplicationFirewallRules_managedRules_RuleGroupOverrides
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WebApplicationFirewallRules_managedRules_RuleGroupOverrides()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .web_application_firewall_rules_managed_rules_rule_group_overrides_rules import WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules

        from .web_application_firewall_rules_managed_rules_rule_group_overrides_rules import WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules

        fields: dict[str, Callable[[Any], None]] = {
            "Exclusions": lambda n : setattr(self, 'exclusions', n.get_collection_of_primitive_values(str)),
            "RuleGroupName": lambda n : setattr(self, 'rule_group_name', n.get_str_value()),
            "Rules": lambda n : setattr(self, 'rules', n.get_collection_of_object_values(WebApplicationFirewallRules_managedRules_RuleGroupOverrides_Rules)),
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
        writer.write_str_value("RuleGroupName", self.rule_group_name)
        writer.write_collection_of_object_values("Rules", self.rules)
        writer.write_additional_data_value(self.additional_data)
    

