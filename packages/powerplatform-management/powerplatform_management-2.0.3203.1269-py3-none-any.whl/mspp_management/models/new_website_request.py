from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .new_website_request_template_name import NewWebsiteRequest_templateName

@dataclass
class NewWebsiteRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Dataverse organization's unique identifier (ID)
    dataverse_organization_id: Optional[UUID] = None
    # Name of the website
    name: Optional[str] = None
    # Language unique identifier (ID) of the website - https://go.microsoft.com/fwlink/?linkid=2208135
    selected_base_language: Optional[int] = None
    # Subdomain for the website URL
    subdomain: Optional[str] = None
    # Website template name
    template_name: Optional[NewWebsiteRequest_templateName] = None
    # Dataverse record unique identifier (ID) of the website
    website_record_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> NewWebsiteRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: NewWebsiteRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return NewWebsiteRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .new_website_request_template_name import NewWebsiteRequest_templateName

        from .new_website_request_template_name import NewWebsiteRequest_templateName

        fields: dict[str, Callable[[Any], None]] = {
            "dataverseOrganizationId": lambda n : setattr(self, 'dataverse_organization_id', n.get_uuid_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "selectedBaseLanguage": lambda n : setattr(self, 'selected_base_language', n.get_int_value()),
            "subdomain": lambda n : setattr(self, 'subdomain', n.get_str_value()),
            "templateName": lambda n : setattr(self, 'template_name', n.get_enum_value(NewWebsiteRequest_templateName)),
            "websiteRecordId": lambda n : setattr(self, 'website_record_id', n.get_str_value()),
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
        writer.write_uuid_value("dataverseOrganizationId", self.dataverse_organization_id)
        writer.write_str_value("name", self.name)
        writer.write_int_value("selectedBaseLanguage", self.selected_base_language)
        writer.write_str_value("subdomain", self.subdomain)
        writer.write_enum_value("templateName", self.template_name)
        writer.write_str_value("websiteRecordId", self.website_record_id)
        writer.write_additional_data_value(self.additional_data)
    

