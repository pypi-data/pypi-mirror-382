from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .connection_reference import ConnectionReference
    from .power_app_properties_app_uris import PowerApp_properties_appUris
    from .power_app_properties_created_by import PowerApp_properties_createdBy
    from .power_app_properties_created_by_client_version import PowerApp_properties_createdByClientVersion
    from .power_app_properties_environment import PowerApp_properties_environment
    from .power_app_properties_last_modified_by import PowerApp_properties_lastModifiedBy
    from .power_app_properties_min_client_version import PowerApp_properties_minClientVersion
    from .power_app_properties_owner import PowerApp_properties_owner
    from .power_app_properties_user_app_metadata import PowerApp_properties_userAppMetadata

@dataclass
class PowerApp_properties(AdditionalDataHolder, Parsable):
    """
    PowerApp properties object.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # PowerApp property app open protocol URI.
    app_open_protocol_uri: Optional[str] = None
    # PowerApp property app open URI.
    app_open_uri: Optional[str] = None
    # PowerApp appUri object.
    app_uris: Optional[PowerApp_properties_appUris] = None
    # PowerApp property appVersion.
    app_version: Optional[datetime.datetime] = None
    # PowerApp background color.
    background_color: Optional[str] = None
    # PowerApp background image URI.
    background_image_uri: Optional[str] = None
    # PowerApp property bypass consent.
    bypass_consent: Optional[bool] = None
    # The connectionReferences property
    connection_references: Optional[list[ConnectionReference]] = None
    # PowerApp created by principal object.
    created_by: Optional[PowerApp_properties_createdBy] = None
    # PowerApp property createdByClientVersion object.
    created_by_client_version: Optional[PowerApp_properties_createdByClientVersion] = None
    # PowerApp property created time.
    created_time: Optional[datetime.datetime] = None
    # PowerApp description.
    description: Optional[str] = None
    # PowerApp display name.
    display_name: Optional[str] = None
    # PowerApp environment property object.
    environment: Optional[PowerApp_properties_environment] = None
    # PowerApp property is featured app.
    is_featured_app: Optional[bool] = None
    # PowerApp property indicating hero application.
    is_hero_app: Optional[bool] = None
    # PowerApp last modified by object.
    last_modified_by: Optional[PowerApp_properties_lastModifiedBy] = None
    # PowerApp property last modified time.
    last_modified_time: Optional[datetime.datetime] = None
    # PowerApp property minClientVersion object.
    min_client_version: Optional[PowerApp_properties_minClientVersion] = None
    # PowerApp owner principal object.
    owner: Optional[PowerApp_properties_owner] = None
    # PowerApp property shared groups count.
    shared_groups_count: Optional[int] = None
    # PowerApp property shared users count.
    shared_users_count: Optional[int] = None
    # PowerApp property user app metadata object.
    user_app_metadata: Optional[PowerApp_properties_userAppMetadata] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PowerApp_properties:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PowerApp_properties
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PowerApp_properties()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .connection_reference import ConnectionReference
        from .power_app_properties_app_uris import PowerApp_properties_appUris
        from .power_app_properties_created_by import PowerApp_properties_createdBy
        from .power_app_properties_created_by_client_version import PowerApp_properties_createdByClientVersion
        from .power_app_properties_environment import PowerApp_properties_environment
        from .power_app_properties_last_modified_by import PowerApp_properties_lastModifiedBy
        from .power_app_properties_min_client_version import PowerApp_properties_minClientVersion
        from .power_app_properties_owner import PowerApp_properties_owner
        from .power_app_properties_user_app_metadata import PowerApp_properties_userAppMetadata

        from .connection_reference import ConnectionReference
        from .power_app_properties_app_uris import PowerApp_properties_appUris
        from .power_app_properties_created_by import PowerApp_properties_createdBy
        from .power_app_properties_created_by_client_version import PowerApp_properties_createdByClientVersion
        from .power_app_properties_environment import PowerApp_properties_environment
        from .power_app_properties_last_modified_by import PowerApp_properties_lastModifiedBy
        from .power_app_properties_min_client_version import PowerApp_properties_minClientVersion
        from .power_app_properties_owner import PowerApp_properties_owner
        from .power_app_properties_user_app_metadata import PowerApp_properties_userAppMetadata

        fields: dict[str, Callable[[Any], None]] = {
            "appOpenProtocolUri": lambda n : setattr(self, 'app_open_protocol_uri', n.get_str_value()),
            "appOpenUri": lambda n : setattr(self, 'app_open_uri', n.get_str_value()),
            "appUris": lambda n : setattr(self, 'app_uris', n.get_object_value(PowerApp_properties_appUris)),
            "appVersion": lambda n : setattr(self, 'app_version', n.get_datetime_value()),
            "backgroundColor": lambda n : setattr(self, 'background_color', n.get_str_value()),
            "backgroundImageUri": lambda n : setattr(self, 'background_image_uri', n.get_str_value()),
            "bypassConsent": lambda n : setattr(self, 'bypass_consent', n.get_bool_value()),
            "connectionReferences": lambda n : setattr(self, 'connection_references', n.get_collection_of_object_values(ConnectionReference)),
            "createdBy": lambda n : setattr(self, 'created_by', n.get_object_value(PowerApp_properties_createdBy)),
            "createdByClientVersion": lambda n : setattr(self, 'created_by_client_version', n.get_object_value(PowerApp_properties_createdByClientVersion)),
            "createdTime": lambda n : setattr(self, 'created_time', n.get_datetime_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "displayName": lambda n : setattr(self, 'display_name', n.get_str_value()),
            "environment": lambda n : setattr(self, 'environment', n.get_object_value(PowerApp_properties_environment)),
            "isFeaturedApp": lambda n : setattr(self, 'is_featured_app', n.get_bool_value()),
            "isHeroApp": lambda n : setattr(self, 'is_hero_app', n.get_bool_value()),
            "lastModifiedBy": lambda n : setattr(self, 'last_modified_by', n.get_object_value(PowerApp_properties_lastModifiedBy)),
            "lastModifiedTime": lambda n : setattr(self, 'last_modified_time', n.get_datetime_value()),
            "minClientVersion": lambda n : setattr(self, 'min_client_version', n.get_object_value(PowerApp_properties_minClientVersion)),
            "owner": lambda n : setattr(self, 'owner', n.get_object_value(PowerApp_properties_owner)),
            "sharedGroupsCount": lambda n : setattr(self, 'shared_groups_count', n.get_int_value()),
            "sharedUsersCount": lambda n : setattr(self, 'shared_users_count', n.get_int_value()),
            "userAppMetadata": lambda n : setattr(self, 'user_app_metadata', n.get_object_value(PowerApp_properties_userAppMetadata)),
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
        writer.write_str_value("appOpenProtocolUri", self.app_open_protocol_uri)
        writer.write_str_value("appOpenUri", self.app_open_uri)
        writer.write_object_value("appUris", self.app_uris)
        writer.write_datetime_value("appVersion", self.app_version)
        writer.write_str_value("backgroundColor", self.background_color)
        writer.write_str_value("backgroundImageUri", self.background_image_uri)
        writer.write_bool_value("bypassConsent", self.bypass_consent)
        writer.write_collection_of_object_values("connectionReferences", self.connection_references)
        writer.write_object_value("createdBy", self.created_by)
        writer.write_object_value("createdByClientVersion", self.created_by_client_version)
        writer.write_datetime_value("createdTime", self.created_time)
        writer.write_str_value("description", self.description)
        writer.write_str_value("displayName", self.display_name)
        writer.write_object_value("environment", self.environment)
        writer.write_bool_value("isFeaturedApp", self.is_featured_app)
        writer.write_bool_value("isHeroApp", self.is_hero_app)
        writer.write_object_value("lastModifiedBy", self.last_modified_by)
        writer.write_datetime_value("lastModifiedTime", self.last_modified_time)
        writer.write_object_value("minClientVersion", self.min_client_version)
        writer.write_object_value("owner", self.owner)
        writer.write_int_value("sharedGroupsCount", self.shared_groups_count)
        writer.write_int_value("sharedUsersCount", self.shared_users_count)
        writer.write_object_value("userAppMetadata", self.user_app_metadata)
        writer.write_additional_data_value(self.additional_data)
    

