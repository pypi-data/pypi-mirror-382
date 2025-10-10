from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .external_currency_type import ExternalCurrencyType

@dataclass
class CurrencyAllocationResponseModelV1(Parsable):
    # The allocated count of currency type
    allocated: Optional[int] = None
    # Available currency type which can be allocated to environment.
    currency_type: Optional[ExternalCurrencyType] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CurrencyAllocationResponseModelV1:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CurrencyAllocationResponseModelV1
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CurrencyAllocationResponseModelV1()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .external_currency_type import ExternalCurrencyType

        from .external_currency_type import ExternalCurrencyType

        fields: dict[str, Callable[[Any], None]] = {
            "allocated": lambda n : setattr(self, 'allocated', n.get_int_value()),
            "currencyType": lambda n : setattr(self, 'currency_type', n.get_enum_value(ExternalCurrencyType)),
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
        writer.write_enum_value("currencyType", self.currency_type)
    

