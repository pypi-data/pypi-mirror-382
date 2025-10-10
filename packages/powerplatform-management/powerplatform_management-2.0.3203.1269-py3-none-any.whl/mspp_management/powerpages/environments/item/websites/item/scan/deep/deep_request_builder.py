from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .get_latest_completed_report.get_latest_completed_report_request_builder import GetLatestCompletedReportRequestBuilder
    from .get_security_score.get_security_score_request_builder import GetSecurityScoreRequestBuilder
    from .start.start_request_builder import StartRequestBuilder

class DeepRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /powerpages/environments/{environmentId}/websites/{id}/scan/deep
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new DeepRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/powerpages/environments/{environmentId}/websites/{id}/scan/deep", path_parameters)
    
    @property
    def get_latest_completed_report(self) -> GetLatestCompletedReportRequestBuilder:
        """
        The getLatestCompletedReport property
        """
        from .get_latest_completed_report.get_latest_completed_report_request_builder import GetLatestCompletedReportRequestBuilder

        return GetLatestCompletedReportRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def get_security_score(self) -> GetSecurityScoreRequestBuilder:
        """
        The getSecurityScore property
        """
        from .get_security_score.get_security_score_request_builder import GetSecurityScoreRequestBuilder

        return GetSecurityScoreRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def start(self) -> StartRequestBuilder:
        """
        The start property
        """
        from .start.start_request_builder import StartRequestBuilder

        return StartRequestBuilder(self.request_adapter, self.path_parameters)
    

