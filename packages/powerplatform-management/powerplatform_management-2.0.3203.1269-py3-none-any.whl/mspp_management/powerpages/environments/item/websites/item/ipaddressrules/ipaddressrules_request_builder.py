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
    from .......models.allowed_ip_addresses_configuration import AllowedIpAddressesConfiguration
    from .......models.error_message import ErrorMessage
    from .......models.ip_address_configuration import IpAddressConfiguration

class IpaddressrulesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /powerpages/environments/{environmentId}/websites/{id}/ipaddressrules
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new IpaddressrulesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/powerpages/environments/{environmentId}/websites/{id}/ipaddressrules?api-version={api%2Dversion}", path_parameters)
    
    async def post(self,body: IpAddressConfiguration, request_configuration: Optional[RequestConfiguration[IpaddressrulesRequestBuilderPostQueryParameters]] = None) -> Optional[AllowedIpAddressesConfiguration]:
        """
        These IP addresses will be able to access the website.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[AllowedIpAddressesConfiguration]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from .......models.error_message import ErrorMessage

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ErrorMessage,
            "401": ErrorMessage,
            "404": ErrorMessage,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .......models.allowed_ip_addresses_configuration import AllowedIpAddressesConfiguration

        return await self.request_adapter.send_async(request_info, AllowedIpAddressesConfiguration, error_mapping)
    
    def to_post_request_information(self,body: IpAddressConfiguration, request_configuration: Optional[RequestConfiguration[IpaddressrulesRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        These IP addresses will be able to access the website.
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
    
    def with_url(self,raw_url: str) -> IpaddressrulesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: IpaddressrulesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return IpaddressrulesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class IpaddressrulesRequestBuilderPostQueryParameters():
        """
        These IP addresses will be able to access the website.
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
    class IpaddressrulesRequestBuilderPostRequestConfiguration(RequestConfiguration[IpaddressrulesRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

