from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class AdvisorRecommendationDetails(AdditionalDataHolder, Parsable):
    """
    Details for a recommendation
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Time when the recommendation will be refreshed again
    expected_next_refresh_timestamp: Optional[datetime.datetime] = None
    # Time when the recommendation was refreshed
    last_refreshed_timestamp: Optional[datetime.datetime] = None
    # The number of resources
    resource_count: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AdvisorRecommendationDetails:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AdvisorRecommendationDetails
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AdvisorRecommendationDetails()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "expectedNextRefreshTimestamp": lambda n : setattr(self, 'expected_next_refresh_timestamp', n.get_datetime_value()),
            "lastRefreshedTimestamp": lambda n : setattr(self, 'last_refreshed_timestamp', n.get_datetime_value()),
            "resourceCount": lambda n : setattr(self, 'resource_count', n.get_int_value()),
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
        writer.write_datetime_value("expectedNextRefreshTimestamp", self.expected_next_refresh_timestamp)
        writer.write_datetime_value("lastRefreshedTimestamp", self.last_refreshed_timestamp)
        writer.write_int_value("resourceCount", self.resource_count)
        writer.write_additional_data_value(self.additional_data)
    

