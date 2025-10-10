from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .error_details import ErrorDetails
    from .instance_package_state import InstancePackageState

@dataclass
class InstancePackageOperation(Parsable):
    # Date and time for creation of the instance package operation
    created_on: Optional[datetime.datetime] = None
    # The errorDetails property
    error_details: Optional[ErrorDetails] = None
    # Instance package ID
    instance_package_id: Optional[UUID] = None
    # Date and time for modification of the instance package operation
    modified_on: Optional[datetime.datetime] = None
    # Operation ID for the operation triggered on the instance package
    operation_id: Optional[UUID] = None
    # State of the instance package
    state: Optional[InstancePackageState] = None
    # Status message
    status_message: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> InstancePackageOperation:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: InstancePackageOperation
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return InstancePackageOperation()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .error_details import ErrorDetails
        from .instance_package_state import InstancePackageState

        from .error_details import ErrorDetails
        from .instance_package_state import InstancePackageState

        fields: dict[str, Callable[[Any], None]] = {
            "createdOn": lambda n : setattr(self, 'created_on', n.get_datetime_value()),
            "errorDetails": lambda n : setattr(self, 'error_details', n.get_object_value(ErrorDetails)),
            "instancePackageId": lambda n : setattr(self, 'instance_package_id', n.get_uuid_value()),
            "modifiedOn": lambda n : setattr(self, 'modified_on', n.get_datetime_value()),
            "operationId": lambda n : setattr(self, 'operation_id', n.get_uuid_value()),
            "state": lambda n : setattr(self, 'state', n.get_enum_value(InstancePackageState)),
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
        writer.write_datetime_value("createdOn", self.created_on)
        writer.write_object_value("errorDetails", self.error_details)
        writer.write_uuid_value("instancePackageId", self.instance_package_id)
        writer.write_datetime_value("modifiedOn", self.modified_on)
        writer.write_uuid_value("operationId", self.operation_id)
        writer.write_enum_value("state", self.state)
        writer.write_str_value("statusMessage", self.status_message)
    

