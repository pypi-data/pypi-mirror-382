from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class CurrencyConsumption(Parsable):
    # The lastUpdatedDay property
    last_updated_day: Optional[datetime.datetime] = None
    # The unitsConsumed property
    units_consumed: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CurrencyConsumption:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CurrencyConsumption
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CurrencyConsumption()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "lastUpdatedDay": lambda n : setattr(self, 'last_updated_day', n.get_datetime_value()),
            "unitsConsumed": lambda n : setattr(self, 'units_consumed', n.get_int_value()),
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
        writer.write_datetime_value("lastUpdatedDay", self.last_updated_day)
        writer.write_int_value("unitsConsumed", self.units_consumed)
    

