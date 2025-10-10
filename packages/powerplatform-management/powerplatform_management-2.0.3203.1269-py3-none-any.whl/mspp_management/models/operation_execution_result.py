from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .environment import Environment
    from .error_info import ErrorInfo
    from .operation_status import OperationStatus
    from .stage_status import StageStatus
    from .user_identity import UserIdentity

@dataclass
class OperationExecutionResult(Parsable):
    """
    Represents the result of an operation execution.
    """
    # The end time of the operation.
    end_time: Optional[datetime.datetime] = None
    # Represents error information for an operation.
    error_detail: Optional[ErrorInfo] = None
    # The name of the operation.
    name: Optional[str] = None
    # The ID of the operation.
    operation_id: Optional[str] = None
    # Represents the identity of a user.
    requested_by: Optional[UserIdentity] = None
    # The list of State statuses associated with the operation.
    stage_statuses: Optional[list[StageStatus]] = None
    # The start time of the operation.
    start_time: Optional[datetime.datetime] = None
    # The status of operation.
    status: Optional[OperationStatus] = None
    # Power platform Environment
    updated_environment: Optional[Environment] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> OperationExecutionResult:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: OperationExecutionResult
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return OperationExecutionResult()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .environment import Environment
        from .error_info import ErrorInfo
        from .operation_status import OperationStatus
        from .stage_status import StageStatus
        from .user_identity import UserIdentity

        from .environment import Environment
        from .error_info import ErrorInfo
        from .operation_status import OperationStatus
        from .stage_status import StageStatus
        from .user_identity import UserIdentity

        fields: dict[str, Callable[[Any], None]] = {
            "endTime": lambda n : setattr(self, 'end_time', n.get_datetime_value()),
            "errorDetail": lambda n : setattr(self, 'error_detail', n.get_object_value(ErrorInfo)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "operationId": lambda n : setattr(self, 'operation_id', n.get_str_value()),
            "requestedBy": lambda n : setattr(self, 'requested_by', n.get_object_value(UserIdentity)),
            "stageStatuses": lambda n : setattr(self, 'stage_statuses', n.get_collection_of_object_values(StageStatus)),
            "startTime": lambda n : setattr(self, 'start_time', n.get_datetime_value()),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(OperationStatus)),
            "updatedEnvironment": lambda n : setattr(self, 'updated_environment', n.get_object_value(Environment)),
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
        writer.write_str_value("operationId", self.operation_id)
        writer.write_object_value("requestedBy", self.requested_by)
        writer.write_collection_of_object_values("stageStatuses", self.stage_statuses)
        writer.write_datetime_value("startTime", self.start_time)
        writer.write_enum_value("status", self.status)
        writer.write_object_value("updatedEnvironment", self.updated_environment)
    

