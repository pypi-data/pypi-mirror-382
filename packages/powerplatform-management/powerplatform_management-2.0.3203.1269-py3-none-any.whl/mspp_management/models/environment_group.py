from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .principal import Principal

@dataclass
class EnvironmentGroup(Parsable):
    # The childrenGroupIds property
    children_group_ids: Optional[list[UUID]] = None
    # The createdBy property
    created_by: Optional[Principal] = None
    # The createdTime property
    created_time: Optional[datetime.datetime] = None
    # The description property
    description: Optional[str] = None
    # The displayName property
    display_name: Optional[str] = None
    # The id property
    id: Optional[UUID] = None
    # The lastModifiedBy property
    last_modified_by: Optional[Principal] = None
    # The lastModifiedTime property
    last_modified_time: Optional[datetime.datetime] = None
    # The parentGroupId property
    parent_group_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> EnvironmentGroup:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: EnvironmentGroup
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return EnvironmentGroup()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .principal import Principal

        from .principal import Principal

        fields: dict[str, Callable[[Any], None]] = {
            "childrenGroupIds": lambda n : setattr(self, 'children_group_ids', n.get_collection_of_primitive_values(UUID)),
            "createdBy": lambda n : setattr(self, 'created_by', n.get_object_value(Principal)),
            "createdTime": lambda n : setattr(self, 'created_time', n.get_datetime_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "displayName": lambda n : setattr(self, 'display_name', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "lastModifiedBy": lambda n : setattr(self, 'last_modified_by', n.get_object_value(Principal)),
            "lastModifiedTime": lambda n : setattr(self, 'last_modified_time', n.get_datetime_value()),
            "parentGroupId": lambda n : setattr(self, 'parent_group_id', n.get_uuid_value()),
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
        writer.write_collection_of_primitive_values("childrenGroupIds", self.children_group_ids)
        writer.write_object_value("createdBy", self.created_by)
        writer.write_datetime_value("createdTime", self.created_time)
        writer.write_str_value("description", self.description)
        writer.write_str_value("displayName", self.display_name)
        writer.write_uuid_value("id", self.id)
        writer.write_object_value("lastModifiedBy", self.last_modified_by)
        writer.write_datetime_value("lastModifiedTime", self.last_modified_time)
        writer.write_uuid_value("parentGroupId", self.parent_group_id)
    

