from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class PowerApp_properties_minClientVersion(AdditionalDataHolder, Parsable):
    """
    PowerApp property minClientVersion object.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # PowerApp property minClientVersion build.
    build: Optional[int] = None
    # PowerApp property minClientVersion major.
    major: Optional[int] = None
    # PowerApp property minClientVersion majorRevision.
    major_revision: Optional[int] = None
    # PowerApp property minClientVersion minor.
    minor: Optional[int] = None
    # PowerApp property minClientVersion minorRevision.
    minor_revision: Optional[int] = None
    # PowerApp property minClientVersion revision.
    revision: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PowerApp_properties_minClientVersion:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PowerApp_properties_minClientVersion
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PowerApp_properties_minClientVersion()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "build": lambda n : setattr(self, 'build', n.get_int_value()),
            "major": lambda n : setattr(self, 'major', n.get_int_value()),
            "majorRevision": lambda n : setattr(self, 'major_revision', n.get_int_value()),
            "minor": lambda n : setattr(self, 'minor', n.get_int_value()),
            "minorRevision": lambda n : setattr(self, 'minor_revision', n.get_int_value()),
            "revision": lambda n : setattr(self, 'revision', n.get_int_value()),
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
        writer.write_int_value("build", self.build)
        writer.write_int_value("major", self.major)
        writer.write_int_value("majorRevision", self.major_revision)
        writer.write_int_value("minor", self.minor)
        writer.write_int_value("minorRevision", self.minor_revision)
        writer.write_int_value("revision", self.revision)
        writer.write_additional_data_value(self.additional_data)
    

