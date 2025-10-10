from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class AdvisorRecommendationResource(AdditionalDataHolder, Parsable):
    """
    Details of a resource included in a recommendation
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The environment unique ID
    environment_id: Optional[str] = None
    # The environment display name
    environment_name: Optional[str] = None
    # Time when the resource was last used
    last_accessed_date: Optional[datetime.datetime] = None
    # Time when the resource was last modified
    last_modified_date: Optional[datetime.datetime] = None
    # Current status of any action taken since the last refresh time
    resource_action_status: Optional[str] = None
    # The resource description
    resource_description: Optional[str] = None
    # The resource unique ID
    resource_id: Optional[str] = None
    # The resource display name
    resource_name: Optional[str] = None
    # The resource owner display name
    resource_owner: Optional[str] = None
    # The resource owner object ID
    resource_owner_id: Optional[str] = None
    # The sub type of the resource
    resource_sub_type: Optional[str] = None
    # The type of resource
    resource_type: Optional[str] = None
    # Number of unique users who used the resource in the last thirty (30) days
    resource_usage: Optional[float] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AdvisorRecommendationResource:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AdvisorRecommendationResource
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AdvisorRecommendationResource()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "environmentId": lambda n : setattr(self, 'environment_id', n.get_str_value()),
            "environmentName": lambda n : setattr(self, 'environment_name', n.get_str_value()),
            "lastAccessedDate": lambda n : setattr(self, 'last_accessed_date', n.get_datetime_value()),
            "lastModifiedDate": lambda n : setattr(self, 'last_modified_date', n.get_datetime_value()),
            "resourceActionStatus": lambda n : setattr(self, 'resource_action_status', n.get_str_value()),
            "resourceDescription": lambda n : setattr(self, 'resource_description', n.get_str_value()),
            "resourceId": lambda n : setattr(self, 'resource_id', n.get_str_value()),
            "resourceName": lambda n : setattr(self, 'resource_name', n.get_str_value()),
            "resourceOwner": lambda n : setattr(self, 'resource_owner', n.get_str_value()),
            "resourceOwnerId": lambda n : setattr(self, 'resource_owner_id', n.get_str_value()),
            "resourceSubType": lambda n : setattr(self, 'resource_sub_type', n.get_str_value()),
            "resourceType": lambda n : setattr(self, 'resource_type', n.get_str_value()),
            "resourceUsage": lambda n : setattr(self, 'resource_usage', n.get_float_value()),
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
        writer.write_str_value("environmentId", self.environment_id)
        writer.write_str_value("environmentName", self.environment_name)
        writer.write_datetime_value("lastAccessedDate", self.last_accessed_date)
        writer.write_datetime_value("lastModifiedDate", self.last_modified_date)
        writer.write_str_value("resourceActionStatus", self.resource_action_status)
        writer.write_str_value("resourceDescription", self.resource_description)
        writer.write_str_value("resourceId", self.resource_id)
        writer.write_str_value("resourceName", self.resource_name)
        writer.write_str_value("resourceOwner", self.resource_owner)
        writer.write_str_value("resourceOwnerId", self.resource_owner_id)
        writer.write_str_value("resourceSubType", self.resource_sub_type)
        writer.write_str_value("resourceType", self.resource_type)
        writer.write_float_value("resourceUsage", self.resource_usage)
        writer.write_additional_data_value(self.additional_data)
    

