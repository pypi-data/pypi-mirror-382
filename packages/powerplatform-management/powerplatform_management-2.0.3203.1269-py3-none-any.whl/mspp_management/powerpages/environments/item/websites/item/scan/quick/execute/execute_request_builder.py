from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from .........models.error_message import ErrorMessage
    from .........models.portal_scan_issues import PortalScanIssues

class ExecuteRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /powerpages/environments/{environmentId}/websites/{id}/scan/quick/execute
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ExecuteRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/powerpages/environments/{environmentId}/websites/{id}/scan/quick/execute?api-version={api%2Dversion}{&lcid*}", path_parameters)
    
    async def post(self,request_configuration: Optional[RequestConfiguration[ExecuteRequestBuilderPostQueryParameters]] = None) -> Optional[list[PortalScanIssues]]:
        """
        Execute a quick scan for a Power Pages website.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[list[PortalScanIssues]]
        """
        request_info = self.to_post_request_information(
            request_configuration
        )
        from .........models.error_message import ErrorMessage

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ErrorMessage,
            "401": ErrorMessage,
            "404": ErrorMessage,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .........models.portal_scan_issues import PortalScanIssues

        return await self.request_adapter.send_collection_async(request_info, PortalScanIssues, error_mapping)
    
    def to_post_request_information(self,request_configuration: Optional[RequestConfiguration[ExecuteRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Execute a quick scan for a Power Pages website.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> ExecuteRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ExecuteRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ExecuteRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ExecuteRequestBuilderPostQueryParameters():
        """
        Execute a quick scan for a Power Pages website.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "api_version":
                return "api%2Dversion"
            if original_name == "lcid":
                return "lcid"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

        # Language code identifier (LCID) for the website.
        lcid: Optional[str] = None

    
    @dataclass
    class ExecuteRequestBuilderPostRequestConfiguration(RequestConfiguration[ExecuteRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

