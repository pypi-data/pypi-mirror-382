from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .pay_as_you_go_state import PayAsYouGoState

@dataclass
class PowerAutomatePolicyModel(Parsable):
    """
    The Power Platform requests policies.
    """
    # The cloudFlowRunsPayAsYouGoState property
    cloud_flow_runs_pay_as_you_go_state: Optional[PayAsYouGoState] = None
    # The desktopFlowAttendedRunsPayAsYouGoState property
    desktop_flow_attended_runs_pay_as_you_go_state: Optional[PayAsYouGoState] = None
    # The desktopFlowUnattendedRunsPayAsYouGoState property
    desktop_flow_unattended_runs_pay_as_you_go_state: Optional[PayAsYouGoState] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PowerAutomatePolicyModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PowerAutomatePolicyModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PowerAutomatePolicyModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .pay_as_you_go_state import PayAsYouGoState

        from .pay_as_you_go_state import PayAsYouGoState

        fields: dict[str, Callable[[Any], None]] = {
            "cloudFlowRunsPayAsYouGoState": lambda n : setattr(self, 'cloud_flow_runs_pay_as_you_go_state', n.get_enum_value(PayAsYouGoState)),
            "desktopFlowAttendedRunsPayAsYouGoState": lambda n : setattr(self, 'desktop_flow_attended_runs_pay_as_you_go_state', n.get_enum_value(PayAsYouGoState)),
            "desktopFlowUnattendedRunsPayAsYouGoState": lambda n : setattr(self, 'desktop_flow_unattended_runs_pay_as_you_go_state', n.get_enum_value(PayAsYouGoState)),
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
        writer.write_enum_value("cloudFlowRunsPayAsYouGoState", self.cloud_flow_runs_pay_as_you_go_state)
        writer.write_enum_value("desktopFlowAttendedRunsPayAsYouGoState", self.desktop_flow_attended_runs_pay_as_you_go_state)
        writer.write_enum_value("desktopFlowUnattendedRunsPayAsYouGoState", self.desktop_flow_unattended_runs_pay_as_you_go_state)
    

