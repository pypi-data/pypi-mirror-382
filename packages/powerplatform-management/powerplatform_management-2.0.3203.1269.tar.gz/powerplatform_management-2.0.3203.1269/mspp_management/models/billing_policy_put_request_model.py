from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .billing_policy_status import BillingPolicyStatus

@dataclass
class BillingPolicyPutRequestModel(Parsable):
    # The name property
    name: Optional[str] = None
    # The desired ISV contract status.
    status: Optional[BillingPolicyStatus] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BillingPolicyPutRequestModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BillingPolicyPutRequestModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BillingPolicyPutRequestModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .billing_policy_status import BillingPolicyStatus

        from .billing_policy_status import BillingPolicyStatus

        fields: dict[str, Callable[[Any], None]] = {
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(BillingPolicyStatus)),
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
        writer.write_str_value("name", self.name)
        writer.write_enum_value("status", self.status)
    

