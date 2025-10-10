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
    from ....models.currency_report_v2 import CurrencyReportV2

class CurrencyReportsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /licensing/tenantCapacity/currencyReports
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new CurrencyReportsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/licensing/tenantCapacity/currencyReports?api-version={api%2Dversion}{&includeAllocations*,includeConsumptions*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[CurrencyReportsRequestBuilderGetQueryParameters]] = None) -> Optional[list[CurrencyReportV2]]:
        """
        Get the currency report for the tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[list[CurrencyReportV2]]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.currency_report_v2 import CurrencyReportV2

        return await self.request_adapter.send_collection_async(request_info, CurrencyReportV2, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[CurrencyReportsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get the currency report for the tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> CurrencyReportsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: CurrencyReportsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return CurrencyReportsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class CurrencyReportsRequestBuilderGetQueryParameters():
        """
        Get the currency report for the tenant.
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
            if original_name == "include_allocations":
                return "includeAllocations"
            if original_name == "include_consumptions":
                return "includeConsumptions"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

        # Flag indicating to include allocations.
        include_allocations: Optional[bool] = None

        # Flag indicating to include consumptions.
        include_consumptions: Optional[bool] = None

    
    @dataclass
    class CurrencyReportsRequestBuilderGetRequestConfiguration(RequestConfiguration[CurrencyReportsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

