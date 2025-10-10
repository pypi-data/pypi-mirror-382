from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .capacity_availability_status import CapacityAvailabilityStatus
    from .capacity_status_message_code import CapacityStatusMessageCode

@dataclass
class CapacitySummary(Parsable):
    # The finOpsStatus property
    fin_ops_status: Optional[CapacityAvailabilityStatus] = None
    # The finOpsStatusMessage property
    fin_ops_status_message: Optional[str] = None
    # The finOpsStatusMessageCode property
    fin_ops_status_message_code: Optional[CapacityStatusMessageCode] = None
    # The status property
    status: Optional[CapacityAvailabilityStatus] = None
    # The statusMessage property
    status_message: Optional[str] = None
    # The statusMessageCode property
    status_message_code: Optional[CapacityStatusMessageCode] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CapacitySummary:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CapacitySummary
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CapacitySummary()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .capacity_availability_status import CapacityAvailabilityStatus
        from .capacity_status_message_code import CapacityStatusMessageCode

        from .capacity_availability_status import CapacityAvailabilityStatus
        from .capacity_status_message_code import CapacityStatusMessageCode

        fields: dict[str, Callable[[Any], None]] = {
            "finOpsStatus": lambda n : setattr(self, 'fin_ops_status', n.get_enum_value(CapacityAvailabilityStatus)),
            "finOpsStatusMessage": lambda n : setattr(self, 'fin_ops_status_message', n.get_str_value()),
            "finOpsStatusMessageCode": lambda n : setattr(self, 'fin_ops_status_message_code', n.get_enum_value(CapacityStatusMessageCode)),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(CapacityAvailabilityStatus)),
            "statusMessage": lambda n : setattr(self, 'status_message', n.get_str_value()),
            "statusMessageCode": lambda n : setattr(self, 'status_message_code', n.get_enum_value(CapacityStatusMessageCode)),
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
        writer.write_enum_value("finOpsStatus", self.fin_ops_status)
        writer.write_str_value("finOpsStatusMessage", self.fin_ops_status_message)
        writer.write_enum_value("finOpsStatusMessageCode", self.fin_ops_status_message_code)
        writer.write_enum_value("status", self.status)
        writer.write_str_value("statusMessage", self.status_message)
        writer.write_enum_value("statusMessageCode", self.status_message_code)
    

