from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .application_visibility import ApplicationVisibility
    from .catalog_visibility import CatalogVisibility
    from .error_details import ErrorDetails
    from .instance_package_state import InstancePackageState

@dataclass
class ApplicationPackage(Parsable):
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
    # Available package custom upgrade
    custom_handle_upgrade: Optional[bool] = None
    # End date for application package
    end_date_utc: Optional[datetime.datetime] = None
    # Available package ID or instance package ID, where both map to the application package ID
    id: Optional[UUID] = None
    # Instance package ID that is used only for a retry of package installation (for example, a reinstall).
    instance_package_id: Optional[UUID] = None
    # The lastError property
    last_error: Optional[ErrorDetails] = None
    # Learn more URL for the application
    learn_more_url: Optional[str] = None
    # Localized description for the application package
    localized_description: Optional[str] = None
    # Localized name of application package
    localized_name: Optional[str] = None
    # Available package platform maximum version
    platform_max_version: Optional[str] = None
    # Available package platform minimum version
    platform_min_version: Optional[str] = None
    # Publisher ID
    publisher_id: Optional[UUID] = None
    # Publisher name
    publisher_name: Optional[str] = None
    # Single Page Application (SPA) URL associated with the application
    single_page_application_url: Optional[str] = None
    # Start date for application package
    start_date_utc: Optional[datetime.datetime] = None
    # State of the instance package
    state: Optional[InstancePackageState] = None
    # List of supported countries/regions for the application
    supported_countries: Optional[list[str]] = None
    # Available package unique name or instance package unique name
    unique_name: Optional[str] = None
    # Available package version or instance package version
    version: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ApplicationPackage:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ApplicationPackage
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ApplicationPackage()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .application_visibility import ApplicationVisibility
        from .catalog_visibility import CatalogVisibility
        from .error_details import ErrorDetails
        from .instance_package_state import InstancePackageState

        from .application_visibility import ApplicationVisibility
        from .catalog_visibility import CatalogVisibility
        from .error_details import ErrorDetails
        from .instance_package_state import InstancePackageState

        fields: dict[str, Callable[[Any], None]] = {
            "applicationDescription": lambda n : setattr(self, 'application_description', n.get_str_value()),
            "applicationId": lambda n : setattr(self, 'application_id', n.get_uuid_value()),
            "applicationName": lambda n : setattr(self, 'application_name', n.get_str_value()),
            "applicationVisibility": lambda n : setattr(self, 'application_visibility', n.get_enum_value(ApplicationVisibility)),
            "catalogVisibility": lambda n : setattr(self, 'catalog_visibility', n.get_enum_value(CatalogVisibility)),
            "customHandleUpgrade": lambda n : setattr(self, 'custom_handle_upgrade', n.get_bool_value()),
            "endDateUtc": lambda n : setattr(self, 'end_date_utc', n.get_datetime_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "instancePackageId": lambda n : setattr(self, 'instance_package_id', n.get_uuid_value()),
            "lastError": lambda n : setattr(self, 'last_error', n.get_object_value(ErrorDetails)),
            "learnMoreUrl": lambda n : setattr(self, 'learn_more_url', n.get_str_value()),
            "localizedDescription": lambda n : setattr(self, 'localized_description', n.get_str_value()),
            "localizedName": lambda n : setattr(self, 'localized_name', n.get_str_value()),
            "platformMaxVersion": lambda n : setattr(self, 'platform_max_version', n.get_str_value()),
            "platformMinVersion": lambda n : setattr(self, 'platform_min_version', n.get_str_value()),
            "publisherId": lambda n : setattr(self, 'publisher_id', n.get_uuid_value()),
            "publisherName": lambda n : setattr(self, 'publisher_name', n.get_str_value()),
            "singlePageApplicationUrl": lambda n : setattr(self, 'single_page_application_url', n.get_str_value()),
            "startDateUtc": lambda n : setattr(self, 'start_date_utc', n.get_datetime_value()),
            "state": lambda n : setattr(self, 'state', n.get_enum_value(InstancePackageState)),
            "supportedCountries": lambda n : setattr(self, 'supported_countries', n.get_collection_of_primitive_values(str)),
            "uniqueName": lambda n : setattr(self, 'unique_name', n.get_str_value()),
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
        writer.write_str_value("applicationDescription", self.application_description)
        writer.write_uuid_value("applicationId", self.application_id)
        writer.write_str_value("applicationName", self.application_name)
        writer.write_enum_value("applicationVisibility", self.application_visibility)
        writer.write_enum_value("catalogVisibility", self.catalog_visibility)
        writer.write_bool_value("customHandleUpgrade", self.custom_handle_upgrade)
        writer.write_datetime_value("endDateUtc", self.end_date_utc)
        writer.write_uuid_value("id", self.id)
        writer.write_uuid_value("instancePackageId", self.instance_package_id)
        writer.write_object_value("lastError", self.last_error)
        writer.write_str_value("learnMoreUrl", self.learn_more_url)
        writer.write_str_value("localizedDescription", self.localized_description)
        writer.write_str_value("localizedName", self.localized_name)
        writer.write_str_value("platformMaxVersion", self.platform_max_version)
        writer.write_str_value("platformMinVersion", self.platform_min_version)
        writer.write_uuid_value("publisherId", self.publisher_id)
        writer.write_str_value("publisherName", self.publisher_name)
        writer.write_str_value("singlePageApplicationUrl", self.single_page_application_url)
        writer.write_datetime_value("startDateUtc", self.start_date_utc)
        writer.write_enum_value("state", self.state)
        writer.write_collection_of_primitive_values("supportedCountries", self.supported_countries)
        writer.write_str_value("uniqueName", self.unique_name)
        writer.write_str_value("version", self.version)
    

