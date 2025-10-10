from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .web_application_firewall_configuration_managed_rules_properties_provisioning_state import WebApplicationFirewallConfiguration_ManagedRules_properties_provisioningState
    from .web_application_firewall_configuration_managed_rules_properties_rule_groups import WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups

@dataclass
class WebApplicationFirewallConfiguration_ManagedRules_properties(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Provisioning state of the managed rule set
    provisioning_state: Optional[WebApplicationFirewallConfiguration_ManagedRules_properties_provisioningState] = None
    # The ruleGroups property
    rule_groups: Optional[list[WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups]] = None
    # Unique identifier of the rule set
    rule_set_id: Optional[str] = None
    # Type of the rule set
    rule_set_type: Optional[str] = None
    # Version of the rule set
    rule_set_version: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WebApplicationFirewallConfiguration_ManagedRules_properties:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WebApplicationFirewallConfiguration_ManagedRules_properties
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WebApplicationFirewallConfiguration_ManagedRules_properties()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .web_application_firewall_configuration_managed_rules_properties_provisioning_state import WebApplicationFirewallConfiguration_ManagedRules_properties_provisioningState
        from .web_application_firewall_configuration_managed_rules_properties_rule_groups import WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups

        from .web_application_firewall_configuration_managed_rules_properties_provisioning_state import WebApplicationFirewallConfiguration_ManagedRules_properties_provisioningState
        from .web_application_firewall_configuration_managed_rules_properties_rule_groups import WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups

        fields: dict[str, Callable[[Any], None]] = {
            "provisioningState": lambda n : setattr(self, 'provisioning_state', n.get_enum_value(WebApplicationFirewallConfiguration_ManagedRules_properties_provisioningState)),
            "ruleGroups": lambda n : setattr(self, 'rule_groups', n.get_collection_of_object_values(WebApplicationFirewallConfiguration_ManagedRules_properties_ruleGroups)),
            "ruleSetId": lambda n : setattr(self, 'rule_set_id', n.get_str_value()),
            "ruleSetType": lambda n : setattr(self, 'rule_set_type', n.get_str_value()),
            "ruleSetVersion": lambda n : setattr(self, 'rule_set_version', n.get_str_value()),
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
        writer.write_enum_value("provisioningState", self.provisioning_state)
        writer.write_collection_of_object_values("ruleGroups", self.rule_groups)
        writer.write_str_value("ruleSetId", self.rule_set_id)
        writer.write_str_value("ruleSetType", self.rule_set_type)
        writer.write_str_value("ruleSetVersion", self.rule_set_version)
        writer.write_additional_data_value(self.additional_data)
    

