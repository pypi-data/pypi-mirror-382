from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .advisor_action_request_action_parameters import AdvisorActionRequest_actionParameters

@dataclass
class AdvisorActionRequest(AdditionalDataHolder, Parsable):
    """
    The request with details to carry out an action on resource(s)
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The collection of parameters to carry out the action for a resource
    action_parameters: Optional[AdvisorActionRequest_actionParameters] = None
    # The name of the recommendation for which the action is triggered
    scenario: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AdvisorActionRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AdvisorActionRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AdvisorActionRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .advisor_action_request_action_parameters import AdvisorActionRequest_actionParameters

        from .advisor_action_request_action_parameters import AdvisorActionRequest_actionParameters

        fields: dict[str, Callable[[Any], None]] = {
            "actionParameters": lambda n : setattr(self, 'action_parameters', n.get_object_value(AdvisorActionRequest_actionParameters)),
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
        writer.write_object_value("actionParameters", self.action_parameters)
        writer.write_str_value("scenario", self.scenario)
        writer.write_additional_data_value(self.additional_data)
    

