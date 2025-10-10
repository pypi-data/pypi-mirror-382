from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .web_application_firewall_configuration_managed_rules_properties import WebApplicationFirewallConfiguration_ManagedRules_properties

@dataclass
class WebApplicationFirewallConfiguration_ManagedRules(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Unique identifier of the managed rule set
    id: Optional[str] = None
    # Name of the managed rule set
    name: Optional[str] = None
    # The properties property
    properties: Optional[WebApplicationFirewallConfiguration_ManagedRules_properties] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WebApplicationFirewallConfiguration_ManagedRules:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WebApplicationFirewallConfiguration_ManagedRules
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WebApplicationFirewallConfiguration_ManagedRules()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .web_application_firewall_configuration_managed_rules_properties import WebApplicationFirewallConfiguration_ManagedRules_properties

        from .web_application_firewall_configuration_managed_rules_properties import WebApplicationFirewallConfiguration_ManagedRules_properties

        fields: dict[str, Callable[[Any], None]] = {
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "properties": lambda n : setattr(self, 'properties', n.get_object_value(WebApplicationFirewallConfiguration_ManagedRules_properties)),
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
        writer.write_str_value("id", self.id)
        writer.write_str_value("name", self.name)
        writer.write_object_value("properties", self.properties)
        writer.write_additional_data_value(self.additional_data)
    

