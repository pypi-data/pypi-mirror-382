from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .advisor_recommendation_details import AdvisorRecommendationDetails

@dataclass
class AdvisorRecommendation(AdditionalDataHolder, Parsable):
    """
    Information for a recommendation
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Details for a recommendation
    details: Optional[AdvisorRecommendationDetails] = None
    # The recommendation name.
    scenario: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AdvisorRecommendation:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AdvisorRecommendation
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AdvisorRecommendation()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .advisor_recommendation_details import AdvisorRecommendationDetails

        from .advisor_recommendation_details import AdvisorRecommendationDetails

        fields: dict[str, Callable[[Any], None]] = {
            "details": lambda n : setattr(self, 'details', n.get_object_value(AdvisorRecommendationDetails)),
            "scenario": lambda n : setattr(self, 'scenario', n.get_str_value()),
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
        writer.write_object_value("details", self.details)
        writer.write_str_value("scenario", self.scenario)
        writer.write_additional_data_value(self.additional_data)
    

