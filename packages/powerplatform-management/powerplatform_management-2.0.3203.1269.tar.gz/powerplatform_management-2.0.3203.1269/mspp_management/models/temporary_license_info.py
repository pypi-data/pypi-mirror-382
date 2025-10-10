from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class TemporaryLicenseInfo(Parsable):
    # The hasTemporaryLicense property
    has_temporary_license: Optional[bool] = None
    # The temporaryLicenseExpiryDate property
    temporary_license_expiry_date: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TemporaryLicenseInfo:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TemporaryLicenseInfo
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TemporaryLicenseInfo()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "hasTemporaryLicense": lambda n : setattr(self, 'has_temporary_license', n.get_bool_value()),
            "temporaryLicenseExpiryDate": lambda n : setattr(self, 'temporary_license_expiry_date', n.get_datetime_value()),
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
        writer.write_bool_value("hasTemporaryLicense", self.has_temporary_license)
        writer.write_datetime_value("temporaryLicenseExpiryDate", self.temporary_license_expiry_date)
    

