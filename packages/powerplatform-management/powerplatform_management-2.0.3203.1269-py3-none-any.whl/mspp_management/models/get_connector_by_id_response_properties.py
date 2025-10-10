from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .get_connector_by_id_response_properties_interfaces import GetConnectorByIdResponse_properties_interfaces
    from .get_connector_by_id_response_properties_metadata import GetConnectorByIdResponse_properties_metadata

@dataclass
class GetConnectorByIdResponse_properties(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The apiEnvironment property
    api_environment: Optional[str] = None
    # The apiVersion property
    api_version: Optional[str] = None
    # The blobUrisAreProxied property
    blob_uris_are_proxied: Optional[bool] = None
    # The capabilities property
    capabilities: Optional[list[str]] = None
    # The changedTime property
    changed_time: Optional[datetime.datetime] = None
    # The createdTime property
    created_time: Optional[datetime.datetime] = None
    # The description property
    description: Optional[str] = None
    # The displayName property
    display_name: Optional[str] = None
    # The doNotUseApiHubNetRuntimeUrl property
    do_not_use_api_hub_net_runtime_url: Optional[str] = None
    # The iconBrandColor property
    icon_brand_color: Optional[str] = None
    # The iconUri property
    icon_uri: Optional[str] = None
    # The interfaces property
    interfaces: Optional[GetConnectorByIdResponse_properties_interfaces] = None
    # The isCustomApi property
    is_custom_api: Optional[bool] = None
    # The metadata property
    metadata: Optional[GetConnectorByIdResponse_properties_metadata] = None
    # The primaryRuntimeUrl property
    primary_runtime_url: Optional[str] = None
    # The publisher property
    publisher: Optional[str] = None
    # The rateLimit property
    rate_limit: Optional[int] = None
    # The releaseTag property
    release_tag: Optional[str] = None
    # The runtimeUrls property
    runtime_urls: Optional[list[str]] = None
    # The tier property
    tier: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetConnectorByIdResponse_properties:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetConnectorByIdResponse_properties
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GetConnectorByIdResponse_properties()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .get_connector_by_id_response_properties_interfaces import GetConnectorByIdResponse_properties_interfaces
        from .get_connector_by_id_response_properties_metadata import GetConnectorByIdResponse_properties_metadata

        from .get_connector_by_id_response_properties_interfaces import GetConnectorByIdResponse_properties_interfaces
        from .get_connector_by_id_response_properties_metadata import GetConnectorByIdResponse_properties_metadata

        fields: dict[str, Callable[[Any], None]] = {
            "apiEnvironment": lambda n : setattr(self, 'api_environment', n.get_str_value()),
            "apiVersion": lambda n : setattr(self, 'api_version', n.get_str_value()),
            "blobUrisAreProxied": lambda n : setattr(self, 'blob_uris_are_proxied', n.get_bool_value()),
            "capabilities": lambda n : setattr(self, 'capabilities', n.get_collection_of_primitive_values(str)),
            "changedTime": lambda n : setattr(self, 'changed_time', n.get_datetime_value()),
            "createdTime": lambda n : setattr(self, 'created_time', n.get_datetime_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "displayName": lambda n : setattr(self, 'display_name', n.get_str_value()),
            "doNotUseApiHubNetRuntimeUrl": lambda n : setattr(self, 'do_not_use_api_hub_net_runtime_url', n.get_str_value()),
            "iconBrandColor": lambda n : setattr(self, 'icon_brand_color', n.get_str_value()),
            "iconUri": lambda n : setattr(self, 'icon_uri', n.get_str_value()),
            "interfaces": lambda n : setattr(self, 'interfaces', n.get_object_value(GetConnectorByIdResponse_properties_interfaces)),
            "isCustomApi": lambda n : setattr(self, 'is_custom_api', n.get_bool_value()),
            "metadata": lambda n : setattr(self, 'metadata', n.get_object_value(GetConnectorByIdResponse_properties_metadata)),
            "primaryRuntimeUrl": lambda n : setattr(self, 'primary_runtime_url', n.get_str_value()),
            "publisher": lambda n : setattr(self, 'publisher', n.get_str_value()),
            "rateLimit": lambda n : setattr(self, 'rate_limit', n.get_int_value()),
            "releaseTag": lambda n : setattr(self, 'release_tag', n.get_str_value()),
            "runtimeUrls": lambda n : setattr(self, 'runtime_urls', n.get_collection_of_primitive_values(str)),
            "tier": lambda n : setattr(self, 'tier', n.get_str_value()),
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
        writer.write_str_value("apiEnvironment", self.api_environment)
        writer.write_str_value("apiVersion", self.api_version)
        writer.write_bool_value("blobUrisAreProxied", self.blob_uris_are_proxied)
        writer.write_collection_of_primitive_values("capabilities", self.capabilities)
        writer.write_datetime_value("changedTime", self.changed_time)
        writer.write_datetime_value("createdTime", self.created_time)
        writer.write_str_value("description", self.description)
        writer.write_str_value("displayName", self.display_name)
        writer.write_str_value("doNotUseApiHubNetRuntimeUrl", self.do_not_use_api_hub_net_runtime_url)
        writer.write_str_value("iconBrandColor", self.icon_brand_color)
        writer.write_str_value("iconUri", self.icon_uri)
        writer.write_object_value("interfaces", self.interfaces)
        writer.write_bool_value("isCustomApi", self.is_custom_api)
        writer.write_object_value("metadata", self.metadata)
        writer.write_str_value("primaryRuntimeUrl", self.primary_runtime_url)
        writer.write_str_value("publisher", self.publisher)
        writer.write_int_value("rateLimit", self.rate_limit)
        writer.write_str_value("releaseTag", self.release_tag)
        writer.write_collection_of_primitive_values("runtimeUrls", self.runtime_urls)
        writer.write_str_value("tier", self.tier)
        writer.write_additional_data_value(self.additional_data)
    

