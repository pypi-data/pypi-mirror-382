from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .modern_flow_type import ModernFlowType

@dataclass
class FlowRun(AdditionalDataHolder, Parsable):
    """
    The flow run object.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The date and time when the flow run was created.
    created_on: Optional[datetime.datetime] = None
    # Duration of the flow run in milliseconds.
    duration_ms: Optional[int] = None
    # The end time of the flow run.
    end_time: Optional[datetime.datetime] = None
    # The flow run ID.
    flow_run_id: Optional[UUID] = None
    # Indicates the modernflow type.
    modern_flow_type: Optional[ModernFlowType] = None
    # The date and time when the flow run was last modified.
    modified_on: Optional[datetime.datetime] = None
    # The flow run name.
    name: Optional[str] = None
    # The owner Dataverse ID.
    owner_id: Optional[UUID] = None
    # The parent run ID.
    parent_run_id: Optional[str] = None
    # The Dataverse ID of the user running the flow.
    running_user: Optional[UUID] = None
    # The start time of the flow run
    start_time: Optional[datetime.datetime] = None
    # The status of the flow run.
    status: Optional[str] = None
    # The trigger type.
    trigger_type: Optional[str] = None
    # Time to live in seconds.
    ttl_in_seconds: Optional[int] = None
    # The workflow ID.
    workflow_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> FlowRun:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: FlowRun
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return FlowRun()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .modern_flow_type import ModernFlowType

        from .modern_flow_type import ModernFlowType

        fields: dict[str, Callable[[Any], None]] = {
            "createdOn": lambda n : setattr(self, 'created_on', n.get_datetime_value()),
            "durationMs": lambda n : setattr(self, 'duration_ms', n.get_int_value()),
            "endTime": lambda n : setattr(self, 'end_time', n.get_datetime_value()),
            "flowRunId": lambda n : setattr(self, 'flow_run_id', n.get_uuid_value()),
            "modernFlowType": lambda n : setattr(self, 'modern_flow_type', n.get_enum_value(ModernFlowType)),
            "modifiedOn": lambda n : setattr(self, 'modified_on', n.get_datetime_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "ownerId": lambda n : setattr(self, 'owner_id', n.get_uuid_value()),
            "parentRunId": lambda n : setattr(self, 'parent_run_id', n.get_str_value()),
            "runningUser": lambda n : setattr(self, 'running_user', n.get_uuid_value()),
            "startTime": lambda n : setattr(self, 'start_time', n.get_datetime_value()),
            "status": lambda n : setattr(self, 'status', n.get_str_value()),
            "triggerType": lambda n : setattr(self, 'trigger_type', n.get_str_value()),
            "ttlInSeconds": lambda n : setattr(self, 'ttl_in_seconds', n.get_int_value()),
            "workflowId": lambda n : setattr(self, 'workflow_id', n.get_uuid_value()),
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
        writer.write_int_value("durationMs", self.duration_ms)
        writer.write_datetime_value("endTime", self.end_time)
        writer.write_uuid_value("flowRunId", self.flow_run_id)
        writer.write_enum_value("modernFlowType", self.modern_flow_type)
        writer.write_datetime_value("modifiedOn", self.modified_on)
        writer.write_str_value("name", self.name)
        writer.write_uuid_value("ownerId", self.owner_id)
        writer.write_str_value("parentRunId", self.parent_run_id)
        writer.write_uuid_value("runningUser", self.running_user)
        writer.write_datetime_value("startTime", self.start_time)
        writer.write_str_value("status", self.status)
        writer.write_str_value("triggerType", self.trigger_type)
        writer.write_int_value("ttlInSeconds", self.ttl_in_seconds)
        writer.write_uuid_value("workflowId", self.workflow_id)
        writer.write_additional_data_value(self.additional_data)
    

