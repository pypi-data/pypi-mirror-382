from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .web_application_firewall_configuration_managed_rules_properties_rule_groups_rules import WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules

@dataclass
class WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Description of the rule group
    description: Optional[str] = None
    # Name of the rule group
    rule_group_name: Optional[str] = None
    # The rules property
    rules: Optional[list[WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .web_application_firewall_configuration_managed_rules_properties_rule_groups_rules import WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules

        from .web_application_firewall_configuration_managed_rules_properties_rule_groups_rules import WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules

        fields: dict[str, Callable[[Any], None]] = {
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "ruleGroupName": lambda n : setattr(self, 'rule_group_name', n.get_str_value()),
            "rules": lambda n : setattr(self, 'rules', n.get_collection_of_object_values(WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups_rules)),
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
        writer.write_str_value("description", self.description)
        writer.write_str_value("ruleGroupName", self.rule_group_name)
        writer.write_collection_of_object_values("rules", self.rules)
        writer.write_additional_data_value(self.additional_data)
    

