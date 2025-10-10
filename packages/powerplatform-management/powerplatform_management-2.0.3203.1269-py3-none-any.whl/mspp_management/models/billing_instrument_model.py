from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class BillingInstrumentModel(Parsable):
    """
    The ISV billing instrument information.
    """
    # The id property
    id: Optional[str] = None
    # The resource group within the tenant subscription.
    resource_group: Optional[str] = None
    # The tenant subscription Id.
    subscription_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BillingInstrumentModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BillingInstrumentModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BillingInstrumentModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "resourceGroup": lambda n : setattr(self, 'resource_group', n.get_str_value()),
            "subscriptionId": lambda n : setattr(self, 'subscription_id', n.get_uuid_value()),
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
        writer.write_str_value("resourceGroup", self.resource_group)
        writer.write_uuid_value("subscriptionId", self.subscription_id)
    

