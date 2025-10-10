from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .flow_action_kind import FlowActionKind
    from .flow_action_type import FlowActionType

@dataclass
class FlowAction(AdditionalDataHolder, Parsable):
    """
    The flow action object.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The connector name.
    connector: Optional[str] = None
    # Whether the action is a trigger.
    is_trigger: Optional[bool] = None
    # The operation ID.
    operation_id: Optional[str] = None
    # Indicates the kind of the operation used in the process stage.
    operation_kind: Optional[FlowActionKind] = None
    # Indicates the type of the operation used in the process stage.
    operation_type: Optional[FlowActionType] = None
    # The owner Dataverse ID.
    owner_id: Optional[UUID] = None
    # The owning business unit Dataverse ID.
    owning_business_unit: Optional[UUID] = None
    # The parameter name.
    parameter_name: Optional[str] = None
    # The parameter value.
    parameter_value: Optional[str] = None
    # The parent process stage ID.
    parent_process_stage_id: Optional[UUID] = None
    # The process stage ID.
    process_stage_id: Optional[UUID] = None
    # The stage name.
    stage_name: Optional[str] = None
    # The workflow ID.
    workflow_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> FlowAction:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: FlowAction
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return FlowAction()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .flow_action_kind import FlowActionKind
        from .flow_action_type import FlowActionType

        from .flow_action_kind import FlowActionKind
        from .flow_action_type import FlowActionType

        fields: dict[str, Callable[[Any], None]] = {
            "connector": lambda n : setattr(self, 'connector', n.get_str_value()),
            "isTrigger": lambda n : setattr(self, 'is_trigger', n.get_bool_value()),
            "operationId": lambda n : setattr(self, 'operation_id', n.get_str_value()),
            "operationKind": lambda n : setattr(self, 'operation_kind', n.get_enum_value(FlowActionKind)),
            "operationType": lambda n : setattr(self, 'operation_type', n.get_enum_value(FlowActionType)),
            "ownerId": lambda n : setattr(self, 'owner_id', n.get_uuid_value()),
            "owningBusinessUnit": lambda n : setattr(self, 'owning_business_unit', n.get_uuid_value()),
            "parameterName": lambda n : setattr(self, 'parameter_name', n.get_str_value()),
            "parameterValue": lambda n : setattr(self, 'parameter_value', n.get_str_value()),
            "parentProcessStageId": lambda n : setattr(self, 'parent_process_stage_id', n.get_uuid_value()),
            "processStageId": lambda n : setattr(self, 'process_stage_id', n.get_uuid_value()),
            "stageName": lambda n : setattr(self, 'stage_name', n.get_str_value()),
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
        writer.write_str_value("connector", self.connector)
        writer.write_bool_value("isTrigger", self.is_trigger)
        writer.write_str_value("operationId", self.operation_id)
        writer.write_enum_value("operationKind", self.operation_kind)
        writer.write_enum_value("operationType", self.operation_type)
        writer.write_uuid_value("ownerId", self.owner_id)
        writer.write_uuid_value("owningBusinessUnit", self.owning_business_unit)
        writer.write_str_value("parameterName", self.parameter_name)
        writer.write_str_value("parameterValue", self.parameter_value)
        writer.write_uuid_value("parentProcessStageId", self.parent_process_stage_id)
        writer.write_uuid_value("processStageId", self.process_stage_id)
        writer.write_str_value("stageName", self.stage_name)
        writer.write_uuid_value("workflowId", self.workflow_id)
        writer.write_additional_data_value(self.additional_data)
    

