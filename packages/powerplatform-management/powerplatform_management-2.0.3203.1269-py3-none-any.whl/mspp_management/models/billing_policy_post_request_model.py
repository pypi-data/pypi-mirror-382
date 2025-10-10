from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .billing_instrument_model import BillingInstrumentModel
    from .billing_policy_status import BillingPolicyStatus

@dataclass
class BillingPolicyPostRequestModel(Parsable):
    # The ISV billing instrument information.
    billing_instrument: Optional[BillingInstrumentModel] = None
    # The location property
    location: Optional[str] = None
    # The name property
    name: Optional[str] = None
    # The desired ISV contract status.
    status: Optional[BillingPolicyStatus] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BillingPolicyPostRequestModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BillingPolicyPostRequestModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BillingPolicyPostRequestModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .billing_instrument_model import BillingInstrumentModel
        from .billing_policy_status import BillingPolicyStatus

        from .billing_instrument_model import BillingInstrumentModel
        from .billing_policy_status import BillingPolicyStatus

        fields: dict[str, Callable[[Any], None]] = {
            "billingInstrument": lambda n : setattr(self, 'billing_instrument', n.get_object_value(BillingInstrumentModel)),
            "location": lambda n : setattr(self, 'location', n.get_str_value()),
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
        writer.write_object_value("billingInstrument", self.billing_instrument)
        writer.write_str_value("location", self.location)
        writer.write_str_value("name", self.name)
        writer.write_enum_value("status", self.status)
    

