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
    from ......models.operation_execution_result import OperationExecutionResult
    from ......models.validation_response import ValidationResponse

class DisablemanagedRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /environmentmanagement/environments/{environment-id}/governancesetting/disablemanaged
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new DisablemanagedRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/environmentmanagement/environments/{environment%2Did}/governancesetting/disablemanaged?api-version={api%2Dversion}{&ValidateOnly*,ValidateProperties*}", path_parameters)
    
    async def post(self,request_configuration: Optional[RequestConfiguration[DisablemanagedRequestBuilderPostQueryParameters]] = None) -> Optional[OperationExecutionResult]:
        """
        Disables managed governance for the specified environment.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[OperationExecutionResult]
        """
        request_info = self.to_post_request_information(
            request_configuration
        )
        from ......models.validation_response import ValidationResponse

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ValidationResponse,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models.operation_execution_result import OperationExecutionResult

        return await self.request_adapter.send_async(request_info, OperationExecutionResult, error_mapping)
    
    def to_post_request_information(self,request_configuration: Optional[RequestConfiguration[DisablemanagedRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Disables managed governance for the specified environment.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json, text/plain;q=0.9")
        return request_info
    
    def with_url(self,raw_url: str) -> DisablemanagedRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: DisablemanagedRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return DisablemanagedRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class DisablemanagedRequestBuilderPostQueryParameters():
        """
        Disables managed governance for the specified environment.
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
            if original_name == "validate_only":
                return "ValidateOnly"
            if original_name == "validate_properties":
                return "ValidateProperties"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

        # The value which indicates whether the operation is a validated only request.Examples:    validateOnly=true with validateProperties non-empty: Validate only the listed properties, ignoring others even if present in the body.    validateOnly=true with empty/absent validateProperties: Validate the entire body (equivalent to full validation).    validateOnly=false or omitted: Process the full request(validate and execute).
        validate_only: Optional[bool] = None

        # The value which indicates what properties should be validated. Need to work together with ValidateOnly.Properties should be separated by ','.Example: "property1,property2,property3".
        validate_properties: Optional[str] = None

    
    @dataclass
    class DisablemanagedRequestBuilderPostRequestConfiguration(RequestConfiguration[DisablemanagedRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

