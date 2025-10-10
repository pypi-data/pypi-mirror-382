from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .website_dto_package_install_status import WebsiteDto_packageInstallStatus
    from .website_dto_site_visibility import WebsiteDto_siteVisibility
    from .website_dto_status import WebsiteDto_status
    from .website_dto_template_name import WebsiteDto_templateName
    from .website_dto_type import WebsiteDto_type

@dataclass
class WebsiteDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Entra ID (formerly Azure Active Directory) object unique identifier (ID)
    application_user_aad_app_id: Optional[str] = None
    # Website creation time in the ISO 8601 UTC format
    created_on: Optional[str] = None
    # Custom hostnames added for the website
    custom_host_names: Optional[list[str]] = None
    # Organization URL of the website
    dataverse_instance_url: Optional[str] = None
    # Organization unique identifier (ID) of the website
    dataverse_organization_id: Optional[str] = None
    # Environment unique identifier (ID) of the website
    environment_id: Optional[str] = None
    # Environment name of the website
    environment_name: Optional[str] = None
    # Website unique identifier (ID)
    id: Optional[str] = None
    # Custom error enablement for Website
    is_custom_error_enabled: Optional[bool] = None
    # Website eligibility for early upgrade
    is_early_upgrade_enabled: Optional[bool] = None
    # Website name
    name: Optional[str] = None
    # User unique identifier (ID) of the website owner
    owner_id: Optional[str] = None
    # Package installation status of the website
    package_install_status: Optional[WebsiteDto_packageInstallStatus] = None
    # Package version of the website
    package_version: Optional[str] = None
    # Language unique identifier (ID) of the website - https://go.microsoft.com/fwlink/?linkid=2208135
    selected_base_language: Optional[int] = None
    # Website visibility status
    site_visibility: Optional[WebsiteDto_siteVisibility] = None
    # Website status
    status: Optional[WebsiteDto_status] = None
    # Subdomain of website
    subdomain: Optional[str] = None
    # Time (in days) to website deletion, if suspended
    suspended_website_deleting_in_days: Optional[int] = None
    # Website template name
    template_name: Optional[WebsiteDto_templateName] = None
    # Tenant unique identifier (ID) of the website
    tenant_id: Optional[str] = None
    # Time (in days) to expiration of the website
    trial_expiring_in_days: Optional[int] = None
    # Application type of the website
    type: Optional[WebsiteDto_type] = None
    # Dataverse record unique identifier (ID) of the website
    website_record_id: Optional[str] = None
    # Website URL
    website_url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WebsiteDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WebsiteDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WebsiteDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .website_dto_package_install_status import WebsiteDto_packageInstallStatus
        from .website_dto_site_visibility import WebsiteDto_siteVisibility
        from .website_dto_status import WebsiteDto_status
        from .website_dto_template_name import WebsiteDto_templateName
        from .website_dto_type import WebsiteDto_type

        from .website_dto_package_install_status import WebsiteDto_packageInstallStatus
        from .website_dto_site_visibility import WebsiteDto_siteVisibility
        from .website_dto_status import WebsiteDto_status
        from .website_dto_template_name import WebsiteDto_templateName
        from .website_dto_type import WebsiteDto_type

        fields: dict[str, Callable[[Any], None]] = {
            "applicationUserAadAppId": lambda n : setattr(self, 'application_user_aad_app_id', n.get_str_value()),
            "createdOn": lambda n : setattr(self, 'created_on', n.get_str_value()),
            "customHostNames": lambda n : setattr(self, 'custom_host_names', n.get_collection_of_primitive_values(str)),
            "dataverseInstanceUrl": lambda n : setattr(self, 'dataverse_instance_url', n.get_str_value()),
            "dataverseOrganizationId": lambda n : setattr(self, 'dataverse_organization_id', n.get_str_value()),
            "environmentId": lambda n : setattr(self, 'environment_id', n.get_str_value()),
            "environmentName": lambda n : setattr(self, 'environment_name', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "isCustomErrorEnabled": lambda n : setattr(self, 'is_custom_error_enabled', n.get_bool_value()),
            "isEarlyUpgradeEnabled": lambda n : setattr(self, 'is_early_upgrade_enabled', n.get_bool_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "ownerId": lambda n : setattr(self, 'owner_id', n.get_str_value()),
            "packageInstallStatus": lambda n : setattr(self, 'package_install_status', n.get_enum_value(WebsiteDto_packageInstallStatus)),
            "packageVersion": lambda n : setattr(self, 'package_version', n.get_str_value()),
            "selectedBaseLanguage": lambda n : setattr(self, 'selected_base_language', n.get_int_value()),
            "siteVisibility": lambda n : setattr(self, 'site_visibility', n.get_enum_value(WebsiteDto_siteVisibility)),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(WebsiteDto_status)),
            "subdomain": lambda n : setattr(self, 'subdomain', n.get_str_value()),
            "suspendedWebsiteDeletingInDays": lambda n : setattr(self, 'suspended_website_deleting_in_days', n.get_int_value()),
            "templateName": lambda n : setattr(self, 'template_name', n.get_enum_value(WebsiteDto_templateName)),
            "tenantId": lambda n : setattr(self, 'tenant_id', n.get_str_value()),
            "trialExpiringInDays": lambda n : setattr(self, 'trial_expiring_in_days', n.get_int_value()),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(WebsiteDto_type)),
            "websiteRecordId": lambda n : setattr(self, 'website_record_id', n.get_str_value()),
            "websiteUrl": lambda n : setattr(self, 'website_url', n.get_str_value()),
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
        writer.write_str_value("applicationUserAadAppId", self.application_user_aad_app_id)
        writer.write_str_value("createdOn", self.created_on)
        writer.write_collection_of_primitive_values("customHostNames", self.custom_host_names)
        writer.write_str_value("dataverseInstanceUrl", self.dataverse_instance_url)
        writer.write_str_value("dataverseOrganizationId", self.dataverse_organization_id)
        writer.write_str_value("environmentId", self.environment_id)
        writer.write_str_value("environmentName", self.environment_name)
        writer.write_str_value("id", self.id)
        writer.write_bool_value("isCustomErrorEnabled", self.is_custom_error_enabled)
        writer.write_bool_value("isEarlyUpgradeEnabled", self.is_early_upgrade_enabled)
        writer.write_str_value("name", self.name)
        writer.write_str_value("ownerId", self.owner_id)
        writer.write_enum_value("packageInstallStatus", self.package_install_status)
        writer.write_str_value("packageVersion", self.package_version)
        writer.write_int_value("selectedBaseLanguage", self.selected_base_language)
        writer.write_enum_value("siteVisibility", self.site_visibility)
        writer.write_enum_value("status", self.status)
        writer.write_str_value("subdomain", self.subdomain)
        writer.write_int_value("suspendedWebsiteDeletingInDays", self.suspended_website_deleting_in_days)
        writer.write_enum_value("templateName", self.template_name)
        writer.write_str_value("tenantId", self.tenant_id)
        writer.write_int_value("trialExpiringInDays", self.trial_expiring_in_days)
        writer.write_enum_value("type", self.type)
        writer.write_str_value("websiteRecordId", self.website_record_id)
        writer.write_str_value("websiteUrl", self.website_url)
        writer.write_additional_data_value(self.additional_data)
    

