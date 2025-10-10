from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class ConsumptionModel(Parsable):
    # The actual property
    actual: Optional[float] = None
    # The actualUpdatedOn property
    actual_updated_on: Optional[datetime.datetime] = None
    # The rated property
    rated: Optional[float] = None
    # The ratedUpdatedOn property
    rated_updated_on: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ConsumptionModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ConsumptionModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ConsumptionModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "actual": lambda n : setattr(self, 'actual', n.get_float_value()),
            "actualUpdatedOn": lambda n : setattr(self, 'actual_updated_on', n.get_datetime_value()),
            "rated": lambda n : setattr(self, 'rated', n.get_float_value()),
            "ratedUpdatedOn": lambda n : setattr(self, 'rated_updated_on', n.get_datetime_value()),
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
        writer.write_float_value("actual", self.actual)
        writer.write_datetime_value("actualUpdatedOn", self.actual_updated_on)
        writer.write_float_value("rated", self.rated)
        writer.write_datetime_value("ratedUpdatedOn", self.rated_updated_on)
    

