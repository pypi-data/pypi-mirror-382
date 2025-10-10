from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .application_visibility import ApplicationVisibility
    from .catalog_visibility import CatalogVisibility
    from .error_details import ErrorDetails

@dataclass
class TenantApplicationPackage(Parsable):
    # Application description
    application_description: Optional[str] = None
    # Application ID
    application_id: Optional[UUID] = None
    # Application name
    application_name: Optional[str] = None
    # Application visibility
    application_visibility: Optional[ApplicationVisibility] = None
    # Catalog visibility for the application
    catalog_visibility: Optional[CatalogVisibility] = None
    # The lastError property
    last_error: Optional[ErrorDetails] = None
    # Learn more URL
    learn_more_url: Optional[str] = None
    # Localized description of the tenant application package
    localized_description: Optional[str] = None
    # Localized name
    localized_name: Optional[str] = None
    # Publisher ID
    publisher_id: Optional[UUID] = None
    # Publisher name
    publisher_name: Optional[str] = None
    # Unique name of the tenant application package
    unique_name: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TenantApplicationPackage:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TenantApplicationPackage
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TenantApplicationPackage()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .application_visibility import ApplicationVisibility
        from .catalog_visibility import CatalogVisibility
        from .error_details import ErrorDetails

        from .application_visibility import ApplicationVisibility
        from .catalog_visibility import CatalogVisibility
        from .error_details import ErrorDetails

        fields: dict[str, Callable[[Any], None]] = {
            "applicationDescription": lambda n : setattr(self, 'application_description', n.get_str_value()),
            "applicationId": lambda n : setattr(self, 'application_id', n.get_uuid_value()),
            "applicationName": lambda n : setattr(self, 'application_name', n.get_str_value()),
            "applicationVisibility": lambda n : setattr(self, 'application_visibility', n.get_enum_value(ApplicationVisibility)),
            "catalogVisibility": lambda n : setattr(self, 'catalog_visibility', n.get_enum_value(CatalogVisibility)),
            "lastError": lambda n : setattr(self, 'last_error', n.get_object_value(ErrorDetails)),
            "learnMoreUrl": lambda n : setattr(self, 'learn_more_url', n.get_str_value()),
            "localizedDescription": lambda n : setattr(self, 'localized_description', n.get_str_value()),
            "localizedName": lambda n : setattr(self, 'localized_name', n.get_str_value()),
            "publisherId": lambda n : setattr(self, 'publisher_id', n.get_uuid_value()),
            "publisherName": lambda n : setattr(self, 'publisher_name', n.get_str_value()),
            "uniqueName": lambda n : setattr(self, 'unique_name', n.get_str_value()),
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
        writer.write_enum_value("catalogVisibility", self.catalog_visibility)
        writer.write_object_value("lastError", self.last_error)
        writer.write_str_value("learnMoreUrl", self.learn_more_url)
        writer.write_str_value("localizedDescription", self.localized_description)
        writer.write_str_value("localizedName", self.localized_name)
        writer.write_uuid_value("publisherId", self.publisher_id)
        writer.write_str_value("publisherName", self.publisher_name)
        writer.write_str_value("uniqueName", self.unique_name)
    

