from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class EnvironmentResponse_retentionDetails(AdditionalDataHolder, Parsable):
    """
    The retention details of the environment.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The available from date and time of the environment.
    available_from_date_time: Optional[datetime.datetime] = None
    # The retention period of the environment.
    retention_period: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> EnvironmentResponse_retentionDetails:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: EnvironmentResponse_retentionDetails
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return EnvironmentResponse_retentionDetails()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "availableFromDateTime": lambda n : setattr(self, 'available_from_date_time', n.get_datetime_value()),
            "retentionPeriod": lambda n : setattr(self, 'retention_period', n.get_str_value()),
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
        writer.write_datetime_value("availableFromDateTime", self.available_from_date_time)
        writer.write_str_value("retentionPeriod", self.retention_period)
        writer.write_additional_data_value(self.additional_data)
    

