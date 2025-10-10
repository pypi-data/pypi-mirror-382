from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .error_info import ErrorInfo

@dataclass
class StageStatus(Parsable):
    """
    The stage status of an operation.
    """
    # The end time of stage.
    end_time: Optional[datetime.datetime] = None
    # Represents error information for an operation.
    error_detail: Optional[ErrorInfo] = None
    # The name of stage.
    name: Optional[str] = None
    # The start time of stage.
    start_time: Optional[datetime.datetime] = None
    # The status of stage.
    status: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> StageStatus:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: StageStatus
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return StageStatus()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .error_info import ErrorInfo

        from .error_info import ErrorInfo

        fields: dict[str, Callable[[Any], None]] = {
            "endTime": lambda n : setattr(self, 'end_time', n.get_datetime_value()),
            "errorDetail": lambda n : setattr(self, 'error_detail', n.get_object_value(ErrorInfo)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "startTime": lambda n : setattr(self, 'start_time', n.get_datetime_value()),
            "status": lambda n : setattr(self, 'status', n.get_str_value()),
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
        writer.write_datetime_value("endTime", self.end_time)
        writer.write_object_value("errorDetail", self.error_detail)
        writer.write_str_value("name", self.name)
        writer.write_datetime_value("startTime", self.start_time)
        writer.write_str_value("status", self.status)
    

