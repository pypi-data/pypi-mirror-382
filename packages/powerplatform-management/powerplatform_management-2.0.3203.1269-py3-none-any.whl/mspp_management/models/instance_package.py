from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .application_visibility import ApplicationVisibility
    from .instance_package_operation import InstancePackageOperation

@dataclass
class InstancePackage(Parsable):
    # Application description associated with the instance package
    application_description: Optional[str] = None
    # Application ID associated with the instance package
    application_id: Optional[UUID] = None
    # Application name associated with the instance package
    application_name: Optional[str] = None
    # Application visibility
    application_visibility: Optional[ApplicationVisibility] = None
    # Custom handle upgrade flag for the application
    custom_handle_upgrade: Optional[bool] = None
    # Instance package ID
    id: Optional[UUID] = None
    # The lastOperation property
    last_operation: Optional[InstancePackageOperation] = None
    # Learn more url for the application
    learn_more_url: Optional[str] = None
    # Localized description of application
    localized_description: Optional[str] = None
    # Localized name of application
    localized_name: Optional[str] = None
    # Package ID
    package_id: Optional[UUID] = None
    # Package unique name.
    package_unique_name: Optional[str] = None
    # Package version
    package_version: Optional[str] = None
    # Publisher ID
    publisher_id: Optional[UUID] = None
    # Publisher name for the application
    publisher_name: Optional[str] = None
    # Single Page Application (SPA) URL
    single_page_application_url: Optional[str] = None
    # Terms of service for the application
    terms_of_service_blob_uris: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> InstancePackage:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: InstancePackage
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return InstancePackage()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .application_visibility import ApplicationVisibility
        from .instance_package_operation import InstancePackageOperation

        from .application_visibility import ApplicationVisibility
        from .instance_package_operation import InstancePackageOperation

        fields: dict[str, Callable[[Any], None]] = {
            "applicationDescription": lambda n : setattr(self, 'application_description', n.get_str_value()),
            "applicationId": lambda n : setattr(self, 'application_id', n.get_uuid_value()),
            "applicationName": lambda n : setattr(self, 'application_name', n.get_str_value()),
            "applicationVisibility": lambda n : setattr(self, 'application_visibility', n.get_enum_value(ApplicationVisibility)),
            "customHandleUpgrade": lambda n : setattr(self, 'custom_handle_upgrade', n.get_bool_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "lastOperation": lambda n : setattr(self, 'last_operation', n.get_object_value(InstancePackageOperation)),
            "learnMoreUrl": lambda n : setattr(self, 'learn_more_url', n.get_str_value()),
            "localizedDescription": lambda n : setattr(self, 'localized_description', n.get_str_value()),
            "localizedName": lambda n : setattr(self, 'localized_name', n.get_str_value()),
            "packageId": lambda n : setattr(self, 'package_id', n.get_uuid_value()),
            "packageUniqueName": lambda n : setattr(self, 'package_unique_name', n.get_str_value()),
            "packageVersion": lambda n : setattr(self, 'package_version', n.get_str_value()),
            "publisherId": lambda n : setattr(self, 'publisher_id', n.get_uuid_value()),
            "publisherName": lambda n : setattr(self, 'publisher_name', n.get_str_value()),
            "singlePageApplicationUrl": lambda n : setattr(self, 'single_page_application_url', n.get_str_value()),
            "termsOfServiceBlobUris": lambda n : setattr(self, 'terms_of_service_blob_uris', n.get_collection_of_primitive_values(str)),
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
        writer.write_str_value("applicationDescription", self.application_description)
        writer.write_uuid_value("applicationId", self.application_id)
        writer.write_str_value("applicationName", self.application_name)
        writer.write_enum_value("applicationVisibility", self.application_visibility)
        writer.write_bool_value("customHandleUpgrade", self.custom_handle_upgrade)
        writer.write_uuid_value("id", self.id)
        writer.write_object_value("lastOperation", self.last_operation)
        writer.write_str_value("learnMoreUrl", self.learn_more_url)
        writer.write_str_value("localizedDescription", self.localized_description)
        writer.write_str_value("localizedName", self.localized_name)
        writer.write_uuid_value("packageId", self.package_id)
        writer.write_str_value("packageUniqueName", self.package_unique_name)
        writer.write_str_value("packageVersion", self.package_version)
        writer.write_uuid_value("publisherId", self.publisher_id)
        writer.write_str_value("publisherName", self.publisher_name)
        writer.write_str_value("singlePageApplicationUrl", self.single_page_application_url)
        writer.write_collection_of_primitive_values("termsOfServiceBlobUris", self.terms_of_service_blob_uris)
    

