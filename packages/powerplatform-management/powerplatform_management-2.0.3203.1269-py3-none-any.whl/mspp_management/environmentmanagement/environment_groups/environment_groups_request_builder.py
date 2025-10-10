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
    from ...models.environment_group import EnvironmentGroup
    from ...models.environment_group_response_with_odata_continuation import EnvironmentGroupResponseWithOdataContinuation
    from ...models.problem_details import ProblemDetails
    from .item.with_group_item_request_builder import WithGroupItemRequestBuilder

class EnvironmentGroupsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /environmentmanagement/environmentGroups
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new EnvironmentGroupsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/environmentmanagement/environmentGroups?api-version={api%2Dversion}", path_parameters)
    
    def by_group_id(self,group_id: str) -> WithGroupItemRequestBuilder:
        """
        Gets an item from the ApiSdk.environmentmanagement.environmentGroups.item collection
        param group_id: The group ID.
        Returns: WithGroupItemRequestBuilder
        """
        if group_id is None:
            raise TypeError("group_id cannot be null.")
        from .item.with_group_item_request_builder import WithGroupItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["groupId"] = group_id
        return WithGroupItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[EnvironmentGroupsRequestBuilderGetQueryParameters]] = None) -> Optional[EnvironmentGroupResponseWithOdataContinuation]:
        """
        List the environment groups.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[EnvironmentGroupResponseWithOdataContinuation]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ...models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.environment_group_response_with_odata_continuation import EnvironmentGroupResponseWithOdataContinuation

        return await self.request_adapter.send_async(request_info, EnvironmentGroupResponseWithOdataContinuation, error_mapping)
    
    async def post(self,body: EnvironmentGroup, request_configuration: Optional[RequestConfiguration[EnvironmentGroupsRequestBuilderPostQueryParameters]] = None) -> Optional[EnvironmentGroup]:
        """
        Create the environment group.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[EnvironmentGroup]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ...models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.environment_group import EnvironmentGroup

        return await self.request_adapter.send_async(request_info, EnvironmentGroup, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[EnvironmentGroupsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        List the environment groups.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: EnvironmentGroup, request_configuration: Optional[RequestConfiguration[EnvironmentGroupsRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Create the environment group.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> EnvironmentGroupsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: EnvironmentGroupsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return EnvironmentGroupsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class EnvironmentGroupsRequestBuilderGetQueryParameters():
        """
        List the environment groups.
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
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

    
    @dataclass
    class EnvironmentGroupsRequestBuilderGetRequestConfiguration(RequestConfiguration[EnvironmentGroupsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class EnvironmentGroupsRequestBuilderPostQueryParameters():
        """
        Create the environment group.
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
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

    
    @dataclass
    class EnvironmentGroupsRequestBuilderPostRequestConfiguration(RequestConfiguration[EnvironmentGroupsRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

