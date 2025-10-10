from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .modern_flow_type import ModernFlowType
    from .workflow_state_code import WorkflowStateCode
    from .workflow_status_code import WorkflowStatusCode

@dataclass
class CloudFlow(AdditionalDataHolder, Parsable):
    """
    The cloud flow object.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The created by Dataverse ID.
    created_by: Optional[UUID] = None
    # Created date and time of the flow (UTC).
    created_on: Optional[datetime.datetime] = None
    # The created on behalf by Dataverse ID.
    created_on_behalf_by: Optional[UUID] = None
    # Client data field of the workflow record.
    definition: Optional[str] = None
    # Description of the flow.
    description: Optional[str] = None
    # Indicates the modernflow type.
    modern_flow_type: Optional[ModernFlowType] = None
    # The modified by Dataverse ID.
    modified_by: Optional[UUID] = None
    # Last modified date and time of the flow (UTC).
    modified_on: Optional[datetime.datetime] = None
    # The modified on behalf by ID.
    modified_on_behalf_by: Optional[UUID] = None
    # The display name of the flow.
    name: Optional[str] = None
    # The owner Dataverse ID.
    owner_id: Optional[UUID] = None
    # The owning business unit Dataverse ID.
    owning_business_unit: Optional[UUID] = None
    # The owning team Dataverse ID.
    owning_team: Optional[UUID] = None
    # The owning user Dataverse ID.
    owning_user: Optional[UUID] = None
    # The parent workflow ID.
    parent_workflow_id: Optional[UUID] = None
    # The resource ID.
    resource_id: Optional[UUID] = None
    # Indicates the workflow state.
    state_code: Optional[WorkflowStateCode] = None
    # Indicates the workflow status.
    status_code: Optional[WorkflowStatusCode] = None
    # The Dataverse unique name.
    unique_name: Optional[str] = None
    # The workflow ID.
    workflow_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CloudFlow:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CloudFlow
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CloudFlow()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .modern_flow_type import ModernFlowType
        from .workflow_state_code import WorkflowStateCode
        from .workflow_status_code import WorkflowStatusCode

        from .modern_flow_type import ModernFlowType
        from .workflow_state_code import WorkflowStateCode
        from .workflow_status_code import WorkflowStatusCode

        fields: dict[str, Callable[[Any], None]] = {
            "createdBy": lambda n : setattr(self, 'created_by', n.get_uuid_value()),
            "createdOn": lambda n : setattr(self, 'created_on', n.get_datetime_value()),
            "createdOnBehalfBy": lambda n : setattr(self, 'created_on_behalf_by', n.get_uuid_value()),
            "definition": lambda n : setattr(self, 'definition', n.get_str_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "modernFlowType": lambda n : setattr(self, 'modern_flow_type', n.get_enum_value(ModernFlowType)),
            "modifiedBy": lambda n : setattr(self, 'modified_by', n.get_uuid_value()),
            "modifiedOn": lambda n : setattr(self, 'modified_on', n.get_datetime_value()),
            "modifiedOnBehalfBy": lambda n : setattr(self, 'modified_on_behalf_by', n.get_uuid_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "ownerId": lambda n : setattr(self, 'owner_id', n.get_uuid_value()),
            "owningBusinessUnit": lambda n : setattr(self, 'owning_business_unit', n.get_uuid_value()),
            "owningTeam": lambda n : setattr(self, 'owning_team', n.get_uuid_value()),
            "owningUser": lambda n : setattr(self, 'owning_user', n.get_uuid_value()),
            "parentWorkflowId": lambda n : setattr(self, 'parent_workflow_id', n.get_uuid_value()),
            "resourceId": lambda n : setattr(self, 'resource_id', n.get_uuid_value()),
            "stateCode": lambda n : setattr(self, 'state_code', n.get_enum_value(WorkflowStateCode)),
            "statusCode": lambda n : setattr(self, 'status_code', n.get_enum_value(WorkflowStatusCode)),
            "uniqueName": lambda n : setattr(self, 'unique_name', n.get_str_value()),
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
        writer.write_uuid_value("createdBy", self.created_by)
        writer.write_datetime_value("createdOn", self.created_on)
        writer.write_uuid_value("createdOnBehalfBy", self.created_on_behalf_by)
        writer.write_str_value("definition", self.definition)
        writer.write_str_value("description", self.description)
        writer.write_enum_value("modernFlowType", self.modern_flow_type)
        writer.write_uuid_value("modifiedBy", self.modified_by)
        writer.write_datetime_value("modifiedOn", self.modified_on)
        writer.write_uuid_value("modifiedOnBehalfBy", self.modified_on_behalf_by)
        writer.write_str_value("name", self.name)
        writer.write_uuid_value("ownerId", self.owner_id)
        writer.write_uuid_value("owningBusinessUnit", self.owning_business_unit)
        writer.write_uuid_value("owningTeam", self.owning_team)
        writer.write_uuid_value("owningUser", self.owning_user)
        writer.write_uuid_value("parentWorkflowId", self.parent_workflow_id)
        writer.write_uuid_value("resourceId", self.resource_id)
        writer.write_enum_value("stateCode", self.state_code)
        writer.write_enum_value("statusCode", self.status_code)
        writer.write_str_value("uniqueName", self.unique_name)
        writer.write_uuid_value("workflowId", self.workflow_id)
        writer.write_additional_data_value(self.additional_data)
    

