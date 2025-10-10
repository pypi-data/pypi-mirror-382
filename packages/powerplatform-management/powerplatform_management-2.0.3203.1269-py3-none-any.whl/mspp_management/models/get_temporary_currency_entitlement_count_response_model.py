from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class GetTemporaryCurrencyEntitlementCountResponseModel(Parsable):
    # The entitledQuantity property
    entitled_quantity: Optional[int] = None
    # The temporaryCurrencyEntitlementCount property
    temporary_currency_entitlement_count: Optional[int] = None
    # The temporaryCurrencyEntitlementsAllowedPerMonth property
    temporary_currency_entitlements_allowed_per_month: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetTemporaryCurrencyEntitlementCountResponseModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetTemporaryCurrencyEntitlementCountResponseModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GetTemporaryCurrencyEntitlementCountResponseModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "entitledQuantity": lambda n : setattr(self, 'entitled_quantity', n.get_int_value()),
            "temporaryCurrencyEntitlementCount": lambda n : setattr(self, 'temporary_currency_entitlement_count', n.get_int_value()),
            "temporaryCurrencyEntitlementsAllowedPerMonth": lambda n : setattr(self, 'temporary_currency_entitlements_allowed_per_month', n.get_int_value()),
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
        writer.write_int_value("entitledQuantity", self.entitled_quantity)
        writer.write_int_value("temporaryCurrencyEntitlementCount", self.temporary_currency_entitlement_count)
        writer.write_int_value("temporaryCurrencyEntitlementsAllowedPerMonth", self.temporary_currency_entitlements_allowed_per_month)
    

