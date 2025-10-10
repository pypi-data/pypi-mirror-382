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
    from .....models.application_install_state import ApplicationInstallState
    from .....models.application_package_continuation_response import ApplicationPackageContinuationResponse
    from .item.with_unique_name_item_request_builder import WithUniqueNameItemRequestBuilder

class ApplicationPackagesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /appmanagement/environments/{environmentId}/applicationPackages
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ApplicationPackagesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/appmanagement/environments/{environmentId}/applicationPackages?api-version={api%2Dversion}{&appInstallState*,lcid*}", path_parameters)
    
    def by_unique_name(self,unique_name: str) -> WithUniqueNameItemRequestBuilder:
        """
        Gets an item from the ApiSdk.appmanagement.environments.item.applicationPackages.item collection
        param unique_name: Package unique name.
        Returns: WithUniqueNameItemRequestBuilder
        """
        if unique_name is None:
            raise TypeError("unique_name cannot be null.")
        from .item.with_unique_name_item_request_builder import WithUniqueNameItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["uniqueName"] = unique_name
        return WithUniqueNameItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ApplicationPackagesRequestBuilderGetQueryParameters]] = None) -> Optional[ApplicationPackageContinuationResponse]:
        """
        Get the list of available application packages that are relevant in the context of a target environment. The client can filter the application packages based on install state (NotInstalled, Installed, All) and any other response parameters utilizing standard OData capabilities.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ApplicationPackageContinuationResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.application_package_continuation_response import ApplicationPackageContinuationResponse

        return await self.request_adapter.send_async(request_info, ApplicationPackageContinuationResponse, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ApplicationPackagesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get the list of available application packages that are relevant in the context of a target environment. The client can filter the application packages based on install state (NotInstalled, Installed, All) and any other response parameters utilizing standard OData capabilities.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> ApplicationPackagesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ApplicationPackagesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ApplicationPackagesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ApplicationPackagesRequestBuilderGetQueryParameters():
        """
        Get the list of available application packages that are relevant in the context of a target environment. The client can filter the application packages based on install state (NotInstalled, Installed, All) and any other response parameters utilizing standard OData capabilities.
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
            if original_name == "app_install_state":
                return "appInstallState"
            if original_name == "lcid":
                return "lcid"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

        # Application package install state.
        app_install_state: Optional[ApplicationInstallState] = None

        # Application package supported language ID.
        lcid: Optional[str] = None

    
    @dataclass
    class ApplicationPackagesRequestBuilderGetRequestConfiguration(RequestConfiguration[ApplicationPackagesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

