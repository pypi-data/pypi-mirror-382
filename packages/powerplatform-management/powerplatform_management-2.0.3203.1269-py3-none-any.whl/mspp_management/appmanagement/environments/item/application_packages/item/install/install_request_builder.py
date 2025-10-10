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
    from .......models.instance_package import InstancePackage
    from .......models.tps_install_request_payload import TpsInstallRequestPayload

class InstallRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /appmanagement/environments/{environmentId}/applicationPackages/{uniqueName}/install
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new InstallRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/appmanagement/environments/{environmentId}/applicationPackages/{uniqueName}/install?api-version={api%2Dversion}", path_parameters)
    
    async def post(self,body: TpsInstallRequestPayload, request_configuration: Optional[RequestConfiguration[InstallRequestBuilderPostQueryParameters]] = None) -> Optional[InstancePackage]:
        """
        Trigger the installation of an application package, based on the package unique name, to be installed into a target environment. The client can also include a custom payload when requesting installation of an application package.
        param body: Payload to be sent during installation of the package
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[InstancePackage]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .......models.instance_package import InstancePackage

        return await self.request_adapter.send_async(request_info, InstancePackage, None)
    
    def to_post_request_information(self,body: TpsInstallRequestPayload, request_configuration: Optional[RequestConfiguration[InstallRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Trigger the installation of an application package, based on the package unique name, to be installed into a target environment. The client can also include a custom payload when requesting installation of an application package.
        param body: Payload to be sent during installation of the package
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
    
    def with_url(self,raw_url: str) -> InstallRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: InstallRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return InstallRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class InstallRequestBuilderPostQueryParameters():
        """
        Trigger the installation of an application package, based on the package unique name, to be installed into a target environment. The client can also include a custom payload when requesting installation of an application package.
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
    class InstallRequestBuilderPostRequestConfiguration(RequestConfiguration[InstallRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

