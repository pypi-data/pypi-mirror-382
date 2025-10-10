from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class PowerApp_tags(AdditionalDataHolder, Parsable):
    """
    tags
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # PowerApp tag device capabilities.
    device_capabilities: Optional[str] = None
    # PowerApp tag minimum required API version.
    minimum_required_api_version: Optional[datetime.datetime] = None
    # PowerApp tag primary device height.
    primary_device_height: Optional[str] = None
    # PowerApp tag primary device width.
    primary_device_width: Optional[str] = None
    # PowerApp tag primary form factor.
    primary_form_factor: Optional[str] = None
    # PowerApp tag publisher version.
    publisher_version: Optional[str] = None
    # PowerApp tag siena version.
    siena_version: Optional[str] = None
    # PowerApp tag supports landscape.
    supports_landscape: Optional[str] = None
    # PowerApp tag supports portrait.
    supports_portrait: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PowerApp_tags:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PowerApp_tags
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PowerApp_tags()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "deviceCapabilities": lambda n : setattr(self, 'device_capabilities', n.get_str_value()),
            "minimumRequiredApiVersion": lambda n : setattr(self, 'minimum_required_api_version', n.get_datetime_value()),
            "primaryDeviceHeight": lambda n : setattr(self, 'primary_device_height', n.get_str_value()),
            "primaryDeviceWidth": lambda n : setattr(self, 'primary_device_width', n.get_str_value()),
            "primaryFormFactor": lambda n : setattr(self, 'primary_form_factor', n.get_str_value()),
            "publisherVersion": lambda n : setattr(self, 'publisher_version', n.get_str_value()),
            "sienaVersion": lambda n : setattr(self, 'siena_version', n.get_str_value()),
            "supportsLandscape": lambda n : setattr(self, 'supports_landscape', n.get_str_value()),
            "supportsPortrait": lambda n : setattr(self, 'supports_portrait', n.get_str_value()),
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
        writer.write_str_value("deviceCapabilities", self.device_capabilities)
        writer.write_datetime_value("minimumRequiredApiVersion", self.minimum_required_api_version)
        writer.write_str_value("primaryDeviceHeight", self.primary_device_height)
        writer.write_str_value("primaryDeviceWidth", self.primary_device_width)
        writer.write_str_value("primaryFormFactor", self.primary_form_factor)
        writer.write_str_value("publisherVersion", self.publisher_version)
        writer.write_str_value("sienaVersion", self.siena_version)
        writer.write_str_value("supportsLandscape", self.supports_landscape)
        writer.write_str_value("supportsPortrait", self.supports_portrait)
        writer.write_additional_data_value(self.additional_data)
    

