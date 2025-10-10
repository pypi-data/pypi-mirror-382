from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .currency_consumption import CurrencyConsumption
    from .external_currency_type import ExternalCurrencyType

@dataclass
class CurrencyReportV2(Parsable):
    # The allocated property
    allocated: Optional[int] = None
    # The consumed property
    consumed: Optional[CurrencyConsumption] = None
    # Available currency type which can be allocated to environment.
    currency_type: Optional[ExternalCurrencyType] = None
    # The purchased property
    purchased: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CurrencyReportV2:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CurrencyReportV2
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CurrencyReportV2()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .currency_consumption import CurrencyConsumption
        from .external_currency_type import ExternalCurrencyType

        from .currency_consumption import CurrencyConsumption
        from .external_currency_type import ExternalCurrencyType

        fields: dict[str, Callable[[Any], None]] = {
            "allocated": lambda n : setattr(self, 'allocated', n.get_int_value()),
            "consumed": lambda n : setattr(self, 'consumed', n.get_object_value(CurrencyConsumption)),
            "currencyType": lambda n : setattr(self, 'currency_type', n.get_enum_value(ExternalCurrencyType)),
            "purchased": lambda n : setattr(self, 'purchased', n.get_int_value()),
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
        writer.write_int_value("allocated", self.allocated)
        writer.write_object_value("consumed", self.consumed)
        writer.write_enum_value("currencyType", self.currency_type)
        writer.write_int_value("purchased", self.purchased)
    

