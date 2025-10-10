from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .portal_scan_issues_category import PortalScanIssues_category
    from .portal_scan_issues_result import PortalScanIssues_result

@dataclass
class PortalScanIssues(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The category of the issue
    category: Optional[PortalScanIssues_category] = None
    # Detailed description of the issue
    description: Optional[str] = None
    # The specific issue identified
    issue: Optional[str] = None
    # URL for more information about the issue
    learn_more_url: Optional[str] = None
    # The result of the issue check
    result: Optional[PortalScanIssues_result] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PortalScanIssues:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PortalScanIssues
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PortalScanIssues()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .portal_scan_issues_category import PortalScanIssues_category
        from .portal_scan_issues_result import PortalScanIssues_result

        from .portal_scan_issues_category import PortalScanIssues_category
        from .portal_scan_issues_result import PortalScanIssues_result

        fields: dict[str, Callable[[Any], None]] = {
            "category": lambda n : setattr(self, 'category', n.get_enum_value(PortalScanIssues_category)),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "issue": lambda n : setattr(self, 'issue', n.get_str_value()),
            "learnMoreUrl": lambda n : setattr(self, 'learn_more_url', n.get_str_value()),
            "result": lambda n : setattr(self, 'result', n.get_enum_value(PortalScanIssues_result)),
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
        writer.write_enum_value("category", self.category)
        writer.write_str_value("description", self.description)
        writer.write_str_value("issue", self.issue)
        writer.write_str_value("learnMoreUrl", self.learn_more_url)
        writer.write_enum_value("result", self.result)
        writer.write_additional_data_value(self.additional_data)
    

