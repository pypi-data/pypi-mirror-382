from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .custom_rule import CustomRule
    from .web_application_firewall_configuration_managed_rules import WebApplicationFirewallConfiguration_ManagedRules

@dataclass
class WebApplicationFirewallConfiguration(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The CustomRules property
    custom_rules: Optional[list[CustomRule]] = None
    # The ManagedRules property
    managed_rules: Optional[list[WebApplicationFirewallConfiguration_ManagedRules]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WebApplicationFirewallConfiguration:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WebApplicationFirewallConfiguration
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WebApplicationFirewallConfiguration()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .custom_rule import CustomRule
        from .web_application_firewall_configuration_managed_rules import WebApplicationFirewallConfiguration_ManagedRules

        from .custom_rule import CustomRule
        from .web_application_firewall_configuration_managed_rules import WebApplicationFirewallConfiguration_ManagedRules

        fields: dict[str, Callable[[Any], None]] = {
            "CustomRules": lambda n : setattr(self, 'custom_rules', n.get_collection_of_object_values(CustomRule)),
            "ManagedRules": lambda n : setattr(self, 'managed_rules', n.get_collection_of_object_values(WebApplicationFirewallConfiguration_ManagedRules)),
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
        writer.write_collection_of_object_values("CustomRules", self.custom_rules)
        writer.write_collection_of_object_values("ManagedRules", self.managed_rules)
        writer.write_additional_data_value(self.additional_data)
    

