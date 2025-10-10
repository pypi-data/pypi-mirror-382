from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .error_details import ErrorDetails
    from .instance_package_operation_status import InstancePackageOperationStatus

@dataclass
class InstancePackageOperationPollingResponse(Parsable):
    # The createdDateTime property
    created_date_time: Optional[datetime.datetime] = None
    # The error property
    error: Optional[ErrorDetails] = None
    # The lastActionDateTime property
    last_action_date_time: Optional[datetime.datetime] = None
    # The operationId property
    operation_id: Optional[UUID] = None
    # The status property
    status: Optional[InstancePackageOperationStatus] = None
    # The statusMessage property
    status_message: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> InstancePackageOperationPollingResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: InstancePackageOperationPollingResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return InstancePackageOperationPollingResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .error_details import ErrorDetails
        from .instance_package_operation_status import InstancePackageOperationStatus

        from .error_details import ErrorDetails
        from .instance_package_operation_status import InstancePackageOperationStatus

        fields: dict[str, Callable[[Any], None]] = {
            "createdDateTime": lambda n : setattr(self, 'created_date_time', n.get_datetime_value()),
            "error": lambda n : setattr(self, 'error', n.get_object_value(ErrorDetails)),
            "lastActionDateTime": lambda n : setattr(self, 'last_action_date_time', n.get_datetime_value()),
            "operationId": lambda n : setattr(self, 'operation_id', n.get_uuid_value()),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(InstancePackageOperationStatus)),
            "statusMessage": lambda n : setattr(self, 'status_message', n.get_str_value()),
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
        writer.write_datetime_value("createdDateTime", self.created_date_time)
        writer.write_object_value("error", self.error)
        writer.write_datetime_value("lastActionDateTime", self.last_action_date_time)
        writer.write_uuid_value("operationId", self.operation_id)
        writer.write_enum_value("status", self.status)
        writer.write_str_value("statusMessage", self.status_message)
    

