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
    from .....models.resource_array_power_app import ResourceArrayPowerApp
    from .item.with_app_item_request_builder import WithAppItemRequestBuilder

class AppsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /powerapps/environments/{environmentId}/apps
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new AppsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/powerapps/environments/{environmentId}/apps?api-version={api%2Dversion}{&%24skiptoken*,%24top*}", path_parameters)
    
    def by_app(self,app: str) -> WithAppItemRequestBuilder:
        """
        Gets an item from the ApiSdk.powerapps.environments.item.apps.item collection
        param app: Name field of the PowerApp.
        Returns: WithAppItemRequestBuilder
        """
        if app is None:
            raise TypeError("app cannot be null.")
        from .item.with_app_item_request_builder import WithAppItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["app"] = app
        return WithAppItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[AppsRequestBuilderGetQueryParameters]] = None) -> Optional[ResourceArrayPowerApp]:
        """
        Returns a list of apps.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ResourceArrayPowerApp]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.resource_array_power_app import ResourceArrayPowerApp

        return await self.request_adapter.send_async(request_info, ResourceArrayPowerApp, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[AppsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a list of apps.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> AppsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: AppsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return AppsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class AppsRequestBuilderGetQueryParameters():
        """
        Returns a list of apps.
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
            if original_name == "skiptoken":
                return "%24skiptoken"
            if original_name == "top":
                return "%24top"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

        # Get next page of responses.
        skiptoken: Optional[str] = None

        # Number of apps in the response.
        top: Optional[int] = None

    
    @dataclass
    class AppsRequestBuilderGetRequestConfiguration(RequestConfiguration[AppsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

