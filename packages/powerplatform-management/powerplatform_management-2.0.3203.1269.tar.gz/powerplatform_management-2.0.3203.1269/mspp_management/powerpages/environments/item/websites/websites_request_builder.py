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
    from .....models.error_message import ErrorMessage
    from .....models.new_website_request import NewWebsiteRequest
    from .....models.o_data_list_websites_dto import ODataListWebsitesDto
    from .item.websites_item_request_builder import WebsitesItemRequestBuilder

class WebsitesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /powerpages/environments/{environmentId}/websites
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WebsitesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/powerpages/environments/{environmentId}/websites?api-version={api%2Dversion}{&skip*}", path_parameters)
    
    def by_id(self,id: str) -> WebsitesItemRequestBuilder:
        """
        Gets an item from the ApiSdk.powerpages.environments.item.websites.item collection
        param id: Website unique identifier (ID).
        Returns: WebsitesItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.websites_item_request_builder import WebsitesItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["id"] = id
        return WebsitesItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WebsitesRequestBuilderGetQueryParameters]] = None) -> Optional[ODataListWebsitesDto]:
        """
        Get a list of all the websites in your environment.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ODataListWebsitesDto]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from .....models.error_message import ErrorMessage

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ErrorMessage,
            "401": ErrorMessage,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.o_data_list_websites_dto import ODataListWebsitesDto

        return await self.request_adapter.send_async(request_info, ODataListWebsitesDto, error_mapping)
    
    async def post(self,body: NewWebsiteRequest, request_configuration: Optional[RequestConfiguration[WebsitesRequestBuilderPostQueryParameters]] = None) -> None:
        """
        Trigger the creation of a new website.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from .....models.error_message import ErrorMessage

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ErrorMessage,
            "401": ErrorMessage,
            "404": ErrorMessage,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WebsitesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get a list of all the websites in your environment.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: NewWebsiteRequest, request_configuration: Optional[RequestConfiguration[WebsitesRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Trigger the creation of a new website.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, '{+baseurl}/powerpages/environments/{environmentId}/websites?api-version={api%2Dversion}', self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> WebsitesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WebsitesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WebsitesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class WebsitesRequestBuilderGetQueryParameters():
        """
        Get a list of all the websites in your environment.
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
            if original_name == "skip":
                return "skip"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

        # The number of items to skip before returning the remaining items.
        skip: Optional[str] = None

    
    @dataclass
    class WebsitesRequestBuilderGetRequestConfiguration(RequestConfiguration[WebsitesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WebsitesRequestBuilderPostQueryParameters():
        """
        Trigger the creation of a new website.
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
    class WebsitesRequestBuilderPostRequestConfiguration(RequestConfiguration[WebsitesRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

