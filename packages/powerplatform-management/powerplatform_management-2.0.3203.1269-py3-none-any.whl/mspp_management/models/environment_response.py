from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .environment_response_retention_details import EnvironmentResponse_retentionDetails

@dataclass
class EnvironmentResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The administrative mode of the environment.
    admin_mode: Optional[str] = None
    # The Azure region of the environment.
    azure_region: Optional[str] = None
    # The background operations state of the environment.
    background_operations_state: Optional[str] = None
    # The creation date and time of the environment.
    created_date_time: Optional[datetime.datetime] = None
    # The value of dataverseId property on the environment object.
    dataverse_id: Optional[str] = None
    # The deletion date and time of the environment.
    deleted_date_time: Optional[datetime.datetime] = None
    # The display name of the environment.
    display_name: Optional[str] = None
    # The domain name of the environment.
    domain_name: Optional[str] = None
    # The ID of the environment group to which this environment belongs.
    environment_group_id: Optional[str] = None
    # The geographical region of the environment.
    geo: Optional[str] = None
    # The value of id property on the environment object.
    id: Optional[str] = None
    # The protection level of the environment.
    protection_level: Optional[str] = None
    # The retention details of the environment.
    retention_details: Optional[EnvironmentResponse_retentionDetails] = None
    # The state of the environment.
    state: Optional[str] = None
    # The value of tenantId property on the environment object.
    tenant_id: Optional[str] = None
    # The type of environment.
    type: Optional[str] = None
    # The URL of the environment.
    url: Optional[str] = None
    # The version of the environment.
    version: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> EnvironmentResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: EnvironmentResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return EnvironmentResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .environment_response_retention_details import EnvironmentResponse_retentionDetails

        from .environment_response_retention_details import EnvironmentResponse_retentionDetails

        fields: dict[str, Callable[[Any], None]] = {
            "adminMode": lambda n : setattr(self, 'admin_mode', n.get_str_value()),
            "azureRegion": lambda n : setattr(self, 'azure_region', n.get_str_value()),
            "backgroundOperationsState": lambda n : setattr(self, 'background_operations_state', n.get_str_value()),
            "createdDateTime": lambda n : setattr(self, 'created_date_time', n.get_datetime_value()),
            "dataverseId": lambda n : setattr(self, 'dataverse_id', n.get_str_value()),
            "deletedDateTime": lambda n : setattr(self, 'deleted_date_time', n.get_datetime_value()),
            "displayName": lambda n : setattr(self, 'display_name', n.get_str_value()),
            "domainName": lambda n : setattr(self, 'domain_name', n.get_str_value()),
            "environmentGroupId": lambda n : setattr(self, 'environment_group_id', n.get_str_value()),
            "geo": lambda n : setattr(self, 'geo', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "protectionLevel": lambda n : setattr(self, 'protection_level', n.get_str_value()),
            "retentionDetails": lambda n : setattr(self, 'retention_details', n.get_object_value(EnvironmentResponse_retentionDetails)),
            "state": lambda n : setattr(self, 'state', n.get_str_value()),
            "tenantId": lambda n : setattr(self, 'tenant_id', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
            "url": lambda n : setattr(self, 'url', n.get_str_value()),
            "version": lambda n : setattr(self, 'version', n.get_str_value()),
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
        writer.write_str_value("adminMode", self.admin_mode)
        writer.write_str_value("azureRegion", self.azure_region)
        writer.write_str_value("backgroundOperationsState", self.background_operations_state)
        writer.write_datetime_value("createdDateTime", self.created_date_time)
        writer.write_str_value("dataverseId", self.dataverse_id)
        writer.write_datetime_value("deletedDateTime", self.deleted_date_time)
        writer.write_str_value("displayName", self.display_name)
        writer.write_str_value("domainName", self.domain_name)
        writer.write_str_value("environmentGroupId", self.environment_group_id)
        writer.write_str_value("geo", self.geo)
        writer.write_str_value("id", self.id)
        writer.write_str_value("protectionLevel", self.protection_level)
        writer.write_object_value("retentionDetails", self.retention_details)
        writer.write_str_value("state", self.state)
        writer.write_str_value("tenantId", self.tenant_id)
        writer.write_str_value("type", self.type)
        writer.write_str_value("url", self.url)
        writer.write_str_value("version", self.version)
        writer.write_additional_data_value(self.additional_data)
    

